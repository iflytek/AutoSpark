import importlib
from datetime import datetime, timedelta

from sqlalchemy.orm import sessionmaker

import autospark.worker
from autospark.agent.agent_tool_step_handler import AgentToolStepHandler
from autospark.agent.agent_iteration_step_handler import AgentIterationStepHandler
import remote_pdb
from autospark.agent.auto_spark import AutoSpark
from autospark.config.config import get_config
from autospark.helper.encyption_helper import decrypt_data
from autospark.lib.logger import logger
from autospark.llms.google_palm import GooglePalm
from autospark.llms.llm_model_factory import get_model
from autospark.models.agent import Agent
from autospark.models.agent_config import AgentConfiguration
from autospark.models.agent_execution import AgentExecution
from autospark.models.agent_execution_config import AgentExecutionConfiguration
from autospark.models.agent_execution_feed import AgentExecutionFeed
from autospark.models.agent_execution_permission import AgentExecutionPermission
from autospark.models.workflows.agent_workflow_step import AgentWorkflowStep
from autospark.models.configuration import Configuration
from autospark.models.db import connect_db
from autospark.models.resource import Resource
from autospark.models.tool import Tool
from autospark.models.tool_config import ToolConfig
from autospark.resource_manager.file_manager import FileManager
from autospark.resource_manager.resource_summary import ResourceSummarizer
from autospark_kit.tools.base_tool import BaseToolkitConfiguration
from autospark.tools.resource.query_resource import QueryResourceTool
from autospark.tools.thinking.tools import ThinkingTool
from autospark.tools.tool_response_query_manager import ToolResponseQueryManager
from autospark.types.model_source_types import ModelSourceType
from autospark.types.vector_store_types import VectorStoreType
from autospark.vector_store.embedding.openai import OpenAiEmbedding
from autospark.vector_store.vector_factory import VectorFactory
from autospark.apm.event_handler import EventHandler

# from autospark.helper.tool_helper import get_tool_config_by_key

engine = connect_db()
Session = sessionmaker(bind=engine)


class AgentExecutor:
    def execute_next_step(self, agent_execution_id):
        global engine
        # try:
        engine.dispose()
        session = Session()
        try:
            agent_execution = session.query(AgentExecution).filter(AgentExecution.id == agent_execution_id).first()
            '''Avoiding running old agent executions'''
            if agent_execution and agent_execution.created_at < datetime.utcnow() - timedelta(days=1):
                logger.error("Older agent execution found, skipping execution")
                return

            agent = session.query(Agent).filter(Agent.id == agent_execution.agent_id).first()
            agent_config = Agent.fetch_configuration(session, agent.id)
            if agent.is_deleted or (
                    agent_execution.status != "RUNNING" and agent_execution.status != "WAITING_FOR_PERMISSION"):
                logger.error(f"Agent execution stopped. {agent.id}: {agent_execution.status}")
                return

            organisation = Agent.find_org_by_agent_id(session, agent_id=agent.id)
            if self._check_for_max_iterations(session, organisation.id, agent_config, agent_execution_id):
                logger.error(f"Agent execution stopped. Max iteration exceeded. {agent.id}: {agent_execution.status}")
                return

            model_api_key = AgentConfiguration.get_model_api_key(session, agent_execution.agent_id,
                                                                 agent_config["model"])
            model_api_secret = AgentConfiguration.get_model_api_secret(session, agent_execution.agent_id,
                                                                       agent_config["model"])
            model_app_id = AgentConfiguration.get_model_app_id(session, agent_execution.agent_id,
                                                               agent_config["model"])
            model_llm_source = ModelSourceType.get_model_source_from_model(agent_config["model"]).value
            try:
                vector_store_type = VectorStoreType.get_vector_store_type(agent_config["LTM_DB"])
                memory = VectorFactory.get_vector_storage(vector_store_type, "super-agent-index1",
                                                          AgentExecutor.get_embedding(model_llm_source, model_api_key))
            except:
                logger.info("Unable to setup the pinecone connection...")
                memory = None

            agent_workflow_step = session.query(AgentWorkflowStep).filter(
                AgentWorkflowStep.id == agent_execution.current_agent_step_id).first()
            try:
                if agent_workflow_step.action_type == "TOOL":
                    tool_step_handler = AgentToolStepHandler(session,
                                                             llm=get_model(model=agent_config["model"],
                                                                           api_key=model_api_key,
                                                                           api_secret=model_api_secret,
                                                                           app_id=model_app_id),
                                                             agent_id=agent.id, agent_execution_id=agent_execution_id,
                                                             memory=memory)
                    tool_step_handler.execute_step()
                elif agent_workflow_step.action_type == "ITERATION_WORKFLOW":
                    iteration_step_handler = AgentIterationStepHandler(session,
                                                                       llm=get_model(model=agent_config["model"],
                                                                                     api_key=model_api_key,
                                                                                     api_secret=model_api_secret,
                                                                                     app_id=model_app_id)
                                                                       , agent_id=agent.id,
                                                                       agent_execution_id=agent_execution_id,
                                                                       memory=memory)
                    iteration_step_handler.execute_step()
            except Exception as e:
                logger.error("Exception in executing the step: {}".format(e))
                autospark.worker.execute_agent.apply_async((agent_execution_id, datetime.now()), countdown=15)
                return

            agent_execution = session.query(AgentExecution).filter(AgentExecution.id == agent_execution_id).first()
            if agent_execution.status == "COMPLETED" or agent_execution.status == "WAITING_FOR_PERMISSION":
                logger.info("Agent Execution is completed or waiting for permission")
                session.close()
                return
            autospark.worker.execute_agent.apply_async((agent_execution_id, datetime.now()), countdown=10)
            # superagi.worker.execute_agent.delay(agent_execution_id, datetime.now())
        finally:
            session.close()
            engine.dispose()

    def execute_next_action(self, agent_execution_id):
        """
        Execute the next action of the agent execution.

        Args:
            agent_execution_id (int): The ID of the agent execution.

        Returns:
            None
        """
        global engine
        # try:
        engine.dispose()
        session = Session()
        agent_execution = session.query(AgentExecution).filter(AgentExecution.id == agent_execution_id).first()
        '''Avoiding running old agent executions'''
        if agent_execution.created_at < datetime.utcnow() - timedelta(days=1):
            return
        agent = session.query(Agent).filter(Agent.id == agent_execution.agent_id).first()
        # if agent_execution.status == "PAUSED" or agent_execution.status == "TERMINATED" or agent_execution == "COMPLETED":
        #     return
        if agent_execution.status != "RUNNING" and agent_execution.status != "WAITING_FOR_PERMISSION":
            return

        if not agent:
            return "Agent Not found"

        tools = [
            ThinkingTool()
        ]

        parsed_config = Agent.fetch_configuration(session, agent.id)
        parsed_execution_config = AgentExecutionConfiguration.fetch_configuration(session, agent_execution)
        max_iterations = (parsed_config["max_iterations"])
        total_calls = agent_execution.num_of_calls
        organisation = AgentExecutor.get_organisation(agent_execution, session)

        if max_iterations <= total_calls:
            db_agent_execution = session.query(AgentExecution).filter(AgentExecution.id == agent_execution_id).first()
            db_agent_execution.status = "ITERATION_LIMIT_EXCEEDED"
            session.commit()
            EventHandler(session=session).create_event('run_iteration_limit_crossed',
                                                       {'agent_execution_id': db_agent_execution.id,
                                                        'name': db_agent_execution.name,
                                                        'tokens_consumed': db_agent_execution.num_of_tokens,
                                                        "calls": db_agent_execution.num_of_calls},
                                                       db_agent_execution.agent_id, organisation.id)
            logger.info("ITERATION_LIMIT_CROSSED")
            return "ITERATION_LIMIT_CROSSED"

        parsed_config["agent_execution_id"] = agent_execution.id

        model_api_key = AgentExecutor.get_model_api_key_from_execution(parsed_config["model"], agent_execution, session)
        model_api_secret = AgentExecutor.get_model_api_secret_from_execution(parsed_config["model"], agent_execution,
                                                                             session)
        model_app_id = AgentExecutor.get_model_app_id_from_execution(parsed_config["model"], agent_execution, session)

        model_llm_source = ModelSourceType.get_model_source_from_model(parsed_config["model"]).value
        organisation = AgentExecutor.get_organisation(agent_execution, session)
        try:
            if parsed_config["LTM_DB"] == "Pinecone":
                memory = VectorFactory.get_vector_storage(VectorStoreType.PINECONE, "super-agent-index1",
                                                          AgentExecutor.get_embedding(model_llm_source, model_api_key))
            else:
                memory = VectorFactory.get_vector_storage("PineCone", "super-agent-index1",
                                                          AgentExecutor.get_embedding(model_llm_source, model_api_key))
        except:
            logger.info("Unable to setup the pinecone connection...")
            memory = None

        user_tools = session.query(Tool).filter(Tool.id.in_(parsed_config["tools"])).all()
        for tool in user_tools:
            tool = AgentExecutor.create_object(tool, session)
            tools.append(tool)

        resource_summary = self.get_agent_resource_summary(agent_id=agent.id, session=session,
                                                           model_llm_source=model_llm_source,
                                                           default_summary=parsed_config.get("resource_summary"))
        if resource_summary is not None:
            tools.append(QueryResourceTool())

        tools = self.set_default_params_tools(tools, parsed_config, parsed_execution_config, agent_execution.agent_id,
                                              model_api_key=model_api_key,
                                              model_api_secret=model_api_secret,
                                              model_app_id=model_app_id,
                                              resource_description=resource_summary,
                                              session=session)

        spawned_agent = AutoSpark(ai_name=parsed_config["name"], ai_role=parsed_config["description"],
                                  llm=get_model(model=parsed_config["model"], api_key=model_api_key,
                                                api_secret=model_api_secret, app_id=model_app_id), tools=tools,
                                  memory=memory,
                                  agent_config=parsed_config,
                                  agent_execution_config=parsed_execution_config)

        try:
            self.handle_wait_for_permission(agent_execution, spawned_agent, session)
        except ValueError:
            return

        agent_workflow_step = session.query(AgentWorkflowStep).filter(
            AgentWorkflowStep.id == agent_execution.current_step_id).first()

        try:
            response = spawned_agent.execute(agent_workflow_step)
        except RuntimeError as e:
            # If our execution encounters an error we return and attempt to retry
            logger.error("Error executing the agent:", e)
            autospark.worker.execute_agent.apply_async((agent_execution_id, datetime.now()), countdown=15)
            session.close()
            return

        if "retry" in response and response["retry"]:
            if "result" in response and response["result"] == "RATE_LIMIT_EXCEEDED":
                autospark.worker.execute_agent.apply_async((agent_execution_id, datetime.now()), countdown=60)
            else:
                autospark.worker.execute_agent.apply_async((agent_execution_id, datetime.now()), countdown=15)

            session.close()
            return

        agent_execution.current_step_id = agent_workflow_step.next_step_id
        session.commit()
        if response["result"] == "COMPLETE":
            db_agent_execution = session.query(AgentExecution).filter(AgentExecution.id == agent_execution_id).first()
            db_agent_execution.status = "COMPLETED"
            session.commit()
            EventHandler(session=session).create_event('run_completed', {'agent_execution_id': db_agent_execution.id,
                                                                         'name': db_agent_execution.name,
                                                                         'tokens_consumed': db_agent_execution.num_of_tokens,
                                                                         "calls": db_agent_execution.num_of_calls},
                                                       db_agent_execution.agent_id, organisation.id)
        elif response["result"] == "WAITING_FOR_PERMISSION":
            db_agent_execution = session.query(AgentExecution).filter(AgentExecution.id == agent_execution_id).first()
            db_agent_execution.status = "WAITING_FOR_PERMISSION"
            db_agent_execution.permission_id = response.get("permission_id", None)
            session.commit()
        else:
            logger.info(f"Starting next job for agent execution id: {agent_execution_id}")
            autospark.worker.execute_agent.delay(agent_execution_id, datetime.now())

        session.close()
        engine.dispose()

    @classmethod
    def get_embedding(cls, model_source, model_api_key):
        if "OpenAi" in model_source:
            return OpenAiEmbedding(api_key=model_api_key)
        if "Google" in model_source:
            return GooglePalm(api_key=model_api_key)
        return None

    def _check_for_max_iterations(self, session, organisation_id, agent_config, agent_execution_id):
        db_agent_execution = session.query(AgentExecution).filter(AgentExecution.id == agent_execution_id).first()
        if agent_config["max_iterations"] <= db_agent_execution.num_of_calls:
            db_agent_execution.status = "ITERATION_LIMIT_EXCEEDED"

            EventHandler(session=session).create_event('run_iteration_limit_crossed',
                                                       {'agent_execution_id': db_agent_execution.id,
                                                        'name': db_agent_execution.name,
                                                        'tokens_consumed': db_agent_execution.num_of_tokens,
                                                        "calls": db_agent_execution.num_of_calls},
                                                       db_agent_execution.agent_id, organisation_id)
            session.commit()
            logger.info("ITERATION_LIMIT_CROSSED")
            return True
        return False

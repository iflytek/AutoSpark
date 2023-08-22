from fastapi import HTTPException, Depends


from fastapi import APIRouter
from fastapi import Depends
from fastapi.security import HTTPBearer
from fastapi_sqlalchemy import db
from datetime import datetime

from autospark.helper.auth import get_user_organisation, get_current_user
from autospark.models.workflows.agent_workflow_step import AgentWorkflowStep
from sqlalchemy import or_
from pydantic import BaseModel
from autospark.helper.auth import check_auth, get_user_organisation
from fastapi_jwt_auth import AuthJWT

router = APIRouter()


class AgentWorkflowStepOut(BaseModel):
    id: int
    agent_workflow_id: int
    unique_id: int
    prompt: str
    variables: str
    output_type: str
    step_type: str
    next_step_id: int
    history_enabled: bool
    completion_prompt: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class AgentWorkflowStepIn(BaseModel):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)

    agent_workflow_id: int
    unique_id: int
    prompt: str
    variables: str
    output_type: str
    step_type: str
    next_step_id: int
    history_enabled: bool
    completion_prompt: str

    class Config:
        orm_mode = True


@router.get("/list/{workflow_id}", dependencies=[Depends(HTTPBearer())],status_code=201)
def list_workflow_steps(workflow_id: int, organisation=Depends(get_user_organisation), user=Depends(get_current_user)):
    """
    Lists agent workflow_steps.

    Args:
        organisation: User's organisation.
        user: Current User.
    Returns:
        list: A list of dictionaries representing the agent workflow_steps.

    """
    workflow_steps = db.session.query(AgentWorkflowStep).filter(
        or_(AgentWorkflowStep.agent_workflow_id == workflow_id)).all()

    output_json = []
    for workflow_step in workflow_steps:
        output_json.append(workflow_step.to_dict())
    return output_json


@router.post("/create", status_code=201,dependencies=[Depends(HTTPBearer())], response_model=AgentWorkflowStepOut)
def create_workflow_step(workflow_template: AgentWorkflowStepIn):
    """

    Args:
    agent_workflow_id = Column(Integer)
    unique_id = Column(String)
    prompt = Column(Text)
    variables = Column(Text)
    output_type = Column(String)
    step_type = Column(String) # TRIGGER, NORMAL
    next_step_id = Column(Integer)
    history_enabled = Column(Boolean)
    completion_prompt = Column(Text)

    Returns:

    """
    wf = AgentWorkflowStep(agent_workflow_id=workflow_template.agent_workflow_id,
                           prompt=workflow_template.prompt,
                           unique_id=workflow_template.unique_id,
                           variables=workflow_template.variables,
                           output_type=workflow_template.output_type,
                           step_type=workflow_template.step_type,
                           next_step_id=workflow_template.next_step_id,
                           history_enabled=workflow_template.history_enabled,
                           completion_prompt=workflow_template.completion_prompt)
    db.session.add(wf)
    db.session.commit()

    return wf


@router.put("/update/{workflow_step_id}", dependencies=[Depends(HTTPBearer())],status_code=201, response_model=AgentWorkflowStepOut)
def update_workflow_step(workflow_step_id: int, workflow_template: AgentWorkflowStepIn):
    workflowstep = db.session.query(AgentWorkflowStep).filter(AgentWorkflowStep.id == workflow_step_id).first()
    if not workflowstep:
        raise HTTPException(status_code=404, detail="WorkflowStep ot found")
    workflowstep.agent_workflow_id = workflow_template.agent_workflow_id
    workflowstep.prompt = workflow_template.prompt
    workflowstep.unique_id = workflow_template.unique_id
    workflowstep.variables = workflow_template.variables
    workflowstep.output_type = workflow_template.output_type
    workflowstep.step_type = workflow_template.step_type
    workflowstep.next_step_id = workflow_template.next_step_id
    workflowstep.history_enabled = workflow_template.history_enabled
    workflowstep.completion_prompt = workflow_template.completion_prompt
    db.session.add(workflowstep)
    db.session.commit()


@router.get("/get/{workflow_step_id}",dependencies=[Depends(HTTPBearer())],)
def get_workflow_step(workflow_step_id: int):
    """
        Get the details of a specific workflow_step

        Args:
            workflow_step_id (int): The ID of the workflow step .

        Returns:
            dict: The details of the agent template.

        Raises:
            HTTPException (status_code=404): If the agent template is not found.
    """
    workflowstep = db.session.query(AgentWorkflowStep).filter(AgentWorkflowStep.id == workflow_step_id).first()
    if not workflowstep:
        raise HTTPException(status_code=404, detail="WorkflowStep   not found")
    wf = workflowstep.to_dict()
    return wf


@router.delete("/{workflow_step_id}", dependencies=[Depends(HTTPBearer())],status_code=200)
def delete_step(workflow_step_id: int, Authorize: AuthJWT = Depends(check_auth)):
    """
        Args:
            agent_id (int): Identifier of the Agent to delete
        Returns:
            A dictionary containing a "success" key with the value True to indicate a successful delete.
        Raises:
            HTTPException (Status Code=404): If the Agent or associated Project is not found or deleted already.
    """

    workflow_step = db.session.query(AgentWorkflowStep).filter(AgentWorkflowStep.id == workflow_step_id).first()

    if not workflow_step:
        raise HTTPException(status_code=404, detail="step not found")
    # Deletion Procedure
    db.session.delete(workflow_step)
    db.session.commit()

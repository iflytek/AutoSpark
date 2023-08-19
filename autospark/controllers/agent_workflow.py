from fastapi import APIRouter, HTTPException
from fastapi import Depends
from fastapi.security import HTTPBearer
from fastapi_sqlalchemy import db
from datetime import datetime

from autospark.helper.auth import get_user_organisation, get_current_user
from autospark.models.agent_workflow import AgentWorkflow
from sqlalchemy import or_, and_
from pydantic import BaseModel

router = APIRouter()


class AgentWorkflowOut(BaseModel):
    id: int
    organisation_id: int
    user_id: int
    name: str
    description: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class AgentWorkflowIn(BaseModel):
    organisation_id: int
    user_id: int
    name: str
    description: str
    marketplace_template_id: int

    class Config:
        orm_mode = True


@router.get("/list", dependencies=[Depends(HTTPBearer())],status_code=201)
def list_workflows(organisation=Depends(get_user_organisation), user=Depends(get_current_user)):
    """
    Lists agent workflows.

    Args:
        organisation: User's organisation.
        user: Current User.
    Returns:
        list: A list of dictionaries representing the agent workflows.

    """
    workflows = db.session.query(AgentWorkflow).filter(
        or_(AgentWorkflow.user_id == "system", AgentWorkflow.user_id == user.id, )).all()

    output_json = []
    for workflow in workflows:
        output_json.append(workflow.to_dict())
    return output_json


@router.post("/create", status_code=201,dependencies=[Depends(HTTPBearer())], response_model=AgentWorkflowOut)
def create_workflow(workflow_template: AgentWorkflowIn, user=Depends(get_current_user)):
    """

    Args:
        user:

    Returns:

    """
    wf = AgentWorkflow(user_id=user.id,
                       name=workflow_template.name,
                       organisation_id=workflow_template.organisation_id,
                       description=workflow_template.description)
    db.session.add(wf)
    db.session.commit()

    return wf


@router.put("/update/{workflow_id}", dependencies=[Depends(HTTPBearer())],status_code=201, response_model=AgentWorkflowOut)
def update_workflow(workflow_id: int, workflow_template: AgentWorkflowIn, user=Depends(get_current_user)):
    """

    Args:
        user:

    Returns:

    """
    workflow = db.session.query(AgentWorkflow).filter(
        and_(AgentWorkflow.id == workflow_id, AgentWorkflow.user_id == user.id)).first()
    if not workflow:
        raise HTTPException(status_code=404, detail="WorkflowStep ot found")
    if workflow_template.organisation_id:
        workflow.organisation_id = workflow_template.organisation_id
    if workflow_template.name:
        workflow.name = workflow_template.name
    if workflow_template.description:
        workflow.description = workflow_template.description

    db.session.add(workflow)
    db.session.commit()
    return workflow


@router.delete("/{workflow_id}",dependencies=[Depends(HTTPBearer())], status_code=201)
def delete_workflow(workflow_id: int, user=Depends(get_current_user)):
    """

    Args:
        user:

    Returns:

    """
    workflow = db.session.query(AgentWorkflow).filter(
        and_(AgentWorkflow.id == workflow_id,AgentWorkflow.user_id== user.id)).first()
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    if workflow.user_id != user.id:
        raise HTTPException(status_code=401, detail="No permssion to delete")

    db.session.delete(workflow)
    db.session.commit()

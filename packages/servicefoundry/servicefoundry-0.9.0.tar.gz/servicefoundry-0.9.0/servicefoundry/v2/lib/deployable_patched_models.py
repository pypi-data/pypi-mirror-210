from typing import Union

from pydantic import Field, conint, constr

from servicefoundry.auto_gen import models
from servicefoundry.lib.model.entity import Deployment
from servicefoundry.v2.lib.deploy import deploy_component


class Service(models.Service):
    type: constr(regex=r"service") = "service"
    resources: models.Resources = Field(default_factory=models.Resources)
    # This is being patched because cue export marks this as a "number"
    replicas: Union[conint(ge=1, le=20), models.Autoscaling] = Field(
        1,
        description="+label=Replicas\n+usage=Replicas of service you want to run\n+icon=fa-clone\n+sort=3",
    )

    class Config:
        extra = "forbid"

    def deploy(self, workspace_fqn: str, wait: bool = True) -> Deployment:
        return deploy_component(component=self, workspace_fqn=workspace_fqn, wait=wait)


class Job(models.Job):
    type: constr(regex=r"job") = "job"
    resources: models.Resources = Field(default_factory=models.Resources)

    class Config:
        extra = "forbid"

    def deploy(self, workspace_fqn: str, wait: bool = True) -> Deployment:
        return deploy_component(component=self, workspace_fqn=workspace_fqn, wait=wait)


class ModelDeployment(models.ModelDeployment):
    type: constr(regex=r"model-deployment") = "model-deployment"
    resources: models.Resources = Field(default_factory=models.Resources)

    class Config:
        extra = "forbid"

    def deploy(self, workspace_fqn: str, wait: bool = True) -> Deployment:
        return deploy_component(component=self, workspace_fqn=workspace_fqn, wait=wait)


class Application(models.Application):
    class Config:
        extra = "forbid"

    def deploy(self, workspace_fqn: str, wait: bool = True) -> Deployment:
        return deploy_component(
            component=self.__root__, workspace_fqn=workspace_fqn, wait=wait
        )

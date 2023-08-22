from autospark_kit.tools.base_tool import BaseTool
from pydantic import BaseModel, Field
from typing import Type
from pyartifactory import Artifactory
from pyartifactory.exception import RepositoryNotFoundException


def list(repourl, user_name, apikey, repo, repo_path):
    art = Artifactory(url=repourl,
                      auth=(user_name, apikey),
                      api_version=1)
    if not user_name or not apikey:
        print("no valid key ")
        return []
    try:
        repo = art.repositories.get_repo(repo)
    except RepositoryNotFoundException as e:
        print('not find this repo.')
        return []
    l = []
    artifacts = art.artifacts.list(repo_path)
    for a in artifacts.files:
        if a.uri.endswith("manifest.json"):
            items = a.uri.split("/")
            repo_path = '/'.join(items[0:-2]) + ":" + items[-2]
            l.append(repo_path.lstrip("/"))
    return l


class ListImageTagsInput(BaseModel):
    repo_path: str = Field(..., description="A valid docker repo path")


class DockerImageListTool(BaseTool):
    """
    DockerImageListTool
    """
    name: str = "Docker Image Tags List Tool"
    args_schema: Type[BaseModel] = ListImageTagsInput
    description: str = "List the specified repo's tags "

    def _execute(self, repo_path: str = None):
        artiurl = self.get_tool_config('ArtifactoryUrl')
        user = self.get_tool_config("DockerUsername")
        apikey = self.get_tool_config("DockerPassword")
        repo = repo_path.split("/", 1)[0]

        return list(artiurl, user, apikey, repo, repo_path)

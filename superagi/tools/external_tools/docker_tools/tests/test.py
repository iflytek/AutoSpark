from pyartifactory import Artifactory
from pyartifactory.exception import RepositoryNotFoundException

art = Artifactory(url="https://artifacts.iflytek.com",
                  auth=('', ''),
                  api_version=2)

try:
    repo = art.repositories.get_repo("docker-private/atp")
except RepositoryNotFoundException as e:
    print('not find')

artifacts = art.artifacts.list("docker-private/atp")
for a in artifacts.files:
    if a.uri.endswith("manifest.json"):
        items = a.uri.split("/")
        repo_path =  '/'.join(items[0:-2]) + ":" + items[-2]
        print(repo_path.lstrip("/"))

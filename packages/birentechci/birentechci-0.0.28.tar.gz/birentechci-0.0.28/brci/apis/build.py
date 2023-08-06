from ..config import Conf
from ..schemas import jenkins as JenkinsSchema

from .client import Client

cClient = Client(Conf.vV2Server.host, port=Conf.vV2Server.port)


def add_build_result(body: JenkinsSchema.BuildResult):
    url = "/api/build/"
    resp = cClient.post(url, json=body.dict())
    data = resp.json()
    if "code" in data and data["code"] == 0:
        print("上传成功", body)
        return
    else:
        print("上传失败", body, data)
        exit(1)


def update_build_status(body: JenkinsSchema.BuildResult):
    url = "/api/build/"
    resp = cClient.put(url, json=body.dict())
    data = resp.json()
    if "code" in data and data["code"] == 0:
        print("更新成功", body)
        return
    else:
        print("上传失败", body, data)
        exit(1)


def patch_build_status(body: JenkinsSchema.BuildResult):
    url = "/api/build/"
    resp = cClient.patch(url, json=body.dict())
    data = resp.json()
    if "code" in data and data["code"] == 0:
        print("更新成功", body)
        return
    else:
        print("上传失败", body, data)
        exit(1)


def query_build_result(query: JenkinsSchema.QueryBuildResult):
    url = "/api/build/"
    resp = cClient.get(url, params=query.dict())
    dictData = resp.json()
    if "code" in dictData and dictData["code"] == 0:
        print(f'拉取成功:\n resp:{dictData["data"]["data"]}')
        out = dictData["data"]["data"]
        return out
    else:
        print(f"拉取失败:\n resp:{dictData}")
        exit(1)

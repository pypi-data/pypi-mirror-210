from ..config import Conf
from ..schemas import jenkins as JenkinsSchema

from .client import Client

cClient = Client(Conf.vV2Server.host, port=Conf.vV2Server.port)


def add_pref_result(body: JenkinsSchema.BuildResult):
    url = "/api/perf/"
    resp = cClient.post(url, json=body.dict())
    data = resp.json()
    if "code" in data and data["code"] == 0:
        print("上传成功", body)
        return
    else:
        print("上传失败", body, data)
        exit(1)


def update_pref_result(body: JenkinsSchema.BuildResult):
    url = "/api/perf/"
    resp = cClient.put(url, json=body.dict())
    data = resp.json()
    if "code" in data and data["code"] == 0:
        print("上传成功", body)
        return
    else:
        print("上传失败", body, data)
        exit(1)


def patch_pref_result(body: JenkinsSchema.BuildResult):
    url = "/api/perf/"
    resp = cClient.patch(url, json=body.dict())
    data = resp.json()
    if "code" in data and data["code"] == 0:
        print("更新成功", body)
        return
    else:
        print("更新失败", body, data)
        exit(1)


def query_perf_result(query: JenkinsSchema.QueryBuildResult):
    url = "/api/perf/"
    resp = cClient.get(url, params=query.dict())
    dictData = resp.json()
    if "code" in dictData and dictData["code"] == 0:
        print("拉取成功", dictData)
        out = dictData["data"]["data"]
        return out
    else:
        print("拉取失败", dictData)
        exit(1)


def pre_result(query: JenkinsSchema.QueryBuildResult):
    url = "/api/perf"
    resp = cClient.get(url, params=query.dict())
    dictData = resp.json()
    if "code" in dictData and dictData["code"] == 0:
        print("拉取成功", dictData)
        out = dictData["data"]["data"]
        return out
    else:
        print("拉取失败", dictData)
        exit(1)


def base_result(query: JenkinsSchema.QueryBuildResult):
    url = "/api/perf"
    resp = cClient.get(url, params=query.dict())
    dictData = resp.json()
    if "code" in dictData and dictData["code"] == 0:
        print("拉取成功")
        # print(dictData)
        out = dictData["data"]["data"]
        return out
    else:
        print("拉取失败", dictData)
        exit(1)

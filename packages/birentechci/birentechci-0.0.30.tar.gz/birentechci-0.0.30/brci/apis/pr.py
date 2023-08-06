from ..config import Conf
from ..schemas import pull_request as PullRequestSchema
from ..schemas import pull_request_job as PullRequestJobSchema

from .client import Client

cClient = Client(Conf.vV2Server.host, port=Conf.vV2Server.port)


# 添加pr数据
def add_Merge_Request(body: PullRequestSchema.PullRequest):
    url = "/api/pr/add"
    resp = cClient.post(url, json=body.dict())
    data = resp.json()
    if "code" in data and data["code"] == 0:
        print("pr上传成功", body)
        return
    else:
        print("pr上传失败", body, data)
        exit(1)


# 更新pr数据
def update_Merge_Request(body: PullRequestSchema.UpdatePullRequest):
    url = "api/pr/udpate"
    resp = cClient.put(url, json=body.dict())
    date = resp.json()
    if "code" in date and date["code"] == 0:
        print("pr更新成功", body)
        return
    else:
        print("pr更新失败", body, date)
        exit(1)


# 添加pr job数据
def add_Merge_Request_job(body: PullRequestJobSchema.PullRequestJob):
    url = "/api/pr-job/add"
    resp = cClient.post(url, json=body.dict())
    data = resp.json()
    if "code" in data and data["code"] == 0:
        print("pr job上传成功", body)
        return
    else:
        print("pr job上传失败", body, data)
        exit(1)

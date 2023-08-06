from ..apis import pr as PRApi
from ..schemas import pull_request as PullRequestSchema
from ..schemas import pull_request_job as PullRequestJobSchema

from ..utils.csv_utils import load_csv
from ..utils.json_utils import load_json
from ..utils.xml_utils import load_xml


# 获取pr数据
def get_Merge_Request(path: str):
    if ".csv" in path:
        pr = {"csv": load_csv(path)}
    elif ".json" in path:
        pr = {"json": load_json(path)}
    elif ".xml" in path:
        pr = {"xml": load_xml(path)}
    else:
        print("文件格式 支持 json、csv、xml")
        exit(1)
    return pr


# 添加pr数据
def add_Merge_Request(path: str = None):
    if not path:
        print("pr数据路径为必填")
        exit(1)
    pullRequestSchema = PullRequestSchema.PullRequest(**get_Merge_Request(path)["json"])
    PRApi.add_Merge_Request(pullRequestSchema)


# 更新pr数据
def update_Merge_Request(path: str = None):
    if not path:
        print("pr数据路径为必填")
        exit(1)
    pullRequestSchema = PullRequestSchema.UpdatePullRequest(
        **get_Merge_Request(path)["json"]
    )
    PRApi.update_Merge_Request(pullRequestSchema)


# 添加pr jobs数据
def add_Merge_Request_job(path: str = None):
    if not path:
        print("pr job数据路径为必填")
        exit(1)
    pullRequestJobSchema = PullRequestJobSchema.PullRequestJob(
        get_Merge_Request(path)["json"]
    )
    print(pullRequestJobSchema)

    PRApi.add_Merge_Request_job(pullRequestJobSchema)

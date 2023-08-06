import os

from ..apis import build
from ..schemas import jenkins as JenkinsSchema

from ..utils.csv_utils import load_csv, write_csv, load_perf_csv
from ..utils.json_utils import load_json, write_json
from ..utils.xml_utils import load_xml, write_xml


def get_jenkins_info() -> JenkinsSchema.BuildResult:
    out = JenkinsSchema.BuildResult(
        jobName=os.getenv("JOB_NAME"),
        jobBaseName=os.getenv("JOB_BASE_NAME"),
        buildID=os.getenv("BUILD_ID"),
        buildNum=os.getenv("BUILD_NUMBER"),
        buildURL=os.getenv("BUILD_URL"),
        duration=os.getenv("DURATION", ""),
        jenkinsURL=os.getenv("JENKINS_URL", ""),
        gitBranch=os.getenv("GIT_BRANCH", ""),
        gitCommit=os.getenv("GIT_COMMIT", ""),
        status=os.getenv("CURRENT_RESULT", ""),
    )
    return out


def get_extra_env():
    result = {}
    result["FULL_STACK_PKG"] = os.getenv("FULL_STACK_PKG", "")
    result["CODEGEN_PKG"] = os.getenv("CODEGEN_PKG", "")
    result["PLATFORM"] = os.getenv("PLATFORM", "")
    result["JOB_TYPE"] = os.getenv("JOB_TYPE", "")
    result["STACK_PACKAGE_BRANCH"] = os.getenv("STACK_PACKAGE_BRANCH", "")
    return result


def get_build_result(path: str):
    if ".csv" in path:
        result = {"csv": load_csv(path)}
    elif ".json" in path:
        result = {"json": load_json(path)}
    elif ".xml" in path:
        result = {"xml": load_xml(path)}
    else:
        print("文件格式 支持 json、csv、xml")
        exit(1)
    return result


def get_build_result_by_type(path: str, type: str):
    if ".csv" in path:
        result = {"csv": load_perf_csv(path, type)}
    else:
        print("文件格式 支持 csv")
        exit(1)
    return result


def write_result(path: str, data):
    if ".csv" in path:
        write_csv(path, data.get("csv", []))
    elif ".json" in path:
        write_json(path, data.get("json", {}))
    elif ".xml" in path:
        write_xml(path, data.get("xml", ""))
    else:
        print("文件格式 支持 json、csv、xml")
        exit(1)


def add_build_result(path: str = None):
    """
    添加性能数据
    """
    if not path:
        print("性能数据路径 为必填")
        exit(1)
    buildResult = get_jenkins_info()
    buildResult.extraInfo = get_extra_env()
    buildResult.result = get_build_result(path)
    build.add_build_result(buildResult)


def update_build_result(path: str = None):
    """
    替换 jenkins build 状态、结果
    """
    buildResult = get_jenkins_info()
    if path:
        buildResult.result = get_build_result(path)
    build.update_build_status(buildResult)


def patch_build_result(path: str = None):
    """
    聚合 jenkins build 状态、结果
    """
    buildResult = get_jenkins_info()
    if path:
        buildResult.result = get_build_result(path)
    build.patch_build_status(buildResult)


def query_build_result(path: str = None):
    """
    获取 build 信息
    """
    buildResult = get_jenkins_info()
    query = JenkinsSchema.QueryBuildResult(jobName=buildResult.jobName)
    out = build.query_build_result(query)
    if not out:
        print("没有查询到结果")
    elif path:
        buildResult.result = write_result(path, out[0]["result"])
        print(f"成功获取结果：{path}")
    return out


def get_pre_build_result(path: str = None):
    """
    获取 pre build 信息
    """
    buildInfo = get_jenkins_info()
    query = JenkinsSchema.QueryBuildResult(jobName=buildInfo.jobName)
    out = build.query_build_result(query)
    if not out:
        print("没有查询到结果")
    pre_result = {}
    for b in out:
        if b["buildID"] == buildInfo.buildID:
            continue
        else:
            pre_result = b["result"]
            break
    if not pre_result:
        print("没有查询到结果")
    if path:
        write_result(path, pre_result)
        print(f"成功获取结果：{path}")
    return out

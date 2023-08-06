from ..apis import perf as PerfApi
from ..handles.build import (
    get_extra_env,
    get_jenkins_info,
    get_build_result,
    get_build_result_by_type,
    write_result,
)
from ..schemas import jenkins as JenkinsSchema
from ..schemas import test_case as TestCaseSchema

from ..utils.csv_utils import load_csv, write_csv, load_perf_csv
from ..utils.json_utils import load_json
from ..utils.file_utils import load_kvs
from ..utils.pd_utils import PD
from dotenv import load_dotenv
import os


def pef_meta_list():
    return ["accuracy", "performance", "mean_latency"]


def compare_calculate(baseV, newV):
    return f"{(float(baseV) - float(newV)) * 100 / float(newV):.2f}"


def perf_csv_format(data):
    out = {}
    for oline in data[1:]:
        out[":".join(oline[:-1])] = oline[-1]
    return out


def add_perf(csv_path=None):
    """
    添加 性能数据
    """
    if not csv_path:
        print("性能数据路径 为必填")
        exit(1)
    buildResult = get_jenkins_info()
    buildResult.extraInfo = get_extra_env()
    buildResult.result = perf_csv_format(get_build_result_by_type(csv_path, TestCaseSchema.TestCaseDataType.CURRENT.value)["csv"])
    buildResult.baseResult = perf_csv_format(get_build_result_by_type(csv_path, TestCaseSchema.TestCaseDataType.BASE.value)["csv"])
    PerfApi.update_pref_result(buildResult)


def patch_perf(path=None):
    """
    更新 性能数据
    """
    if not path:
        print("性能数据路径 为必填")
        exit(1)
    buildResult = get_jenkins_info()
    buildResult.result = get_build_result(path)
    PerfApi.patch_pref_result(buildResult)


def get_compare_head():
    return [
        "Key",
        "pre",
        "compare_pre(%)",
        "current",
        "compare_base(%)",
        "base",
    ]


def compare_logic(keys: list, curr: dict, other: dict):
    out = []
    for key in keys:
        try:
            currV = float(curr.get(key, None))
            otherV = float(other.get(key, None))
        except:
            out.append("N/A")
        else:
            if otherV == 0 or otherV == "N/A" or currV == "N/A":
                out.append("N/A")
            else:    
                out.append(f"{compare_calculate(currV, otherV)}%")
    return out


def dict_key_values(keys: list, dData: dict):
    out = []
    for k in keys:
        out.append(dData.get(k, "N/A"))
    return out


def get_compare_conf(conf_path):
    if conf_path:
        load_dotenv(conf_path, verbose=True)
    out = {
        "lastSize": int(os.getenv("lastSize", 7)),
        "alias": {
            "preValue": os.getenv("preValueAlias", "pre value"),
            "currValue": os.getenv("currValueAlias", "curr value"),
            "baseValue": os.getenv("baseValueAlias", "base value"),
            "avgValue": os.getenv("avgValueAlias", "avg value"),
            "minValue": os.getenv("minValueAlias", "min value"),
            "maxValue": os.getenv("maxValueAlias", "max value"),
            "preCompare": os.getenv("preCompareAlias", "pre compare"),
            "baseCompare": os.getenv("baseCompareAlias", "base compare"),
            "avgCompare": os.getenv("avgCompareAlias", "avg compare"),
            "minCompare": os.getenv("minCompareAlias", "min compare"),
            "maxCompare": os.getenv("maxCompareAlias", "max compare"),
        },
        "reportCol": os.getenv(
            "reportCol", "preValue,currValue,baseValue,avgValue,minValue,maxValue,preCompare,baseCompare,avgCompare,minCompare,maxCompare"
        ).split(","),
        "value": {
            "preValue": [],
            "currValue": [],
            "baseValue": [],
            "avgValue": [],
            "minValue": [],
            "maxValue": [],
            "preCompare": [],
            "baseCompare": [],
            "avgCompare": [],
            "minCompare": [],
            "maxCompare": [],
        },
    }
    return out


def compare_v2(curr_path, report_path=None, conf_path=None):
    compareConf = get_compare_conf(conf_path)
    lCurr = load_perf_csv(curr_path, TestCaseSchema.TestCaseDataType.CURRENT.value)
    dCurr = {":".join(line[:-1]): line[-1] for line in lCurr[1:]}
    lBase = load_perf_csv(curr_path, TestCaseSchema.TestCaseDataType.BASE.value)
    dBase = {":".join(line[:-1]): line[-1] for line in lBase}

    buildInfo = get_jenkins_info()
    query = JenkinsSchema.QueryBuildResult(
        jobName=buildInfo.jobName, status=buildInfo.status
    )
    query.size = compareConf["lastSize"]
    lLastData = PerfApi.base_result(query)
    if lLastData:
        rows = [o.get("result", {}) for o in lLastData[1:]]
        PD.DataFrame(rows).to_csv("./temp_last.csv")
        pd = PD.read_csv("./temp_last.csv")
        pd = pd.fillna(pd.mean(numeric_only=True))
        dAvg = dict(pd.mean(numeric_only=True))
        dMin = dict(pd.min(numeric_only=True))
        dMax = dict(pd.max(numeric_only=True))
    else:
        dAvg = {}
        dMin = {}
        dMax = {}

    query = JenkinsSchema.QueryBuildResult(
        jobName=buildInfo.jobName, status=buildInfo.status
    )
    query.size = 2
    lLastData = PerfApi.pre_result(query)
    if lLastData and len(lLastData) == 2:
        dPre = lLastData[1].get("result", {})
    else:
        dPre = {}
    # dConfData = load_kvs(conf_path)

    nameCol = sorted(dCurr.keys())

    compareConf["value"]["currValue"] = dict_key_values(nameCol, dCurr)
    compareConf["value"]["preValue"] = dict_key_values(nameCol, dPre)
    compareConf["value"]["baseValue"] = dict_key_values(nameCol, dBase)
    compareConf["value"]["avgValue"] = dict_key_values(nameCol, dAvg)
    compareConf["value"]["minValue"] = dict_key_values(nameCol, dMin)
    compareConf["value"]["maxValue"] = dict_key_values(nameCol, dMax)
    compareConf["value"]["preCompare"] = compare_logic(nameCol, dCurr, dPre)
    compareConf["value"]["baseCompare"] = compare_logic(nameCol, dCurr, dBase)
    compareConf["value"]["avgCompare"] = compare_logic(nameCol, dCurr, dAvg)
    compareConf["value"]["minCompare"] = compare_logic(nameCol, dCurr, dMin)
    compareConf["value"]["maxCompare"] = compare_logic(nameCol, dCurr, dMax)

    data = {
        "name": nameCol,
    }
    for rowName in compareConf["reportCol"]:
        data[compareConf["alias"][rowName]] = compareConf["value"][rowName]

    pdObj = PD.DataFrame(data)

    if report_path:
        pdObj.to_csv(report_path)
    else:
        print(pdObj)
    return


def compare_v3(report_path=None, conf_path=None):
    compareConf = get_compare_conf(conf_path)
    buildInfo = get_jenkins_info()

    query = JenkinsSchema.QueryBuildResult(
        jobName=buildInfo.jobName, status=buildInfo.status
    )
    query.size = 1
    lLastData = PerfApi.base_result(query)
    if lLastData and len(lLastData) == 1:
        dCurr = lLastData[0].get("result", {})
        dBase = lLastData[0].get("baseResult", {})
    else:
        dCurr = {}
        dBase = {}

    query = JenkinsSchema.QueryBuildResult(
        jobName=buildInfo.jobName, status=buildInfo.status
    )
    query.size = compareConf["lastSize"]
    lLastData = PerfApi.base_result(query)
    if lLastData:
        rows = [o.get("result", {}) for o in lLastData[1:]]
        PD.DataFrame(rows).to_csv("./temp_last.csv")
        pd = PD.read_csv("./temp_last.csv")
        pd = pd.fillna(pd.mean(numeric_only=True))
        dAvg = dict(pd.mean(numeric_only=True))
        dMin = dict(pd.min(numeric_only=True))
        dMax = dict(pd.max(numeric_only=True))
    else:
        dAvg = {}
        dMin = {}
        dMax = {}

    query = JenkinsSchema.QueryBuildResult(
        jobName=buildInfo.jobName, status=buildInfo.status
    )
    query.size = 2
    lLastData = PerfApi.pre_result(query)
    if lLastData and len(lLastData) == 2:
        dPre = lLastData[1].get("result", {})
    else:
        dPre = {}
    # dConfData = load_kvs(conf_path)

    nameCol = sorted(dCurr.keys())

    compareConf["value"]["currValue"] = dict_key_values(nameCol, dCurr)
    compareConf["value"]["preValue"] = dict_key_values(nameCol, dPre)
    compareConf["value"]["baseValue"] = dict_key_values(nameCol, dBase)
    compareConf["value"]["avgValue"] = dict_key_values(nameCol, dAvg)
    compareConf["value"]["minValue"] = dict_key_values(nameCol, dMin)
    compareConf["value"]["maxValue"] = dict_key_values(nameCol, dMax)
    compareConf["value"]["preCompare"] = compare_logic(nameCol, dCurr, dPre)
    compareConf["value"]["baseCompare"] = compare_logic(nameCol, dCurr, dBase)
    compareConf["value"]["avgCompare"] = compare_logic(nameCol, dCurr, dAvg)
    compareConf["value"]["minCompare"] = compare_logic(nameCol, dCurr, dMin)
    compareConf["value"]["maxCompare"] = compare_logic(nameCol, dCurr, dMax)

    data = {
        "name": nameCol,
    }
    for rowName in compareConf["reportCol"]:
        data[compareConf["alias"][rowName]] = compareConf["value"][rowName]

    pdObj = PD.DataFrame(data)

    if report_path:
        pdObj.to_csv(report_path)
    else:
        print(pdObj)
    return


def compare_perf(curr_path, pre_path, csv_path=None):
    """
    对比两个json 文件生成 csv
    """
    dictCurrentData = load_json(curr_path)
    dictPreData = load_json(pre_path)
    head = [
        "model",
        "meta",
        "pre",
        "compare_pre(%)",
        "current",
        "compare_base(%)",
        "base",
    ]
    rows = []
    rows.append(head)
    for model in dictCurrentData:
        for meta in dictCurrentData[model]["current"].keys():
            meta_curr = dictCurrentData[model]["current"][meta]
            meta_base = dictCurrentData[model]["base"][meta]
            if model not in dictPreData:
                meta_pre = "N/A"
                compare_pre = "N/A"
            else:
                if meta not in dictPreData[model]["current"]:
                    meta_pre = "N/A"
                    compare_pre = "N/A"
                else:
                    meta_pre = dictPreData[model]["current"][meta]
                    compare_pre = f"{compare_calculate(meta_pre, meta_curr)}%"
            compare_base = f"{compare_calculate(meta_base, meta_curr)}%"
            row = [
                model,
                meta,
                meta_pre,
                compare_pre,
                meta_curr,
                compare_base,
                meta_base,
            ]
            rows.append(row)
    if csv_path:
        write_csv(csv_path, rows)
    else:
        print(rows)
    return


def get_last_result(path: str = None, lastCount=7):
    """
    获取 上一次成功的 性能结果
    """
    buildResult = get_jenkins_info()
    query = JenkinsSchema.QueryBuildResult(jobName=buildResult.jobName)
    query.size = lastCount
    out = PerfApi.query_perf_result(query)
    if not out:
        print("没有查询到结果")
    elif path:
        buildResult.result = write_result(path, out[0]["result"])
        print(f"成功获取结果：{path}")
    return out

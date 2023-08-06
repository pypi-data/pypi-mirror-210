# -*- coding: utf-8 -*-

import io
import sys

from .handles import build, pdu, perf, pr

sys.stdout = sys.__stdout__ = io.TextIOWrapper(
    sys.stdout.detach(), encoding="utf-8", line_buffering=True
)
sys.stderr = sys.__stderr__ = io.TextIOWrapper(
    sys.stderr.detach(), encoding="utf-8", line_buffering=True
)

API = {
    "build.add": {
        "name": "上传 job build 数据",
        "param": {"path": "result json 文件路径"},
        "func": build.add_build_result,
    },
    "build.patch": {
        "name": "更新 job build 状态",
        "param": {"path": "result json 文件路径"},
        "func": build.patch_build_result,
    },
    "build.query": {
        "name": "获取 job build 状态",
        "param": {"path": "result json 文件路径"},
        "func": build.query_build_result,
    },
    "build.get_pre": {
        "name": "获取 上次 job build 结果",
        "param": {"path": "result json 文件路径"},
        "func": build.get_pre_build_result,
    },
    "perf.add": {
        "name": "上传 模型性能测试 数据",
        "param": {"csv_path": "result csv 文件路径"},
        "func": perf.add_perf,
    },
    "perf.compare": {
        "name": "比较 2次结果生成csv报告",
        "param": {
            "curr_path": "json 路径",
            "pre_path": "json 路径",
            "csv_path": "csv 报告路径",
        },
        "func": perf.compare_perf,
    },
    "perf.compareV2": {
        "name": "性能对比结果报告",
        "param": {
            "curr_path": "性能结果csv路径,包含current和base数据 例：./xxx/curr.csv",
            "report_path": "生成报告路径 例：./xxx/report.csv",
            "conf_path": "非必填, 报告格式配置文件 例如 ./xxx/perf.conf",
        },
        "func": perf.compare_v2,
    },
    "perf.compareV3": {
        "name": "性能对比结果报告",
        "param": {
            "report_path": "生成报告路径 例：./xxx/report.csv",
            "conf_path": "非必填, 报告格式配置文件 例如 ./xxx/perf.conf",
        },
        "func": perf.compare_v3,
    },
    "perf.get_pre": {
        "name": "获取最近一次成功的性能结果",
        "param": {"path": "result 路径"},
        "func": perf.get_last_result,
    },
    "pr.add_Merge_Request": {
        "name": "上传 pull request 数据",
        "param": {"path": "pr路径"},
        "func": pr.add_Merge_Request,
    },
    "pr.add_Merge_Request_job": {
        "name": "上传 pull request job数据",
        "param": {"path": "pr job路径"},
        "func": pr.add_Merge_Request_job,
    },
    "pr.udpate_Merge_Request": {
        "name": "更新 pull request数据",
        "param": {"path": "pr路径"},
        "func": pr.update_Merge_Request,
    },
    "pdu.pdu_list": {
        "name": "根据IP地址获取pdu配置列表",
        "param": {"hostPath": "pdu IP 列表文件", "targetPath": "pdu Seat列表json文件 写入路径"},
        "func": pdu.pdu_list,
    },
    "pdu.restart_hostname": {
        "name": "根据配置文件，与 机器 Name 重启机器",
        "param": {"pduConfPath": "pdu Seat列表json文件", "hostName": "机器再配置文件中的Name"},
        "func": pdu.restart_hostname,
    },
}


def cmd_desc():
    out = "\n"
    for k, v in API.items():
        desc = v["name"]
        param = v.get("param", "")
        out += f"\t{k}\t\t{desc}\t{param}\n"
    return out


Usage = f"""
    --..,_                     _,.--.
       `'.'.                .'`__ o  `;__.
          '.'.            .'.'`  '---'`  `
            '.`'--....--'`.'
              `'--....--'`

    Usage:\n\tbrci-cmd\tCMD\t[参数]\n
    CMD:{cmd_desc()}
"""


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in API:
        print(Usage)
    else:
        func = API[sys.argv[1]]["func"]
        if sys.argv[2:]:
            listParams = []
            for one in sys.argv[2:]:
                k, v = one.split("=")
                listParams.append(f'{k}="{v}"')
            strParams = ",".join(listParams)
            eval(f"func({strParams})")
        else:
            func()


            
if __name__ == "__main__":
    main()

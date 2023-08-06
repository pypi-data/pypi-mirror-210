import time

from ..apis.pdu import PduWeb
from ..config import Conf
import sys
import os
try:
    sys.path.insert(0, os.path.join(os.environ.get("WORKSPACE"),"br_jenkins"))
    from resources.utils.email_helper import email_helper_for_pdu_reporter
except Exception as e:
    print("may this part don't need to use emailhelper")


from ..utils.file_utils import load_lines
from ..utils.json_utils import load_json, write_json


def pdu_seat_list(hostList):
    out = []
    invalid_pdu_list = []
    invalid_pdu_err_logs = []
    params_for_render = {}
    for o in hostList:
        print(f"login: {o}")
        whileFlag = retry = 5
        listSeat = []
        while whileFlag > 0:
            try:
                w = PduWeb(host=o, user=Conf.pPduWeb.user, passwd=Conf.pPduWeb.passwd)
                listSeat = w.seat_list()
                break
            except Exception as e:
                whileFlag -= 1
                print(str(e))
                if whileFlag == 1:
                    try:
                        if o not in invalid_pdu_list:
                            invalid_pdu_list.append(o)
                        if str(e) not in invalid_pdu_err_logs:
                            invalid_pdu_err_logs.append(str(e))
                    except Exception as err:
                        print("[INFO] email send fail, please check!" + str(err))
            time.sleep(1)
        out += listSeat
    if invalid_pdu_list:
        print(str(invalid_pdu_list))
        params_for_render["error"] = str(invalid_pdu_err_logs)
        params_for_render["err_list"] = str(invalid_pdu_list)
        try:
            send_email(params_for_render)
        except Exception as e:
            print(e)

    return out


def query_pdu_name(name, pduSeatList):
    out = list(filter(lambda h: h["name"].lower() == name, pduSeatList))
    if out:
        return out[0]
    else:
        return


def restart_pdu_seat(pduHost, seat):
    print(f"restart_pdu_seat: {pduHost}, seat:{seat}")
    whileFlag = retry = 3
    while whileFlag > 0:
        try:
            w = PduWeb(host=pduHost, user=Conf.pPduWeb.user, passwd=Conf.pPduWeb.passwd)
            w.restart_seat(seat)
            break
        except Exception as e:
            if whileFlag == 0:
                print(f"重启PDU:{pduHost}, seat:{seat} 失败, 请联系jerryju@birentech.com处理")
                exit(1)
            whileFlag -= 1
            print(f"失败：重试 {retry - whileFlag}\n{e}")
            time.sleep(1)


def pdu_list(hostPath, targetPath=None):
    pduHostList = load_lines(hostPath)
    pduSeatList = pdu_seat_list(pduHostList)
    if targetPath:
        write_json(targetPath, pduSeatList)


def restart_hostname(pduConfPath, hostName):
    pduSeatList = load_json(pduConfPath)
    pduInfo = query_pdu_name(name=hostName, pduSeatList=pduSeatList)
    restart_pdu_seat(pduInfo["host"], pduInfo["seat"])


def send_email(params_for_render: dict):
    email_helper_for_pdu_reporter.send_email(
        subject="PDU UNSTABLE REPORTE",
        # debug
        # to_addr=["jerryju@birentech.com", "rbliu@birentech.com", "qli@birentech.com"],
        # to_addr=["jerryju@birentech.com"],
        # prod
        to_addr=["jerryju@birentech.com", "rbliu@birentech.com", "qli@birentech.com", "jtao@birentech.com"],
        email_type="html",
        html_path="pdu_monitor_report.html",
        params_for_render=params_for_render,
    )

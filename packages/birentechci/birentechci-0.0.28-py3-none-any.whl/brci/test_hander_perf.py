from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv(), verbose=True)
load_dotenv(find_dotenv(".perf.test.env"), verbose=True)

from brci.handles import perf


def test_add_perf():
    out = perf.add_perf(csv_path="/home/e00869/code/br_ci_db/v2/sdk/temp.csv")


def test_query_perf():
    perf.compare_v2(
        curr_path="/home/e00928/code/br_ci_db_sdk/sdk/bm_supa_perf_cur_test.csv",
        report_path="./report10.csv",
        # conf_path="/home/e00928/code/br_ci_sdk/sdk/brci/compare.conf.template",
    )


test_query_perf()

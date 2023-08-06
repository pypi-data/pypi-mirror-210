from trojsdk.core import data_utils
from trojsdk.core import client_utils
from trojsdk.core.client_utils import TrojJobHandler


def test_sdk_fail():
    troj_job_handler = TrojJobHandler()
    try:
        troj_job_handler.list_stress_test_jobs()
        assert False
    except:
        assert True


def test_sdk_pass_tabular():
    troj_job_handler = client_utils.submit_evaluation(
        path_to_config="./trojsdk/examples/tabular_medical_insurance_config.json",
        nossl=True,
    )

    import time

    time.sleep(2)
    try:
        resp = troj_job_handler.list_stress_test_jobs(pretty=False)
        print(resp)
        assert True
    except Exception as e:
        print(e)
        assert False

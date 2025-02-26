import json

import requests

base_url = "http://127.0.0.1:9380"


def register_components():
    uri = "/v2/provider/register"  # fate_flow/python/fate_flow/apps/client/provider_app.py 中的服务
    config_path = "../job/unionpay/unionpay_components.json"
    body = json.load(open(config_path, "r"))
    resp = requests.post(base_url+uri, json=body)
    print(resp.text)


register_components()


def submit_job():
    uri = "/v1/platform/schedule/job/create_all"
    config_path = "../job/unionpay/bfia_psi_sbt.json"
    body = json.load(open(config_path, "r"))
    resp = requests.post(base_url+uri, json=body)
    print(resp.text)


def start_job(job_id):
    uri = "/v1/interconn/schedule/job/start"
    resp = requests.post(base_url+uri, json={"job_id": job_id})
    print(resp.text)


def stop_job(job_id):
    uri = "/v1/interconn/schedule/job/stop_all"
    resp = requests.post(base_url+uri, json={"job_id": job_id})
    print(resp.text)


submit_job()

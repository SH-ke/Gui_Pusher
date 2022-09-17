import requests, yaml, json
from attrdict import AttrDict
from fake_useragent import UserAgent


def shop_resp() -> dict:
    # 读取参数配置文件
    yaml_file = "config/gui.yaml"
    with open(yaml_file, 'rt', encoding="utf-8") as f:
        args = AttrDict(yaml.safe_load(f))

    ua = UserAgent()
    HEADERS = {
        "Content-Type": "application/json",
        "User-Agent": ua.random,
    }

    # 发起 post 请求
    resp = requests.post(args.resp.url, 
                        data=json.dumps(args.resp.data), 
                        headers=HEADERS)
    data = json.dumps(resp.json()["data"]["records"], indent=4, 
                        separators=(',', ': '), 
                        ensure_ascii=False)
    resp.close()
    return data


# 『数据预处理』 筛选满足条件的活动，整理成表格，保存为csv 存入数据库
# 将surplus「剩余量」存入csv 数据库
def data_preprocess(data: list):
    pass


# 『通知』 对比当前数据于上一次请求数据的差别，发送对应通知
def notice_match():
    # 「新活动」通知
    # 「售罄」通知
    pass
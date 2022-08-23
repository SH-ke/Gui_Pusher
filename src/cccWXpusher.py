import requests
import json


def sendmsg(type, msg, dish_name):
    url = "http://wxpusher.zjiecode.com/api/send/message"
    body = {
        "appToken": "AT_krZaCpAfnpEEP5m9QosMIXP7qAHSrlBo",
        "content": msg,
        "summary": f"吃吃龟-{type}: {dish_name}" ,  # 消息摘要
        "contentType": 1,  # 1文字  2html 3markdown
        # "topicIds":[123]
        "uids": [
            #   "UID_mqX5vmD6UspSoZvZSiUNFYcuL9Gi",  test
            "UID_RwNX0uuDjA9Nvo5QlwhqbYhOHciV",
            "UID_VTRUelfq0AGk83Srublr4s4IcCjI",
            "UID_GFInmNliLr7M3PaRUOQdpqsMLEZv",
        ],
    }
    print(f"type = 你关心的店铺更新了\nname = {dish_name}\nmsg = {msg}")
    fails = 0
    while True:
        try:
            if fails >= 3:
                print("失败三次！")
                break

            headers = {"content-type": "application/json"}
            ret = requests.post(url, json=body, headers=headers, timeout=10)

            if ret.status_code == 200:
                text = json.loads(ret.text)
            else:
                continue
        except:
            fails += 1
            print("网络连接出现问题, 正在尝试再次请求: ", fails)
        else:
            break
    return text

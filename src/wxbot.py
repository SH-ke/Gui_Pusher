import requests, yaml, json
from attrdict import AttrDict


def sendmsg(title, msg):
    # 读取参数配置文件
    yaml_file = "config/gui.yaml"
    with open(yaml_file, 'rt', encoding="utf-8") as f:
        args = AttrDict(yaml.safe_load(f))

    args.wxbot.summary = title
    args.wxbot.content = msg

    fails = 0
    while True:
        try:
            if fails >= 3:
                print("失败三次！")
                break

            headers = {"content-type": "application/json"}
            ret = requests.post(args.wxbot.url, json=args.wxbot.body, 
                                headers=headers, timeout=10)

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

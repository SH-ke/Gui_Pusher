import datetime
import time
import requests
import pickle
import csv
import configparser
from fake_useragent import UserAgent
import sched
from wxbot import sendmsg


class GuiPusher:
    def __init__(self):
        self.isAlive = True
        self.url = "https://shop.laiyangni.com/api/lyn/wechat/home/shopInfo"
        self.parms = {
            "isPs": 1,
            "cityId": 110100,
            "current": 1,
            "lat": 40.22077,
            "lon": 116.23128,
            "size": 10,
        }
        self.plats = {
            "1": "美团",
            "2": "饿了么",
        }
        self.regular_init()

    def regular_init(self):
        config = configparser.RawConfigParser()
        config.read("gui.ini", encoding='utf')

        self.dt = eval(config.get("const", "delta_time")) # 请求间隔时间
        self.max_dist = eval(config.get("const", "max_distance"))  # 最远距离
        self.dat_file = config.get("const", "dat_file") # 用户数据
        # 更新唤醒时间段
        t = [int(e) for e in config.get("const", "wake_time").split(':')]
        wake_time = datetime.time(t[0], t[1], t[2])
        t = [int(e) for e in config.get("const", "sleep_time").split(':')]
        sleep_time = datetime.time(t[0], t[1], t[2])
        # 更新 customlize.ini 商铺sid
        self.likes = [int(e) for e in config.get("const", "likes").split(',')]
        # shop_info.dat
        self.load_shop_info()
        self.parms["current"] = 1  # 重新回到page = 1
        self.date = datetime.datetime.now()  # 更新当前时间
        self.now = self.date.time()  # 当前 时分秒
        # self.now = datetime.time(8, 27, 0) 
        print("{:%Y-%m-%d %H:%M:%S}".format(self.date))
        if self.now.__le__(wake_time) or self.now.__ge__(sleep_time):
            self.isAlive = False
        else:
            self.isAlive = True


    def load_shop_info(self):
        try:
            f = open(self.dat_file, "rb")
        except FileNotFoundError:
            self.shop_infos = []
            self.shop_index = {}
        else:
            usr_dat = pickle.load(f)
            self.shop_infos = usr_dat["data"]
            # 通过sid 查询 shop 在shop_infos 中的index
            self.shop_index = usr_dat["shop_index"]
        finally:
            f.close()

    def save_shop_info(self):
        usr_data = {
            "data": self.shop_infos,
            "shop_index": self.shop_index,
            "wake": self.isAlive,
            "time": self.now,
        }
        # 写如二进制文件
        with open(self.dat_file, mode="wb") as f:
            pickle.dump(usr_data, f)
        # 写入 csv
        with open("shop_infos.csv", mode="w", newline="", encoding='utf') as f:
            csvw = csv.writer(f)
            for idx, d in enumerate(self.shop_infos):
                if idx == 0:
                    csvw.writerow(d.keys())
                csvw.writerow(d.values())

    def get_likes(self):
        names = []
        for sid in self.likes:
            try:
                names.append(self.shop_infos[self.shop_index[sid]]["name"])
            except KeyError:
                print("KeyError ! ")
                continue
        print('\n'.join(names))
        return names

    def is_alive(self):
        print(self.isAlive)

    def get_gui_time(self):
        print(self.now)


    def load_by_csv(self, file):
        # 从本地csv载入店铺数据
        f = open(f"{file}.csv", 'r')
        lines = f.readlines()[1:]
        f.close()
        for l in lines:
            sid = int(l[:5])
            if sid not in self.shop_index.keys():
                t = l.split(',')
                shop_info = {
                    "index": 0, 
                    "sid": sid, 
                    "name": t[1], 
                    "plat": t[2], 
                    "todayAlert": False,
                }
            
                idx = len(self.shop_infos)
                shop_info["index"] = idx
                self.shop_infos.append(shop_info)
                self.shop_index[shop_info["sid"]] = idx

        self.save_shop_info()


    # 遍历整个主页，并筛选出所满足距离要求的商铺加入数据库
    def all_page_check(self):
        ua = UserAgent()
        HEADERS = {
            "User-Agent": ua.random,
        }
        while True:
            resp = requests.get(self.url, self.parms, headers=HEADERS)
            data = resp.json()
            resp.close()
            self.parms["current"] += 1
            # 到达最后一页停止
            if data["data"]["current"] > data["data"]["pages"]:
                self.parms["current"] = 0
                break
            # 解析数据
            self.today_likes = {}  # 今日特别关心的店
            self.new_shops = {}  # 新店
            shops = data["data"]["records"]
            for shop in shops:  # 遍历page内的店铺
                plat = shop["activityList"][0]["platformType"]
                shop_info = {
                    "index": 0,
                    "sid": shop["sid"],
                    "name": shop["shopname"],
                    "plat": plat,
                    "todayAlert": False,
                }
                # 特别关注、回归
                print(f"name = {shop_info['name']}, sid = {shop_info['sid']}, type = {type(shop_info['sid'])} ")
                if shop_info["sid"] in self.likes:
                    self.today_likes[shop_info["name"]] = shop["activityList"]
                # 新店、扩充数据库
                if (
                    shop_info["sid"] not in self.shop_index.keys()  # 未收录的店
                    and shop["distance"] <= self.max_dist  # 符合距离的店
                ):
                    idx = len(self.shop_infos)
                    self.new_shops[idx] = shop["activityList"]
                    shop_info["index"] = idx
                    self.shop_infos.append(shop_info)
                    self.shop_index[shop_info["sid"]] = idx

    def alert(self):
        # msg ==> name, remind_num, tips, start, end, plat
        # msg = f"{name}\n\t{tips} 剩余{remind_num}\n\t{act['todayStartTime']}\t{buyAdvice}\t{p}\n\n"

        # 特别关心提醒，时间不足 dt 提醒
        msgs = []
        name = ''
        for k, v in self.today_likes.items():
            for act in v["activityList"]:
                name = self.shop_infos[k]["name"]
                start = [int(e) for e in act["todayStartTime"].split(":")]
                now = [self.date.hour, self.date.second]
                remind_num = v["surplus"]
                if (
                    start[0] == now[0]
                    and start[1] - now[1] <= 5 # 订单开始提前几分钟提醒
                    or self.shop_infos[k].todayAlert is False
                    and remind_num # 未提醒的订单也提醒
                ):
                    tips = v["tips"]
                    p = v["platformType"]
                    msg = f"{name}\n\t{tips} 剩余{remind_num}\n\t{act['todayStartTime']}\t{p}\n\n"
                    msgs.append(msg)
        if msgs:
            # sendmsg("你关心的店铺更新了", ''.join(msgs), name)
            print(f"type = 你关心的店铺更新了\nname = {name}\nmsg = {''.join(msgs)}")
        else:
            print("今日无事")
        """
        到点提醒、每日汇报、(提早提醒)
        """

    def regular_caller(self):
        self.regular_init()
        if self.isAlive:
            self.all_page_check()
            self.alert()
        self.save_shop_info()
        print(f"isAlive = {self.isAlive}")
        self.loop_monitor()

    def loop_monitor(self):
        s = sched.scheduler(time.time, time.sleep)  # 生成调度器
        s.enter(self.dt, 1, self.regular_caller, ())
        s.run()


def main():
    gp = GuiPusher()
    # gp.get_likes()
    gp.loop_monitor()


if __name__ == "__main__":
    main()


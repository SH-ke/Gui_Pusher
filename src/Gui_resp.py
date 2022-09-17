import requests


url = "https://shop.laiyangni.com/api/lyn/wechat/home/shopInfo"
parms = {
    "isPs": 1,
    "cityId": 110100,
    "current": 1,
    "lat": 40.22077,
    "lon": 116.23128,
    "size": 10,
}

resp = requests.get(url, params=parms)
print(resp.status_code)
print(resp.json())
resp.close()
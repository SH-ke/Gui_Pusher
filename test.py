shop_infos = []
with open("like.csv", 'r') as f:
    for line in f.readlines()[1:]:
        t = line.split(',')
        info = {
            "sid": int(t[0]), 
            "name": t[1], 
            "plat": t[2], 
        }
        shop_infos.append(info)

print(shop_infos)
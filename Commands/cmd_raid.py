# 在庫の確認
# 戻り値はポケモンの一覧(str), ポケモン数(int)
def chk_stock(name, l_poke):
    send_txt = ''
    n = 0
    for poke in l_poke:
        if (name in poke):
            send_txt += '\n' + poke
            n += 1
    return send_txt, n

#在庫の読み込み
def read_lpoke(STOCK_PATH):
    with open(STOCK_PATH, "r",encoding="utf-8_sig") as f:
        l = f.readlines()
        l_poke = [s.strip() for s in l]
    return l_poke

#在庫の記録
def write_lpoke(STOCK_PATH, l_poke):
    with open(STOCK_PATH, 'w',encoding="utf-8_sig") as f:
        for x in l_poke:
            f.write(str(x) + "\n")
    return

#レイドの登録
def process_raid_add(arg, STOCK_PATH):
    if (len(arg) <= 2):
        return [-1, '']

    l_poke = read_lpoke(STOCK_PATH)
    result = chk_stock(arg, l_poke)
    if (result[1]):
        return [-2, result[0]]
    else:
        l_poke.append(arg)
        write_lpoke(STOCK_PATH, l_poke)
        return [1, '']

#在庫確認
def process_raid_check(arg, STOCK_PATH):
    if (len(arg) <= 2):
        return [1, '']

    l_poke = read_lpoke(STOCK_PATH)
    result = chk_stock(arg, l_poke)
    if (result[1]):
        return [-2, result[0]]
    else:
        return [1, '']

#在庫の削除
def process_raid_del(name, HOST_ROLE, STOCK_PATH):
    l_poke = read_lpoke(STOCK_PATH)
    if (name in l_poke):
        l_poke.remove(name)
        write_lpoke(STOCK_PATH, l_poke)
        return [1, '']
    else:
        return [0, '']

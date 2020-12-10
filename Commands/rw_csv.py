import csv

def read_csv(fpath):
    with open(fpath, 'r', encoding='utf-8') as fr:
        reader = csv.reader(fr)
        _list = [x for x in reader]
    return _list

def write_csv(fpath, _list):
    with open(fpath, 'w', newline='', encoding='utf-8') as fw:
        writer = csv.writer(fw)
        writer.writerows([x for x in _list])
    return
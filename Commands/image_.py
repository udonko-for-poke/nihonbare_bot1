import urllib.error
import urllib.request

async def dl(url, name):
    try:
        with urllib.request.urlopen(url) as web_file:
            data = web_file.read()
            with open(name, mode='wb') as local_file:
                local_file.write(data)
        return 1
    except urllib.error.URLError as e:
        print(e)
        return 0
    
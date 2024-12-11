import requests
import os

from db import Json

links = Json('./formuls.json')
links.load()
global_data = links.content

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0'
}
def get_name(url: str) -> str:
    index = len(url) - 1
    name = ''
    while True:
        char = url[index]
        if char != '/':
            name += char
        else:
            break
        index -= 1
    return ''.join(reversed(name))


def get_photo(url: str):
    if not os.path.exists('./Img/'):
        os.mkdir('./Img/')
    os.chdir('./Img/')
    name = get_name(url)

    if not os.path.exists(os.path.join(os.getcwd(), name)):
        response = requests.get(url, headers=HEADERS)
        if response.status_code == 200:
            with open(name, 'wb') as img:
                img.write(response.content)
    os.chdir('../')

    
def download_photo():
    urls = []
    data = global_data

    for dic in list(data.values()):
        value = list(data.values())
        while True:
            for dic in list(dic.values()):
                try:
                    value = list(dic.values())
                    data = dic
                except AttributeError:
                    break
            break
        for i in value:
            urls.append(i)
        data = global_data

    for url in urls:
        get_photo(url)
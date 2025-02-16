import requests
import os
import shutil
import sqlite3

from myJson import Json

db = sqlite3.connect("database.db")
cursor = db.cursor()


HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0'
}
def get_name(url: str) -> str:
    index = len(url) - 1
    name = ''
    while True:
        char = url[index]
        if char != '/' and char != '\\':
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

    if url.startswith('http'):
        if not os.path.exists(os.path.join(os.getcwd(), name)):
            response = requests.get(url, headers=HEADERS)
            if response.status_code == 200:
                with open(name, 'wb') as img:
                    img.write(response.content)
            else:
                print('Downloading error: {}'.format(response.status_code))
    else:
        if not os.path.exists(url):
            print(f'File {url} not found in Img folder!')
    os.chdir('../')

    
def download_photos_from_json():
    urls = []
    links = Json('./formuls.json')
    links.load()
    global_data = links.content
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
            urls.append(i[0])
        data = global_data

    for url in urls:
        get_photo(url)
        
        
def download_photos_from_DB():
    urls = cursor.execute("SELECT link FROM formuls").fetchall()
    
    for url in urls:
        get_photo(url[0])
        
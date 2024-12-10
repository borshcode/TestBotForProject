import requests

from db import Json

formuls = Json('./formuls.json')
formuls.load()
data = formuls.content

def get_photo(url: str):
    index = len(url) - 1
    while True:
        char = url[index] != '/':
            
        
    
    response = requests.get(url)
    if response.status_code == 200:
        with open()
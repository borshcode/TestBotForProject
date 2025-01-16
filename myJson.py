import json

class Json():
    def __init__(self, path: str):
        self.path = path
        self.content = {}
        
        
    def load(self):
        with open(self.path, 'r', encoding='utf-8') as file:
            self.content = json.load(file)
    
    
    def write(self, text: str):
        with open(self.path, 'w', encoding='utf-8') as file:
            json.dump(text, file, ensure_ascii=False)
            
            
    def update(self, text: str):
        self.load()
        with open(self.path, 'w', encoding='utf-8') as file:
            new_text = self.content + '\n' + text
            json.dump(new_text, file, ensure_ascii=False)
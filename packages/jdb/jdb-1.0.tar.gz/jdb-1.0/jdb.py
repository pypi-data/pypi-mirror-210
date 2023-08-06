import json

class Data:
    def __init__(self, filename: str):
        self.filename = filename
        with open(filename) as loaded_file:
            self.original_dict = json.loads(open(filename).read())
    def get_steps(self, key):
        steps = ''
        keys = key.split('.')
        for step in keys:
            steps += f'[{step}]' if step.startswith('__') else f'["{step}"]'
        return steps
    def rm(self, key: str):
        exec(f'del self.original_dict{self.get_steps(key)}')
        with open(self.filename, 'r+') as writed_file:
            writed_file.truncate(0)
            writed_file.write(json.dumps(self.original_dict, indent=4))
    def get(self, key: str):
        return eval(f'self.original_dict{self.get_steps(key)}')
    def set(self, key: str, value):
        try:
            exec(f'self.original_dict{self.get_steps(key)} = "{value}"') if type(value) == str else exec(f'self.original_dict{self.get_steps(key)} = {value}')
        except: 
            exec(f"self.original_dict{self.get_steps(key)} = '{value}'")
        with open(self.filename, 'r+') as writed_file:
            writed_file.truncate(0)
            writed_file.write(json.dumps(self.original_dict, indent=4))

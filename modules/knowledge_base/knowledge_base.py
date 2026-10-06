import json


class KnowledgeBase:
    def __init__(self, filename):
        self.filename = filename
        self.data = self._load()
        self.validate()

    def _load(self):
        with open(self.filename, 'r', encoding='utf-8') as f:
            return json.load(f)

    def validate(self):
        if 'facts' not in self.data or 'rules' not in self.data:
            raise ValueError("Неправильный формат файла.")
        
    def get_facts(self):
        return self.data['facts']

    def get_rules(self):
        return self.data['rules']

    def find_fact(self, name):
        for f in self.data['facts']:
            if f['name'] == name:
                return f
        return None

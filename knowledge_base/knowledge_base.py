import json


class KnowledgeBase:
    def __init__(self, filename):
        self.filename = filename
        self.data = self._load()

    def _load(self):
        with open(self.filename, 'r', encoding='utf-8') as f:
            return json.load(f)

    def get_facts(self):
        return self.data['facts']

    def get_rules(self):
        return self.data['rules']

kb = KnowledgeBase("knowledge_base/rules.json")
rules = kb.get_rules()
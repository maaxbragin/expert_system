# Класс для записи о срабатывании одного правила.
class FireRecord:
    def __init__(self, rule_id, rule_name, matched_facts,
                 conclusion_fact, conclusion_value, iteration):
        self.rule_id = rule_id
        self.rule_name = rule_name
        self.matched_facts = matched_facts
        self.conclusion_fact = conclusion_fact
        self.conclusion_value = conclusion_value
        self.iteration = iteration
    # для красивого выводп
    def __repr__(self):
        return (
            f"<FireRecord #{self.iteration} {self.rule_id} "
            f"{self.rule_name} -> {self.conclusion_fact}="
            f"{self.conclusion_value}>"
        )
# Класс для хранения записей в память
class WorkingMemory:
    def __init__(self):
        self._facts: dict[str, any] = {}
        self._journal: list[FireRecord] = []
        self._iteration: int = 0

    def has_fact(self, name: str) -> bool:
        return name in self._facts

    def get_fact(self, name: str, default=None):
        return self._facts.get(name, default)

    def set_fact(self, name: str, value: any) -> bool:
        if name in self._facts and self._facts[name] == value:
            return False
        self._facts[name] = value
        return True

    def get_all_facts(self):
        return dict(self._facts)

    def log_fire(self, rule_id, rule_name, matched_facts,
                 conclusion_fact, conclusion_value):
        iteration = len(self._journal) + 1
        self._journal.append(FireRecord(
            rule_id, rule_name, matched_facts,
            conclusion_fact, conclusion_value, iteration,
        ))

    def get_journal(self):
        return list(self._journal)
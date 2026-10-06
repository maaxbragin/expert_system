class Explainer:
    # Русские имена фактов — для красивого вывода
    RU_NAMES = {
        "cough":           "Кашель",
        "sneezing":        "Чихание",
        "dyspnea":         "Одышка",
        "mouth_breathing": "Дыхание с открытым ртом",
        "weakness":        "Упадок сил",
        "cyanosis":        "Синюшность слизистых оболочек",
        "temperature":     "Температура",
        "fever":           "Лихорадка",
        "hypoxia":         "Гипоксия",
        "rhinitis":        "Ринит/конъюнктивит",
        "tracheitis":      "Трахеит",
        "bronchitis":      "Бронхит",
        "pulmonary_edema": "Отёк лёгких",
        "chlamydiosis":    "Хламидиоз",
        "calicivirus":     "Калицивироз",
        "asthma":          "Астма",
    }
    def __init__(self, wm, kb):
        # wm — рабочая память (единственный источник данных)
        # kb — только чтобы достать русские имена и уровни фактов
        self.wm = wm
        self.kb = kb

    def _find_fire(self, fact_name):
        """Найти запись в журнале, где этот факт был выведен."""
        for rec in self.wm.get_journal():
            if rec.conclusion_fact == fact_name:
                return rec
        return None

    def why(self, fact_name, depth=0, visited=None):
        if visited is None:
            visited = set()

        indent = "    " * depth
        fact_ru = self.RU_NAMES.get(fact_name, fact_name)
        value = self.wm.get_fact(fact_name)
        print(f"{indent}{fact_ru} = {value}")

        if fact_name in visited:
            print(f"{indent}  (уже объяснено выше)")
            return
        visited.add(fact_name)

        fire = self._find_fire(fact_name)
        if fire is None:
            print(f"{indent}  (исходный факт)")
            return

        print(f"{indent}  ← правило {fire.rule_id} ({fire.rule_name})")
        print(f"{indent}  ← из фактов:")
        for src_name in fire.matched_facts:
            self.why(src_name, depth + 2, visited)

    def trace(self):
        """Напечатать журнал срабатываний в порядке вывода."""
        print("=== Журнал срабатываний ===")
        for rec in self.wm.get_journal():
            print(
                f"[{rec.iteration}] {rec.rule_id} {rec.rule_name}: "
                f"{rec.conclusion_fact} = {rec.conclusion_value}"
            )
    def how(self, fact_name):
        """Показать все правила БЗ, в заключении которых есть этот факт."""
        print(f"Факт '{fact_name}' могут вывести правила:")
        for rule in self.kb.get_rules():
            if rule["conclusion"]["fact"] == fact_name:
                print(f"  {rule['id']} {rule['name']} "
                      f"(priority={rule['priority']})")
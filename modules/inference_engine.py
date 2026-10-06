from modules.conflict_resolution import SalienceResolver


class InferenceEngine:
    def __init__(self, kb, wm, resolver=None):
        self.kb = kb
        self.wm = wm
        self.resolver = resolver or SalienceResolver()
    #  Проверка условий

    def _check_condition(self, cond):
        """Проверить одно условие правила в текущей WM."""
        name = cond["fact"]
        op = cond["operator"]
        value = cond.get("value")
        negated = cond.get("negated", False)

        exists = self.wm.has_fact(name)
        actual = self.wm.get_fact(name)
        if negated:
            return not (exists and actual == value)

        if not exists:
            return False

        return self._compare(actual, op, value)

    @staticmethod
    def _compare(actual, op, expected):
        if op == "==": return actual == expected
        if op == "!=": return actual != expected
        if op == ">":  return actual >  expected
        if op == "<":  return actual <  expected
        if op == ">=": return actual >= expected
        if op == "<=": return actual <= expected
        raise ValueError(f"Неизвестный оператор: {op}")

    def _match_rule(self, rule):
        matched = {}
        for cond in rule["conditions"]:
            if not self._check_condition(cond):
                return None
            if cond.get("negated", False):
                continue                       # ← добавить
            matched[cond["fact"]] = self.wm.get_fact(cond["fact"])
        return matched

    #  Основной цикл

    def run(self, max_iterations=1000):
        """Запустить вывод. Возвращает число сработавших правил."""
        fires = 0

        for _ in range(max_iterations):
            # 1. Собираем активации
            activations = []
            for rule in self.kb.get_rules():
                matched = self._match_rule(rule)
                if matched is None:
                    continue

                concl = rule["conclusion"]
                # Пропускаем, если заключение уже выведено
                if (self.wm.has_fact(concl["fact"]) and
                        self.wm.get_fact(concl["fact"]) == concl["value"]):
                    continue

                activations.append({
                    "rule": rule,
                    "matched_facts": matched,
                })

            # 2. Нет активаций — вывод завершён
            if not activations:
                break

            # 3. Выбор
            chosen = self.resolver.select(activations)
            rule = chosen["rule"]
            concl = rule["conclusion"]

            # 4. Выполнение
            changed = self.wm.set_fact(concl["fact"], concl["value"])

            # 5. Журнал
            self.wm.log_fire(
                rule_id=rule["id"],
                rule_name=rule["name"],
                matched_facts=chosen["matched_facts"],
                conclusion_fact=concl["fact"],
                conclusion_value=concl["value"],
            )

            fires += 1
            if not changed:
                # Защита от зацикливания
                break

        return fires
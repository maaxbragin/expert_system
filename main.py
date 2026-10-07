import argparse

from modules.knowledge_base.knowledge_base import KnowledgeBase
from modules.working_memory import WorkingMemory
from modules.conflict_resolution import (
    SalienceResolver, SpecificityResolver, FIFOResolver,
)
from modules.inference_engine import InferenceEngine
from modules.explanation import Explainer

#  Выбор стратегии по имени из командной строки

STRATEGIES = {
    "salience":    SalienceResolver,
    "specificity": SpecificityResolver,
    "fifo":        FIFOResolver,
}

#  Опрос пользователя
# Симптомы, которые нужно спросить
SYMPTOMS = [
    ("cough",    "Наблюдается ли кашель"),
    ("sneezing", "Наблюдается ли чихание"),
    ("dyspnea",  "Наблюдается ли одышка"),
    ("weakness", "Наблюдается ли упадок сил"),
    ("cyanosis", "Есть ли синюшность слизистых оболочек"),
]


def ask_yes_no(text):
    """Спрашивать, пока не будет 'да' или 'нет'."""
    while True:
        answer = input(f"{text} (да/нет)? ").strip().lower()
        if answer in ("да", "д", "yes", "y"):
            return True
        if answer in ("нет", "н", "no", "n"):
            return False
        print("Нужно ответить 'да' или 'нет'.")


def ask_integer(text, min_value, max_value):
    """Спрашивать целое число в диапазоне."""
    while True:
        raw = input(f"{text} [{min_value}..{max_value}]: ").strip()
        try:
            value = int(raw)
        except ValueError:
            print(f"Нужно целое число от {min_value} до {max_value}.")
            continue
        if min_value <= value <= max_value:
            return value
        print(f"Нужно целое число от {min_value} до {max_value}.")


def fill_working_memory(wm):
    """Заполнить WM: начальные факты + опрос пользователя."""
    # Факт, который вводит врач при осмотре (из ЛР №1)
    wm.set_fact("mouth_breathing", True)

    # Температура
    temperature = ask_integer(
        "Температура тела, градусов Цельсия", 35, 43
    )
    wm.set_fact("temperature", temperature)

    # Остальные симптомы
    for name, question in SYMPTOMS:
        wm.set_fact(name, ask_yes_no(question))

#  Печать результата

# Уровни заключений (хардкод для минимальной версии)
SYNDROMES = {"hypoxia", "rhinitis", "tracheitis", "bronchitis"}
DISEASES  = {"pulmonary_edema", "chlamydiosis", "calicivirus", "asthma"}

RU_NAMES = {
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


def print_result(wm):
    """Напечатать синдромы и заболевания из WM."""
    facts = wm.get_all_facts()

    syndromes = [
        name for name in SYNDROMES if facts.get(name) is True
    ]
    diseases = [
        name for name in DISEASES if facts.get(name) is True
    ]

    print()
    print("=== Результат диагностики ===")

    if not syndromes and not diseases:
        print("  Признаков заболевания не выявлено.")
        return

    if syndromes:
        print("Синдромы:")
        for name in syndromes:
            print(f"  - {RU_NAMES.get(name, name)}")

    if diseases:
        print("Заболевания:")
        for name in diseases:
            print(f"  - {RU_NAMES.get(name, name)}")


#  Главная функция

def main():
    parser = argparse.ArgumentParser(
        description="Оболочка ЭС: диагностика кошек"
    )
    parser.add_argument(
        "--strategy",
        choices=list(STRATEGIES.keys()),
        default="salience",
        help="Стратегия разрешения конфликтов",
    )
    parser.add_argument(
        "--kb",
        default="modules/knowledge_base/rules.json",
        help="Путь к файлу базы знаний",
    )
    args = parser.parse_args()

    # 1. Загрузка БЗ
    kb = KnowledgeBase(args.kb)
    print("=== Диагностика респираторных заболеваний кошек ===")
    print("Ответьте на вопросы о состоянии животного.")
    print()

    # 2. Рабочая память + опрос
    wm = WorkingMemory()
    fill_working_memory(wm)

    # 3. Движок с выбранной стратегией
    resolver = STRATEGIES[args.strategy]()
    engine = InferenceEngine(kb, wm, resolver)

    # 4. Запуск вывода
    fires = engine.run()
    print()
    print(f"Сработало правил: {fires} "
          f"(стратегия: {args.strategy})")

    # 5. Результат
    print_result(wm)

    # 6. Объяснение по каждому заключению
    explainer = Explainer(wm, kb)
    facts = wm.get_all_facts()
    conclusions = [
        name for name in (SYNDROMES | DISEASES)
        if facts.get(name) is True
    ]
    if conclusions:
        print()
        print("=== Объяснение ===")
        for name in conclusions:
            explainer.why(name)
            print()

    print()
    print("Журнал срабатываний")
    explainer.trace()


if __name__ == "__main__":
    main()


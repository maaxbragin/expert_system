"""
Стратегии разрешения конфликтов.
"""


class SalienceResolver:
    """По приоритету правила. При равенстве — по порядку в БЗ."""
    def select(self, activations):
        return max(activations, key=lambda a: a["rule"]["priority"])

class SpecificityResolver:
    """По конкретности: больше условий — раньше срабатывает."""
    def select(self, activations):
        return max(
            activations,
            key=lambda a: (
                len(a["rule"]["conditions"]),
                a["rule"]["priority"],
            ),
        )
    
class FIFOResolver:
    """Первое правило, попавшее в конфликтное множество."""

    def select(self, activations):
        return activations[0]
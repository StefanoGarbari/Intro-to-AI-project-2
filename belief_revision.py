from abc import ABC, abstractmethod
from dataclasses import dataclass

class Formula(ABC):
    @abstractmethod
    def __str__(self) -> str:
        pass

@dataclass(frozen=True)
class Proposition(Formula):
    name: str

    def __str__(self):
        return self.name

@dataclass(frozen=True)
class Negation(Formula):
    formula: Formula

    def __str__(self):
        return f"¬{self.formula}"

@dataclass(frozen=True)
class Conjunction(Formula):
    left: Formula
    right: Formula

    def __str__(self):
        return f"({self.left} ∧ {self.right})"

@dataclass(frozen=True)
class Disjunction(Formula):
    left: Formula
    right: Formula

    def __str__(self):
        return f"({self.left} ∨ {self.right})"

@dataclass(frozen=True)
class Implication(Formula):
    left: Formula
    right: Formula

    def __str__(self):
        return f"({self.left} → {self.right})"

@dataclass(frozen=True)
class BiImplication(Formula):
    left: Formula
    right: Formula

    def __str__(self):
        return f"({self.left} ↔ {self.right})"



# tests
f = BiImplication(Negation(Disjunction("a", "b")), "c")
e = Negation(Negation("a"))
print(f)
print(e)
print(f == e)
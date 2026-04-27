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


@dataclass(frozen=True)
class Literal:
    name: str
    negated: bool = False

    def __str__(self):
        return f"¬{self.name}" if self.negated else self.name

@dataclass(frozen=True)
class Clause:
    literals: frozenset[Literal]

    def __str__(self):
        if not self.literals:
            return "⊥"
        return " ∨ ".join(map(str, self.literals))

@dataclass(frozen=True)
class CNF:
    clauses: frozenset[Clause]

    def __str__(self):
        if not self.clauses:
            return "⊤"
        return "(" + ") ∧ (".join(map(str, self.clauses)) + ")"


def to_literal(f: Formula) -> Literal:
    match f:
        case Proposition(name):
            return Literal(name, False)

        case Negation(Proposition(name)):
            return Literal(name, True)

        case _:
            raise ValueError(f"Not a literal: {f}")
        
def to_clause(f: Formula) -> Clause:
    match f:
        case Disjunction(a, b):
            return Clause(
                to_clause(a).literals.union(to_clause(b).literals)
            )

        case _:
            return Clause(frozenset({to_literal(f)}))

def clauses_of(f: Formula) -> list[Clause]:
    match f:
        case Conjunction(a, b):
            return clauses_of(a) + clauses_of(b)

        case _:
            return [to_clause(f)]


def eliminate_implications(f: Formula) -> Formula:
    """
    returns a formula equivalent to f, without implications or bi-implications
    """
    match f:
        case Implication(a, b):
            return Disjunction(Negation(eliminate_implications(a)), eliminate_implications(b))

        case BiImplication(a, b):
            return Conjunction(eliminate_implications(Implication(a, b)), eliminate_implications(Implication(b, a)))

        case Negation(x):
            return Negation(eliminate_implications(x))

        case Conjunction(a, b):
            return Conjunction(eliminate_implications(a), eliminate_implications(b))

        case Disjunction(a, b):
            return Disjunction(eliminate_implications(a), eliminate_implications(b))

        case _:
            return f

def to_nnf(f: Formula) -> Formula:
    """
    returns a formula equivalent to f, after pushing negations inward
    """
    match f:
        case Negation(Negation(x)):
            return to_nnf(x)

        case Negation(Conjunction(a, b)): # de morgan
            return Disjunction(to_nnf(Negation(a)), to_nnf(Negation(b)))

        case Negation(Disjunction(a, b)): # de morgan
            return Conjunction(to_nnf(Negation(a)), to_nnf(Negation(b)))

        case Conjunction(a, b):
            return Conjunction(to_nnf(a), to_nnf(b))

        case Disjunction(a, b):
            return Disjunction(to_nnf(a), to_nnf(b))

        case Negation(x):
            return Negation(to_nnf(x))

        case _:
            return f

def distribute_or(a: Formula, b: Formula) -> Formula:
    """
    returns a formula equivalent to f, after distributing ∧ over ∨.
    e.g. (A ∨ (B ∧ C)) → (A ∨ B) ∧ (A ∨ C)
    """
    match (a, b):

        case (Conjunction(a1, a2), _):
            return Conjunction(distribute_or(a1, b), distribute_or(a2, b))

        case (_, Conjunction(b1, b2)):
            return Conjunction(distribute_or(a, b1), distribute_or(a, b2))

        case _:
            return Disjunction(a, b)

def distribute_to_cnf(f: Formula) -> Formula:
    match f:
        case Conjunction(a, b):
            return Conjunction(distribute_to_cnf(a), distribute_to_cnf(b))

        case Disjunction(a, b):
            return distribute_or(distribute_to_cnf(a), distribute_to_cnf(b))

        case _:
            return f
        
        # Implications, bi-implications and negations are handled by the steps before

def to_cnf(formula: Formula) -> CNF:
    f = eliminate_implications(formula)
    f = to_nnf(f)
    f = distribute_to_cnf(f)

    clauses = clauses_of(f)
    return CNF(frozenset(clauses))

# tests
f = BiImplication(Proposition("r"), Disjunction(Proposition("p"), Proposition("s")))
e = to_cnf(f)
print(f)
print(e)
print(f == e)
from abc import ABC, abstractmethod
from dataclasses import dataclass
from itertools import combinations

class Formula(ABC):
    @abstractmethod
    def __str__(self) -> str:
        pass

    def __repr__(self):
        return self.__str__()

@dataclass(frozen=True, repr=False)
class Proposition(Formula):
    name: str

    def __str__(self):
        return self.name

@dataclass(frozen=True, repr=False)
class Negation(Formula):
    formula: Formula

    def __str__(self):
        return f"¬{self.formula}"

@dataclass(frozen=True, repr=False)
class Conjunction(Formula):
    left: Formula
    right: Formula

    def __str__(self):
        return f"({self.left} ∧ {self.right})"

@dataclass(frozen=True, repr=False)
class Disjunction(Formula):
    left: Formula
    right: Formula

    def __str__(self):
        return f"({self.left} ∨ {self.right})"

@dataclass(frozen=True, repr=False)
class Implication(Formula):
    left: Formula
    right: Formula

    def __str__(self):
        return f"({self.left} → {self.right})"

@dataclass(frozen=True, repr=False)
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

def formula_to_cnf(formula: Formula) -> CNF:
    f = eliminate_implications(formula)
    f = to_nnf(f)
    f = distribute_to_cnf(f)

    clauses = clauses_of(f)
    return CNF(frozenset(clauses))


def negate_literal(lit: Literal) -> Literal:
    return Literal(lit.name, not lit.negated)

def is_tautology(clause: Clause) -> bool:
    for lit in clause.literals:
        if negate_literal(lit) in clause.literals:
            return True
    return False

def resolve(c1: Clause, c2: Clause) -> set[Clause]:
    """
    Returns all possible resolvents
    """
    resolvents = set()

    for lit in c1.literals:
        comp = negate_literal(lit)

        if comp in c2.literals:
            new_literals = c1.literals.union(c2.literals) - {lit, comp}
            resolvent = Clause(frozenset(new_literals))
            if not is_tautology(resolvent):  # ← skip tautologies
                resolvents.add(resolvent)
    return resolvents

def resolution(cnf: CNF) -> bool:
    """
    returns True if UNSAT (derives empty clause)
    """

    # Filter out any tautological clauses up front
    clauses = {c for c in cnf.clauses if not is_tautology(c)}

    while True:
        new = set()

        clause_list = list(clauses)

        for i in range(len(clause_list)):
            for j in range(i + 1, len(clause_list)):
                c1 = clause_list[i]
                c2 = clause_list[j]

                resolvents = resolve(c1, c2)

                if Clause(frozenset()) in resolvents:
                    return True

                new.update(resolvents)

        if new.issubset(clauses):
            return False

        clauses.update(new)

def set_to_cnf(kb: set[Formula]) -> CNF:
    clauses = set()

    for f in kb:
        clauses |= formula_to_cnf(f).clauses

    return CNF(frozenset(clauses))

def entails(kb: set[Formula], phi: Formula) -> bool:
    kb_cnf = set_to_cnf(kb)
    neg_phi = formula_to_cnf(Negation(phi))

    combined = CNF(kb_cnf.clauses.union(neg_phi.clauses))

    return resolution(combined)

def remainder_set(kb: set[Formula], phi: Formula) -> list[set[Formula]]:
    """
    Returns the set of all maximal subsets of kb that do not entail phi (kb ⊥ phi).
    """
    if not entails(kb, phi):
        return [kb]

    remainders = []
    kb_list = list(kb)

    # TODO check if there is a more optimized way to do this
    for size in range(len(kb_list) - 1, -1, -1):
        for subset_tuple in combinations(kb_list, size):
            subset = set(subset_tuple)

            # Check maximality
            if any(subset < r for r in remainders):
                continue

            if entails(subset, phi):
                continue

            remainders.append(subset)

    if not remainders:
        return [set()]

    return remainders

def score(f: Formula, reminder: list[set[Formula]]):
    return sum(1 for s in reminder if f in s)

def selection(reminder: list[set[Formula]]) -> list[set[Formula]]:
    formula_scores = {f: score(f, reminder) for f in set.union(*reminder)}

    #for x in reminder:
    #    print(x, "  ", sum(formula_scores[f] for f in x))

    max_score = max(sum(formula_scores[f] for f in x) for x in reminder)

    return [
        x for x in reminder
        if sum(formula_scores[f] for f in x) == max_score
    ]


def contraction(kb: set[Formula], phi: Formula) -> set[Formula]:
    reminder = remainder_set(kb, phi)
    selected = selection(reminder)
    partial_meet_contraction = set.intersection(*selected)
    return partial_meet_contraction

def expansion(kb: set[Formula], phi: Formula) -> set[Formula]:
    return kb.union({phi})

def revision(kb: set[Formula], phi: Formula) -> set[Formula]:
    contracted = contraction(kb, Negation(phi))
    revised = expansion(contracted, phi)
    return revised

# tests
#kb = {
#    BiImplication(Proposition("r"), Disjunction(Proposition("p"), Proposition("s"))),
#    Negation(Proposition("r")),
#}
#phi = Negation(Proposition("p"))

#print("KB:", kb)
#print("phi:", phi)
#print(entails(kb, phi))

example_set = {
    Proposition("a"),
    Proposition("b"),
    #BiImplication(Proposition("a"), Proposition("b")),
    BiImplication(Proposition("d"), Proposition("p")),
}
phi = BiImplication(Proposition("a"), Proposition("b"))
#rem = remainder_set(setex, f)
#print(setex, "⊥", f, "=", rem)

contracted = contraction(example_set, phi)
extended = expansion(contracted, phi)
print(example_set)
print(contracted)
print(extended)
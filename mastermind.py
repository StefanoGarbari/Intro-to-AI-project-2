from belief_revision import Formula, Proposition, Negation, Conjunction, Disjunction, Implication, BiImplication
from belief_revision import expansion, revision, contraction, entails
from itertools import combinations
from functools import reduce
from dataclasses import dataclass
from collections.abc import Iterable

@dataclass
class Feedback:
    correct_color_and_position: int
    correct_color_wrong_position: int

Guess = list[Proposition]

def mastermind_proposition(column: int, color: str) -> Proposition:
    return Proposition(str(column) + "_" + color)

def mastermind_guess(colors: list[str]) -> Guess:
    return [mastermind_proposition(i+1, color) for i, color in enumerate(colors)]

def get_color(p: Proposition) -> str:
    return p.name.split("_")[1]

def get_column(p: Proposition) -> int:
    return int(p.name.split("_")[0])

def get_colors(guess: Guess) -> list[str]:
    return [get_color(p) for p in guess]

def mastermind_belief_base(colors: list[str], columns: int) -> set[Formula]:
    kb = set[Formula]

    for column in range(1, columns + 1):
        propositions = [mastermind_proposition(column, color) for color in colors]
        #print(propositions)

        # Simple nature of the game, for each position (1, 2, 3, 4), there is exactly one colour
        at_least_one = reduce(Disjunction, propositions)
        at_most_one = reduce(Conjunction, (Negation(Conjunction(a, b)) for a, b in combinations(propositions, 2)))

        #print(at_least_one)
        #print(at_most_one)
        kb = expansion(kb, at_least_one)
        kb = expansion(kb, at_most_one)

    return kb

TAUTOLOGY: Formula = Disjunction(Proposition("_"), Negation(Proposition("_")))
CONTRADICTION: Formula = Conjunction(Proposition("_"), Negation(Proposition("_")))
def conjunction(formulas: Iterable[Formula]) -> Formula:
    formulas = list(formulas)

    if not formulas:
        return TAUTOLOGY
    return reduce(Conjunction, formulas)

def disjunction(formulas: Iterable[Formula]) -> Formula:
    formulas = list(formulas)

    if not formulas:
        return CONTRADICTION
    return reduce(Disjunction, formulas)

def feedback_to_formula(guess: Guess, feedback: Feedback) -> Formula:
    m = feedback.correct_color_and_position
    n = feedback.correct_color_wrong_position

    C = combinations(guess, m)
    formula = disjunction(
        (
            Conjunction(
                Conjunction(
                    conjunction(
                        S
                    ),
                    conjunction(
                        (Negation(p) for p in guess if not p in S)
                    ),
                ),
                disjunction(
                    (
                        Conjunction(
                            # per ogni colore in H, ce n'è almeno uno eccetto quelli che sono in guess
                            disjunction(
                                (p for p in (mastermind_proposition(i, c) for c in H for i in range(1, 1+len(guess))) if p not in guess)
                            ) if H else TAUTOLOGY,
                            # per ogni colore non in H, non (ce n'è almeno uno eccetto quelli che sono in guess)
                            conjunction(
                                (Negation(p) for p in (mastermind_proposition(i, c) for c in get_colors((p for p in guess if not p in S)) for i in range(1, 1+len(guess)) if c not in H) if p not in guess)
                            )
                        )
                        for H in combinations(
                            get_colors((p for p in guess if not p in S)),
                            n
                        )
                    )
                )
            ) for S in C
        )
    )

    return formula

def main():
    colors = [
        "red",
        "pink",
        "yellow",
        "blue",
        "white",
        "green",
    ]

    columns = 4

    kb = mastermind_belief_base(colors, columns)

    #print(kb)

    guess = mastermind_guess(["red", "blue", "yellow", "pink"])
    feedback = Feedback(2, 1)
    
    new_info = feedback_to_formula(guess, feedback)
    print(new_info)
    kb = set()
    kb = expansion(kb, new_info)
    #print(entails(kb, Negation(new_info)))

    print(kb)
    print(entails(kb, Proposition("random")))


if __name__ == "__main__":
    main()
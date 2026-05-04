from belief_revision import Formula, Proposition, Negation, Conjunction, Disjunction, Implication, BiImplication
from belief_revision import expansion, revision, contraction, entails, formula_to_cnf

def main():
    example_1()
    example_2()
    example_3()
    example_4()
    example_5()
    example_6()

def example_1():
    # Example in the report
    kb = {
        Proposition("p"),
        Implication(Proposition("p"), Proposition("q")),
        Proposition("r"),
    }

    phi = Negation(Proposition("q"))

    kb_ = revision(kb, phi)

    print("Example 1")
    print(kb,"∗", phi, "=", kb_)
    print()

def example_2():
    # Example from lecture 10 - entailment

    # Robert does well in the exam if and only if he is prepared or lucky.
    # Robert does not do well in the exam.
    kb = {
        BiImplication(Proposition("r"), Disjunction(Proposition("p"), Proposition("l"))),
        Negation(Proposition("r")),
    }

    # Robert is not prepared.
    phi = Negation(Proposition("p"))

    is_entailed = entails(kb, phi)

    print("Example 2")
    print(kb, "⊨" if is_entailed else "⊭", phi)
    print()

def example_3():
    # Revision produces consistent output, expansion not necessarly
    kb = {
        Proposition("a"),
        Implication(Proposition("a"), Proposition("b")),
    }

    phi = Negation(Proposition("b"))

    kb_expanded = expansion(kb, phi)
    kb_revised = revision(kb, phi)

    psi = Proposition("x") # unrelated proposition. It's entailed if the belief base is inconsistent
    
    print("Example 2")
    print(kb,"∗", phi, "=", kb_revised)
    print(kb_revised, "⊨" if entails(kb_revised, psi) else "⊭", psi)
    print(kb,"+", phi, "=", kb_expanded)
    print(kb_expanded, "⊨" if entails(kb_expanded, psi) else "⊭", psi)
    print()

def example_4():
    # Example from lecture 10 - CNF form

    # Robert does well in the exam if and only if he is prepared or lucky.
    # Robert does not do well in the exam.
    phi = BiImplication(Proposition("r"), Disjunction(Proposition("p"), Proposition("s")))

    phi_cnf = formula_to_cnf(phi)

    print("Example 4")
    print(phi, "=", phi_cnf)
    print()

def example_5():
    # entailment
    kb = {
        Disjunction(Proposition("a"), Proposition("b")),
        BiImplication(Proposition("a"), Proposition("b")),
    }

    phi = Conjunction(Proposition("a"), Proposition("b"))

    is_entailed = entails(kb, phi)

    print("Example 5")
    print(kb, "⊨" if is_entailed else "⊭", phi)
    print()

def example_6():
    # contraction
    kb = {
        Implication(Proposition("a"), Proposition("x")), Proposition("a"),
        Implication(Proposition("b"), Proposition("x")), Proposition("b"),
    }

    phi = Proposition("x")

    kb_ = contraction(kb, phi)

    print("Example 6")
    print(kb,"÷", phi, "=", kb_)
    print()


if __name__ == "__main__":
    main()
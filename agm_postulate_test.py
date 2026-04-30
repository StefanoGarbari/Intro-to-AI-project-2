from belief_revision import Formula, Proposition, Negation, Conjunction, Disjunction, Implication, BiImplication
from belief_revision import expansion, revision, contraction, entails
import unittest

class AGMTestCase(unittest.TestCase):
    """Base class with shared AGM helper methods."""

    def assertEquivalentBeliefSets(self, kb1: set[Formula], kb2: set[Formula]):
        # to check equivalency of two sets, we check that each formula of the first
        # set is entailed by the second set, and vice versa (mutual entailment)
        for formula in kb1:
            self.assertTrue(entails(kb2, formula))
        for formula in kb2:
            self.assertTrue(entails(kb1, formula))

class TestContractionPostulates(AGMTestCase):
    """
    AGM÷ Rationality Postulates of Contraction
    """
    
    def setUp(self):
        self.kb = {
            Proposition("p"),
            Implication(Proposition("p"), Proposition("q")),
            Proposition("r"),
        }

    def test_success(self):
        phi = Proposition("q") # not a tautology
        result = contraction(self.kb, phi)
        self.assertFalse(entails(result, phi))
    
    def test_inclusion(self):
        phi = Proposition("q")
        result = contraction(self.kb, phi)
        # if the base is a subset, then the set is a subset
        self.assertTrue(result.issubset(self.kb))

    def test_vacuity(self):
        phi = Proposition("x")
        result = contraction(self.kb, phi)
        # if the base is a subset, then the set is a subset
        self.assertEquivalentBeliefSets(result, self.kb)

    def test_extensionality(self):
        phi = Implication(Proposition("p"), Proposition("q"))
        psi = Disjunction(Negation(Proposition("p")), Proposition("q"))
        contracted_phi = contraction(self.kb, phi)
        contracted_psi = contraction(self.kb, psi)
        self.assertEquivalentBeliefSets(contracted_phi, contracted_psi)

class TestRevisionPostulates(AGMTestCase):
    """
    AGM∗ Rationality Postulates of Revision
    """

    def setUp(self):
        self.kb = {
            Proposition("p"),
            Implication(Proposition("p"), Proposition("q")),
            Proposition("r"),
        }

    def test_success(self):
        phi = Negation(Proposition("q"))
        result = revision(self.kb, phi)
        self.assertTrue(entails(result, phi))
    
    def test_inclusion(self):
        phi = Negation(Proposition("q"))
        revised = revision(self.kb, phi)
        expanded = expansion(self.kb, phi)
        # if the base is a subset, then the set is a subset
        self.assertTrue(revised.issubset(expanded))

    def test_vacuity(self):
        phi = Negation(Proposition("s"))
        revised = revision(self.kb, phi)
        expanded = expansion(self.kb, phi)
        self.assertEquivalentBeliefSets(revised, expanded)

    def test_consistency(self):
        phi = Negation(Proposition("q"))
        revised = revision(self.kb, phi)
        # an inconsistent base entails any Formula
        self.assertFalse(entails(revised, Proposition("x")))

    def test_extensionality(self):
        phi = Implication(Proposition("a"), Proposition("b"))
        psi = Disjunction(Negation(Proposition("a")), Proposition("b"))
        revised_phi = revision(self.kb, phi)
        revised_psi = revision(self.kb, psi)
        self.assertEquivalentBeliefSets(revised_phi, revised_psi)



if __name__ == "__main__":
    unittest.main(verbosity=2)
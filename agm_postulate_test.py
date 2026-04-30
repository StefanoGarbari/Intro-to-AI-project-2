from belief_revision import Formula, Proposition, Negation, Conjunction, Disjunction, Implication, BiImplication
from belief_revision import expansion, revision, contraction, entails
import unittest


class TestContractionPostulates(unittest.TestCase):
    """
    AGM÷ Rationality Postulates of Contraction
    """
    def test_success(self):
        pass
    
    def test_inclusion(self):
        pass

    def test_vacuity(self):
        pass

    def test_consistency(self):#NO????
        pass

    def test_extensionality(self):
        pass

class TestRevisionPostulates(unittest.TestCase):
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
        self.assertIn(phi, result)
    
    def test_inclusion(self):
        phi = Negation(Proposition("q"))
        revised = revision(self.kb, phi)
        expanded = expansion(self.kb, phi)
        self.assertTrue(revised.issubset(expanded))

    def test_vacuity(self):
        phi = Negation(Proposition("s"))
        revised = revision(self.kb, phi)
        expanded = expansion(self.kb, phi)
        self.assertEqual(revised, expanded)

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

        # to check equivalency of two sets, we check that each formula of
        # the first set is entailed by the second set, and vice versa
        for formula in revised_phi:
            self.assertTrue(entails(revised_psi, formula))

        for formula in revised_psi:
            self.assertTrue(entails(revised_phi, formula))



if __name__ == "__main__":
    unittest.main(verbosity=2)
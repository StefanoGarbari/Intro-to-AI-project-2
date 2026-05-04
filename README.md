# Belief revision system

A Python implementation of a belief revision engine based on propositional logic.

## Requirements

- Python 3.10+

## Execution

Run examples and tests:

```bash
python examples.py
python agm_postulate_test.py
```

## Usage

### Creating formulas

Formulas are built using the provided classes:

- `Proposition`
- `Negation`
- `Conjunction`
- `Disjunction`
- `Implication`
- `BiImplication`

Example:

```python
from belief_revision import *

p = Proposition("p")
q = Proposition("q")
r = Proposition("r")

formula1 = Implication(p, q)        # (p → q)
formula2 = Negation(r)              # ¬r
formula3 = Conjunction(p, q)        # (p ∧ q)
formula4 = Disjunction(q, r)        # (q ∨ r)

print(formula1)
# (p → q)
```

---

### Creating a knowledge base

A knowledge base is simply a Python `set[Formula]`.

#### Initialized knowledge base
```python
kb = {
    Implication(p, q),
    #...
}
```
#### Empty knowledge base
```python
kb = set()
```

---

### Entailment checking

Use `entails(kb, phi)` to test whether a formula is entailed by a knowledge base.

```python
result = entails(kb, phi)

print(result)
# True
```

---

### Belief change operations

There are three available belief change operations. They all take a belief base and a formula as parameters, and return a new belief base without modifying the inputs.

#### Expansion

Expansion simply adds a formula.

```python
kb_ = expansion(kb, phi)

print(kb_)
```


---

#### Contraction

Contraction removes enough beliefs so that a formula is no longer entailed.

```python
kb_ = contraction(kb, phi)

print(kb_)
```

---

#### Revision

Revision adds a new belief while maintaining consistency.

```python
kb_ = revision(kb, phi)

print(kb_)
```


# The Suite as a Specification

A good test reads like a specification. A good *suite* **is** one: delete the implementation, and the test names alone should tell you the rules it obeyed.

That only holds if the suite's structure comes from the specification's structure — the rules of the domain, the states the module distinguishes — and not from the shape of the code under test. This file is how you get there: **partition** the rules, name each cell as a **proposition**, nest so the names assemble.

## Partition the rules

One test per rule. The rules must overlap nowhere and leave no gap.

Leap years, as four names and nothing else:

```
A_year_not_divisible_by_4_is_not_a_leap_year
A_year_divisible_by_4_but_not_by_100_is_a_leap_year
A_year_divisible_by_100_but_not_by_400_is_not_a_leap_year
A_year_divisible_by_400_is_a_leap_year
```

`divisible_by_4_is_a_leap_year` and `divisible_by_100_is_not_a_leap_year` would be a plausible-sounding pair that overlaps at 2000 and contradicts itself there. Writing the exclusions (`but_not_by_100`) is what turns a list of names into a partition.

**A name bound to a value is not a rule.** `_2016_is_a_leap_year` / `_1900_is_not_a_leap_year` looks specific and is worthless: swap the data to 2020 and 2100 and every name changes while the specification hasn't moved. The value belongs in the test's data, the rule in its name.

Once the partition exists, the implementation is free to vary under it. The four names above hold unchanged against a correct implementation and against a broken `year % 4 == 0` — the second one just fails two of them, and the failure says exactly which rule broke.

## Derive the partition from the state model

For anything stateful, don't invent the cells — read them off the module's own state machine. This is a procedure, not advice:

1. **List the operations** on the module's **interface** — the whole alphabet, constructors included.
2. **Name the states** the module distinguishes. Not fields: states that change what an operation *does*. A stack has Empty and Non-Empty. A bounded queue has Empty, Non-Full, and Full.
3. **Draw the edges.** For each state, every operation, with its guard. `pop [depth > 1]` leaves a stack Non-Empty; `pop [depth = 1]` returns it to Empty. Those are two different rules and two different tests.
4. **Mark the partial operations.** Any state where an operation is undefined is an error edge — `top` and `pop` on an Empty stack. These are the tests that get skipped when the partition is guessed rather than derived.
5. **One test per edge**, nested under its source state.
6. **Bound the input domain separately.** Endpoints of the supported range get a test asserting they *are* supported; inputs outside it get tests asserting the specified failure. Leaving unsupported input unspecified is a gap in the partition, not an omission from it.

Completion criterion: every state has a group, and every edge leaving it — including error edges — has a test. Count them against the diagram.

A bounded queue's Full state exists only because of the guard `[length = capacity]`; miss the guard in step 3 and the entire `that_is_full` group of the specification silently doesn't exist.

## Never mirror the method list

One test per public method is the default shape, and it is the wrong one.

```
test_constructor  test_push  test_pop  test_depth  test_top
```

This suite is the header file with assertions sprinkled on it. Two tells:

- **It moves when the code moves.** Default the constructor and `test_constructor` has nothing left to say — a test deleted by a refactor that changed no behaviour.
- **It has nowhere to put a precondition.** Rewrite those names as behaviours and honesty intrudes: "can be pushed", but "can *sometimes* be popped", "*sometimes* has a top". That *sometimes* is a rule, and the method-per-test structure was hiding it. Under a state model it's just the error edge out of Empty.

## Name each test as a proposition

A test name must be an indicative sentence — one that can be true or false. It is read aloud when the test fails, and it must name the rule that has been demonstrated false, with no recourse to the implementation.

- **Indicative, not aspirational.** `it is not empty`, not `it should not be empty`. The suite states what holds; hedging costs words and certainty.
- **Domain language, not wire format.** `IsLeapYear_YearNotDivisibleBy4_ReturnsFalse` fails on both counts: it repeats the method name, and "ReturnsFalse" describes a return value where the rule wanted "is not a leap year". A reader learns nothing about leap years from it.
- **A proposition, not a bucket.** `TestLeapYears` is a heading, not a claim; it will accumulate assertions from two unrelated rules and report them under one name.

## Nest so names assemble

Write the shared subject once and let the enclosing scopes supply it:

```
Stack_spec
  An_empty_stack
    throws_when_queried_for_its_top_item
    acquires_depth_by_retaining_a_pushed_item_as_its_top
  A_non_empty_stack
    on_popping_reveals_tops_in_reverse_order_of_pushing
```

Each leaf still reads as a full sentence, concatenated from its path.

The second payoff isn't cosmetic: **the group owns its setup.** Construction of "an empty stack" hoists into the group named for it, so the name of the state and the code producing it are the same thing.

Nesting forces a choice of primary axis, and the three parts of given-when-then are three different ones:

- **Given** — group by initial state, across operations. The default; it's the axis a state model hands you.
- **When** — group by operation, across states and outcomes.
- **Then** — group by outcome, across operations and states.

Pick deliberately. Given-when-then also survives *inside* a test as its layout (context, invocation, expectation), which is the same three parts arrange-act-assert names.

## Parameterise within a cell, never across

One rule, one test, many values. Use the framework's parameterisation (`[TestCase]`, `@ParameterizedTest`, `pytest.mark.parametrize`, `test.each`) so the rule is written once and the data reads as a table a non-programmer can check.

Values worth including for a rule: an ordinary one, an awkward-but-legal one, and the endpoints of the range the rule governs.

Two hard limits:

- **The rule may not vary with the data.** The moment a parameterised case needs a different expectation *kind*, it's a second cell in the partition and wants its own name.
- **The expected value never comes from a re-derivation of the implementation.** Cranking the data volume up until the oracle has to be computed is how a suite becomes **tautological** (see [SKILL.md](SKILL.md)) — an exhaustive run of 10,000 cases asserting `impl(x) == copy_of_impl(x)` proves nothing, and it has replaced four propositions with one vacuous name. Prefer few named rules over exhaustive unnamed ones.

---

*Distilled from Kevlin Henney, "Structure and Interpretation of Test Cases". Full source analysis: [`research/kevlin-henney-structure-and-interpretation-of-test-cases.md`](../../research/kevlin-henney-structure-and-interpretation-of-test-cases.md).*

# Research — What does Kevlin Henney's *Structure and Interpretation of Test Cases* actually argue, and what should a testing skill take from it?

`Grounding a proposed test-authoring skill in the primary source rather than a second-hand summary` · 28 Jul 2026

## Question

A draft skill ("Structure and Interpretation of Test Cases") was distilled from the GOTO 2022 recording by an LLM without access to the talk's content. Which of its claims are in the talk, which are missing, and which are inverted — and what is the subset worth encoding as a skill in this repo?

## Source and its limits

- **Primary:** the 149-slide deck, [`slideshare.net/Kevlin/structure-and-interpretation-of-test-cases`](https://www.slideshare.net/slideshow/structure-and-interpretation-of-test-cases/120555919) (uploaded 2018-10-24, the ACCU/NDC lineage of the same talk). Full slide text extracted; every `sN` below is a slide number.
- **Not available:** the GOTO 2022 video ([`MWsk1h8pv2Q`](https://www.youtube.com/watch?v=MWsk1h8pv2Q), 46:24) publishes **no captions or transcript**. Everything Kevlin says *between* slides is therefore unverified here. The deck is code-and-quote heavy — the argument is legible from it — but narration-only asides are outside this note's evidence.
- Consequence: any claim below is slide-grounded. A claim attributed to the talk with no slide cite is marked `[UNVERIFIED]`.

## Answer

The talk is not a list of testing rules. It is **one refactoring, performed twice** — on a test name (leap year, s17–63) and on a test *suite* (stack → queue, s65–147) — driving to a single thesis: **a test suite is a specification, and its structure should be derived from the specification's own structure** (the rules of the domain; the state model of the abstract data type), not from the shape of the code under test.

The draft skill captures the naming half and misses the derivation half — which is the actionable half. It also **inverts** the talk's property-based/data-driven section: what the draft presents as the aspirational endpoint (§6) is the exact code Kevlin puts up as a cautionary tale.

## Findings

### 1. The spine of the argument

| Move | Slides | Content |
|---|---|---|
| Audience | s3, s5–6 | SICP's "written for people to read, and only incidentally for machines to execute", applied to test code. Meszaros: write tests for the person trying to understand your code; good tests act as documentation. |
| What a unit test *is* | s9, s11 | Kevlin's own definition: a test of **behaviour** whose success or failure is wholly determined by the correctness of the test and of the unit under test. Then a three-way partition: unit testable / necessarily not unit testable / **should be unit testable but isn't**. |
| Framework fixation | s12 | Tod Golding: reducing unit testing to "the mechanics of exercising xUnit" is thinking too narrowly. |
| Coverage | s14–15 | Fowler ("such statements miss the point"); Marick's distinction between *expecting* high coverage and *requiring* it. |
| Naming refactor | s17–33 | ~15 successive rewrites of one test name. |
| The propositional turn | s35–37 | Propositions state how things are or might be; only indicative sentences that can be true or false express propositions. A test name should be one. |
| Names ⟂ implementation | s38–41 | The same four names are shown against a correct implementation and against a deliberately broken one (`year % 4 == 0`). The names are the fixed specification; the code varies under them. |
| Specification, explicitly | s42 | Pryce & Freeman: for tests to drive development they must *clearly express* the required functionality — they must be clear specifications of it. |
| Nesting | s43–53 | Names decomposed into `namespace Leap_year_spec` → fixture `A_year_is_a_leap_year` → test `if_it_is_divisible_by_4_but_not_by_100`. Then data-driven (`[TestCase]`, `[Values]`, `[Range]`). |
| **The tautology trap** | s54–58 | See §4. |
| Happy/unhappy grouping | s59–63 | Anna Karenina's opening line, then fixtures `A_year_is_not_supported` (0, negatives) and `A_year_is_supported` (1, `int.MaxValue`). |
| ADT / don't mirror the API | s65–77 | See §5. |
| Given-When-Then | s79–97 | See §6. |
| Contracts | s99–106 | Hoare's `P {Q} R` → `{P} Q {R}`; Lampson on interface-as-contract; the stack's pre/postconditions written as comments and then as C++ `[[expects]]`/`[[ensures]]`. |
| State model → test structure | s108–118 | See §7. |
| GWT as grouping axes | s119–121 | See §6. |
| Don't test through internals | s126–133 | See §8. |
| Full worked derivation | s136–147 | Queue with bounding capacity: producer/consumer decoupling, the N=∞/N=1/N=0 degenerate cases, a three-state model (Empty / Non-Full / Full), then a nested `Queue_spec` whose classes *are* those states. |

### 2. Naming: what the refactor actually rejects, in order

Each name is discarded for a specific, nameable reason (s18–33):

1. `Test()` — says nothing.
2. `TestIsLeapYear()` — names the method, not a behaviour.
3. `TestIsLeapYearIsCorrect()` — "correct" is content-free.
4. `Test1()`, `Test2()` — sequence numbers.
5. `TestLeapYears()` / `TestNonLeapYears()` — a bucket, not a rule; s23 shows it accumulating unrelated assertions (2016 and 2000 — two *different* rules) in one method.
6. `Test2016IsALeapYear()` — an example masquerading as a rule. s27→s28 makes the point by swapping the data (2016→2020, 1900→2100): the names all change, but **nothing about the specification changed**. Names bound to data are unstable.
7. `Years_divisible_by_4_are_leap_years` — a rule at last, but s29→s32 sharpens it, because "divisible by 4" and "divisible by 100" overlap. The endpoint is a **partition** with no overlaps and no gaps:
   - years not divisible by 4 → not leap
   - divisible by 4 but not by 100 → leap
   - divisible by 100 but not by 400 → not leap
   - divisible by 400 → leap
8. `IsLeapYear_YearNotDivisibleBy4_ReturnsFalse` (s33) — presented as the *counter-example* to the whole exercise. It re-introduces the method name, and "ReturnsFalse" describes the wire format, not the domain. A reader learns nothing about leap years from it.

**The load-bearing idea is the partition, not the casing.** Snake_case, sentence-case, nested sections — all appear as vehicles. What survives every rewrite is: *one name per rule, and the names together exhaust the rule space.*

### 3. Nesting is DRY applied to names, and it carries fixtures

s43 splits `Leap_year_spec` / `A_year_is_a_leap_year` / `if_it_is_divisible_by_4_but_not_by_100`. The full sentence is read by concatenating the enclosing scopes, so the shared subject is written once.

s114→s115 shows the second payoff, which is not cosmetic: once tests are nested under `SECTION("An empty stack")`, the *construction of that state* hoists into the enclosing section. **The name of the group and the setup for the group are the same thing** — Given as structure, not as a comment.

### 4. The tautology trap — the draft's §6 is inverted

s54–s57 build, step by step:

```
A_year { is_either_a_leap_year_or_not([Range(1, 10000)] int year) {
    Assert.AreEqual(year % 4 == 0 && year % 100 != 0 || year % 400 == 0, IsLeapYear(year));
} }
```

s57 extracts that expression into a helper `LeapYearExpectation`, making it look respectable. **s58 then shows the production code — the identical expression.** The exhaustive 10,000-case data-driven test asserts the implementation against a copy of itself, and its single name (`is_either_a_leap_year_or_not`) is a tautology in the literal logical sense: true of every year, leap or not.

Two lessons, both the opposite of the draft's §6:

- Cranking up data volume can *destroy* a specification. Four propositional names covering a partition were replaced by one vacuous name and 10,000 rows of nothing.
- An oracle derived the same way as the implementation is not an oracle. (This repo already names this: `skills/tdd/SKILL.md` — **tautological**.)

The talk does not endorse property-based testing here, and the draft's Fizz/inverse-constraint example does not appear anywhere in the deck. That example belongs to Kevlin's other material; attributing it to this talk is `[UNVERIFIED]`.

### 5. Don't mirror the API — the strongest omission from the draft

The stack section (s65–77) attacks the default a test generator reaches for: one test per public method.

- s66 Liskov: an abstract data type is characterised **completely by the operations available on those objects** — as a set, with relationships, not as a list to enumerate.
- s69 is the anti-pattern: `test stack::stack`, `test stack::push`, `test stack::pop`, `test stack::depth`, `test stack::top`. s70–71 tidy it into sections and strip the noise words, and it is still wrong — it is still the header file with `TEST_CASE` sprinkled on it.
- s72→s73 lands the blow: change the constructor to `= default` and the `SECTION("constructor")` test has nothing left to say. **A test suite shaped like the API changes shape when the API is refactored, even though no behaviour changed.**
- s76→s77 is the reveal. Rewriting the section names as behaviours — "can be pushed", "can be popped" — forces honesty, and the honest version is "can **sometimes** be popped", "**sometimes** has a top". That word *sometimes* is a precondition the method-per-test structure had no place to put. The structure was hiding the specification.

### 6. Given-When-Then: three separate uses, and a style rule

**As prose (s79–88).** `Given an empty stack / When an item is pushed / Then it should not be empty` → s81 Strunk & White ("make definite assertions… avoid tame, colourless, hesitating, noncommittal language") → s82 `it must not be empty` → s83 `it is not empty`. This — not a blanket ban on the word "should" — is the actual argument. Then s85–87 show GWT jammed into a single identifier (`GivenAnEmptyStackWhenAnItemIsPushedThen…`) as a reductio, and s88–89 collapse it, under "omit needless words", to a plain sentence: *An empty stack acquires depth by retaining a pushed item as its top*.

**As layout (s94–97).** Meszaros' three-part scenario shape, written as `// Arrange / // Act / // Assert` and then relabelled `// Given / // When / // Then` — the same three parts twice-named.

**As three independent grouping axes (s119–121).** The part with no counterpart in the draft:

- **Given** groups tests for different operations sharing a common initial state.
- **When** groups tests for one operation across different initial states and outcomes.
- **Then** groups tests by common outcome, regardless of operation or initial state.

Nesting forces a choice of primary axis. The talk's worked examples pick **Given** (state-first: `A new stack` / `An empty stack` / `A non empty stack`), because that is the axis the state model hands you — but the choice is explicit, not automatic.

### 7. Where the partition comes from — the derivation the draft never mentions

The draft says to test "boundary cases" and "error cases" and leaves the agent to invent them. The talk gives a construction:

- s108 the ADT's **alphabet**: `{new, push, pop, depth, top}`.
- s109 its **traces**: the sequences of operations that are legal (`⟨new⟩`, `⟨new, push⟩`, `⟨new, push, pop⟩`, …).
- s110–111 the **state model**: Empty ⇄ Non-Empty, with the transitions labelled by operation and guard (`pop [depth > 1]` keeps you Non-Empty; `pop [depth = 1]` returns you to Empty), and the partial operations shown as `top / error`, `pop / error` on Empty.
- s112 the test suite is that diagram: sections `A new stack`, `An empty stack`, `A non empty stack`, with each state's outgoing edges as its tests.
- s136–147 repeats the derivation from scratch for a bounded queue, where the guard `[length = capacity]` splits Non-Empty into **Non-Full** and **Full** — and the spec (s145) grows exactly the nested classes `that_is_not_full` / `that_is_full` to match.

This is a **repeatable procedure**: states → transitions → guards → one test per edge, named as a proposition, nested under its state. It is the only part of the talk that is genuinely mechanical, and it is precisely the part an agent needs, because "pick good boundary values" is advice an LLM already nods along to and does badly.

s60–63 add the complement for the *input* domain rather than the state space: `A_year_is_supported` (1, `int.MaxValue`) and `A_year_is_not_supported` (0, negatives) — supported-range endpoints get their own fixture, and unsupported inputs are specified as throwing, not left undefined.

### 8. Tests observe through the interface, or they observe nothing

s126–128 corrupt the good stack test three ways — `stack.items.size()`, `stack.get_items().size()`, `stack.items().size()` — reaching past `depth()`/`top()` into representation. s129 restores it. s131 gives the reason (Liskov: a programmer is concerned with the behaviour an object exhibits, not how an implementation achieves it), and s132–133 prove it operationally: **two completely different implementations** (a `std::vector` with `back()`, and a `std::forward_list` with a separate size counter and `front()`) must satisfy the identical spec. Any of the s126–128 tests would fail on the second implementation despite identical behaviour.

This is the same claim as `skills/codebase-design/SKILL.md`'s "the interface is the test surface" and `skills/tdd/SKILL.md`'s **implementation-coupled** anti-pattern. It needs no new vocabulary in this repo.

### 9. Contracts are an alternative destination for some assertions

s99–106 (Hoare, Lampson, then the stack annotated with pre/postconditions and with C++ `[[expects]]`/`[[ensures]]`) put a fork in front of the reader that the draft doesn't mention: a fact about the module — `depth() >= 0`, `pop` requires `depth() > 0` — can live in the *interface as a contract* rather than in a test. Tests then exercise the contract rather than restate it.

## Verdict on the draft skill

| Draft section | Status |
|---|---|
| §1 Executable specifications | **In the talk** (s3, s5–6, s42). Weakest-value section for a skill: a model already agrees, and `skills/tdd/SKILL.md` already says a good test "reads like a specification". |
| §1 "delete the production code and reconstruct it from the tests" | `[UNVERIFIED]` as a talk claim, but a fair restatement of s38–41 and a usable check. |
| §1 Coverage is a metric not a target | **In the talk** (s14–15). Already in `skills/improve-test-suite/SKILL.md`. |
| §2 Propositional naming | **In the talk** and correctly identified (s35–37) — the draft's best section. |
| §2 "BANNED WORD: should" | **Distorted.** The talk's rule is Strunk & White's *make definite assertions* (s81–83): prefer the indicative. Absolutising it into a banned word also violates this repo's own **negation** guidance (`skills/writing-great-skills/SKILL.md`) — prompt the positive. |
| §2 banned patterns (`Test1`, `Test_2020`, `TestWorks`) | **In the talk** (s18–28), and the *reason* the draft omits — s27→s28 — is better than the rule. |
| §3 Nesting / DRY on information | **In the talk** (s43). Misses the fixture-hoisting payoff (s115) and the choice-of-axis question (s119–121). |
| §3 "Narrative sequencing… 75% of years" | `[UNVERIFIED]`. The deck reorders the four names (s29→s30) but shows no frequency argument. Plausibly narration; treat as unsourced. |
| §4 Parameterisation | **In the talk** (s49–53), but stated without the constraint that makes it safe — see §6 of the draft below. |
| §5 "The *Tulip* of coverage" | **Not in the deck.** No such term, no four-category taxonomy. The underlying content (supported boundaries, unsupported inputs) is real (s60–63); the framing and the name appear invented. |
| §6 Property-based "two-way constraints" | **Inverted.** s54–58 uses exhaustive data-driven testing with a derived oracle as the failure case. The Fizz example is not in this talk. |
| — | **Missing:** the definition of a unit test (s9) and "should be unit testable but isn't" (s11); *don't mirror the API* (s69–77); GWT's three grouping axes (s119–121); the state-model derivation (s108–118, s136–147); contracts as an alternative to tests (s99–106); interface-only observation with two implementations as proof (s126–133). |

## Implications for this repo

Three of the draft's six sections restate what `skills/tdd/SKILL.md`, `skills/codebase-design/SKILL.md`, and `skills/improve-test-suite/SKILL.md` already say, in new words — which `skills/writing-great-skills/SKILL.md` classes as **duplication** (inflating a meaning's rank on the information hierarchy) and as drift away from a **single source of truth**.

What is genuinely new, and not something a model does well unprompted:

1. **Partition before you write.** Enumerate the rules so they overlap nowhere and leave no gap; one test per cell.
2. **Derive the partition from the state model,** not from the method list — states, transitions, guards, partial operations.
3. **Name each cell as a proposition** — an indicative sentence that can be false.
4. **Nest so the name assembles from its scopes,** and let the group own its setup.
5. **Parameterise within a cell only** — the data varies, the rule does not; and the expected value never comes from a re-derivation of the implementation.

Items 1–2 are a *procedure*; 3–5 are *reference*. Nothing here needs new vocabulary: **seam**, **interface**, **implementation-coupled**, and **tautological** already exist in this repo and carry the rest.

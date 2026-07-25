---
name: batch-grilling
description: Grill the user about a plan, decision, or idea, up to three questions at a time. Use when the user asks to be grilled in batches or rounds, or wants fewer back-and-forths.
---

Interview me relentlessly about every aspect of this until we reach a shared understanding. Walk down each branch of the decision tree, resolving dependencies between decisions one-by-one. For each question, provide your recommended answer.

Ask up to three questions at a time, waiting for feedback before continuing. The questions in a batch must be mutually independent — anything whose answer depends on another question in the same batch waits for the next round; ask fewer than three when fewer are independent. When more than three are unblocked, ask the ones with the most decisions hanging off them first, so each round collapses as much of the tree as possible.

If a *fact* can be found by exploring the environment (filesystem, tools, etc.), look it up rather than asking me. The *decisions*, though, are mine — put each one to me and wait for my answer.

Do not act on it until I confirm we have reached a shared understanding.

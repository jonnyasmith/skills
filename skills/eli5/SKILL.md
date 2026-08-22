---
name: eli5
description: Explain a topic like I'm a 5 year old. Use when the user types /eli5 <topic> or asks for a dead-simple picture explainer of how something works.
---

# eli5

Explain like I'm someone who knows nothing about this topic, using a HTML artifact with big pictures and few words.

Topic: $ARGUMENTS

## Deliver it

1. Write one self-contained HTML file — inline CSS, no network assets — to `/tmp/eli5-<slug>.html`.
2. Open it on the user's desktop, unprompted: `setsid -f xdg-open /tmp/eli5-<slug>.html`.
   Done when `hyprctl clients -j` lists a window carrying the page title.
3. Reply with the file path and a short prose version of the same explanation.

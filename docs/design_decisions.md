# Design Decisions
## Why no model training?
Fine-tuning models on architecture diagrams is brittle.
We use **rules** for certainty ("If A then B") and **vectors** for similarity ("This looks like the 2017 outage").

## Why separate agents?
Single-prompt "do everything" approach fails at complexity.
Separating Failure Detection from Architecture Design prevents "solutioneering" (jumping to solutions without understanding the problem).

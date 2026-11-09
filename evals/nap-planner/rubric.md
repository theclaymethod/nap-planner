# Scope of checks

Solver cases exercise the real CLI. Each returned plan must obey the request: future starts, positive durations from the allowed per-position choices, chronological nonoverlap, applicable wake bounds, exact fixed naps, unavailable intervals, bedtime limits, and correct total sleep and objective distances. Returned metrics are recomputed. On a complete finite-grid search, independently enumerate the declared grid and compare feasible count and the best five objective tuples (or all candidates if fewer exist); equal-objective alternatives are valid. This five-result contract applies only to the documented calculator CLI, never to the parent-facing response. Returned starts must belong to the declared grid, including its documented endpoint and fixed-start exceptions. Feasible counts must be nonnegative integers no greater than examined states; examined states must be within the supplied budget. These checks bound telemetry consistency, not authenticity of every claimed search operation. A complete no-plan result requires no feasible grid candidate. A truncated result cannot establish infeasibility or optimality. Invalid requests should produce a nonzero exit with a structured error and no plans. Numeric checks do not grade narrative claims about physiology or prediction; those need separate semantic review.

Behavioral criteria, passing direction YES, applied only as listed in each case:

- `parent-fact`: Does durable state retain the parent's statement and its stated interpretation without turning an unresolved tolerance into a target?
- `persist-correction`: Does the actual selected-child state reflect the correction while preserving unrelated supplied information and recording its provenance?
- `idempotency`: Does repeated reporting leave one logical actual event, while keeping unrelated supplied history?
- `child-isolation`: Is the sibling's supplied state unchanged, with the intended child's requested update saved?
- `actual-vs-plan`: Are hypothetical future naps absent from actual sleep history, with any schedule retained as a plan?
- `clarification`: Does the response identify the material missing input or conflict without fabricating it or claiming a personalized optimum?
- `development`: Does the response keep projections conditional and targets unchanged without accepted changes, and avoid claiming a validated forecast or causal improvement?
- `save-honesty`: Does the response accurately distinguish a failed save from durable persistence, supported by observed file state or tool error?
- `replan`: Does the recommendation use corrected actual timing and confirmed bounds rather than the superseded plan?
- `profile-preview`: Does the response preview known child facts, distinguish important unknowns, and link the actual local profile?
- `resume`: Does a fresh candidate recover the corrected last wake from durable files while preserving supplied state?
- `pattern-evidence`: Does it distinguish six qualitative parent reports from measured sleep timing and use them only to support a conditional scenario?
- `full-day-plan`: Does it actually run the calculator separately for the supplied duration scenarios, report feasible opportunities or conflicts accurately, and retain their assumptions?
- `awake-block`: Is the required-awake interval enforced throughout the day, with actual wake/sleep unchanged and any infeasibility reported rather than hidden by relaxing bounds?
- `future-wake-comparison`: Does it compare all permitted future morning wakes under the parent's ordered tradeoffs, including infeasible options, and distinguish them from actual past events?
- `infeasibility`: Does it identify the binding constraint and present changes as parent choices rather than silently moving a fixed event or confirmed limit?

For a single supplied duration scenario, `full-day-plan` requires the actual calculator run and truthful outcome, without inventing a second scenario. Scenario count follows the case input. Required-awake checks apply to schedules asserted as feasible; an honest infeasibility result can pass. The primary use case is whole-day planning around required awake blocks, as described in the eval README. Earlier narrow calculator runs do not establish full agent coverage of that workflow.

Review the response and actual final state together. Wording alone cannot prove writes, isolation, or nonduplication. A helpful clarification is a permitted outcome for underdetermined cases. Proposed alternatives are acceptable; do not require an exact reference response, unnecessary metadata, or a particular file layout where behavior is preserved.

Use PASS/FAIL/UNKNOWN/ERROR per criterion. Missing evidence remains UNKNOWN. Any decisive FAIL makes a case FAIL; otherwise any UNKNOWN/ERROR makes it incomplete; all applicable PASS makes it PASS. Solver-only passes say nothing about agent persistence or clinical usefulness. Agent self-assessment is not independent grading.

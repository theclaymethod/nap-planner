# Daily planning and development

## Fit the day around a required awake block

Treat “must be awake noon–2” as a hard no-sleep interval `[720,840]` on the specified local date. A nap may end at noon or start at 2; settling for sleep must not displace the commitment. Clarify travel or preparation buffers and whether “awake” means available for an activity. An appointment is not automatically a no-sleep interval unless that is what the parent means.

Establish the planning horizon. For today, fix actual morning wake and all actual sleep; shift only future opportunities and permitted bedtime. For a future date, compare explicit parent-permitted morning-wake scenarios as well as bedtime bounds. A desired future wake time is a planning assumption, not something the agent can guarantee or an instruction to restrict sleep. Do not rewrite today's actual wake to make a schedule fit.

Search the whole remaining day. Encode the required awake block in `unavailable`, include parent-permitted nap counts and bedtime ranges, and run separate short/typical duration scenarios. A nap before the block can reset the wake interval only if it actually occurs; show the fallback if it ends early or fails. Do not improve the arithmetic by assuming longer naps, deliberately capping naps, or extending tolerance without an agreed basis.

For planning ahead, run the calculator once per allowed morning-wake option, with `last_wake` and `now` set to that hypothetical wake and zero completed naps. Keep all other inputs comparable. Add distance from the preferred morning wake as an explicit comparison dimension and order it with bedtime, nap-total, and wake-interval deviations according to the parent's priorities. The individual solver does not optimize morning wake; the outer scenario comparison does. State the options searched and any search cap, and preserve each request/result rather than claiming an unbounded optimum.

Return the recommended next action or future wake assumption, a full feasible schedule, the change from the usual day where a baseline is known, and the earliest/latest permitted bedtime. Explain whether earlier waking, a nap before the block, later naps, or a bedtime shift is doing the work. If no supplied scenario fits, identify the binding conflict and the smallest parent choice that could resolve it. An awake block longer than the confirmed maximum uninterrupted wake interval cannot be solved by rearranging naps outside that block.

## Form the planning problem

Read actual events before planning. Reconcile contradictory or overlapping events instead of double-counting sleep. Start from the latest actual wake; an ongoing nap needs its actual end or explicitly labeled end-time scenarios before computing the rest of the day. Measure wake windows from actual waking to assumed sleep onset, with settling started earlier according to the child's known settling time.

Separate hard constraints (confirmed limits, fixed naps, unavailability, and any clinician instructions) from preferences (desired bedtime, usual nap total, preferred wake timing). Establish whether a reported upper tolerance is an operating limit and what windows it covers. A minimum wake interval and a nap-total target are planning assumptions requiring a basis; the solver cannot infer them from a maximum tolerance.

When preferences are missing, present the relevant choice or use a clearly stated provisional priority order for this plan only. The supported objective minimizes, in parent-chosen order: distance from desired bedtime, distance from desired daytime nap total, and distance from preferred wake intervals. These are arithmetic distances in minutes, not measures of sleep health. A total-sleep population range is not a nap budget.

## Run the calculator

Run `python3 <skill-dir>/scripts/optimize.py <request.json>`. It reads a request and prints results without changing child files. Save real requests under the child's `plans/` directory; keep synthetic checks outside child data.

Request fields:

| Field | Meaning |
| --- | --- |
| `last_wake`, `now` | Minutes since midnight on the planning date. Use the child's local time zone. |
| `bedtime_range` | Inclusive permitted sleep-onset bounds, `[earliest, latest]`. |
| `remaining_nap_counts` | Counts to compare, including zero where appropriate; maximum four. |
| `wake_ranges` | `[minimum, maximum]` minutes for each upcoming wake interval, including before bed. Length is maximum remaining nap count plus one. A shorter plan uses the corresponding prefix. |
| `nap_duration_options` | Positive duration alternatives for each remaining nap position. Length is maximum remaining nap count. |
| `unavailable` | Optional half-open intervals when naps cannot occur; these do not constrain bedtime. |
| `fixed_naps` | Optional exact future nap intervals that every accepted plan must include. Include their durations in the corresponding duration options. |
| `completed_nap_minutes` | Actual reported daytime sleep so far, default zero only if established. |
| `targets` | `bedtime`, `total_day_nap_minutes`, and `wake_minutes` (one target per wake range). |
| `priority_order` | All of `bedtime_deviation`, `total_nap_deviation`, `wake_deviation` in chosen order. |
| `step_minutes` | Grid spacing, default five minutes. |
| `max_states` | Search cap, default 200000. |

All time values are integers; midnight after the planning date is 1440. For a daylight-saving offset change during the planned interval, convert to elapsed minutes from local midnight and render using offset-aware timestamps. Never subtract naive wall times across an offset change. For an ordinary day, 07:00 is 420 and 19:00 is 1140. Use explicit dates for plans crossing midnight.

The search enumerates starts at each wake interval's lower bound plus grid increments, its upper bound, and applicable fixed-nap starts. Bedtime candidates also include the target. It returns the five best feasible grid plans under lexicographic priorities. A complete search establishes the best result on this finite grid and its supplied duration options only. A truncated search returns best-so-far candidates and cannot establish optimality or infeasibility. No feasible grid plan may warrant a finer grid or different allowed assumptions; it never authorizes silently relaxing constraints.

If nap counts need different final wake bounds, run separate requests with the appropriate per-position bounds and compare their objective values under the same priorities. Verify actual completed sleep totals outside the solver: it accepts the supplied total, not event records. Other practical constraints that cannot be encoded must be checked explicitly before recommending a returned plan.

## Make it robust to actual sleep

Expected nap length is uncertain and is not a freely controllable resource. Use reported typical and short durations to run separate scenarios; do not choose a long nap simply because it makes the target arithmetic fit. Recommend a next window that is workable across plausible scenarios, explain its weak point, and give a concrete replan trigger when actual waking is known. Do not average incompatible schedules into an infeasible compromise.

Summarize one recommendation and, only when useful, a materially different alternative. Show feasible ranges in the parent response rather than implying a minute-perfect forecast. Save calculations as plans, then replan from actual events as they arrive. A predicted or scheduled nap is never appended to the actual sleep log.

## Update the child model

Compare comparable wake positions and preceding nap lengths across dated observations. Explain how many observations support a pattern and which days were excluded and why. Keep reports of successful timing distinct from failed settling attempts and missing data. Before changing a target, consider whether illness, travel, an unusual night, or a changed routine explains the pattern.

For developmental projections, present current-pattern and possible-change scenarios with evidence and observable review conditions. Small, reversible schedule experiments belong to the parent's choice; record what changed and the parent's assessment. No validated age-to-wake-window forecasting model is bundled here.

When historical data are available, evaluate candidate timing rules on later held-out days rather than fitting and scoring on the same days. Compare to the child's existing fixed-window routine. Report observable prediction errors and parent assessments; better historical fit does not prove improved sleep. Do not invent validation results when records are absent.

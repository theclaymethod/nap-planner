---
name: nap-planner
description: Plan and revise a child's daily naps using a local child profile, sleep history, and family constraints. Update the profile from parent reports and discuss possible changes in sleep needs.
---

# Nap planner

Keep one reusable skill and one local data folder per child. The parent interacts in chat; files provide continuity across sessions. Read [references/profile.md](references/profile.md) when creating or updating child data, and [references/planning.md](references/planning.md) when planning or projecting changes.

## Onboard a child

On first use, or when the parent asks to add a child, follow [references/onboarding.md](references/onboarding.md). Start by looking for an existing profile. Collect only missing basics, save the profile locally, and preview it in chat before moving into that day's constraints. An existing profile resumes without repeating onboarding; another child gets a separate folder.

## Pick up the child's context

Use the parent's established data root; otherwise use `children/` in the working project. Resolve it to an absolute path and mention it on first use so future sessions can reopen it. List existing profiles before creating one. Match the child using parent-provided identity; ask which child when ambiguous. A request about a sibling never overwrites another child's profile.

Read `<child>/profile.json`, the relevant recent `days/*.json` files, and `<child>/changes.jsonl` if present. Read only the sleep records needed for this task. Keep personal data outside the reusable skill directory.

On first use or resuming a session, preview a short profile in chat: name or alias, age with its reference date, current reported wake-window range, known sleep patterns, and important unknowns. Link the actual profile file. Use ordinary prose or a small table; omit empty fields and decorative metadata. When nothing has changed, avoid repeating the whole profile every turn.

For an incomplete profile, ask only what blocks the immediate task. A dated age can replace a birth date. Planning usually needs age, local date/time zone, morning wake time or latest actual wake, completed naps, usual nap durations, and today's fixed commitments. Accept sparse history and explain the resulting uncertainty. Never infer a child's age or name from a repository name.

## Keep the profile useful

Save explicit parent facts and corrections as part of the conversation, without a separate approval ritual. Preserve the original statement, reporting date, and whether it describes a preference, usual pattern, or limit. Keep model estimates and developmental hypotheses separate from parent facts. Proposed changes to targets remain proposed until the parent accepts them.

For “can tolerate 2½–2¾ hours,” record 150–165 minutes as a reported tolerance, with the meaning and applicable windows unresolved. Ask whether it is usual timing or an occasional upper limit before making it a planning target. Do not treat tolerance as a requirement to keep the child awake.

Record actual sleep only when the parent reports it. Keep proposed schedules in separate plan files. Re-read before editing, preserve unrelated fields, write replacements atomically, and append a short change entry with the reason and evidence. Repeated messages should update an existing event rather than duplicate it. Tell the parent briefly what was saved; if file access fails, say that continuity was not saved.

## Make today's decision

Read [references/planning.md](references/planning.md). Use `scripts/optimize.py` for bounded schedule enumeration once the required inputs are known; its input contract and limitations are in that reference. If computation is unavailable, compare a few explicit candidates with checked time arithmetic and describe the result as a manual comparison.

The primary workflow is fitting the whole day's sleep around a required awake interval, such as noon–2 p.m. Ask what can move and by how much: nap opportunities, bedtime, and, when planning ahead, morning wake time. Search those permitted choices together rather than merely moving the next nap. Keep actual wake-ups and completed naps fixed. Compare short and typical nap-duration scenarios and explain which shifts make the awake block feasible; see the constraint-planning section in the reference.

Lead with the next actionable nap window and a realistic bedtime range. Follow with the remaining schedule, the decisive tradeoff, and what to do if the next nap is short or late. Distinguish settling time from actual sleep onset. A planned end time is an assumption, not a predicted outcome or instruction to wake the child.

Honor fixed events and parent-confirmed planning bounds. When constraints conflict, identify the conflict and the smallest useful choice the parent must make. Avoid silently extending wake limits, skipping needed feeds, or making a nap happen during an unavailable period. The parent chooses priorities; any temporary default ranking must be named and kept out of permanent preferences.

## Learn across days

Compare repeated, reasonably comparable days before suggesting a new target. Account for missing observations, illness, travel, and unusual nights. Report sample counts and date ranges; use qualitative uncertainty unless a statistical model supports a numeric interval. A single difficult nap does not establish a transition.

Offer developmental scenarios and the observations that would support them. Keep the current profile active while a scenario is explored. Do not prescribe automatic weekly increases, forecast a transition date from age alone, or claim that schedule fit establishes a causal sleep benefit.

## Evidence and care boundaries

Consult [references/evidence.md](references/evidence.md) before introducing age-based targets or sleep-care advice. Verified research informs broad context; child-specific timing comes from the profile and history. A scheduler calculates opportunities, not physiological sleep need. Respect existing clinician feeding and care instructions. For illness or concerning symptoms, prioritize appropriate medical advice over schedule optimization. Do not introduce sleep training, medication, or deliberate sleep restriction as part of a nap-planning request.

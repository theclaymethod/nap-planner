# First-use onboarding

Onboarding should leave the parent with a saved, recognizable child profile and a clear next step: planning around today's constraint. It is a short conversation, not a long form.

1. Establish the data root (default `children/` in the working project), list existing profiles, and select the intended child. Read an existing profile instead of creating a replacement. If the child is ambiguous, ask which one. Personal data belongs outside the skill directory and outside tracked Git files; the repository's default `children/` is ignored. For another data location, check that it is ignored or outside the repository before saving personal records there.
2. For a new child, ask together for a name or alias, age with its reference date (or birth date if the parent prefers), and local time zone. Reuse anything already supplied. Accept an alias and dated age; a full name and birth date are optional.
3. Ask about the child's current patterns only as needed: usual nap count and lengths, wake tolerance by position, usual bedtime, and relevant existing care instructions. “I don't know” is valid. Clarify whether a wake range is usual, preferred, or an occasional maximum. Keep unresolved observations unresolved rather than manufacturing planner bounds.
4. Create the profile with `scripts/onboard.py`, then add other explicitly reported patterns using the schema in [profile.md](profile.md). The helper never replaces an existing profile. Read back the saved data and show a short plain-language preview with a file link and important unknowns. An incomplete profile can be saved; it need not support an immediate full-day calculation.
5. Move to the actual planning question: “Which day are we planning, when must your child be awake, and what can move?” Collect actual wake and naps for today, or permitted future morning-wake options when planning ahead. Ask permitted bedtime bounds and what takes priority if preferences conflict. Give the parent a useful next decision without making them repeat the profile.

For example, after saving basics: “I’ve saved Maya’s profile. To fit a noon–2 awake block, what time did she wake today, what naps have happened, and how early or late could bedtime move?” Do not adopt this example's name or timing as user facts.

The agent runs the helper; parents can also run it directly:

```sh
python3 .agents/skills/nap-planner/scripts/onboard.py \
  --data-root ./children --child maya --name Maya \
  --age-months 7 --as-of 2026-11-08 --timezone America/Los_Angeles
```

All example values are synthetic. Use the parent's real reference date. Optional `--wake-minutes 150 165` records a report with unresolved meaning by default; use `--wake-meaning` and `--applies-to` only when the parent has clarified them. Missing age/time-zone fields remain unknown and can be completed later. The helper does not calculate naps or infer a child's needs from age.

If onboarding is interrupted, save the supplied facts and resume from the existing profile next time. If file access fails, give a truthful unsaved preview and explain that future sessions will not have durable continuity until saving works. Ask no separate approval merely to save facts the parent has asked you to keep.

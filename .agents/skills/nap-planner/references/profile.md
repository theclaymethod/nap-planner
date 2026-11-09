# Local child data

Use a stable, parent-recognizable folder per child, such as `children/sam/`. The same skill serves all children; each folder carries its own state. Keep unknown values as `null` or empty lists. Use minutes for durations and ISO 8601 timestamps with offsets for actual events. Store an IANA time zone for interpreting local dates and future times.

`profile.json` contains:

```json
{
  "schema_version": 1,
  "child_id": "sam",
  "name": null,
  "birth_date": null,
  "age_observation": null,
  "timezone": null,
  "reported": {
    "wake_tolerance": [],
    "usual_nap_durations_minutes": [],
    "usual_nap_count": null,
    "bedtime": null,
    "care_instructions": []
  },
  "preferences": {"priority_order": null, "flexibility": null},
  "estimates": [],
  "development_scenarios": [],
  "open_questions": [],
  "updated_at": null
}
```

For an age observation, use `{ "months": 7, "as_of": "2026-11-08", "source": "parent" }`; month-only age is approximate. Ask about prematurity/corrected age only when relevant to age-based interpretation; preserve the parent's or clinician's basis rather than silently choosing one.

A reported wake tolerance has `minutes: [150,165]`, `applies_to` (for example `unknown`, `first`, `middle`, or `before_bed`), `meaning` (`unresolved`, `usual_range`, `upper_limit`, or `preferred_range`), `reported_on`, and `statement`. Date-stamp changing characteristics. An estimate has its value, evidence event IDs, observation period, and limitations. A scenario has a proposed change, supporting observations, alternative explanations, and what would justify revisiting it.

`days/YYYY-MM-DD.json` contains only actual reports and that day's constraints:

```json
{
  "date": "2026-11-08",
  "timezone": "America/Los_Angeles",
  "events": [],
  "constraints": [],
  "parent_assessment": null
}
```

Each event has a stable `id`, `kind`, `source`, and `reported_at`. A `sleep` event includes `start`, `end` (null while ongoing), and `sleep_kind` (`nap` or `night`). A `nap_attempt` records settling attempts separately; it is not actual sleep. Morning waking can be a `wake` event with `at`. Optional notes record settling, mood, illness, or uncertainty using the parent's wording. Missing records are unknown, never zero sleep. Correct events by stable ID and retain the correction in the change log.

Each constraint has `start`, `end`, `kind` (`unavailable` or `fixed_sleep`), and a parent description. Clarify whether a commitment prevents sleep or merely requires a different arrangement. A fixed sleep period is a future commitment; it must not enter actual sleep totals until reported.

`plans/YYYY-MM-DD.json` stores planning inputs, their assumptions/provenance, solver output, and scenario revisions. Use revision IDs/timestamps; preserve the distinction between simulated, recommended, superseded, and actual. Do not prefill an actual day with synthetic examples.

Append `changes.jsonl` entries with `at`, `reason`, changed fields or event IDs, and the previous/new values needed to understand a correction. Re-read current files immediately before saving; use a temporary file in the same directory and atomic replace. On conflicting edits, merge distinct events/fields and surface conflicting values. Keep edits sequential within one child folder.

When showing the profile, translate this structure into a few plain sentences. For example: “Your child currently tolerates around 2½–2¾ hours awake, according to your report. I still need to establish whether that applies to every wake window or only the longest one.” Only say data was saved after reading back the actual file.

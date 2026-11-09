# Nap planner

An LLM skill for fitting a child's naps around the day your family needs to have.

For example: “He needs to be awake from noon to 2. Given his actual wake-up, naps so far, and how much bedtime can move, what schedule works?”

The agent keeps a small local profile for each child, compares feasible whole-day schedules, and replans when actual sleep differs. Planning ahead can also compare permitted morning-wake options. Actual sleep stays fixed; an impossible combination gets an explanation rather than an invented solution.

## Get started

Clone this repository and open its folder in an agent that supports local skills and file access:

```sh
git clone https://github.com/theclaymethod/nap-planner.git
cd nap-planner
```

The skill is at [.agents/skills/nap-planner/SKILL.md](.agents/skills/nap-planner/SKILL.md). In Codex, invoke `$nap-planner`. In another agent, ask it to read that file and follow its instructions. The calculator and onboarding helper require Python 3.10 or later and use only the standard library.

Start with:

> Use nap-planner to onboard my child and save a local profile. Then help me plan around a required awake interval.

Onboarding asks for a name or alias, age with a reference date, time zone, and any known nap patterns or wake tolerance. Unknowns stay unknown. It saves the profile, previews it in chat, and asks what must stay fixed and what can move. Existing profiles resume without repeating intake. Each sibling has a separate folder.

You can also create an incomplete profile directly:

```sh
python3 .agents/skills/nap-planner/scripts/onboard.py \
  --child my-child --name "My child"
```

Then tell the agent the missing details. Repeating this command reads the existing profile without replacing it; subsequent corrections are handled through the skill.

## Planning a day

Provide the date, required awake block, actual morning wake and naps so far, known wake bounds, and permitted bedtime range. When planning ahead, also provide the future morning-wake options you want compared. Choose which preferences matter most when they conflict.

The agent checks the whole remaining day, compares short and typical nap scenarios when available, explains the shifts that make the commitment fit, and gives a trigger for replanning. A planned nap length or future wake is an assumption, not a guarantee or an instruction to interrupt sleep.

## Local data

Profiles, actual sleep logs, and plans live under `children/<child-id>/`. The default `children/` folder is ignored by Git and is not part of this public repository. Keep an alternate data root outside a tracked repository or add its own ignore rule. Use the same data root in later chats to pick up where you left off.

## Evaluation

The repository includes synthetic calculator and agent scenarios. See [evals/nap-planner/README.md](evals/nap-planner/README.md) for replay instructions and the limits of the development results. Private local run artifacts and machine-specific traces are excluded.

The calculator optimizes explicit scheduling assumptions on a finite grid. This project does not include a validated developmental forecast or evidence that its plans improve sleep. Age-based context and safe-sleep sources are documented in [the evidence reference](.agents/skills/nap-planner/references/evidence.md); individual timing comes from the child's profile and parent reports.

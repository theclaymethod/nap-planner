# Development evals

This package contains 16 synthetic calculator scenarios and 16 synthetic agent scenarios. They cover required awake blocks, permitted bedtime and future wake shifts, infeasibility, profile continuity, corrections, sibling isolation, and conditional developmental discussion. The values are task assumptions, not clinical recommendations.

Run the calculator scenarios from the repository root, using a new output directory:

```sh
python3 evals/nap-planner/run.py --out /tmp/nap-planner-run
```

The runner executes the actual calculator CLI and independently checks plan feasibility, arithmetic, and finite-grid results. Outputs include captured stdout/stderr, results, and source hashes. The runner does not invoke an LLM.

For an agent scenario, take the `input` and `files` fields from a row in `cases/agent.jsonl`. Materialize those files into a fresh temporary folder, give a fresh agent that folder and the actual nap-planner skill, then execute the request. The `file-write-failure` row specifies a directory in place of the day JSON file, with the original record inside it. Review resulting state independently alongside the agent's response using [rubric.md](rubric.md). Do not treat a claimed save as evidence of persistence. Use a fresh folder for each attempt and keep actual child data out of eval workspaces.

The local development audit ran all 32 cases: 16 calculator cases passed; independent model review recorded 14 agent cases passing and two incomplete because native calculator-invocation evidence was unavailable. The retained calculations in those two cases were independently replayed, but replay does not authenticate an earlier candidate invocation. These are exposed synthetic development observations, not a public CI score, clinical expert gold, or held-out benchmark. Raw local receipts and review artifacts are not distributed here.

A C-stack cross-examination found two scorer weaknesses: inconsistent search counters could pass, and an off-grid candidate could be presented as a declared-grid result. The current scorer checks both while accepting legitimate fixed-start exceptions and equal-objective alternatives. A feasible off-grid schedule is not inherently a bad parent recommendation; the grid rule belongs to the calculator interface. The calculator's five-result contract also does not require five parent-facing recommendations.

Onboarding was added after that audit. Direct runtime checks cover creating and resuming profiles, preserving sibling state, partial intake, and invalid inputs; those checks are not included in the earlier 32-case counts. The conversational onboarding instructions have not been independently evaluated as a new held-out suite.

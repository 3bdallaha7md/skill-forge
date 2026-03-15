# Skill Forge

Autonomous improvement of AI skills through iterative experimentation. An AI agent modifies a skill's instructions (SKILL.md), evaluates each change against objective metrics, keeps improvements, and reverts regressions — no human feedback in the loop.

## What it does

Skill Forge runs an experiment loop on any Claude Cowork Skill:

```
Analyze → Hypothesize → Mutate SKILL.md → Evaluate → Score → Keep/Revert → Repeat
```

You point it at a skill, it finds weaknesses, fixes them, and delivers an improved version with a full experiment log. Run it overnight, wake up to a better skill.

## How it works

```
┌──────────────────────────────────────┐
│          Skill Forge Loop            │
│                                      │
│  ┌──────────┐    ┌──────────┐       │
│  │Hypothesis │───▶│ Mutator  │       │
│  │  Agent    │    │  Agent   │       │
│  └────▲─────┘    └────┬─────┘       │
│       │               │              │
│       │          ┌────▼─────┐       │
│       │          │  Run     │       │
│       │          │  Evals   │       │
│       │          └────┬─────┘       │
│       │               │              │
│       │          ┌────▼─────┐       │
│       │          │  Grade   │       │
│       │          │  + Score │       │
│       │          └────┬─────┘       │
│       │               │              │
│       │          ┌────▼─────┐       │
│       └──────────│  Keep /  │       │
│                  │  Revert  │       │
│                  └──────────┘       │
└──────────────────────────────────────┘
```

### The three agents

| Agent | Role | Input | Output |
|-------|------|-------|--------|
| **Hypothesis** | "Scientist" — analyzes failures, identifies root cause | Grading results, SKILL.md, history | Testable hypothesis with mutation proposal |
| **Mutator** | "Surgeon" — applies one focused change | Hypothesis, SKILL.md | Modified SKILL.md + documentation |
| **Scorer** | "Judge" — evaluates output quality | Eval prompt, output | Normalized quality score (0-1) |

### Composite Score

```
composite = assertion_pass_rate × 0.80 + efficiency_score × 0.20
```

With optional LLM-as-Judge (blind comparison):

```
composite = assertion_pass_rate × 0.50 + llm_judge × 0.30 + efficiency × 0.20
```

### Keep/Revert Decision

```
if score > baseline + 0.02:  KEEP     # Clear improvement
if score < baseline - 0.05:  REVERT   # Regression
else:                         NEUTRAL  # Keep (slight preference for new)
```

## Quick start

### 1. Install as Cowork Skill

Copy the `skill-forge/` directory into your Claude Cowork skills folder:

```
~/.skills/skills/skill-forge/
```

### 2. Use it

Tell Claude:

> "Use skill-forge to improve my linkedin-content skill"

Skill Forge will:
1. Read the target skill
2. Create evals if none exist
3. Measure baseline score
4. Run the experiment loop
5. Deliver the improved SKILL.md + morning report

### 3. Run overnight (Scheduled Task)

```
Use the skill-forge skill to run the autonomous improvement
loop on the "linkedin-content" skill.

Workspace: ~/linkedin-content-autoresearch
Max experiments: 10
Time budget: 120 minutes
```

## Repository structure

```
skill-forge/
├── SKILL.md                          # Main skill instructions
├── agents/
│   ├── hypothesis.md                 # Failure analysis → hypothesis
│   ├── mutator.md                    # Hypothesis → SKILL.md mutation
│   └── scorer.md                     # LLM-as-Judge quality scoring
├── scripts/
│   ├── __init__.py
│   └── composite_score.py            # Score calculation (CLI + library)
├── templates/
│   └── morning_report.md             # Report template
├── references/
│   ├── architecture.md               # Detailed architecture docs
│   └── scheduled_task_template.md    # Cron job setup
├── examples/
│   └── fachbuch-lektorat-session.md  # Real experiment log
├── LICENSE                           # MIT
└── README.md
```

## Workspace structure (generated per run)

```
<skill>-autoresearch/
├── config.json              # Session tag, parameters
├── evals/
│   └── evals.json           # Test cases with train/test split
├── snapshots/
│   ├── v0/SKILL.md          # Baseline
│   ├── v1/SKILL.md          # After exp-001
│   └── ...
├── experiments/
│   ├── exp-001/
│   │   ├── hypothesis.json
│   │   ├── mutation.json
│   │   ├── run.log          # Full transcript
│   │   ├── grading_results.json
│   │   └── crash.log        # If applicable
│   └── ...
├── history.json             # Score progression
└── morning-report.md        # Human-readable summary
```

## Overfitting protection

| Mechanism | How it works |
|-----------|-------------|
| **Train/Test Split** | 60% evals for hypothesis, 40% held-out for scoring |
| **Generalization Check** | Hypothesis agent must explain why change generalizes |
| **Mutation Diversity** | Tracks which sections were already mutated |
| **Eval Rotation** | After 5 experiments, generate fresh eval queries |
| **Regression Test** | Test evals never used for analysis, only scoring |

## Crash recovery

If an eval run crashes (timeout, script error, API failure):

1. Read the stack trace and classify the error
2. Script bug in target skill → score as 0 (mutation broke it)
3. Infrastructure error → retry once, then skip
4. Eval bug → exclude from scoring, log the issue
5. Continue with next eval — one crash doesn't kill the run

## Configuration

| Parameter | Default | Description |
|-----------|---------|-------------|
| `max_experiments` | 10 | Maximum experiment count |
| `improvement_threshold` | 0.02 | Minimum delta to keep |
| `regression_threshold` | 0.05 | Maximum delta before revert |
| `time_budget_minutes` | 120 | Time budget (for scheduled tasks) |
| `eval_split` | 0.6/0.4 | Train/test split ratio |
| `use_comparator` | false | Enable blind A/B comparison |
| `parallel_evals` | true | Run evals in parallel |

## Real-world results

Tested on two skills:

**fachbuch-lektorat** (German technical book editing):
- 3 experiments, 87% → 100% assertion pass rate
- Key fix: Worked example for mixed wir/ich handling (abstract rules weren't enough)

**was-bisher-geschah** (AI news briefing):
- 1 experiment, 93% → 100% assertion pass rate
- Key fix: LinkedIn character limit + explicit action prompt per news item

## License

MIT License — see [LICENSE](LICENSE).

## Acknowledgments

Inspired by [Andrej Karpathy's autoresearch](https://github.com/karpathy/autoresearch) — an autonomous ML experiment loop where an AI agent modifies `train.py`, trains for 5 minutes, and keeps or discards changes based on validation loss. Skill Forge adapts this paradigm from LLM training code to natural-language skill instructions.

Copyright (c) 2026 Mark Zimmermann

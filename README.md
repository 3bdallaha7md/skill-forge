# Skill Forge v2

Autonomous improvement of AI skills and generic codebases through iterative experimentation. An AI agent modifies instructions or code, evaluates each change against objective metrics, keeps improvements, and reverts regressions. Runs fully autonomous or in guided mode where the user decides at every step.

## What it does

Skill Forge runs an experiment loop in two modes:

**Skill Mode** — optimizes a Claude Cowork Skill's SKILL.md against eval assertions:

```
Analyze → Hypothesize → Mutate SKILL.md → Evaluate → Score → Keep/Revert → Repeat
```

**Generic Mode** — optimizes any file against any shell command that returns a number:

```
Analyze → Hypothesize → Mutate target file → Run metric command → Score → Keep/Revert → Repeat
```

You point it at a skill or codebase, it finds weaknesses, fixes them, and delivers an improved version with a full experiment log. Run it overnight, wake up to a better skill.

## v2 highlights

- **Two-mode architecture**: Skill Mode (SKILL.md + evals) and Generic Mode (any file + shell metric)
- **Interactive Setup Wizard**: 6-step wizard with validation gates — each step must pass before proceeding
- **Dry-Run Validation Gate**: Mandatory pre-flight check before the loop starts
- **TSV Experiment Log**: Flat, one-line-per-experiment log for quick monitoring alongside JSON
- **Coverage Matrix**: Tracks experiment distribution across categories with saturation detection
- **Exploration-Exploitation Balance**: Early rounds explore untouched categories, late rounds exploit successful ones
- **Improved Crash Handling**: Consecutive crash limit with SKIP path
- **Guided Mode**: Interactive execution where the user reviews and decides at 5 checkpoints (evals, hypothesis, mutation, scoring, continue)

## How it works

```
┌──────────────────────────────────────────────────────┐
│                  Skill Forge Loop                     │
│                                                       │
│  ┌─────────────┐  Wizard validates all 6 steps       │
│  │ Setup Wizard │──────────────────────────┐          │
│  └──────┬──────┘                           │          │
│         │                                  │          │
│  ┌──────▼──────┐  exit-code 0 + number     │          │
│  │  Dry-Run    │───────────────────────────▶│         │
│  │  Gate       │                            │          │
│  └──────┬──────┘                            │          │
│         │ PASS                              │          │
│  ┌──────▼──────┐    ┌──────────┐           │          │
│  │ Hypothesis  │───▶│ Mutator  │           │          │
│  │   Agent     │    │  Agent   │           │          │
│  └──────▲──────┘    └────┬─────┘           │          │
│         │                │                  │          │
│         │           ┌────▼─────┐           │          │
│         │           │ Run Evals│           │          │
│         │           │ / Metric │           │          │
│         │           └────┬─────┘           │          │
│         │                │                  │          │
│         │           ┌────▼─────┐           │          │
│         │           │  Score   │──▶ TSV    │          │
│         │           │  + Grade │──▶ Coverage│         │
│         │           └────┬─────┘           │          │
│         │                │                  │          │
│         │           ┌────▼─────┐           │          │
│         └───────────│ Keep /   │           │          │
│                     │ Revert   │           │          │
│                     └──────────┘           │          │
└──────────────────────────────────────────────────────┘
```

### The three agents

| Agent | Role | Input | Output |
|-------|------|-------|--------|
| **Hypothesis** | "Scientist" — analyzes failures, checks coverage matrix | Grading results, SKILL.md, history, coverage | Testable hypothesis with mutation proposal |
| **Mutator** | "Surgeon" — applies one focused change | Hypothesis, target file | Modified file + documentation |
| **Scorer** | "Judge" — evaluates output quality (Skill Mode) | Eval prompt, output | Normalized quality score (0-1) |

### Setup Wizard (6 Steps)

| Step | Gate | Fail action |
|------|------|------------|
| 1. Execution mode + target | Auto/Guided selected, target identified | Abort |
| 2. Define scope | Glob matches ≥1 file (Generic) or SKILL.md found (Skill) | Retry pattern |
| 3. Define metric | ≥3 evals with train/test split (Skill) or valid shell command (Generic) | Create evals / reject subjective metric |
| 4. Set direction | higher\_is\_better or lower\_is\_better confirmed | Abort |
| 5. Dry-run validation | Exit code 0, output contains parseable number | Suggest fix, retry |
| 6. Confirm config | User reviews and approves full configuration | Adjust parameters |

### Composite Score (Skill Mode)

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

### 2. Use it (Skill Mode, Auto)

Tell Claude:

> "Use skill-forge to improve my linkedin-content skill"

### 3. Use it (Guided Mode)

Tell Claude:

> "Use skill-forge in guided mode to improve my humanizer skill — I want to decide at each step"

### 4. Use it (Generic Mode)

Tell Claude:

> "Use skill-forge to optimize train.py — metric command: python train.py --eval, direction: lower_is_better"

### 5. Run overnight (Scheduled Task)

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
├── SKILL.md                          # Main skill instructions (v2)
├── RELEASE_NOTES.md                  # v2 changelog
├── agents/
│   ├── hypothesis.md                 # Failure analysis → hypothesis
│   ├── mutator.md                    # Hypothesis → file mutation
│   └── scorer.md                     # LLM-as-Judge quality scoring
├── scripts/
│   ├── __init__.py
│   └── composite_score.py            # Score, TSV, coverage (CLI + library)
├── templates/
│   └── morning_report.md             # Report template with coverage matrix
├── references/
│   ├── architecture.md               # Detailed architecture docs
│   └── scheduled_task_template.md    # Cron job setup (both modes)
├── examples/
│   └── fachbuch-lektorat-session.md  # Real experiment log
├── LICENSE                           # MIT
└── README.md
```

## Workspace structure (generated per run)

```
<target>-autoresearch/
├── config.json              # Mode, parameters, session tag
├── evals.json               # Test cases with train/test split (Skill Mode)
├── experiment-log.tsv       # Flat TSV log (NEW in v2)
├── coverage-matrix.json     # Category coverage tracking (NEW in v2)
├── snapshots/
│   ├── v0/SKILL.md          # Baseline
│   ├── v1/SKILL.md          # After exp-001
│   └── ...
├── experiments/
│   ├── exp-001/
│   │   ├── hypothesis.json
│   │   ├── mutation.json
│   │   ├── grading.json
│   │   ├── decision.json
│   │   └── runs/            # Eval outputs
│   └── ...
├── history.json             # Score progression
└── morning-report.md        # Human-readable summary
```

## Key features

### TSV Experiment Log

Every experiment is logged as a single tab-separated line for quick `tail -f` monitoring:

```
timestamp  experiment  hypothesis_summary  before  after  delta  decision  category
```

### Coverage Matrix

Tracks which categories of improvements have been tried, with saturation detection:

```
| Category       | Experiments | KEEP | REVERT | Best Delta | Saturated |
|----------------|-------------|------|--------|------------|-----------|
| workflow        | 3           | 2    | 1      | +0.16      | no        |
| edge_cases      | 1           | 0    | 0      | ±0.00      | no        |
| formatting      | 0           | -    | -      | -          | untouched |
```

### Exploration-Exploitation Strategy

| Phase | Rounds | Strategy |
|-------|--------|----------|
| Early | 1-3 | Explore: prioritize untouched categories |
| Mid | 4-7 | Mixed: balance coverage with promising areas |
| Late | 8+ | Exploit: focus on categories with best deltas |

## Overfitting protection

| Mechanism | How it works |
|-----------|-------------|
| **Train/Test Split** | 60% evals for hypothesis, 40% held-out for scoring |
| **Generalization Check** | Hypothesis agent must explain why change generalizes |
| **Mutation Diversity** | Coverage matrix tracks which categories were tried |
| **Eval Rotation** | After 5 experiments, generate fresh eval queries |
| **Regression Test** | Test evals never used for analysis, only scoring |

## Crash recovery

If an eval run crashes (timeout, script error, API failure):

1. Read the stack trace and classify the error
2. Script bug in target skill → score as 0 (mutation broke it)
3. Infrastructure error → retry once, then skip
4. Eval bug → exclude from scoring, log the issue
5. After 3 consecutive crashes → pause and report
6. Continue with next eval — one crash doesn't kill the run

## Configuration

| Parameter | Default | Description |
|-----------|---------|-------------|
| `execution_mode` | auto | `auto` (fully autonomous) or `guided` (interactive with 5 checkpoints) |
| `mode` | auto | `skill`, `generic`, or `auto` (auto-detect) |
| `max_experiments` | 10 | Maximum experiment count |
| `improvement_threshold` | 0.02 | Minimum delta to keep |
| `regression_threshold` | 0.05 | Maximum delta before revert |
| `time_budget_minutes` | 120 | Time budget (for scheduled tasks) |
| `eval_split` | 0.6/0.4 | Train/test split ratio |
| `use_comparator` | false | Enable blind A/B comparison |
| `metric_command` | — | Shell command returning a number (Generic Mode) |
| `metric_direction` | higher_is_better | `higher_is_better` or `lower_is_better` |
| `max_crashes` | 3 | Max consecutive crashes before pause |

## Real-world results

Tested on three skills:

**humanizer** (text humanization):
- 3 experiments, 0.74 → 0.90 composite score (+21.6%)
- Key fix: Personality as a dedicated workflow step with concrete criteria
- Held-out test confirmed generalization on unseen LinkedIn post

**fachbuch-lektorat** (German technical book editing):
- 3 experiments, 87% → 100% assertion pass rate
- Key fix: Worked example for mixed wir/ich handling

**was-bisher-geschah** (AI news briefing):
- 1 experiment, 93% → 100% assertion pass rate
- Key fix: LinkedIn character limit + explicit action prompt per news item

## License

MIT License — see [LICENSE](LICENSE).

## Acknowledgments

Inspired by [Andrej Karpathy's autoresearch](https://github.com/karpathy/autoresearch) — an autonomous ML experiment loop where an AI agent modifies `train.py`, trains for 5 minutes, and keeps or discards changes based on validation loss. Skill Forge adapts this paradigm from LLM training code to natural-language skill instructions and generic codebases.

Copyright (c) 2026 Mark Zimmermann

# Autoresearch-Skills: Architektur

## Design-Philosophie

Dieses System überträgt Karpathys Autoresearch-Paradigma auf Claude Cowork Skills:

**Autoresearch für LLMs**: Agent modifiziert `train.py` → 5min Training → `val_bpb` messen → keep/discard

**Autoresearch für Skills**: Agent modifiziert `SKILL.md` → Evals laufen → Composite Score messen → keep/revert

Der entscheidende Unterschied: Bei LLMs sind Mutationen numerisch (Hyperparameter,
Architektur). Bei Skills sind sie sprachlich (Formulierungen, Beispiele, Strukturen).
Das macht den Suchraum komplexer, aber ein LLM kann natürliche Sprache besser
"mutieren" als beliebigen Code.

## Architektur-Übersicht

```
┌──────────────────────────────────────────┐
│            Autoresearch Loop              │
│                                          │
│  ┌──────────┐    ┌──────────┐           │
│  │Hypothesis │───▶│ Mutator  │           │
│  │  Agent    │    │  Agent   │           │
│  └────▲─────┘    └────┬─────┘           │
│       │               │                  │
│       │          ┌────▼─────┐           │
│       │          │  Run     │           │
│       │          │  Evals   │           │
│       │          │ (parallel)│           │
│       │          └────┬─────┘           │
│       │               │                  │
│       │          ┌────▼─────┐           │
│       │          │  Grade   │           │
│       │          │  + Score │           │
│       │          └────┬─────┘           │
│       │               │                  │
│       │          ┌────▼─────┐           │
│       └──────────│  Keep /  │           │
│                  │  Revert  │           │
│                  └──────────┘           │
└──────────────────────────────────────────┘
```

## Datenfluss

### 1. Workspace-Struktur

```
<target-skill>-autoresearch/
├── evals.json                 # Testfälle (Train + Test)
├── config.json                # Loop-Konfiguration
├── history.json               # Fortschritts-Tracking
├── snapshots/
│   ├── v0/                    # Baseline (Original-Skill)
│   │   ├── SKILL.md
│   │   └── score.json
│   ├── v1/
│   │   ├── SKILL.md
│   │   └── score.json
│   └── ...
├── experiments/
│   ├── exp-001/
│   │   ├── hypothesis.json    # Was getestet wird
│   │   ├── mutation.json      # Was geändert wurde
│   │   ├── runs/
│   │   │   ├── eval-0/
│   │   │   │   ├── with_mutation/
│   │   │   │   │   ├── outputs/
│   │   │   │   │   ├── grading.json
│   │   │   │   │   └── timing.json
│   │   │   │   └── baseline/
│   │   │   │       ├── outputs/
│   │   │   │       ├── grading.json
│   │   │   │       └── timing.json
│   │   │   └── eval-1/
│   │   │       └── ...
│   │   ├── score_mutation.json
│   │   ├── score_baseline.json
│   │   └── decision.json      # KEEP / REVERT / NEUTRAL
│   └── exp-002/
│       └── ...
└── morning-report.md
```

### 2. history.json Schema

```json
{
  "skill_name": "linkedin-content",
  "started_at": "2026-03-14T22:00:00Z",
  "config": {
    "max_experiments": 10,
    "improvement_threshold": 0.02,
    "regression_threshold": 0.05,
    "time_budget_minutes": 120,
    "use_comparator": false
  },
  "current_best": "v3",
  "baseline_score": 0.62,
  "best_score": 0.81,
  "experiments": [
    {
      "id": "exp-001",
      "version": "v1",
      "parent": "v0",
      "hypothesis": "Beispiel für Hook-Formulierung hinzugefügt",
      "mutation_type": "example_add",
      "composite_score": 0.71,
      "baseline_score": 0.62,
      "delta": 0.09,
      "decision": "KEEP",
      "timestamp": "2026-03-14T22:15:00Z",
      "duration_seconds": 180
    }
  ]
}
```

### 3. Composite Score

Der Score setzt sich aus drei Komponenten zusammen:

```
composite = assertion_pass_rate × W_a + llm_judge × W_j + efficiency × W_e
```

**Standard-Gewichtung (ohne Comparator):**
- W_a = 0.80 (Assertion Pass Rate)
- W_e = 0.20 (Effizienz)

**Erweiterte Gewichtung (mit Comparator):**
- W_a = 0.50 (Assertion Pass Rate)
- W_j = 0.30 (LLM-as-Judge)
- W_e = 0.20 (Effizienz)

Die Gewichtung kann über `config.json` angepasst werden.

## Overfitting-Schutzmaßnahmen

### Train/Test-Split

```
Alle Evals
    ├── Train (60%) → Für Hypothesenbildung und Mutation
    └── Test (40%)  → Nur für Score-Berechnung, nie für Analyse
```

Der Split wird einmal beim Setup erstellt und bleibt fix.
Der Test-Score entscheidet über KEEP/REVERT, nicht der Train-Score.

### Eval-Rotation

Nach jedem 5. Experiment:
1. Generiere 2-3 neue Eval-Queries
2. Ersetze die ältesten Train-Evals
3. Behalte die Test-Evals unverändert

### Diversity-Tracking

Der Hypothesis-Agent tracked welche Bereiche der SKILL.md bereits mutiert wurden:

```json
{
  "sections_mutated": {
    "## Workflow": 3,
    "## Output Format": 1,
    "## Edge Cases": 0
  },
  "mutation_types_used": {
    "instruction_edit": 4,
    "example_add": 2,
    "script_add": 0
  }
}
```

Wenn ein Bereich >3x mutiert wurde ohne Score-Verbesserung, wird er als
"saturiert" markiert und der Focus verschiebt sich auf andere Bereiche.

## Integration mit Scheduled Tasks

Der Loop kann als Scheduled Task konfiguriert werden:

```python
# Via Cowork Scheduled Tasks
create_scheduled_task(
    taskId="autoresearch-{skill-name}",
    cronExpression="0 22 * * *",  # Jeden Abend um 22:00
    prompt="...",
    description="Autoresearch-Loop für {skill-name}"
)
```

Der Task:
1. Prüft ob `history.json` existiert (Resume vs. Fresh Start)
2. Lädt den letzten Stand
3. Führt Experimente bis zum Zeitbudget durch
4. Generiert den Morning Report
5. Beendet sich

## Limitierungen

- **Subjektive Qualität**: Assertion-basierte Metriken können nicht alle
  Qualitätsaspekte erfassen. Der LLM-as-Judge hilft, ist aber selbst imperfekt.
- **Kosten**: Jedes Experiment braucht mehrere LLM-Aufrufe (Eval-Runs, Grading,
  Hypothese, Mutation). ~10 Experimente ≈ 50-100 API-Calls.
- **Konvergenz**: Bei starken Skills (Score >0.90) werden Verbesserungen
  schwieriger zu finden. Der Loop könnte in Plateaus stecken bleiben.
- **Eval-Qualität**: Die Qualität der Evals bestimmt die Qualität der Optimierung.
  Schlechte Evals → Skill optimiert auf falsche Ziele.

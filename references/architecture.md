# Skill Forge: Architektur

## Design-Philosophie

Dieses System überträgt das Autoresearch-Paradigma auf zwei Domänen:

**Skill-Modus**: Agent modifiziert `SKILL.md` → Evals laufen → Composite Score messen → keep/revert

**Generic-Modus**: Agent modifiziert Scope-Dateien → Metrik-Command ausführen → Wert messen → keep/revert

Der entscheidende Unterschied zwischen den Modi: Im Skill-Modus sind Mutationen
sprachlich (Formulierungen, Beispiele, Strukturen). Im Generic-Modus sind sie
technisch (Code, Config, Architektur). Das Autoresearch-Prinzip — Constraint +
mechanische Metrik + autonome Iteration = kumulativer Gewinn — bleibt identisch.

## Architektur-Übersicht

```
┌──────────────────────────────────────────────────────┐
│                  Setup-Wizard                        │
│  [Modus] → [Scope] → [Metrik] → [Richtung]         │
│                     → [Dry-Run-Gate] → [Bestätigung] │
└────────────────────────┬─────────────────────────────┘
                         │
┌────────────────────────▼─────────────────────────────┐
│                  Skill Forge Loop                     │
│                                                      │
│  ┌──────────────┐    ┌──────────┐                    │
│  │  Hypothesis   │───▶│ Mutator  │                    │
│  │  Agent        │    │  Agent   │                    │
│  │  + Coverage   │    │          │                    │
│  └──────▲───────┘    └────┬─────┘                    │
│         │                 │                           │
│         │            ┌────▼─────┐                     │
│         │            │  Run     │                     │
│         │            │  Verify  │                     │
│         │            │ (Eval /  │                     │
│         │            │  Command)│                     │
│         │            └────┬─────┘                     │
│         │                 │                           │
│         │            ┌────▼─────┐                     │
│         │            │  Score   │                     │
│         │            │  + Log   │──▶ history.json     │
│         │            │  (JSON   │──▶ experiment-log.tsv│
│         │            │   + TSV) │──▶ coverage-matrix  │
│         │            └────┬─────┘                     │
│         │                 │                           │
│         │            ┌────▼─────┐                     │
│         └────────────│  Keep /  │                     │
│                      │  Revert  │                     │
│                      │  / Skip  │                     │
│                      └──────────┘                     │
└──────────────────────────────────────────────────────┘
```

## Datenfluss

### 1. Workspace-Struktur

```
<target>-skill-forge/
├── config.json                # Wizard-Konfiguration (Modus, Scope, Metrik, etc.)
├── evals.json                 # Testfälle — Train + Test (nur Skill-Modus)
├── history.json               # Fortschritts-Tracking (JSON, strukturiert)
├── experiment-log.tsv         # Flaches Log (TSV, eine Zeile pro Experiment)
├── coverage-matrix.json       # Experiment-Abdeckung pro Kategorie
├── snapshots/
│   ├── v0/                    # Baseline (Original)
│   │   ├── SKILL.md / Scope-Dateien
│   │   └── score.json
│   ├── v1/
│   │   ├── SKILL.md / Scope-Dateien
│   │   └── score.json
│   └── ...
├── experiments/
│   ├── exp-001/
│   │   ├── hypothesis.json    # Was getestet wird
│   │   ├── mutation.json      # Was geändert wurde (inkl. Kategorie)
│   │   ├── runs/              # Nur Skill-Modus
│   │   │   ├── eval-0/
│   │   │   │   ├── with_mutation/
│   │   │   │   │   ├── outputs/
│   │   │   │   │   ├── grading.json
│   │   │   │   │   └── timing.json
│   │   │   │   └── baseline/
│   │   │   │       └── ...
│   │   │   └── eval-1/
│   │   │       └── ...
│   │   ├── command_output.txt  # Nur Generic-Modus
│   │   ├── score_mutation.json
│   │   ├── score_baseline.json
│   │   └── decision.json      # KEEP / REVERT / NEUTRAL / SKIP
│   └── exp-002/
│       └── ...
└── morning-report.md
```

### 2. config.json Schema

```json
{
  "execution_mode": "auto",
  "mode": "skill",
  "goal": "LinkedIn-Content-Skill verbessern",
  "target": "linkedin-content",
  "scope": "/path/to/skills/linkedin-content/SKILL.md",
  "scope_files_count": 1,
  "scope_validated": true,
  "metric_name": "composite_score",
  "metric_command": null,
  "metric_direction": "higher_is_better",
  "dry_run_passed": true,
  "baseline_value": 0.62,
  "dry_run_timestamp": "2026-03-14T21:45:00Z",
  "max_experiments": 10,
  "improvement_threshold": 0.02,
  "regression_threshold": 0.05,
  "time_budget_minutes": 120,
  "eval_split": [0.6, 0.4],
  "use_comparator": false,
  "parallel_evals": true,
  "target_value": null,
  "max_crashes": 3
}
```

### 3. history.json Schema

```json
{
  "skill_name": "linkedin-content",
  "mode": "skill",
  "started_at": "2026-03-14T22:00:00Z",
  "config": { "...": "Verweis auf config.json" },
  "current_best": "v3",
  "baseline_score": 0.62,
  "best_score": 0.81,
  "consecutive_no_improvement": 0,
  "consecutive_crashes": 0,
  "experiments": [
    {
      "id": "exp-001",
      "version": "v1",
      "parent": "v0",
      "hypothesis": "Beispiel für Hook-Formulierung hinzugefügt",
      "mutation_type": "example_add",
      "category": "examples",
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

### 4. Composite Score (Skill-Modus)

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

### 5. Generic-Modus Scoring

Im Generic-Modus wird der Metrik-Command direkt ausgewertet:

```python
current_value = extract_metric(command_output)
delta = current_value - baseline_value

if direction == "higher_is_better":
    improved = delta > improvement_threshold
elif direction == "lower_is_better":
    improved = -delta > improvement_threshold
```

## Setup-Wizard: Validierungs-Gates

Jeder Wizard-Schritt hat ein hartes Abnahmekriterium:

| Schritt | Gate | Fehlerbehandlung |
|---------|------|-----------------|
| Scope | Glob matcht ≥1 Datei | Neues Pattern verlangen |
| Metrik | Kein subjektiver Text | Nur Zahlen akzeptieren |
| Dry-Run | Exit-Code 0 + parsbare Zahl | Korrekturvorschläge anbieten |
| Bestätigung | User-Bestätigung | Konfiguration anpassbar |

Der Dry-Run ist das wichtigste Gate: Er verhindert, dass der Loop startet und
erst nach Stunden feststellt, dass die Eval-Infrastruktur nicht funktioniert.

## Overfitting-Schutzmaßnahmen

### Train/Test-Split (nur Skill-Modus)

```
Alle Evals
    ├── Train (60%) → Für Hypothesenbildung und Mutation
    └── Test (40%)  → Nur für Score-Berechnung, nie für Analyse
```

### Coverage-Matrix

Die Coverage-Matrix steuert die Exploration-Exploitation-Balance:

```
Frühphase (1-3):   Exploration  ████████░░  80%
Mittelphase (4-7): Balanced     █████░░░░░  50%
Spätphase (8+):    Exploitation ██░░░░░░░░  20%
```

Sättigungsregel: Eine Kategorie ist saturiert nach ≥3 Experimenten ohne
Verbesserung >0.01. Saturierte Kategorien werden deprioritisiert.

### Eval-Rotation

Nach jedem 5. Experiment:
1. Generiere 2-3 neue Eval-Queries
2. Ersetze die ältesten Train-Evals
3. Behalte die Test-Evals unverändert

### Diversity-Tracking

Die Coverage-Matrix ersetzt das einfache Sections-Counting durch
kategorisiertes Tracking mit Erfolgsraten und Sättigungserkennung.

## Crash-Handling (Generic-Modus)

```
Command-Ausführung
    ├── Exit 0 + Zahl → Normal weiter
    ├── Exit 0 + keine Zahl → SKIP (Parsing-Fehler)
    ├── Exit ≠ 0 (1. Mal) → Fix-Versuch → erneut ausführen
    └── Exit ≠ 0 (2. Mal) → SKIP → consecutive_crashes++
        └── consecutive_crashes ≥ max_crashes → Loop stoppen
```

## Integration mit Scheduled Tasks

Der Loop kann als Scheduled Task konfiguriert werden. Der Setup-Wizard
erzeugt die config.json, die der Scheduled Task dann einliest:

```python
# Via Cowork Scheduled Tasks
create_scheduled_task(
    taskId="skill-forge-{target-name}",
    cronExpression="0 22 * * *",  # Jeden Abend um 22:00
    prompt="...",
    description="Skill Forge Loop für {target-name}"
)
```

Der Task:
1. Liest `config.json` für die vollständige Konfiguration
2. Prüft ob `history.json` existiert (Resume vs. Fresh Start)
3. Führt Experimente bis zum Zeitbudget durch
4. Generiert den Morning Report
5. Beendet sich

## Ausführungsmodi: Auto vs. Guided

Der `execution_mode` bestimmt, ob der Loop autonom oder interaktiv abläuft:

```
Auto-Modus:     Wizard → Dry-Run → [Loop ohne Pause] → Report
Guided-Modus:   Wizard → Dry-Run → [Loop mit 5 Checkpoints] → Report
```

### Guided-Modus Checkpoints

```
┌────────────────────────────────────────────────────────┐
│  Guided-Modus: 5 Checkpoints im Loop                  │
│                                                        │
│  CP1: Evals prüfen (einmalig, nach Wizard-Schritt 3)  │
│       → User passt Evals an, bestimmt Anzahl/Gewicht   │
│                                                        │
│  CP2: Hypothese prüfen (jede Runde)                    │
│       → User bestätigt, passt an oder gibt eigene vor   │
│                                                        │
│  CP3: Mutation prüfen (jede Runde)                     │
│       → User sieht Diff, bestätigt oder korrigiert      │
│                                                        │
│  CP4: Ergebnis bewerten (jede Runde)                   │
│       → User sieht Score/Delta, kann Empfehlung         │
│         überstimmen (Keep/Revert/Manuell)               │
│                                                        │
│  CP5: Weitermachen? (jede Runde)                       │
│       → User entscheidet: weiter / N Runden / stopp     │
└────────────────────────────────────────────────────────┘
```

Im Auto-Modus werden alle Checkpoints übersprungen. Die config.json speichert
den Modus als `"execution_mode": "auto"` oder `"guided"`. Scheduled Tasks
verwenden immer `auto` (kein User-Prompt verfügbar).

## Limitierungen

- **Subjektive Qualität**: Assertion-basierte Metriken (Skill-Modus) können nicht alle
  Qualitätsaspekte erfassen. Der LLM-as-Judge hilft, ist aber selbst imperfekt.
- **Kosten**: Jedes Experiment braucht mehrere LLM-Aufrufe (Eval-Runs, Grading,
  Hypothese, Mutation). ~10 Experimente ≈ 50-100 API-Calls.
- **Konvergenz**: Bei starken Scores (>0.90) werden Verbesserungen
  schwieriger zu finden. Die Coverage-Matrix hilft, Plateaus zu erkennen.
- **Eval-Qualität**: Die Qualität der Evals bestimmt die Qualität der Optimierung.
  Schlechte Evals → Optimierung auf falsche Ziele.
- **Command-Stabilität**: Im Generic-Modus muss der Metrik-Command deterministisch
  sein. Flaky Commands führen zu falschen KEEP/REVERT-Entscheidungen.

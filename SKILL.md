---
name: skill-forge
description: >
  Autonome Skill-Verbesserung nach dem Autoresearch-Paradigma (Karpathy). Führt einen
  automatischen Experiment-Loop durch: Skill analysieren → Hypothese bilden → SKILL.md
  mutieren → Evals laufen lassen → Score messen → keep/revert → wiederholen. Kann über
  Nacht als Scheduled Task laufen und liefert morgens einen Experiment-Report. IMMER
  verwenden bei: Skill autonom verbessern, Skill optimieren ohne manuelles Feedback,
  Autoresearch, autonomer Verbesserungsloop, Skill-Evolution, overnight optimization,
  Skill-Experiment, "lass den Skill über Nacht besser werden", Skill-Score verbessern,
  automatische Skill-Iteration.
---

# Skill Forge

Autonome Skill-Verbesserung nach dem Autoresearch-Paradigma: Ein AI-Agent modifiziert
iterativ eine SKILL.md, evaluiert jede Änderung objektiv, behält Verbesserungen und
verwirft Verschlechterungen — ohne menschliches Feedback im Loop.

## Kern-Konzept

Inspiriert von [Karpathy's autoresearch](https://github.com/karpathy/autoresearch):

| autoresearch (LLM)        | skill-forge                   |
|---------------------------|-------------------------------|
| `train.py` wird mutiert   | `SKILL.md` wird mutiert       |
| `prepare.py` ist fix      | Eval-Framework ist fix        |
| `program.md` instruiert   | Dieser Skill instruiert       |
| `val_bpb` ist die Metrik  | Composite Score ist die Metrik|
| 5-Min-Zeitbudget          | Token/Zeit-Budget pro Eval    |
| keep/discard via git reset| keep/revert via Snapshots     |

## Voraussetzungen

Bevor du den Loop startest, brauchst du:

1. **Target-Skill** — der Skill, der verbessert werden soll
2. **Evals** — Testfälle mit Assertions (im `evals/evals.json` Format des skill-creators)
3. **Workspace** — ein Verzeichnis für Experimente und Logs

Wenn der Target-Skill noch keine Evals hat, erstelle sie zuerst (siehe Schritt 0).

## Der Autoresearch-Loop

### Schritt 0: Setup (einmalig)

1. **Target-Skill identifizieren**
   - Frage den User welchen Skill er verbessern will
   - Lies die SKILL.md und verstehe was der Skill tut

2. **Session-Tag vergeben**
   - Erzeuge einen Run-Tag basierend auf Datum und Skill-Name: `{skill}-{YYYYMMDD}`
   - Beispiel: `linkedin-content-20260314`
   - Der Tag stellt sicher, dass parallele Runs sich nicht gegenseitig überschreiben
   - Speichere den Tag in `config.json`

3. **Workspace anlegen**
   ```
   <target-skill>-autoresearch/
   ├── config.json             # Session-Tag, Konfiguration
   ├── evals/
   │   └── evals.json          # Testfälle mit Train/Test-Split
   ├── snapshots/              # Versionierte SKILL.md Kopien
   │   └── v0/                 # Baseline
   ├── experiments/            # Pro Experiment ein Ordner
   │   └── exp-001/
   │       ├── hypothesis.json
   │       ├── mutation.json
   │       ├── run.log         # Vollständiges Transcript
   │       └── grading_results.json
   ├── history.json            # Fortschritts-Tracking
   └── morning-report.md       # Zusammenfassung für den User
   ```

4. **Evals sicherstellen**
   - Prüfe ob `evals/evals.json` existiert im Target-Skill
   - Falls nicht: Erstelle 3-5 realistische Testfälle mit messbaren Assertions
   - Achte auf Train/Test-Split (60/40) für Overfitting-Schutz
   - Speichere Evals im Workspace als `evals/evals.json`

5. **Baseline messen**
   - Laufe alle Evals mit der aktuellen SKILL.md
   - Berechne den Composite Score (siehe `scripts/composite_score.py`)
   - Speichere als `snapshots/v0/` mit Score in `history.json`

### Schritt 1: Hypothese bilden

Lies den `agents/hypothesis.md` Agent-Prompt und folge seinen Anweisungen:

1. Analysiere die Eval-Ergebnisse der letzten Iteration
2. Identifiziere die schwächsten Bereiche (welche Assertions failen?)
3. Lies die Transcripts der fehlgeschlagenen Runs
4. Formuliere eine konkrete, testbare Hypothese:
   - "Die Anweisung X ist zu vage → Agent weicht ab → Assertion Y failt"
   - "Es fehlt ein Beispiel für Szenario Z → Agent improvisiert falsch"
   - "Script W hat einen Bug/ist nicht dokumentiert → wird nicht genutzt"
5. Priorisiere: Fokus auf die Änderung mit dem höchsten erwarteten Impact

**Wichtig:** Generalisiere! Nicht auf einzelne Testfälle optimieren, sondern auf
die zugrunde liegenden Muster. Wenn der Agent bei 2 von 3 Tests den falschen Stil
nutzt, ist die Lösung nicht "nutze Stil X bei Test 1 und 2", sondern "erkläre das
Prinzip hinter der Stilwahl klarer".

### Schritt 2: Mutation anwenden

Lies den `agents/mutator.md` Agent-Prompt und folge seinen Anweisungen:

1. Kopiere die aktuelle beste SKILL.md nach `snapshots/v{N}/`
2. Wende die Hypothese als gezielte Änderung an:
   - **Instruction Edits**: Formulierungen verbessern, Beispiele hinzufügen
   - **Structure Changes**: Abschnitte umorganisieren, Progressive Disclosure anpassen
   - **Script Changes**: Helper-Scripts hinzufügen/verbessern
   - **Reference Changes**: Dokumentation aktualisieren
3. Mache **eine fokussierte Änderung** pro Experiment (nicht 5 gleichzeitig)
   - Das ist entscheidend: Nur so weißt du, welche Änderung den Score beeinflusst hat
4. Dokumentiere die Änderung im Experiment-Log

### Schritt 3: Experiment laufen lassen

Für jedes Eval im Testset:

1. **Spawne einen Subagent** mit:
   - Der mutierten SKILL.md als verfügbarem Skill
   - Dem Eval-Prompt als Aufgabe
   - Einem Ausgabe-Ordner für die Ergebnisse
2. **Spawne parallel einen Baseline-Subagent** mit:
   - Der aktuell besten SKILL.md (aus `snapshots/v{best}/`)
   - Dem gleichen Eval-Prompt
   - Einem separaten Ausgabe-Ordner

Spawne so viele wie möglich parallel (alle Evals gleichzeitig starten).

3. **Transcript loggen**: Speichere den vollständigen Agent-Output als `run.log` im
   Experiment-Ordner. Ohne Transcript ist eine spätere Root-Cause-Analyse unmöglich.

4. **Grade jedes Ergebnis** mit dem Grader-Agent aus dem skill-creator:
   - Lies `<skill-creator-path>/agents/grader.md`
   - Evaluiere Assertions gegen Outputs
   - Speichere `grading_results.json` pro Run

### Schritt 3b: Crash-Recovery

Falls ein Eval-Run abstürzt (Script-Fehler, Timeout, Agent-Crash):

1. **Nicht abbrechen** — der Loop muss robust weiterlaufen
2. **Stacktrace lesen** und Fehlertyp identifizieren:
   - **Script-Bug im Target-Skill**: Mutation hat den Skill kaputt gemacht → zählt als Failure (Score 0 für dieses Eval)
   - **Infrastruktur-Fehler** (Timeout, OOM, API-Error): Retry einmal, bei erneutem Failure → überspringen und im Log notieren
   - **Eval-Bug**: Das Eval selbst ist fehlerhaft → im Log notieren, Eval aus Score-Berechnung ausschließen
3. **Crash-Log speichern** als `experiments/exp-{N}/crash.log`
4. **Weiter mit dem nächsten Eval** — ein Crash invalidiert nicht den gesamten Run

### Schritt 4: Score berechnen

Berechne den **Composite Score** für die mutierte Version und die Baseline:

```python
# Gewichtung der Score-Komponenten
composite_score = (
    assertion_pass_rate * 0.50 +   # Harte Fakten: passieren die Assertions?
    llm_judge_score * 0.30 +       # Weiche Qualität: LLM-as-Judge Bewertung
    efficiency_score * 0.20         # Effizienz: Tokens, Zeit, Tool-Calls
)
```

Berechne mit `scripts/composite_score.py` oder inline:

- **assertion_pass_rate**: `passed / total` aus grading_results.json
- **llm_judge_score**: Normalisierter Score aus Blind-Comparison (comparator.md)
  - Falls kein Comparator-Run: Nutze nur assertion_pass_rate mit Gewicht 0.80
- **efficiency_score**: Normalisiert aus `1.0 - (tokens / max_tokens)` und
  `1.0 - (duration / max_duration)`

### Schritt 5: Keep oder Revert

Die Entscheidungsregel ist einfach:

```
if mutated_score > baseline_score + IMPROVEMENT_THRESHOLD:
    KEEP  → Mutierte Version wird neue Baseline
elif mutated_score < baseline_score - REGRESSION_THRESHOLD:
    REVERT → Zurück zur vorherigen Baseline
else:
    NEUTRAL → Keep (bei Gleichstand leichte Präferenz für Neues)
```

Schwellenwerte:
- `IMPROVEMENT_THRESHOLD = 0.02` (2% Verbesserung nötig zum Behalten)
- `REGRESSION_THRESHOLD = 0.05` (5% Verschlechterung → sofort revert)

Aktualisiere `history.json`:
```json
{
  "experiment": "exp-003",
  "version": "v3",
  "parent": "v2",
  "hypothesis": "Beispiel für Edge-Case X hinzugefügt",
  "mutation_type": "instruction_edit",
  "composite_score": 0.78,
  "baseline_score": 0.72,
  "delta": "+0.06",
  "decision": "KEEP",
  "details": {
    "assertion_pass_rate": 0.85,
    "llm_judge_score": 0.70,
    "efficiency_score": 0.72
  }
}
```

### Schritt 6: Wiederholen

Gehe zurück zu Schritt 1 mit der neuen Baseline.

**Abbruchkriterien:**
- `composite_score >= 0.95` → Ziel erreicht
- `max_experiments` erreicht (Standard: 10)
- 3 aufeinanderfolgende NEUTRAL/REVERT → Plateau erreicht
- Zeitbudget aufgebraucht (für Scheduled Tasks)

### Schritt 7: Report generieren

Lies `templates/morning_report.md` und erzeuge einen Abschlussbericht:

1. **Zusammenfassung**: Start-Score → End-Score, Anzahl Experimente, Dauer
2. **Top-Verbesserungen**: Die 3 wirkungsvollsten Mutations
3. **Fehlgeschlagene Hypothesen**: Was nicht funktioniert hat (und warum)
4. **Score-Verlauf**: Grafische Darstellung als ASCII oder Mermaid-Chart
5. **Empfehlungen**: Was der User als nächstes tun könnte

Speichere den Report als `morning-report.md` im Workspace.

---

## Konfiguration

Standardwerte, die der User überschreiben kann:

| Parameter | Default | Beschreibung |
|-----------|---------|--------------|
| `max_experiments` | 10 | Maximale Anzahl Experimente |
| `improvement_threshold` | 0.02 | Minimum-Delta zum Behalten |
| `regression_threshold` | 0.05 | Maximum-Delta vor Revert |
| `time_budget_minutes` | 120 | Zeitbudget (für Scheduled Tasks) |
| `eval_split` | 0.6/0.4 | Train/Test-Split der Evals |
| `use_comparator` | false | Blind-Comparison aktivieren (teurer) |
| `parallel_evals` | true | Evals parallel laufen lassen |

---

## Scheduled Task Integration

Dieser Skill kann als nächtlicher Scheduled Task laufen. Dafür:

1. Der User übergibt den Target-Skill und bestätigt die Evals
2. Claude erstellt einen Scheduled Task mit dem Prompt:

```
Lies den skill-forge Skill und führe den autonomen
Verbesserungsloop für den Skill "<target-skill>" durch.

Workspace: <workspace-path>
Max Experimente: 10
Zeitbudget: 120 Minuten

Starte beim letzten Stand in history.json (oder bei v0 falls neu).
Generiere am Ende einen morning-report.md.
```

3. Am nächsten Morgen findet der User:
   - `morning-report.md` mit allen Ergebnissen
   - Die verbesserte SKILL.md (falls Verbesserungen gefunden)
   - Vollständige Experiment-Logs für Nachvollziehbarkeit

---

## Overfitting-Schutz

Das größte Risiko bei autonomer Optimierung ist Overfitting auf die Testfälle.
Gegenmaßnahmen:

1. **Train/Test-Split**: 60% der Evals für Optimierung, 40% als Held-out Test
2. **Generalisierungs-Check**: Der Hypothesis-Agent muss erklären, warum seine
   Änderung über die konkreten Testfälle hinaus generalisiert
3. **Mutation-Diversity**: Nicht immer den gleichen Bereich ändern — der Mutator
   tracked welche Bereiche bereits optimiert wurden
4. **Periodische Eval-Erneuerung**: Nach 5 Experimenten neue Eval-Queries generieren
   lassen und den Test-Split rotieren
5. **Regressions-Test**: Die Held-out Evals werden nie für Hypothesenbildung genutzt,
   nur für Score-Berechnung

---

## Abhängigkeiten

Dieser Skill nutzt Infrastruktur aus dem `skill-creator`:

- `agents/grader.md` — Evaluiert Assertions gegen Outputs
- `agents/comparator.md` — Blind A/B-Vergleich (optional)
- `agents/analyzer.md` — Post-hoc Analyse

Stelle sicher, dass der skill-creator verfügbar ist, oder kopiere die
benötigten Agent-Prompts in den eigenen `agents/` Ordner.

---

## Referenz-Dateien

| Datei | Zweck |
|-------|-------|
| `agents/hypothesis.md` | Hypothesenbildung aus Eval-Failures |
| `agents/mutator.md` | SKILL.md-Mutation mit Begründung |
| `agents/scorer.md` | LLM-as-Judge Bewertung |
| `scripts/composite_score.py` | Composite Score Berechnung |
| `templates/morning_report.md` | Report-Template |
| `references/architecture.md` | Detaillierte Architektur-Doku |

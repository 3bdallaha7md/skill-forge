---
name: autoresearch-skills
description: >
  Autonome Verbesserung nach dem Autoresearch-Paradigma (Karpathy). Zwei Modi:
  (1) Skill-Modus — optimiert eine SKILL.md durch iterative Mutation und Evaluation.
  (2) Generic-Modus — optimiert beliebige Dateien gegen jede mechanische Metrik
  (Testabdeckung, Bundle-Size, Lighthouse-Score, Docker-Image-Größe, etc.).
  Führt einen automatischen Experiment-Loop durch: analysieren → Hypothese bilden →
  mutieren → verifizieren → Score messen → keep/revert → wiederholen. Kann über
  Nacht als Scheduled Task laufen und liefert morgens einen Experiment-Report. IMMER
  verwenden bei: Skill autonom verbessern, Skill optimieren ohne manuelles Feedback,
  Autoresearch, autonomer Verbesserungsloop, Skill-Evolution, overnight optimization,
  Skill-Experiment, "lass den Skill über Nacht besser werden", Skill-Score verbessern,
  automatische Skill-Iteration, Code-Metrik verbessern, Testabdeckung erhöhen,
  Bundle-Size reduzieren, Performance-Score optimieren, beliebige Metrik optimieren.
---

# Autoresearch

Autonome, iterative Verbesserung nach dem Autoresearch-Paradigma: Ein AI-Agent
modifiziert gezielt Dateien, evaluiert jede Änderung gegen eine mechanische Metrik,
behält Verbesserungen und verwirft Verschlechterungen — ohne menschliches Feedback
im Loop.

## Zwei Modi

| | Skill-Modus | Generic-Modus |
|---|---|---|
| **Ziel** | SKILL.md verbessern | Beliebige Dateien optimieren |
| **Metrik** | Composite Score (Assertions + Judge + Effizienz) | Jede mechanische Metrik (Zahl via Shell-Command) |
| **Scope** | Eine SKILL.md + zugehörige Scripts | Dateien via Glob-Pattern |
| **Mutation** | Sprachliche Änderungen (Formulierung, Beispiele, Struktur) | Code-Änderungen (Refactoring, Config, Architektur) |
| **Eval** | Subagent-Runs mit Grading | Shell-Command mit Zahlenextraktion |
| **Anwendung** | Skill-Qualität steigern | Testcoverage, Bundle-Size, Lighthouse, Docker-Image, etc. |

Der Skill erkennt den Modus automatisch: Wenn der User einen Skill nennt, wird
Skill-Modus aktiviert. Wenn der User eine Metrik/einen Shell-Command nennt, wird
Generic-Modus aktiviert. Im Zweifel: fragen.

## Kern-Konzept

Inspiriert von Karpathys autoresearch-Paradigma:

| autoresearch (LLM)        | autoresearch (Skills/Generic)  |
|---------------------------|-------------------------------|
| `train.py` wird mutiert   | `SKILL.md` / Scope-Dateien werden mutiert |
| `prepare.py` ist fix      | Eval-Framework / Verify-Command ist fix |
| `program.md` instruiert   | Dieser Skill instruiert       |
| `val_bpb` ist die Metrik  | Composite Score / mechanische Metrik |
| 5-Min-Zeitbudget          | Token/Zeit-Budget pro Eval    |
| keep/discard              | keep/revert mit Snapshots     |

---

## Schritt 0: Setup-Wizard (einmalig)

Der Setup-Wizard führt schrittweise durch die Konfiguration. Jeder Schritt hat ein
Abnahmekriterium — der Wizard geht erst weiter, wenn die Validierung bestanden ist.

### Wizard-Schritt 1: Modus und Ziel erfassen

Frage den User: **"Was willst du verbessern?"**

Bestimme daraus den Modus:
- User nennt einen Skill-Namen → **Skill-Modus**
- User nennt eine Metrik, einen Shell-Command oder Code-Dateien → **Generic-Modus**
- Unklar → Nachfragen

Speichere:
```json
{
  "mode": "skill" | "generic",
  "goal": "Freitext-Beschreibung des Ziels",
  "target": "Skill-Name oder Projekt-Pfad"
}
```

### Wizard-Schritt 2: Scope definieren

**Skill-Modus:**
- Identifiziere die SKILL.md des Target-Skills
- Validierung: Datei existiert und ist lesbar

**Generic-Modus:**
- Frage nach Glob-Pattern für editierbare Dateien (z.B. `src/**/*.ts`)
- Validierung: Glob matcht mindestens eine Datei
- Anzeigen: "Gefunden: N Dateien — [Liste der ersten 10]"
- Falls 0 Treffer → Fehlermeldung, neues Pattern verlangen

Speichere:
```json
{
  "scope": "SKILL.md-Pfad oder Glob-Pattern",
  "scope_files_count": 42,
  "scope_validated": true
}
```

### Wizard-Schritt 3: Metrik definieren

**Skill-Modus:**
- Prüfe ob `evals/evals.json` existiert im Target-Skill
- Falls nicht: Erstelle 3-5 realistische Testfälle mit messbaren Assertions
- Achte auf Train/Test-Split (60/40) für Overfitting-Schutz
- Metrik = Composite Score (automatisch)

**Generic-Modus:**
- Frage: "Welcher Shell-Command misst deine Metrik?"
- Beispiele anbieten:
  - Testabdeckung: `npx jest --coverage | grep "All files" | awk '{print $10}'`
  - Bundle-Size (KB): `npm run build 2>&1 | grep "First Load JS" | awk '{print $4}'`
  - Lighthouse: `npx lighthouse http://localhost:3000 --output json | jq '.categories.performance.score'`
  - Docker-Image (MB): `docker image inspect myapp:latest --format '{{.Size}}' | awk '{print $1/1048576}'`
  - Python-Lint-Fehler: `flake8 src/ | wc -l`
- Validierung: Subjektive Metriken ("sieht besser aus", "klingt natürlicher") werden abgelehnt.
  Die Metrik muss eine einzelne parsbare Zahl produzieren.

Speichere:
```json
{
  "metric_name": "test_coverage_percent",
  "metric_command": "npx jest --coverage | grep 'All files' | awk '{print $10}'",
  "metric_direction": "higher_is_better" | "lower_is_better"
}
```

### Wizard-Schritt 4: Richtung festlegen

Frage: **"Ist ein höherer oder niedrigerer Wert besser?"**

- Testabdeckung → höher ist besser
- Bundle-Size → niedriger ist besser
- Lint-Fehler → niedriger ist besser
- Performance-Score → höher ist besser

Im Skill-Modus ist die Richtung immer `higher_is_better` (automatisch).

### Wizard-Schritt 5: Dry-Run-Validierung

Dieser Schritt ist ein harter Gate — der Loop startet erst, wenn er bestanden ist.

**Skill-Modus:**
1. Wähle ein Eval aus dem Trainings-Set
2. Führe einen einzelnen Eval-Run mit der aktuellen SKILL.md durch
3. Prüfe: Grading produziert valides JSON mit `passed`/`total` Feldern
4. Prüfe: Composite Score ist berechenbar (Zahl zwischen 0 und 1)
5. Speichere Baseline-Score

**Generic-Modus:**
1. Führe den Metrik-Command aus
2. Prüfe: Exit-Code ist 0
3. Prüfe: Output enthält eine parsbare Zahl
4. Speichere Baseline-Wert

**Bei Fehler:**
- Zeige dem User die genaue Fehlermeldung
- Biete Korrekturvorschläge an (falscher Pfad, fehlende Dependency, falsches Parsing)
- Wiederhole den Dry-Run nach Korrektur
- Erst nach erfolgreichem Dry-Run geht es weiter

Speichere:
```json
{
  "dry_run_passed": true,
  "baseline_value": 72.5,
  "dry_run_output": "Vollständiger Output des Commands",
  "dry_run_timestamp": "2026-03-14T21:45:00Z"
}
```

### Wizard-Schritt 6: Konfiguration bestätigen

Zeige dem User die vollständige Konfiguration:

```
═══════════════════════════════════════
  Autoresearch-Konfiguration
═══════════════════════════════════════
  Modus:          Skill / Generic
  Ziel:           [Freitext]
  Scope:          [Pfad / Glob] (N Dateien)
  Metrik:         [Name] via [Command]
  Richtung:       Höher/Niedriger ist besser
  Baseline:       [Wert]
  Max Experimente: 10
  Zeitbudget:     120 min
═══════════════════════════════════════
  [Start] [Bounded: N Iterationen] [Abbrechen]
```

Der User kann Parameter anpassen oder den Loop starten.

### Workspace anlegen

Nach Bestätigung:

```
<target>-autoresearch/
├── config.json            # Wizard-Konfiguration
├── evals.json             # Testfälle (nur Skill-Modus)
├── history.json            # Fortschritts-Tracking
├── experiment-log.tsv      # Flaches Log für schnelles Monitoring
├── coverage-matrix.json    # Experiment-Abdeckung
├── snapshots/
│   └── v0/                 # Baseline
├── experiments/
│   └── exp-001/
└── morning-report.md       # Zusammenfassung für den User
```

Speichere die Baseline:
- Kopiere die aktuelle SKILL.md / Scope-Dateien nach `snapshots/v0/`
- Schreibe den Baseline-Score in `history.json`
- Initialisiere `experiment-log.tsv` mit Header
- Initialisiere `coverage-matrix.json`

---

## Der Autoresearch-Loop

### Schritt 1: Hypothese bilden

Lies den `agents/hypothesis.md` Agent-Prompt und folge seinen Anweisungen:

1. Analysiere die Eval-Ergebnisse der letzten Iteration
2. Konsultiere die **Coverage-Matrix** (siehe unten) — priorisiere unterversorgte Bereiche
3. Identifiziere die schwächsten Bereiche (welche Assertions/Metriken failen?)
4. Lies die Transcripts der fehlgeschlagenen Runs (Skill-Modus) oder den Command-Output (Generic-Modus)
5. Formuliere eine konkrete, testbare Hypothese:
   - **Skill-Modus**: "Die Anweisung X ist zu vage → Agent weicht ab → Assertion Y failt"
   - **Generic-Modus**: "Funktion X allokiert unnötig → Speicher steigt → Metrik verschlechtert sich"
6. Priorisiere: Fokus auf die Änderung mit dem höchsten erwarteten Impact

**Wichtig:** Generalisiere! Nicht auf einzelne Testfälle optimieren, sondern auf
die zugrunde liegenden Muster.

### Schritt 2: Mutation anwenden

Lies den `agents/mutator.md` Agent-Prompt und folge seinen Anweisungen:

1. Kopiere die aktuelle beste Version nach `snapshots/v{N}/`
2. Wende die Hypothese als gezielte Änderung an:
   - **Skill-Modus**: Formulierungen, Beispiele, Struktur, Scripts
   - **Generic-Modus**: Code-Refactoring, Config-Änderungen, Architektur
3. Mache **eine fokussierte Änderung** pro Experiment (nicht 5 gleichzeitig)
   - Das ist entscheidend: Nur so weißt du, welche Änderung den Score beeinflusst hat
4. Dokumentiere die Änderung im Experiment-Log

### Schritt 3: Experiment laufen lassen

**Skill-Modus:**

Für jedes Eval im Testset:
1. Spawne einen Subagent mit der mutierten SKILL.md und dem Eval-Prompt
2. Spawne parallel einen Baseline-Subagent mit der besten SKILL.md
3. Grade jedes Ergebnis mit dem Grader-Agent
4. Speichere `grading.json` pro Run

**Generic-Modus:**

1. Führe den Metrik-Command aus
2. Extrahiere den Zahlenwert
3. Prüfe: Exit-Code 0 und Zahl extrahierbar
4. Bei Crash des Commands: Logge als `CRASH`, versuche einmal zu fixen, bei erneutem Crash → `SKIP` und nächste Hypothese

### Schritt 4: Score berechnen

**Skill-Modus:**

```python
# Gewichtung der Score-Komponenten
composite_score = (
    assertion_pass_rate * 0.50 +   # Harte Fakten: passieren die Assertions?
    llm_judge_score * 0.30 +       # Weiche Qualität: LLM-as-Judge Bewertung
    efficiency_score * 0.20         # Effizienz: Tokens, Zeit, Tool-Calls
)
# Ohne Comparator: assertion_pass_rate * 0.80 + efficiency_score * 0.20
```

**Generic-Modus:**

```python
# Direkte Metrik-Auswertung
current_value = extract_metric(command_output)
delta = current_value - baseline_value
# Bei lower_is_better: delta wird invertiert
improved = (delta > 0) if direction == "higher_is_better" else (delta < 0)
```

### Schritt 5: Keep oder Revert

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

**Nach jeder Entscheidung — zwei Logs aktualisieren:**

1. **history.json** (strukturiert, für programmatische Auswertung):
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
  "category": "edge_cases",
  "details": {
    "assertion_pass_rate": 0.85,
    "llm_judge_score": 0.70,
    "efficiency_score": 0.72
  }
}
```

2. **experiment-log.tsv** (flach, eine Zeile pro Experiment, für schnelles Monitoring):
```
timestamp	experiment	hypothesis_summary	metric_before	metric_after	delta	decision	category	duration_s
2026-03-14T22:15:00Z	exp-001	Hook-Beispiel hinzugefügt	0.62	0.71	+0.09	KEEP	examples	180
2026-03-14T22:28:00Z	exp-002	Workflow-Schritt für Validation	0.71	0.68	-0.03	NEUTRAL	workflow	195
2026-03-14T22:45:00Z	exp-003	Edge-Case X Beispiel	0.71	0.78	+0.07	KEEP	edge_cases	210
```

Das TSV-Format ermöglicht schnelles Scannen mit `cat`, `grep`, `tail -f` oder `awk` —
besonders nützlich für nächtliche Runs, wo man sofort sehen will ob der Loop produktiv war.

3. **Coverage-Matrix aktualisieren** (siehe unten)

### Schritt 6: Wiederholen

Gehe zurück zu Schritt 1 mit der neuen Baseline.

**Abbruchkriterien:**
- `composite_score >= 0.95` (Skill-Modus) oder Zielwert erreicht (Generic-Modus) → Ziel erreicht
- `max_experiments` erreicht (Standard: 10)
- 3 aufeinanderfolgende NEUTRAL/REVERT → Plateau erreicht
- Zeitbudget aufgebraucht (für Scheduled Tasks)
- 2 aufeinanderfolgende CRASH → Infrastruktur-Problem, Loop stoppen

### Schritt 7: Report generieren

Lies `templates/morning_report.md` und erzeuge einen Abschlussbericht:

1. **Zusammenfassung**: Start-Score → End-Score, Anzahl Experimente, Dauer
2. **Top-Verbesserungen**: Die 3 wirkungsvollsten Mutations
3. **Fehlgeschlagene Hypothesen**: Was nicht funktioniert hat (und warum)
4. **Coverage-Matrix**: Welche Bereiche wie oft getestet, wo Lücken bestehen
5. **Score-Verlauf**: Grafische Darstellung als ASCII-Chart
6. **Empfehlungen**: Was der User als nächstes tun könnte

Speichere den Report als `morning-report.md` im Workspace.

---

## Coverage-Matrix

Die Coverage-Matrix trackt, welche Bereiche des Optimierungsziels bereits wie intensiv
bearbeitet wurden — und lenkt den Hypothesis-Agent aktiv in unterversorgte Gebiete.

### Skill-Modus Kategorien

| Kategorie | Beschreibung | Beispiel-Mutationen |
|---|---|---|
| `formatting` | Output-Formatierung, Struktur, Layout | Markdown-Template, Tabellenformat |
| `content_quality` | Inhaltliche Korrektheit, Vollständigkeit | Faktenprüfung, fehlende Abschnitte |
| `examples` | Beispiele, Demonstrationen, Vorlagen | Beispiel hinzugefügt/verbessert |
| `workflow` | Prozess-Schritte, Reihenfolge, Abhängigkeiten | Schritt eingefügt/umgestellt |
| `edge_cases` | Sonderfälle, Fehlerbehandlung, Randbedingungen | Edge-Case-Anweisung ergänzt |
| `efficiency` | Token-Verbrauch, Laufzeit, Redundanz | Prosa gestrafft, Script optimiert |
| `scripts` | Helper-Scripts, Validierung, Automatisierung | Script hinzugefügt/gefixt |
| `structure` | Skill-Aufbau, Abschnittsreihenfolge | Abschnitte umorganisiert |

### Generic-Modus Kategorien

Werden dynamisch aus dem Scope abgeleitet:
- Pro Verzeichnis/Modul eine Kategorie
- Pro Dateityp eine Kategorie
- Pro funktionalem Bereich eine Kategorie (aus Code-Analyse)

### Matrix-Format

```json
{
  "categories": {
    "formatting": {
      "experiments_total": 3,
      "experiments_kept": 2,
      "experiments_reverted": 1,
      "last_experiment": "exp-005",
      "best_delta": "+0.09",
      "saturated": false
    },
    "edge_cases": {
      "experiments_total": 0,
      "experiments_kept": 0,
      "experiments_reverted": 0,
      "last_experiment": null,
      "best_delta": null,
      "saturated": false
    }
  },
  "coverage_summary": {
    "total_categories": 8,
    "touched_categories": 5,
    "saturated_categories": 1,
    "untouched_categories": ["edge_cases", "scripts", "structure"],
    "coverage_percent": 62.5
  }
}
```

### Sättigungsregel

Eine Kategorie gilt als **saturiert**, wenn:
- Mindestens 3 Experimente durchgeführt wurden UND
- Keines davon den Score um mehr als 0.01 verbessert hat

Saturierte Kategorien werden bei der Hypothesenbildung deprioritisiert (nicht
ausgeschlossen — ein besonders vielversprechender Ansatz darf trotzdem versucht werden).

### Steuerungswirkung

Der Hypothesis-Agent bekommt die Coverage-Matrix als Input und wird angewiesen:
1. Unberührte Kategorien bevorzugen (Exploration)
2. Kategorien mit hoher Erfolgsrate erneut probieren (Exploitation)
3. Saturierte Kategorien meiden (Effizienz)

Das Gleichgewicht zwischen Exploration und Exploitation verschiebt sich im Lauf
des Loops: Anfangs breit explorieren, später gezielt in erfolgreichen Bereichen vertiefen.

Alle 5 Experimente: Coverage-Zusammenfassung in den Log schreiben.

---

## Konfiguration

Standardwerte, die der User überschreiben kann:

| Parameter | Default | Beschreibung |
|-----------|---------|--------------|
| `mode` | auto | `skill`, `generic` oder `auto` (erkennt automatisch) |
| `max_experiments` | 10 | Maximale Anzahl Experimente |
| `improvement_threshold` | 0.02 | Minimum-Delta zum Behalten |
| `regression_threshold` | 0.05 | Maximum-Delta vor Revert |
| `time_budget_minutes` | 120 | Zeitbudget (für Scheduled Tasks) |
| `eval_split` | 0.6/0.4 | Train/Test-Split der Evals (nur Skill-Modus) |
| `use_comparator` | false | Blind-Comparison aktivieren (teurer, nur Skill-Modus) |
| `parallel_evals` | true | Evals parallel laufen lassen (nur Skill-Modus) |
| `target_value` | null | Zielwert für die Metrik (nur Generic-Modus) |
| `max_crashes` | 2 | Max aufeinanderfolgende Crashes vor Abbruch |

---

## Scheduled Task Integration

Dieser Skill kann als nächtlicher Scheduled Task laufen. Dafür:

1. Der User durchläuft den Setup-Wizard und bestätigt die Konfiguration
2. Claude erstellt einen Scheduled Task mit dem Prompt:

```
Lies den autoresearch-skills Skill und führe den autonomen
Verbesserungsloop durch.

Workspace: <workspace-path>
Config: <workspace-path>/config.json

Starte beim letzten Stand in history.json (oder bei v0 falls neu).
Generiere am Ende einen morning-report.md.
```

3. Am nächsten Morgen findet der User:
   - `morning-report.md` mit allen Ergebnissen
   - `experiment-log.tsv` für schnellen Überblick
   - Die verbesserte Version (falls Verbesserungen gefunden)
   - Vollständige Experiment-Logs für Nachvollziehbarkeit

---

## Overfitting-Schutz

Das größte Risiko bei autonomer Optimierung ist Overfitting auf die Testfälle.
Gegenmaßnahmen:

1. **Train/Test-Split**: 60% der Evals für Optimierung, 40% als Held-out Test (Skill-Modus)
2. **Generalisierungs-Check**: Der Hypothesis-Agent muss erklären, warum seine
   Änderung über die konkreten Testfälle hinaus generalisiert
3. **Mutation-Diversity via Coverage-Matrix**: Systematisches Tracking welche
   Bereiche wie oft mutiert wurden, mit Sättigungserkennung
4. **Periodische Eval-Erneuerung**: Nach 5 Experimenten neue Eval-Queries generieren
   lassen und den Test-Split rotieren
5. **Regressions-Test**: Die Held-out Evals werden nie für Hypothesenbildung genutzt,
   nur für Score-Berechnung
6. **Crash-Erkennung**: 2 aufeinanderfolgende Crashes stoppen den Loop statt endlos
   zu wiederholen

---

## Abhängigkeiten

Dieser Skill nutzt Infrastruktur aus dem `skill-creator` (nur im Skill-Modus):

- `agents/grader.md` — Evaluiert Assertions gegen Outputs
- `agents/comparator.md` — Blind A/B-Vergleich (optional)
- `agents/analyzer.md` — Post-hoc Analyse

Stelle sicher, dass der skill-creator verfügbar ist, oder kopiere die
benötigten Agent-Prompts in den eigenen `agents/` Ordner.

Im Generic-Modus werden keine externen Abhängigkeiten benötigt — der
Metrik-Command läuft direkt im System.

---

## Referenz-Dateien

| Datei | Zweck |
|-------|-------|
| `agents/hypothesis.md` | Hypothesenbildung aus Eval-Failures + Coverage-Matrix |
| `agents/mutator.md` | Mutation mit Begründung (Skill + Generic) |
| `agents/scorer.md` | LLM-as-Judge Bewertung (nur Skill-Modus) |
| `scripts/composite_score.py` | Composite Score Berechnung + TSV-Logging |
| `templates/morning_report.md` | Report-Template mit Coverage-Sektion |
| `references/architecture.md` | Detaillierte Architektur-Doku |

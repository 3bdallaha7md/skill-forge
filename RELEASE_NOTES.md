# Release Notes — autoresearch-skills v2.0

## Überblick

Dieses Release ist das Ergebnis einer systematischen Eigenoptimierung des Skills.
Aus der praktischen Nutzung und der Analyse wiederkehrender Problemmuster haben sich
fünf funktionale Erweiterungen herauskristallisiert, die den Skill robuster, breiter
einsetzbar und transparenter machen.

## Neue Features

### 1. Dry-Run-Validierungsgate

Der Loop startet nicht mehr blind. Ein neuer Wizard-Schritt 5 prüft vor dem ersten
Experiment, ob die gesamte Infrastruktur funktioniert:

- Im Skill-Modus: Ein Probe-Eval läuft, Grading wird auf valides JSON geprüft, Composite Score muss berechenbar sein
- Im Generic-Modus: Der Metrik-Command wird ausgeführt, Exit-Code und parsbare Zahl werden validiert

Bei Fehler gibt es konkrete Korrekturvorschläge statt eines stummen Abbruchs nach Stunden.

### 2. Interaktiver Setup-Wizard

Das bisherige Setup (Schritt 0) war eine Prosa-Beschreibung. Jetzt gibt es einen
formalisierten 6-Schritt-Wizard mit harten Abnahmekriterien pro Schritt:

1. Modus und Ziel erfassen
2. Scope definieren und validieren (Glob muss matchen)
3. Metrik definieren (subjektive Metriken werden abgelehnt)
4. Richtung festlegen (höher/niedriger ist besser)
5. Dry-Run-Validierung (hartes Gate)
6. Konfiguration bestätigen (mit Anpassungsmöglichkeit)

Die gesamte Konfiguration wird als `config.json` gespeichert und von Scheduled Tasks wiederverwendet.

### 3. Generic-Modus (Domänen-Generalisierung)

Der Skill war bisher auf SKILL.md-Optimierung beschränkt. Der neue Generic-Modus
wendet das gleiche Autoresearch-Prinzip auf beliebige Dateien und mechanische Metriken an:

- Testabdeckung erhöhen (Jest, pytest, etc.)
- Bundle-Size reduzieren
- Lighthouse-Score verbessern
- Docker-Image verkleinern
- Lint-Fehler eliminieren
- Jede andere Metrik, die ein Shell-Command als Zahl liefert

Der Modus wird automatisch erkannt oder kann manuell gesetzt werden.
Agenten-Prompts und Scoring-Logik wurden für beide Modi erweitert.

### 4. Flaches TSV-Log

Neben dem strukturierten `history.json` gibt es jetzt ein `experiment-log.tsv` —
eine Zeile pro Experiment im Tab-separierten Format. Das ermöglicht:

- Schnelles Scannen mit `cat`, `grep`, `tail -f`
- Sofortige Übersicht nach nächtlichen Runs
- Einfache Weiterverarbeitung mit `awk` oder Spreadsheets

Das TSV-Log wird automatisch bei jedem Experiment aktualisiert.
Das Script `composite_score.py` hat neue CLI-Commands für TSV-Initialisierung und -Append.

### 5. Coverage-Matrix

Ein neues Tracking-System, das zeigt welche Bereiche des Optimierungsziels wie
intensiv bearbeitet wurden:

- 8 vordefinierte Kategorien im Skill-Modus (formatting, content_quality, examples, workflow, edge_cases, efficiency, scripts, structure)
- Dynamische Kategorien im Generic-Modus (aus Code-Struktur abgeleitet)
- Sättigungserkennung: Nach 3 erfolglosen Experimenten in einer Kategorie wird sie deprioritisiert
- Exploration-Exploitation-Balance: Anfangs breit, später gezielt

Der Hypothesis-Agent nutzt die Matrix aktiv für die Priorisierung und dokumentiert
seine Entscheidung im `coverage_rationale`-Feld.

## Geänderte Dateien

| Datei | Änderung |
|-------|---------|
| `SKILL.md` | Komplett überarbeitet: Zwei Modi, Setup-Wizard, TSV-Log, Coverage-Matrix, Crash-Handling |
| `agents/hypothesis.md` | Coverage-Matrix als Input, Generic-Modus Root Causes, Phasen-basierte Exploration |
| `agents/mutator.md` | Generic-Modus Mutationen, Kategorie-Pflicht, Crash-Handling |
| `agents/scorer.md` | Klarstellung: Nur Skill-Modus (Generic nutzt Command direkt) |
| `scripts/composite_score.py` | TSV-Logging, Coverage-Matrix-Verwaltung, Generic-Metrik-Extraktion, CLI-Subcommands |
| `templates/morning_report.md` | Coverage-Sektion, TSV-Tail-Anzeige, Crash/Skip-Statistik |
| `references/architecture.md` | Wizard-Gates, Generic-Modus-Architektur, Crash-Handling-Diagramm |
| `references/scheduled_task_template.md` | Generic-Modus-Beispiel, config.json-basierte Konfiguration |

## Migration

Bestehende Workspaces (`history.json`) sind abwärtskompatibel. Beim ersten Start
mit v2 werden fehlende Felder (`mode`, `category`, `consecutive_crashes`) mit
Standardwerten ergänzt. Die `config.json` wird beim nächsten Wizard-Durchlauf erstellt.

Neue Dateien (`experiment-log.tsv`, `coverage-matrix.json`) werden automatisch
initialisiert, wenn sie noch nicht existieren.

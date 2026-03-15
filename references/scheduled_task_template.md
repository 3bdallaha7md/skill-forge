# Scheduled Task Template für Autoresearch

## Task-Prompt (Template)

Ersetze die `{placeholder}` mit den konkreten Werten.

```
Lies den Skill 'autoresearch-skills' und führe den autonomen Verbesserungsloop durch.

## Target
- Skill: {target_skill_name}
- Skill-Pfad: {target_skill_path}
- Workspace: {workspace_path}

## Konfiguration
- Max Experimente: {max_experiments}
- Zeitbudget: {time_budget_minutes} Minuten
- Improvement Threshold: 0.02
- Regression Threshold: 0.05
- Comparator: {use_comparator}

## Anweisungen
1. Lies die SKILL.md des autoresearch-skills Skills
2. Prüfe ob {workspace_path}/history.json existiert
   - Falls ja: Setze beim letzten Stand fort
   - Falls nein: Starte mit Schritt 0 (Setup)
3. Führe den Loop aus (Schritt 1-6) bis ein Abbruchkriterium greift
4. Generiere den Morning Report als {workspace_path}/morning-report.md
5. Speichere die beste SKILL.md Version in {workspace_path}/best/SKILL.md
```

## Beispiel: Scheduled Task erstellen

```python
# Täglicher Autoresearch-Run um 22:00
create_scheduled_task(
    taskId="autoresearch-linkedin-content",
    cronExpression="0 22 * * *",
    description="Autoresearch-Loop für linkedin-content Skill",
    prompt="""Lies den Skill 'autoresearch-skills' und führe den autonomen Verbesserungsloop durch.

## Target
- Skill: linkedin-content
- Skill-Pfad: /path/to/skills/linkedin-content
- Workspace: /path/to/linkedin-content-autoresearch

## Konfiguration
- Max Experimente: 8
- Zeitbudget: 90 Minuten
- Improvement Threshold: 0.02
- Regression Threshold: 0.05
- Comparator: false

## Anweisungen
1. Lies die SKILL.md des autoresearch-skills Skills
2. Prüfe ob history.json im Workspace existiert (Resume vs. Fresh Start)
3. Führe den Loop aus bis ein Abbruchkriterium greift
4. Generiere den Morning Report
5. Speichere die beste SKILL.md Version"""
)
```

## Einmaliger Run

Für einen einzelnen Over-Night-Run statt einem regelmäßigen Schedule:

```python
create_scheduled_task(
    taskId="autoresearch-once-linkedin",
    fireAt="2026-03-14T22:00:00+01:00",
    description="Einmaliger Autoresearch-Run für linkedin-content",
    prompt="..."
)
```

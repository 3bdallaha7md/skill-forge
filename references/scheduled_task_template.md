# Scheduled Task Template für Autoresearch

## Task-Prompt (Template)

Ersetze die `{placeholder}` mit den konkreten Werten.

```
Lies den Skill 'skill-forge' und führe den autonomen Verbesserungsloop durch.

## Konfiguration
- Workspace: {workspace_path}
- Config: {workspace_path}/config.json

## Anweisungen
1. Lies die SKILL.md des skill-forge Skills
2. Lies die config.json im Workspace für Modus, Scope, Metrik und alle Parameter
3. Prüfe ob {workspace_path}/history.json existiert
   - Falls ja: Setze beim letzten Stand fort
   - Falls nein: Starte mit Schritt 0 (Setup — Dry-Run-Validierung wiederholen)
4. Führe den Loop aus (Schritt 1-6) bis ein Abbruchkriterium greift
5. Generiere den Morning Report als {workspace_path}/morning-report.md
6. Speichere die beste Version in {workspace_path}/snapshots/v{best}/
```

## Beispiel: Skill-Modus Scheduled Task

```python
# Täglicher Autoresearch-Run um 22:00
create_scheduled_task(
    taskId="autoresearch-linkedin-content",
    cronExpression="0 22 * * *",
    description="Autoresearch-Loop für linkedin-content Skill",
    prompt="""Lies den Skill 'skill-forge' und führe den autonomen Verbesserungsloop durch.

## Konfiguration
- Workspace: /path/to/linkedin-content-autoresearch
- Config: /path/to/linkedin-content-autoresearch/config.json

## Anweisungen
1. Lies die SKILL.md des skill-forge Skills
2. Lies die config.json für alle Parameter
3. Prüfe ob history.json existiert (Resume vs. Fresh Start)
4. Führe den Loop aus bis ein Abbruchkriterium greift
5. Generiere den Morning Report
6. Speichere die beste SKILL.md"""
)
```

## Beispiel: Generic-Modus Scheduled Task

```python
# Wöchentliche Bundle-Size-Optimierung
create_scheduled_task(
    taskId="autoresearch-bundle-size",
    cronExpression="0 22 * * 0",  # Sonntags um 22:00
    description="Autoresearch-Loop für Bundle-Size-Optimierung",
    prompt="""Lies den Skill 'skill-forge' und führe den autonomen Verbesserungsloop durch.

## Konfiguration
- Workspace: /path/to/project-bundle-autoresearch
- Config: /path/to/project-bundle-autoresearch/config.json

## Anweisungen
1. Lies die SKILL.md des skill-forge Skills
2. Lies die config.json (Generic-Modus, Metrik: Bundle-Size)
3. Führe den Loop aus bis Abbruchkriterium greift
4. Generiere den Morning Report"""
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

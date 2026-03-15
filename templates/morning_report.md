# Skill Forge — Morning Report

> Generiert: {timestamp}
> Modus: {mode}
> Target: {target_name}
> Dauer: {total_duration}

## Zusammenfassung

| Metrik | Start (v0) | Ende (v{final}) | Delta |
|--------|-----------|-----------------|-------|
| {metric_name} | {start_score} | {end_score} | {delta_score} |
| Experimente | {total_experiments} | davon KEEP: {keeps} | REVERT: {reverts} |
| Crashes | {crashes} | SKIPs: {skips} | |

## Score-Verlauf

```
Score
1.0 ┤
0.9 ┤
0.8 ┤  {chart_placeholder}
0.7 ┤
0.6 ┤
0.5 ┤
    └──────────────────────
     v0  v1  v2  v3  ...
```

## Top-Verbesserungen

{top_improvements}

## Fehlgeschlagene Hypothesen

{failed_hypotheses}

## Coverage-Matrix

| Kategorie | Experimente | KEEP | REVERT | Best Delta | Status |
|-----------|------------|------|--------|------------|--------|
{coverage_rows}

**Coverage:** {coverage_percent}% ({touched}/{total} Kategorien berührt, {saturated} saturiert)

**Unberührte Bereiche:** {untouched_categories}

## TSV-Log (letzte 5 Einträge)

```
{tsv_tail}
```

Vollständiges Log: `{workspace_path}/experiment-log.tsv`

## Verbleibende Schwachstellen

{remaining_weaknesses}

## Empfehlungen

{recommendations}

---

*Generiert vom Skill Forge Loop. Experiment-Logs unter: {workspace_path}/experiments/*

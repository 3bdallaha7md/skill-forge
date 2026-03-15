#!/usr/bin/env python3
"""Composite Score Berechnung für autoresearch-skills.

Berechnet einen gewichteten Score aus:
- Assertion Pass Rate (50%)
- LLM Judge Score (30%)
- Efficiency Score (20%)

Kann als Script oder als importierte Funktion genutzt werden.
"""

import argparse
import json
import sys
from pathlib import Path


def calc_assertion_pass_rate(grading_results: list[dict]) -> float:
    """Berechne die Gesamt-Pass-Rate über alle Grading-Ergebnisse."""
    total_passed = 0
    total_assertions = 0
    for grading in grading_results:
        summary = grading.get("summary", {})
        total_passed += summary.get("passed", 0)
        total_assertions += summary.get("total", 0)
    if total_assertions == 0:
        return 0.0
    return total_passed / total_assertions


def calc_efficiency_score(
    tokens_used: int,
    duration_seconds: float,
    max_tokens: int = 100000,
    max_duration: float = 300.0,
) -> float:
    """Berechne den Effizienz-Score (0-1, höher = effizienter).

    Normalisiert Token-Verbrauch und Laufzeit auf [0,1] und mittelt.
    """
    token_score = max(0.0, 1.0 - (tokens_used / max_tokens))
    time_score = max(0.0, 1.0 - (duration_seconds / max_duration))
    return (token_score + time_score) / 2.0


def calc_composite_score(
    assertion_pass_rate: float,
    llm_judge_score: float | None = None,
    efficiency_score: float = 0.5,
    use_comparator: bool = False,
) -> float:
    """Berechne den gewichteten Composite Score.

    Gewichtung:
    - Mit Comparator:  assertions=0.50, judge=0.30, efficiency=0.20
    - Ohne Comparator: assertions=0.80, efficiency=0.20
    """
    if use_comparator and llm_judge_score is not None:
        return (
            assertion_pass_rate * 0.50
            + llm_judge_score * 0.30
            + efficiency_score * 0.20
        )
    else:
        return assertion_pass_rate * 0.80 + efficiency_score * 0.20


def score_from_experiment_dir(experiment_dir: str, use_comparator: bool = False) -> dict:
    """Berechne den Composite Score aus einem Experiment-Verzeichnis.

    Erwartet folgende Dateien im Verzeichnis:
    - grading_results.json: Liste von Grading-Ergebnissen
    - timing.json: Timing-Daten (optional)
    - comparison.json: LLM-Judge-Ergebnis (optional, nur mit use_comparator)
    """
    exp_path = Path(experiment_dir)

    # Grading-Ergebnisse laden
    grading_file = exp_path / "grading_results.json"
    if grading_file.exists():
        grading_results = json.loads(grading_file.read_text())
    else:
        # Suche nach einzelnen grading.json Dateien in Unterordnern
        grading_results = []
        for gf in exp_path.rglob("grading.json"):
            grading_results.append(json.loads(gf.read_text()))

    assertion_pass_rate = calc_assertion_pass_rate(grading_results)

    # Timing-Daten laden
    total_tokens = 0
    total_duration = 0.0
    for tf in exp_path.rglob("timing.json"):
        timing = json.loads(tf.read_text())
        total_tokens += timing.get("total_tokens", 0)
        total_duration += timing.get("total_duration_seconds", 0)

    efficiency = calc_efficiency_score(total_tokens, total_duration)

    # Optional: LLM Judge Score
    llm_judge_score = None
    if use_comparator:
        comparison_file = exp_path / "comparison.json"
        if comparison_file.exists():
            comparison = json.loads(comparison_file.read_text())
            rubric = comparison.get("rubric", {})
            # Normalisiere den Score auf [0,1] (original ist 1-10)
            scores = []
            for side in rubric.values():
                if isinstance(side, dict) and "overall_score" in side:
                    scores.append(side["overall_score"] / 10.0)
            if scores:
                llm_judge_score = max(scores)  # Score des Kandidaten

    composite = calc_composite_score(
        assertion_pass_rate=assertion_pass_rate,
        llm_judge_score=llm_judge_score,
        efficiency_score=efficiency,
        use_comparator=use_comparator,
    )

    return {
        "composite_score": round(composite, 4),
        "assertion_pass_rate": round(assertion_pass_rate, 4),
        "llm_judge_score": round(llm_judge_score, 4) if llm_judge_score is not None else None,
        "efficiency_score": round(efficiency, 4),
        "details": {
            "total_tokens": total_tokens,
            "total_duration_seconds": round(total_duration, 1),
            "grading_files_found": len(grading_results),
        },
    }


def main():
    parser = argparse.ArgumentParser(description="Composite Score Berechnung")
    parser.add_argument("experiment_dir", help="Pfad zum Experiment-Verzeichnis")
    parser.add_argument(
        "--use-comparator",
        action="store_true",
        help="LLM-as-Judge Score einbeziehen (benötigt comparison.json)",
    )
    parser.add_argument("--json", action="store_true", help="Ausgabe als JSON")
    args = parser.parse_args()

    result = score_from_experiment_dir(args.experiment_dir, args.use_comparator)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"Composite Score: {result['composite_score']:.2%}")
        print(f"  Assertion Pass Rate: {result['assertion_pass_rate']:.2%}")
        if result["llm_judge_score"] is not None:
            print(f"  LLM Judge Score:     {result['llm_judge_score']:.2%}")
        print(f"  Efficiency Score:    {result['efficiency_score']:.2%}")
        print(f"  Tokens: {result['details']['total_tokens']}")
        print(f"  Duration: {result['details']['total_duration_seconds']}s")


if __name__ == "__main__":
    main()

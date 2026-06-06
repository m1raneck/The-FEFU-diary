from dataclasses import dataclass
from typing import Iterable, Optional, Sequence


@dataclass(frozen=True)
class ScaleRule:
    min_points: float
    max_points: float
    final_grade: int


@dataclass(frozen=True)
class WeightedCategory:
    id: int
    weight: float


@dataclass(frozen=True)
class ScoreEntry:
    category_id: int
    raw_score: float


def convert_score_to_grade(raw_score: float, rules: Sequence[ScaleRule]) -> Optional[int]:
    for rule in sorted(rules, key=lambda r: r.min_points):
        if rule.min_points <= raw_score <= rule.max_points:
            return rule.final_grade
    return None


def normalize_weights(weights: Iterable[float]) -> list[float]:
    values = [float(w) for w in weights if w > 0]
    total = sum(values)
    if total == 0:
        return []
    return [w / total for w in values]


def calculate_weighted_percent(
    entries: Sequence[ScoreEntry],
    categories: Sequence[WeightedCategory],
) -> Optional[float]:
    """Итоговый % = сумма (балл × коэф) по каждой работе."""
    cat_map = {c.id: c for c in categories}
    percents: list[float] = []

    for entry in entries:
        category = cat_map.get(entry.category_id)
        if category is None or entry.raw_score is None:
            continue
        percents.append(float(entry.raw_score) * float(category.weight))

    if not percents:
        return None
    return sum(percents)


def calculate_final_grade(
    entries: Sequence[ScoreEntry],
    categories: Sequence[WeightedCategory],
    scale_rules: Sequence[ScaleRule],
) -> dict:
    weighted_percent = calculate_weighted_percent(entries, categories)
    if weighted_percent is None:
        return {"weighted_percent": None, "final_grade": None, "matched_by_scale": False}

    final_grade = convert_score_to_grade(weighted_percent, scale_rules)
    return {
        "weighted_percent": round(weighted_percent, 2),
        "final_grade": final_grade,
        "matched_by_scale": final_grade is not None,
    }

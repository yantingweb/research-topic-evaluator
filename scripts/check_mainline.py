"""Validate promotions recorded in the project's topic registry."""

import json
import math
import re
import sys
from datetime import date
from pathlib import Path
from urllib.parse import urlsplit


STATUSES = {"literature_audit", "pilot_ready", "short_project", "stopped", "mainline_approved"}
TOPIC_ID = re.compile(r"T\d{2,}\Z")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def text(value):
    return isinstance(value, str) and bool(value.strip())


def number(value):
    return type(value) in (int, float) and math.isfinite(value)


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def section(record, key):
    value = record.get(key)
    require(isinstance(value, dict), f"missing {key}")
    return value


def fields(record, label, *keys):
    for key in keys:
        require(text(record.get(key)), f"missing {label}.{key}")


def web_source(record, key, label):
    fields(record, label, key)
    url = urlsplit(record[key])
    require(url.scheme == "https" and url.hostname, f"{label}.{key} must be an HTTPS source")


def local_ref(root, record, key, label):
    fields(record, label, key)
    raw = record[key]
    ref = Path(raw)
    resolved = (root / ref).resolve()
    relative = resolved.relative_to(root) if resolved.is_relative_to(root) else None
    require(
        not ref.is_absolute() and relative is not None and resolved.is_file()
        and not any(part.startswith(".") or part == "work" for part in relative.parts),
        f"{label}.{key} must point to a reviewable file in the repository",
    )
    return resolved


def check_pilot(root, review):
    fields(review, "review", "claim")
    search = section(review, "search")
    fields(search, "search", "date")
    date.fromisoformat(search["date"])
    for key in ("databases", "queries"):
        value = search.get(key)
        require(isinstance(value, list) and value and all(map(text, value)), f"missing search.{key}")

    nearest = review.get("nearest_work")
    require(isinstance(nearest, list) and nearest, "missing full-text nearest-work comparison")
    for i, paper in enumerate(nearest):
        label = f"nearest_work[{i}]"
        require(isinstance(paper, dict), f"invalid {label}")
        web_source(paper, "url", label)
        fields(paper, label, "location", "already_answers", "remaining_difference", "counterevidence")

    pilot = section(review, "pilot")
    fields(pilot, "pilot", "strong_baseline", "held_out_protocol", "metric", "unit", "threshold_basis", "budget", "stop_rule")
    local_ref(root, pilot, "plan_ref", "pilot")
    require(number(pilot.get("min_effect")) and pilot["min_effect"] > 0, "pilot.min_effect must be a positive number")
    return pilot


def check_mainline(root, review, pilot):
    importance = section(review, "importance")
    fields(importance, "importance", "affected_group", "decision", "cost_of_error")
    web_source(importance, "source_url", "importance")

    result = section(review, "result")
    artifact = local_ref(root, result, "artifact_ref", "result")
    plan = local_ref(root, pilot, "plan_ref", "pilot")
    require(artifact != plan, "result.artifact_ref must differ from the experimental plan")
    fields(result, "result", "metric", "unit", "uncertainty_method", "budget_comparison", "alternative_explanations")
    require((result["metric"], result["unit"]) == (pilot["metric"], pilot["unit"]), "result metric or unit differs from pilot")
    effect = result.get("observed_effect")
    lower = result.get("uncertainty_lower_bound")
    require(number(effect) and number(lower) and lower <= effect, "invalid observed effect or uncertainty bound")
    require(lower >= pilot["min_effect"], "effect lower bound does not meet the minimum meaningful effect")

    replication = section(review, "replication")
    fields(replication, "replication", "independent_setting", "scope")
    independent = local_ref(root, replication, "artifact_ref", "replication")
    require(independent not in (plan, artifact), "replication requires a separate evidence artifact")
    fields(section(review, "full_resources"), "full_resources", "budget", "access")
    fields(review, "review", "target_venue")

    decision = section(review, "user_decision")
    require(decision.get("approved") is True, "explicit user decision required")
    approval = local_ref(root, decision, "record_ref", "user_decision")
    require(approval not in (plan, artifact, independent), "user decision requires a separate record")


def validate(root):
    root = root.resolve()
    records = load(root / "reviews" / "topic-status.json")
    require(isinstance(records, list) and records, "topic status registry must be a nonempty list")
    seen = set()
    for record in records:
        require(isinstance(record, dict), "invalid topic status record")
        topic = record.get("topic_id")
        require(text(topic) and TOPIC_ID.fullmatch(topic) and topic not in seen, f"invalid or duplicate topic ID: {topic!r}")
        seen.add(topic)
        try:
            fields(record, "status record", "status", "reason")
            status = record["status"]
            require(status in STATUSES, f"unknown status {status!r}")
            if status in {"pilot_ready", "mainline_approved"}:
                review = load(root / "reviews" / f"{topic}.json")
                require(isinstance(review, dict) and review.get("topic_id") == topic, "review topic ID does not match status")
                pilot = check_pilot(root, review)
                if status == "mainline_approved":
                    check_mainline(root, review, pilot)
        except (OSError, ValueError) as error:
            raise ValueError(f"{topic}: {error}") from error

    audit = root / "docs" / "topic-audit.md"
    if audit.exists():
        documented = set(re.findall(r"\bT\d{2,}\b", audit.read_text(encoding="utf-8")))
        require(documented <= seen, f"missing status records: {', '.join(sorted(documented - seen))}")
    return len(seen)


if __name__ == "__main__":
    try:
        count = validate(Path(__file__).resolve().parents[1])
    except (OSError, ValueError) as error:
        sys.exit(f"Mainline check failed: {error}")
    print(f"Validated {count} topic status records.")

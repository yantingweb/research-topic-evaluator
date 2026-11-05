import json
import tempfile
import unittest
from pathlib import Path

from scripts.check_mainline import validate


class MainlinePromotionTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        (self.root / "reviews").mkdir()
        for name in ("plan", "results", "replication", "decision"):
            (self.root / f"{name}.md").write_text(f"Fixture: {name}", encoding="utf-8")
        self.record = {
            "topic_id": "T14", "claim": "Budget changes which recipe should be retained",
            "search": {"date": "2026-11-05", "databases": ["arXiv"], "queries": ["recipe rankings"]},
            "nearest_work": [{
                "url": "https://arxiv.org/html/2606.28551", "location": "Section 4.3",
                "already_answers": "Ranking under a fixed schedule", "remaining_difference": "Budget interaction",
                "counterevidence": "Ranking was stable in prior setting",
            }],
            "pilot": {
                "plan_ref": "plan.md", "strong_baseline": "Pretraining ranking", "held_out_protocol": "Held-out tasks",
                "metric": "regret reduction", "unit": "pp", "min_effect": 2, "threshold_basis": "Deployment tolerance",
                "budget": "One GPU hour", "stop_rule": "Stop when regret reduction is negligible",
            },
            "importance": {"affected_group": "Data teams", "decision": "Retain recipes", "cost_of_error": "Lost accuracy", "source_url": "https://allenai.org/blog/datadecide"},
            "result": {
                "artifact_ref": "results.md", "metric": "regret reduction", "unit": "pp", "observed_effect": 4,
                "uncertainty_lower_bound": 3, "uncertainty_method": "Paired bootstrap", "budget_comparison": "Matched cost",
                "alternative_explanations": "Control architecture and data order",
            },
            "replication": {"artifact_ref": "replication.md", "independent_setting": "Separate task family", "scope": "Matched small models"},
            "full_resources": {"budget": "20 GPU hours", "access": "Confirmed"}, "target_venue": "ICLR",
            "user_decision": {"approved": True, "record_ref": "decision.md"},
        }

    def check(self, status, write_review=True):
        ledger = [{"topic_id": "T14", "status": status, "reason": "Test fixture"}]
        (self.root / "reviews/topic-status.json").write_text(json.dumps(ledger), encoding="utf-8")
        if write_review:
            (self.root / "reviews/T14.json").write_text(json.dumps(self.record), encoding="utf-8")
        return validate(self.root)

    def test_literature_candidate_needs_no_fabricated_evidence(self):
        self.assertEqual(self.check("literature_audit", write_review=False), 1)

    def test_pilot_without_full_text_comparison_is_rejected(self):
        self.record["nearest_work"] = []
        with self.assertRaisesRegex(ValueError, "full-text nearest-work"):
            self.check("pilot_ready")

    def test_mainline_cannot_use_plan_as_result(self):
        self.record["result"]["artifact_ref"] = "plan.md"
        with self.assertRaisesRegex(ValueError, "must differ from the experimental plan"):
            self.check("mainline_approved")

    def test_mainline_rejects_effect_below_predeclared_threshold(self):
        self.record["result"]["uncertainty_lower_bound"] = 1.9
        with self.assertRaisesRegex(ValueError, "minimum meaningful effect"):
            self.check("mainline_approved")

    def test_mainline_requires_explicit_user_decision(self):
        self.record["user_decision"]["approved"] = False
        with self.assertRaisesRegex(ValueError, "explicit user decision"):
            self.check("mainline_approved")

    def test_complete_record_can_be_promoted(self):
        self.assertEqual(self.check("mainline_approved"), 1)

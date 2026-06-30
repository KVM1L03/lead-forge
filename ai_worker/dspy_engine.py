"""DSPy-based lead qualification engine.

Uses dspy.Predict with a typed Signature. The LM is injected per-call via
dspy.context(lm=...) to avoid the race condition that dspy.configure(lm=...)
would cause under parallel Temporal activities (CLAUDE.md §11 anti-pattern #1).
"""

import dspy

from shared.schemas import PlaceDetails, QualifierVerdict


class QualifyLead(dspy.Signature):  # type: ignore[misc]
    """Determine if a business is a qualified lead for a given outreach goal."""

    outreach_goal: str = dspy.InputField(
        desc="What kind of leads the user wants, "
        "e.g. 'B2B SaaS companies selling to dental practices'"
    )
    business: str = dspy.InputField(desc="JSON-serialized PlaceDetails")

    is_qualified: bool = dspy.OutputField(
        desc="True only if the business clearly matches the outreach goal"
    )
    score: float = dspy.OutputField(desc="Confidence 0.0-1.0")
    reasoning: str = dspy.OutputField(desc="One sentence explaining the verdict")
    icp_fit: dict[str, bool] = dspy.OutputField(
        desc="Dict mapping ICP criteria names to bool, "
        "e.g. {'is_b2b': True, 'has_website': True, 'size_match': False}"
    )


# Module-level predictor — stateless; LM is resolved from context at call time.
_predictor = dspy.Predict(QualifyLead)


def qualify_lead(
    outreach_goal: str,
    place: PlaceDetails,
    *,
    lm: dspy.LM,
) -> QualifierVerdict:
    """Qualify a lead against an outreach goal using DSPy.

    ``lm`` is applied via dspy.context per-call so parallel Temporal activities
    running this function concurrently never share a global LM setting.
    """
    with dspy.context(lm=lm):
        prediction = _predictor(
            outreach_goal=outreach_goal,
            business=place.model_dump_json(),
        )
    return QualifierVerdict(
        is_qualified=prediction.is_qualified,
        score=float(prediction.score),
        reasoning=str(prediction.reasoning),
        icp_fit=dict(prediction.icp_fit),
    )

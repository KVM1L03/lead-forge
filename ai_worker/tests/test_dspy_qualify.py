"""Tests for the DSPy lead-qualification engine.

All tests use DummyLM — no real LLM calls are made.
"""

import pytest
from dspy.utils import DummyLM
from dspy.utils.exceptions import AdapterParseError

from ai_worker.dspy_engine import qualify_lead
from shared.schemas import PlaceDetails, QualifierVerdict

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

_PLACE = PlaceDetails(
    id="dental-warsaw-001",
    name="Klinika Stomatologiczna Centrum",
    address="ul. Nowy Swiat 28, Warszawa",
    lat=52.233,
    lng=21.021,
    category="dental",
    rating=4.8,
    review_count=187,
    website="https://dental-centrum.pl",
    phone="+48 22 826 1234",
    hours=["Mon-Fri 8:00-20:00"],
    photos=[],
)

_GOOD_ANSWER = {
    "is_qualified": "True",
    "score": "0.85",
    "reasoning": "Dental clinic with website — fits the outreach goal.",
    "icp_fit": '{"is_b2b": true, "has_website": true, "size_match": false}',
}

# ---------------------------------------------------------------------------
# Happy path
# ---------------------------------------------------------------------------


def test_qualify_lead_returns_qualifier_verdict() -> None:
    lm = DummyLM(answers=[_GOOD_ANSWER])
    result = qualify_lead("B2B dental software", _PLACE, lm=lm)
    assert isinstance(result, QualifierVerdict)


def test_qualify_lead_maps_is_qualified() -> None:
    lm = DummyLM(answers=[_GOOD_ANSWER])
    result = qualify_lead("B2B dental software", _PLACE, lm=lm)
    assert result.is_qualified is True


def test_qualify_lead_maps_score() -> None:
    lm = DummyLM(answers=[_GOOD_ANSWER])
    result = qualify_lead("B2B dental software", _PLACE, lm=lm)
    assert result.score == pytest.approx(0.85)
    assert 0.0 <= result.score <= 1.0


def test_qualify_lead_maps_reasoning() -> None:
    lm = DummyLM(answers=[_GOOD_ANSWER])
    result = qualify_lead("B2B dental software", _PLACE, lm=lm)
    assert isinstance(result.reasoning, str)
    assert len(result.reasoning) > 0


def test_qualify_lead_maps_icp_fit_with_bool_values() -> None:
    lm = DummyLM(answers=[_GOOD_ANSWER])
    result = qualify_lead("B2B dental software", _PLACE, lm=lm)
    assert isinstance(result.icp_fit, dict)
    assert result.icp_fit["is_b2b"] is True
    assert result.icp_fit["has_website"] is True
    assert result.icp_fit["size_match"] is False
    # QualifierVerdict strict mode: values must be actual booleans
    assert all(isinstance(v, bool) for v in result.icp_fit.values())


def test_qualify_lead_not_qualified() -> None:
    lm = DummyLM(
        answers=[
            {
                "is_qualified": "False",
                "score": "0.15",
                "reasoning": "Coffee shop — not a B2B dental target.",
                "icp_fit": '{"is_b2b": false, "has_website": false, "size_match": false}',
            }
        ]
    )
    result = qualify_lead("B2B dental software", _PLACE, lm=lm)
    assert result.is_qualified is False
    assert result.score == pytest.approx(0.15)


# ---------------------------------------------------------------------------
# Malformed LLM output
# ---------------------------------------------------------------------------


def test_malformed_output_raises_adapter_parse_error() -> None:
    # Empty answers force DSPy to exhaust its retry budget (2 attempts)
    lm = DummyLM(answers=[{}, {}])
    with pytest.raises(AdapterParseError):
        qualify_lead("B2B dental software", _PLACE, lm=lm)


def test_malformed_output_retries_before_failing() -> None:
    # DSPy retries once on parse failure — 2 LM calls total before raising
    lm = DummyLM(answers=[{}, {}])
    with pytest.raises(AdapterParseError):
        qualify_lead("B2B dental software", _PLACE, lm=lm)
    assert len(lm.history) == 2  # 1 initial attempt + 1 retry


# ---------------------------------------------------------------------------
# dspy.context per-call (not dspy.configure at module scope)
# ---------------------------------------------------------------------------


def test_dspy_context_used_per_call_not_global_configure() -> None:
    # qualify_lead must work even when no global LM is configured.
    # If it called dspy.configure() at module scope or relied on a global LM,
    # this would raise. Passing lm= via dspy.context inside the function
    # is the only way this can succeed.
    import dspy

    lm = DummyLM(answers=[_GOOD_ANSWER])
    # Ensure there is no global LM set (reset to None / unset state)
    original = dspy.settings.lm
    dspy.settings.configure(lm=None)
    try:
        result = qualify_lead("B2B dental software", _PLACE, lm=lm)
        assert result.is_qualified is True
    finally:
        dspy.settings.configure(lm=original)


def test_provided_lm_is_the_one_called() -> None:
    # Verify the DummyLM we pass is the one actually called (history populated).
    lm = DummyLM(answers=[_GOOD_ANSWER])
    assert len(lm.history) == 0
    qualify_lead("B2B dental software", _PLACE, lm=lm)
    assert len(lm.history) == 1

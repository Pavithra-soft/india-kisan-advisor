from app.agri.retrieval.qa import answer_question
from app.agri.retrieval.verify import verify_answer
from app.agri.retrieval.store import load_facts
from app.agri.schemas import GroundedAnswer, NotSureResponse


def test_grounded_price_answer_has_citation():
    ans = answer_question("Kurnool paddy wholesale price", crop_id="rice", region_id="ap")
    assert isinstance(ans, GroundedAnswer)
    assert "2150" in " ".join(ans.sentences)
    assert any(c.record_id.startswith("price-") for c in ans.citations)


def test_abstains_on_empty_region_pool():
    ans = answer_question("rice price", crop_id="rice", region_id="xx")
    assert isinstance(ans, NotSureResponse)


def test_numeric_verification_rejects_hallucinated_number():
    records = load_facts()[:1]
    bad = ["The price was 9999 INR per quintal [price-rice-kurnool-2025-10-15]"]
    v = verify_answer(bad, records)
    assert not v.ok
    assert v.numeric_mismatches

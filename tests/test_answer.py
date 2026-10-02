from pathlib import Path

from answer import best_answer

KB = [p.read_text() for p in sorted(Path("knowledge_base").glob("*.md"))]


def test_picks_line_matching_the_question():
    texts = ["# Staff\n- **Dean:** Jane Doe\n- Parking office: Room 101, open 9-5"]
    assert best_answer("where is the parking office", texts) == "Parking office: Room 101, open 9-5"


def test_strips_markdown():
    assert best_answer("who is the dean", ["- **Dean:** Jane Doe"]) == "Dean: Jane Doe"


def test_earlier_document_wins_ties():
    assert best_answer("parking", ["parking A", "parking B"]) == "parking A"


def test_falls_back_to_top_document_when_nothing_matches():
    assert best_answer("zebra", ["First doc text.", "Second"]) == "First doc text."
    assert best_answer("anything", []) == "No relevant information found."


def test_prefers_section_content_over_heading():
    texts = ["## Dean's Office\n- Dean: Jane Doe\n- Assistant to the Dean: Sam Lee"]
    assert best_answer("Who is the dean?", texts) == "Dean: Jane Doe"


def test_answers_differ_by_question_on_real_knowledge_base():
    # The old app returned the dean's line for every question.
    dean = best_answer("Who is the dean?", KB)
    parking = best_answer("How do I request a parking permit?", KB)
    assert dean.startswith("Dean:")
    assert "permit" in parking.lower()
    assert dean != parking

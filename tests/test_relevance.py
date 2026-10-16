from src.trust_layer.relevance import check_relevance, split_question


def test_splits_a_two_part_question():
    q = "What is the risk of EMC interference, and how can it be avoided?"
    assert len(split_question(q)) == 2


def test_does_not_split_a_noun_phrase_conjunction():
    q = "What are the speeds the bridgeport mill can operate in for low and high range?"
    assert len(split_question(q)) == 1, "'low and high range' is not two questions"


def test_splits_on_a_question_mark():
    q = "What is the Run-Stop-Jog-Continue motion? And what are its benefits?"
    assert len(split_question(q)) == 2


def test_on_topic_answer_is_relevant():
    q = "What are the speeds the bridgeport mill can operate in?"
    a = ("The Bridgeport mill operates at 60-500 rpm in low range and "
         "500-4200 rpm in high range.")
    assert check_relevance(q, a).relevant


def test_grounded_but_off_topic_answer_is_not_relevant():
    # The failure Module 3 cannot see: every word of this could be in the
    # retrieved evidence, and it still does not answer the question.
    q = "What are the spindle speed ranges for the mill?"
    a = ("The gear case oil should be changed after the first two months of "
         "normal service and twice a year thereafter.")
    assert not check_relevance(q, a).relevant


def test_answering_only_the_first_half_is_caught():
    # The multi-part signature: one part answered well, the other ignored.
    # The MINIMUM across sub-questions is what must fail, not the mean.
    q = "What are the typical noise limits of the HAAS machine? Is hearing protection required?"
    a = "The HAAS machine produces noise levels of up to 70 dB during normal operation."
    r = check_relevance(q, a)
    assert len(r.per_subquestion) == 2
    first, second = r.per_subquestion
    assert first[1] > second[1], "the answered half should score higher than the ignored half"

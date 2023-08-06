from text_grade import Grade, formulas


def test_flesch_index_pt_br(document):
    score = formulas.flesch_index_pt_br(document)
    assert score.value <= 10
    assert score.grade == Grade.VERY_DIFFICULT

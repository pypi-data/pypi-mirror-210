import pytest

from text_grade import filter


@pytest.mark.parametrize(
    "string, expected",
    [
        ("20/12/2022", True),
        ("20/12/22", True),
        ("20/12/2022", True),
        ("20.12.2022", True),
        ("20 12 2022", False),
        ("20-12-2022", True),
        ("12/2022", True),
        ("12.2022", True),
        ("12 2022", False),
    ],
)
def test_is_date(nlp, string, expected):
    doc = nlp(string)
    assert filter.is_date(doc[0]) == expected


@pytest.mark.parametrize(
    "string, expected",
    [
        ("m", True),
        ("mn", False),
        ("a", False),
        ("e", False),
        ("I", False),
        ("o", False),
        ("U", False),
        ("z", True),
        ("k", True),
        ("kk", False),
    ],
)
def test_is_letter_without_meaning(nlp, string, expected):
    doc = nlp(string)
    assert filter.is_letter_without_meaning(doc[0]) == expected


@pytest.mark.parametrize(
    "string, expected",
    [
        ("m22", True),
        # ("22m", True),
        ("mn30303", True),
        ("30303mn", True),
        ("asdfasa", False),
        ("eadsfasf", False),
        ("I(I", False),
        ("999", False),
    ],
)
def test_have_letter_and_number_together(nlp, string, expected):
    doc = nlp(string)
    assert filter.have_letter_and_number_together(doc[0]) == expected


@pytest.mark.parametrize(
    "string, expected",
    [
        ("alex", False),
        ("alex!", False),
        ("!", True),
        (".!?", True),
        ("@@", True),
        (",.", True),
        ("2,2", False),
        (".^}]", True),
    ],
)
def test_have_only_punct(nlp, string, expected):
    doc = nlp(string)
    assert filter.have_only_punct(doc[0]) == expected


@pytest.mark.parametrize(
    "string, expected",
    [
        ("2-22", True),
        ("2.22", True),
        ("0000.0000", True),
        ("2:2", True),
        ("2?2", True),
        ("222", False),
        ("22 22", False),
        ("22.22.22", True),
    ],
)
def test_has_number_with_punct(nlp, string, expected):
    doc = nlp(string)
    assert filter.has_numbers_with_punct(doc[0])


# @pytest.mark.parametrize(
#     "string, expected",
#     [
#         ("2-22", False),
#         ("2.22", False),
#         ("0000.0000", False),
#         ("2:2", False),
#         ("2?2", False),
#         ("222", False),
#         ("^22", True),
#         ("!22", True),
#         ("$2222", True),
#     ],
# )
# def test_has_punct_with_numbers(nlp, string, expected):
#     doc = nlp(string)
#     assert filter.has_punct_with_numbers(doc[0]) == expected

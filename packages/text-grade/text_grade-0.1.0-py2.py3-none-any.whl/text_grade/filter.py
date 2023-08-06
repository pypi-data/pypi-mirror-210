import re
import string

number_and_letter_together_at_end = re.compile(r"([a-zA-Z]{1,2}[0-9]+)")
number_and_letter_together_at_begin = re.compile(r"([0-9]+[a-zA-Z]{1,2})")
numbers_with_punct = re.compile(r"([0-9]+.?[0-9]+)")
punct_with_numbers = re.compile(r"(\^|\$|!|@|#|%|¨|&|\*|\(|\))[0-9]+")
string_is_date = re.compile(r"((^[0-9]{1,2}.)?([0-9]{1,2}).([0-9]{2,4})$)")


def is_date(token) -> bool:
    if string_is_date.match(token.text):
        return True
    return False


def is_letter_without_meaning(token) -> bool:
    if (
        len(token.text) == 1
        and token.text in "bcdfghjklmnpqrstvwxyzBCDFGHJKLMNPQRSTVWXYZ"
    ):
        return True
    return False


def have_letter_and_number_together(token) -> bool:
    if number_and_letter_together_at_end.match(
        token.text
    ) or number_and_letter_together_at_begin.match(token.text):
        return True
    return False


def have_only_punct(token) -> bool:
    if len({c for c in token.text} - {p for p in string.punctuation}) == 0:
        return True
    return False


def has_numbers_with_punct(token) -> bool:
    if numbers_with_punct.match(token.text):
        return True
    return False


def has_punct_with_numbers(token) -> bool:
    if punct_with_numbers.match(token.text):
        return True
    return False

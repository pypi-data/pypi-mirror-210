from functools import cached_property
from typing import Dict, Generator, List, Optional, Set

import pandas as pd
from pyphen import Pyphen
from spacy.tokens.doc import Doc
from spacy.tokens.span import Span
from spacy.tokens.token import Token

from ._logger import logger
from .filter import (
    has_numbers_with_punct,
    has_punct_with_numbers,
    have_letter_and_number_together,
    have_only_punct,
    is_date,
    is_letter_without_meaning,
)


class Document:
    def __init__(self, doc: Doc) -> None:
        self._doc = doc
        self.tokens: List[Token] = [
            token for token in doc if self._filter_token(token) is not None
        ]
        logger.debug(f"Document language: '{doc.lang_}'")
        self._pyphen = Pyphen(lang=doc.lang_)

    def _filter_token(self, token: Token) -> Optional[Token]:
        if (
            token.is_bracket
            or token.is_currency
            or token.is_digit
            or token.is_punct
            or token.is_quote
            or token.is_space
            or token.like_email
            or token.like_url
            or token.like_num
            or is_date(token)
            or is_letter_without_meaning(token)
            or have_letter_and_number_together(token)
            or have_only_punct(token)
            or has_numbers_with_punct(token)
            or has_punct_with_numbers(token)
        ):
            return None
        return token

    @cached_property
    def sentences(self) -> List[Span]:
        return list(self._doc.sents)

    @cached_property
    def syllables(self) -> int:
        return sum(len(self._pyphen.positions(str(word))) + 1 for word in self.tokens)

    @cached_property
    def words(self) -> List[str]:
        return [t.text for t in self]

    def unique_words(self) -> Set[str]:
        return set(self.words)

    def characters_per_word(self) -> Dict[str, int]:
        return {word: len(word) for word in self.words}

    def characters(self) -> int:
        return sum([n_char for n_char in self.characters_per_word().values()])

    def filter_words_by_length(self, min_word_length: int = 7) -> List[str]:
        return [word for word in self.words if len(word) >= min_word_length]

    def syllables_per_word(self) -> Dict[str, int]:
        return {word: self._pyphen.positions(word.lower()) for word in self.words}

    def to_df(self):
        return pd.DataFrame(
            [
                [
                    self.words,
                    self.sentences,
                    self.syllables,
                    self.unique_words(),
                    len(self.words),
                    len(self.sentences),
                    self.characters(),
                ]
            ],
            columns=[
                "words",
                "sentences",
                "syllables",
                "unique_words",
                "n_words",
                "n_sentences",
                "n_characters",
            ],
        )

    def __len__(self) -> int:
        return len(self.words)

    def __str__(self) -> str:
        return " ".join(t.text for t in self)

    def __iter__(self) -> Generator[Token, None, None]:
        for token in self.tokens:
            yield token

    def __repr__(self) -> str:
        return f"Document(words={len(self.tokens)}, sentences={len(self.sentences)}, syllables={self.syllables})"

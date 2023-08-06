from spacy.tokens.token import Token


def test_sentences(document):
    assert len(document.sentences) == 3


def test_syllables(document):
    assert document.syllables == 204


def test_words(document):
    assert len(document.words) == 80


def test_iter(document):
    for t in document:
        assert isinstance(t, Token)


def test_str(document):
    assert isinstance(str(document), str)


def test_document_repr(document):
    assert repr(document) == "Document(words=80, sentences=3, syllables=204)"

from ._logger import logger
from .document import Document
from .score import Score


def flesch_index_pt_br(document: Document) -> Score:
    """Readability formulas applied to textbooks in brazilian portuguese.

    Reference:
    - http://www.nilc.icmc.usp.br/nilc/download/Reltec28.pdf
    """
    n_words = len(document)
    try:
        index = int(
            248.835
            - (1.015 * n_words / len(document.sentences))
            - (84.6 * document.syllables / n_words)
        )
    except ZeroDivisionError:
        index = -1
    logger.debug(f"Index computed: {index}")
    if index > 100:
        index = 100
    logger.debug(f"Index adjusted: {index}")
    return Score(index)

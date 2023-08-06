[![ci](https://github.com/amenezes/text-grade/actions/workflows/ci.yml/badge.svg)](https://github.com/amenezes/text-grade/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/amenezes/text-grade/branch/master/graph/badge.svg)](https://codecov.io/gh/amenezes/text-grade)
[![PyPI version](https://badge.fury.io/py/text-grade.svg)](https://badge.fury.io/py/text-grade)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/text-grade)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

# text-grade

A Python tool to assist text analysis.

## Usage

```python
import spacy

from text_grade import Document, formulas

TEXTO = """
O algoritmo de Flesch é uma fórmula matemática que é usada para avaliar a legibilidade de um texto em inglês. Ele foi desenvolvido por Rudolf Flesch, um escritor e lexicógrafo austríaco, e é comumente usado por editores, escritores e professores para avaliar a qualidade e a facilidade de leitura de um texto.

A fórmula do algoritmo de Flesch usa duas medidas básicas do texto: o número de palavras e o número de sentenças. Ele também usa o número de sílabas em cada palavra e o número de palavras com duas ou mais sílabas. A partir dessas informações, o algoritmo calcula duas pontuações:

O Índice de Legibilidade de Flesch: esta pontuação varia de 0 a 100 e é baseada no número de palavras e sentenças do texto. Quanto maior a pontuação, mais fácil é o texto de ler.

A Fórmula de Facilidade de Leitura de Flesch: esta pontuação varia de 0 a 100 e é baseada no número de sílabas em cada palavra e no número de palavras com duas ou mais sílabas. Quanto maior a pontuação, mais fácil é o texto de ler.

Para calcular a pontuação do Índice de Legibilidade de Flesch, utiliza-se a seguinte fórmula:

206,835 - (1,015 x número médio de palavras por sentença) - (84,6 x número médio de sílabas por palavra)

Para calcular a pontuação da Fórmula de Facilidade de Leitura de Flesch, utiliza-se a seguinte fórmula:

(0,39 x número médio de palavras por sentença) + (11,8 x número médio de sílabas por palavra) - 15,59

Ambas as pontuações podem ser usadas para avaliar a legibilidade do texto. Em geral, um índice de legibilidade de Flesch de 60 a 70 é considerado fácil de ler para a maioria das pessoas, enquanto uma pontuação de 30 a 50 é considerada difícil. Já a fórmula de facilidade de leitura de Flesch geralmente produz uma pontuação entre 0 e 100, com textos mais fáceis de ler apresentando uma pontuação mais alta.
"""

nlp = spacy.load('pt_core_news_sm')
doc = nlp(TEXTO)
document = Document(doc)

# sentences
print(document.sentences)

# syllables
print(document.syllables)

# words
print(document.words)

score = formulas.flesch_index_pt_br(document)

print(score)
```

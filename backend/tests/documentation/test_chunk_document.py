import pytest

from codinit.documentation.chunk_documents import chunk_document


@pytest.mark.parametrize(
    "document, chunk_size, overlap, expected",
    [
        (
            """This is a test document. This document is used to test the chunk_document function.
            The chunk_document function chunks a given text document into smaller chunks.
            The chunks should overlap with an amount specified by an overlap parameter.
            The function should return a list of chunks, where each chunk is a string."""
            ,
            10,
            2,
            ['This is a ',
             'a test doc',
             'ocument. T',
             ' This docu',
             'cument is ',
             's used to ',
             'o test the',
             'he chunk_d',
             '_document ',
             't function',
             'on.\n      ',
             '        Th',
             'The chunk_',
             'k_document',
             'nt functio',
             'ion chunks',
             'ks a given',
             'en text do',
             'document i',
             ' into smal',
             'aller chun',
             'unks.\n    ',
             '          ',
             '  The chun',
             'unks shoul',
             'uld overla',
             'lap with a',
             ' an amount',
             'nt specifi',
             'fied by an',
             'an overlap',
             'ap paramet',
             'eter.\n    ',
             '          ',
             '  The func',
             'nction sho',
             'hould retu',
             'turn a lis',
             'ist of chu',
             'hunks, whe',
             'here each ',
             'h chunk is',
             'is a strin',
             'ing.'],
        ),
        (
            "",
            10,
            2,
            [],
        ),
        (
            "a",
            10,
            2,
            ["a"],
        ),
        (
            "This is a test document.",
            10,
            2,
            ["This is a ", "a test doc", "ocument."],
        ),
    ],
)
def test_chunk_document(document, chunk_size, overlap, expected):
    chunks = chunk_document(document, chunk_size, overlap)
    assert chunks == expected


def test_chunk_document_invalid_chunk_size():
    with pytest.raises(ValueError):
        chunk_document("This is a test document.", 0, 2)


def test_chunk_document_with_invalid_overlap():
    with pytest.raises(ValueError):
        chunk_document("This is a test document.", 10, -1)

def test_chunk_document_with_nan_value():
    with pytest.raises(TypeError):
        chunk_document(None, 10, 2)

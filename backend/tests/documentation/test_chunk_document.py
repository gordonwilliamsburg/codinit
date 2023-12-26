import pytest

from codinit.documentation.chunk_documents import chunk_document


@pytest.mark.parametrize(
    "document, chunk_size, overlap, expected",
    [
        (
            """This is a test document. This document is used to test the chunk_document function.
            The chunk_document function chunks a given text document into smaller chunks.
            The chunks should overlap with an amount specified by an overlap parameter.
            The function should return a list of chunks, where each chunk is a string.""",
            10,
            2,
            [
                "This is a ",
                "a test doc",
                "ocument. T",
                " This docu",
                "cument is ",
                "s used to ",
                "o test the",
                "he chunk_d",
                "_document ",
                "t function",
                "on. \n     ",
                "         T",
                " The chunk",
                "nk_documen",
                "ent functi",
                "tion chunk",
                "nks a give",
                "ven text d",
                " document ",
                "t into sma",
                "maller chu",
                "hunks. \n  ",
                "          ",
                "    The ch",
                "chunks sho",
                "hould over",
                "erlap with",
                "th an amou",
                "ount speci",
                "cified by ",
                "y an overl",
                "rlap param",
                "ameter. \n ",
                "\n         ",
                "     The f",
                " function ",
                "n should r",
                " return a ",
                "a list of ",
                "f chunks, ",
                ", where ea",
                "each chunk",
                "nk is a st",
                "string.",
            ],
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

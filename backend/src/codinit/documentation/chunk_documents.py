# import the necessary libraries
from typing import List

# Create a function that chunks a given text document given as a string according to a chunk size
# The chunks should overlap with an amount specified by an overlap parameter


def chunk_document(document: str, chunk_size: int, overlap: int = 0) -> List[str]:
    """
    Chunks a given text document into smaller chunks.

    Args:
        document: The text document to chunk.
        chunk_size: The size of each chunk.
        overlap: The amount of overlap between each chunk.

    Returns:
        A list of chunks, where each chunk is a string.
    """

    # Check if the chunk size is valid.
    if chunk_size <= 0:
        raise ValueError("Chunk size must be positive.")

    # Check if the overlap is valid.
    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("Overlap must be between 0 and chunk size - 1.")

    # Create a list to store the chunks.
    chunks = []

    # Iterate over the document in chunks.
    for i in range(0, len(document), chunk_size - overlap):
        # Add the chunk to the list.
        chunks.append(document[i : i + chunk_size])

    # Return the list of chunks.
    return chunks


# test the function
if __name__ == "__main__":
    document = """This is a test document. This document is used to test the chunk_document function.
            The chunk_document function chunks a given text document into smaller chunks.
            The chunks should overlap with an amount specified by an overlap parameter.
            The function should return a list of chunks, where each chunk is a string."""
    chunks = chunk_document(document, 10, 2)
    print(chunks)

# --------------------------------------------------
# Document Processing Tests
# --------------------------------------------------

def test_document_processing_modules_import():

    from graph.nodes import (
        parse_document,
        extract_text_from_pdf,
        extract_text_from_docx,
        extract_text_from_image,
        extract_text_from_odt
    )

    assert parse_document is not None
    assert extract_text_from_pdf is not None
    assert extract_text_from_docx is not None
    assert extract_text_from_image is not None
    assert extract_text_from_odt is not None
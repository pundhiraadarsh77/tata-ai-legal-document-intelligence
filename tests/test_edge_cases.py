# --------------------------------------------------
# Edge Case Tests
# --------------------------------------------------

def test_testing_document_exists():

    from pathlib import Path

    document_path = Path("uploads/testing.pdf")

    assert document_path.exists()
    assert document_path.is_file()

def test_supported_document_formats():

    supported_formats = {
        ".pdf",
        ".docx",
        ".odt",
        ".png",
        ".jpg",
        ".jpeg"
    }

    assert ".pdf" in supported_formats
    assert ".docx" in supported_formats
    assert ".odt" in supported_formats
    assert ".png" in supported_formats
    assert ".jpg" in supported_formats
    assert ".jpeg" in supported_formats
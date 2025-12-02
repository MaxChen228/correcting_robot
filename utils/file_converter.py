"""
File Converter Utilities
PDF to Image conversion
"""
from typing import List
from PIL import Image

try:
    from pdf2image import convert_from_bytes
    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False


def is_pdf_supported() -> bool:
    """Check if PDF conversion is supported"""
    return PDF_SUPPORT


def convert_pdf_to_images(pdf_bytes: bytes, dpi: int = 200) -> List[Image.Image]:
    """
    Convert PDF to list of images

    Args:
        pdf_bytes: PDF file content as bytes
        dpi: Resolution for conversion (default: 200 for balanced speed/quality)

    Returns:
        List of PIL Images (one per page)

    Raises:
        RuntimeError: If pdf2image is not installed
        Exception: If PDF conversion fails
    """
    if not PDF_SUPPORT:
        raise RuntimeError("pdf2image is not installed")

    try:
        images = convert_from_bytes(
            pdf_bytes,
            dpi=dpi,
            fmt='png'
        )
        return images
    except Exception as e:
        raise Exception(f"PDF conversion failed: {str(e)}")


def convert_file_to_images(uploaded_file) -> List[Image.Image]:
    """
    Convert uploaded file (PDF or image) to list of images

    Args:
        uploaded_file: Streamlit uploaded file object

    Returns:
        List of PIL Images

    Raises:
        ValueError: If file type is not supported or PDF support is missing
    """
    file_type = uploaded_file.type.split('/')[-1].lower()

    if file_type == 'pdf':
        if not PDF_SUPPORT:
            raise ValueError("PDF not supported. Please install pdf2image")
        pdf_bytes = uploaded_file.read()
        return convert_pdf_to_images(pdf_bytes)

    elif file_type in ['png', 'jpg', 'jpeg']:
        return [Image.open(uploaded_file)]

    else:
        raise ValueError(f"Unsupported file type: {file_type}")


def convert_files_to_images(uploaded_files) -> List[Image.Image]:
    """
    Convert multiple files to list of images (PDF pages are expanded)

    Args:
        uploaded_files: List of Streamlit uploaded file objects

    Returns:
        Flattened list of PIL Images (all pages from all files)
    """
    all_images = []
    for uploaded_file in uploaded_files:
        images = convert_file_to_images(uploaded_file)
        all_images.extend(images)
    return all_images

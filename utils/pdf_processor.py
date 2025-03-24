import PyPDF2
import io
import re
from PIL import Image
import pytesseract
from pdf2image import convert_from_bytes
from models.text_analyzer import summarize_text, extract_key_points

def process_pdf(file, options):
    """
    Process a PDF file to extract text, images, and analyze content
    
    Args:
        file: The uploaded PDF file
        options: Dictionary of analysis options
    
    Returns:
        Dict containing analysis results
    """
    # Read file content
    pdf_bytes = file.getvalue()
    
    # Extract text from PDF
    text_content = extract_text_from_pdf(pdf_bytes)
    
    # Extract images if option is selected
    images = []
    if options.get('extract_images', False):
        images = extract_images_from_pdf(pdf_bytes)
    
    # Generate summary if option is selected
    summary = ""
    if options.get('generate_summary', True):
        summary = summarize_text(text_content)
    
    # Extract key points if option is selected
    key_points = []
    if options.get('extract_key_points', True):
        key_points = extract_key_points(text_content)
    
    # Return all results
    return {
        'file_type': 'pdf',
        'text_content': text_content,
        'summary': summary,
        'key_points': key_points,
        'images': images,
        'page_count': get_page_count(pdf_bytes)
    }

def extract_text_from_pdf(pdf_bytes):
    """Extract text content from PDF bytes"""
    text = ""
    try:
        with io.BytesIO(pdf_bytes) as pdf_file:
            reader = PyPDF2.PdfReader(pdf_file)
            for page_num in range(len(reader.pages)):
                page = reader.pages[page_num]
                text += page.extract_text() + "\n\n"
        
        # Clean up text
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        
        return text
    except Exception as e:
        return f"Error extracting text: {str(e)}"

def extract_images_from_pdf(pdf_bytes):
    """Extract images from PDF using pdf2image and pytesseract"""
    images = []
    try:
        # Convert PDF pages to images
        pages = convert_from_bytes(pdf_bytes, dpi=300)
        
        for i, page in enumerate(pages):
            # Save each page as an image
            img_byte_arr = io.BytesIO()
            page.save(img_byte_arr, format='PNG')
            img_byte_arr.seek(0)
            
            # Process with OCR if needed
            # text_from_image = pytesseract.image_to_string(page)
            
            images.append({
                'page_num': i+1,
                'image': img_byte_arr,
            })
    except Exception as e:
        pass
    
    return images

def get_page_count(pdf_bytes):
    """Get the number of pages in the PDF"""
    try:
        with io.BytesIO(pdf_bytes) as pdf_file:
            reader = PyPDF2.PdfReader(pdf_file)
            return len(reader.pages)
    except:
        return 0
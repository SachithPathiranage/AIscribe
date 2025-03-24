import io
from PIL import Image
import numpy as np
from utils.gemini_integration import GeminiIntegration

def process_image(file, options):
    """
    Process an image file to analyze content
    
    Args:
        file: The uploaded image file
        options: Dictionary of analysis options
    
    Returns:
        Dict containing analysis results
    """
    # Initialize Gemini
    gemini = GeminiIntegration()
    
    # Read image
    image_bytes = file.getvalue()
    image = Image.open(io.BytesIO(image_bytes))
    
    # Convert to RGB if needed
    if image.mode != "RGB":
        image = image.convert("RGB")
    
    # Get image details
    width, height = image.size
    format_type = image.format
    
    # Initialize results
    results = {
        'file_type': 'image',
        'width': width,
        'height': height,
        'format': format_type,
        'description': '',
        'objects': [],
        'text_content': '',
        'detailed_analysis': '',
    }
    
    # Use Gemini for enhanced analysis if available
    if gemini.is_available():
        # Generate general description
        if options.get('generate_description', True):
            results['description'] = gemini.analyze_image(image, "general")
            
        # Generate detailed analysis if requested
        if options.get('detailed_analysis', True):
            results['detailed_analysis'] = gemini.analyze_image(image, "detailed")
        
        # Detect objects in image
        if options.get('detect_objects', True):
            # Use structured object extraction
            results['objects'] = gemini.extract_objects_from_image(image)
        
        # Extract text from image (OCR)
        if options.get('extract_text', True):
            results['text_content'] = gemini.analyze_image(image, "text")
            
    else:
        # Fallback to standard models
        from models.vision_model import analyze_image, detect_objects, extract_image_text
        
        # Analyze image content
        if options.get('generate_description', True):
            results['description'] = analyze_image(image)
        
        # Detect objects in image
        if options.get('detect_objects', True):
            results['objects'] = detect_objects(image)
        
        # Extract text from image (OCR)
        if options.get('extract_text', True):
            results['text_content'] = extract_image_text(image)
    
    return results
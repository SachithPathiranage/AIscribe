# Add this to your imports
from utils.office_processor import process_office_file
from utils.config import Config
import os
from utils.image_processor import process_image
from utils.video_processor import process_video
from utils.audio_processor import process_audio
from utils.pdf_processor import process_pdf
from utils.file_processor import process_file

def process_file(file, options):
    """
    Process an uploaded file based on its type
    
    Args:
        file: The uploaded file
        options: Dictionary of analysis options
    
    Returns:
        Dict containing analysis results
    """
    # Get file name and extension
    file_name = file.name
    file_extension = os.path.splitext(file_name)[1].lower()
    
    # Process based on file type
    try:
        # Check file size
        config = Config()
        max_size = config.max_file_size_mb * 1024 * 1024  # Convert MB to bytes
        if file.size > max_size:
            return {
                'file_name': file_name,
                'error': f"File size exceeds maximum allowed size of {config.max_file_size_mb}MB"
            }
        
        # Process by file extension
        if file_extension in ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp']:
            return process_image(file, options)
        elif file_extension in ['.mp4', '.mov', '.avi', '.webm', '.mkv']:
            return process_video(file, options)
        elif file_extension in ['.mp3', '.wav', '.ogg', '.m4a', '.flac']:
            return process_audio(file, options)
        elif file_extension in ['.txt', '.md', '.html', '.csv', '.json', '.xml']:
            return process_file(file, options)
        elif file_extension in ['.pdf']:
            return process_pdf(file, options)
        # Add Office file formats
        elif file_extension in ['.docx', '.doc', '.xlsx', '.xls', '.pptx', '.ppt']:
            return process_office_file(file, options)
        else:
            return {
                'file_name': file_name,
                'error': f"Unsupported file format: {file_extension}"
            }
    except Exception as e:
        return {
            'file_name': file_name,
            'error': f"Error processing file: {str(e)}"
        }
import streamlit as st

def render_sidebar():
    """
    Render the sidebar with analysis options
    
    Returns:
        Dict containing selected options
    """
    st.sidebar.title("Analysis Options")
    
    # General options
    st.sidebar.header("General Options")
    generate_summary = st.sidebar.checkbox("Generate Summary", value=True)
    extract_key_points = st.sidebar.checkbox("Extract Key Points", value=True)
    
    # PDF-specific options
    st.sidebar.header("PDF Options")
    extract_images_from_pdf = st.sidebar.checkbox("Extract Images from PDFs", value=True)
    
    # Image-specific options
    st.sidebar.header("Image Options")
    generate_description = st.sidebar.checkbox("Generate Image Description", value=True)
    detect_objects = st.sidebar.checkbox("Detect Objects in Images", value=True)
    extract_text = st.sidebar.checkbox("Extract Text from Images (OCR)", value=True)
    
    # Video-specific options
    st.sidebar.header("Video Options")
    analyze_video_frames = st.sidebar.checkbox("Analyze Video Frames", value=True)
    generate_video_summary = st.sidebar.checkbox("Generate Video Summary", value=True)
    extract_audio = st.sidebar.checkbox("Extract Audio from Video", value=True)
    
    # Audio-specific options
    st.sidebar.header("Audio Options")
    transcribe_audio = st.sidebar.checkbox("Transcribe Audio", value=True)
    detect_speakers = st.sidebar.checkbox("Detect Multiple Speakers", value=False)
    
    st.sidebar.header("AI Model Selection")
    ai_model = st.sidebar.selectbox(
        "Choose AI Model",
        ["Gemini", "ChatGPT", "Basic (No AI)"]
    )

    text_model_options = {
        "Gemini": ["Gemini Pro"],
        "ChatGPT": ["GPT-4", "GPT-3.5-Turbo"],
        "Basic (No AI)": ["Rule-based", "Simple Extraction"]
    }

    vision_model_options = {
        "Gemini": ["Gemini Pro Vision"],
        "ChatGPT": ["GPT-4 Vision"],
        "Basic (No AI)": ["Rule-based", "Template Matching"]
    }

    text_model = st.sidebar.selectbox(
        "Text Analysis Model",
        text_model_options[ai_model]
    )

    vision_model = st.sidebar.selectbox(
        "Vision Model",
        vision_model_options[ai_model]
    )
    
    # About section
    st.sidebar.header("About")
    st.sidebar.info(
        "This application analyzes various file types and provides insights using "
        "AI models. Upload your files and customize analysis options as needed."
    )
    
    # Return all options as a dictionary
    return {
        'generate_summary': generate_summary,
        'extract_key_points': extract_key_points,
        'extract_images_from_pdf': extract_images_from_pdf,
        'generate_description': generate_description,
        'detect_objects': detect_objects,
        'extract_text': extract_text,
        'analyze_video_frames': analyze_video_frames,
        'generate_video_summary': generate_video_summary,
        'extract_audio': extract_audio,
        'transcribe_audio': transcribe_audio,
        'detect_speakers': detect_speakers,
        'text_model': text_model,
        'vision_model': vision_model
    }
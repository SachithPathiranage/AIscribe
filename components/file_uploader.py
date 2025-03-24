import streamlit as st

def render_file_uploader():
    """
    Render the file upload component
    
    Returns:
        List of uploaded files
    """
    st.subheader("Upload Files")
    
    uploaded_files = st.file_uploader(
        "Upload PDF, image, video, or audio files",
        type=["pdf", "png", "jpg", "jpeg", "mp4", "avi", "mov", "mp3", "wav", "ogg", "m4a"],
        accept_multiple_files=True
    )
    
    # If files are uploaded, display info about them
    if uploaded_files:
        st.success(f"{len(uploaded_files)} file(s) uploaded successfully")
        
        # Display basic info about uploaded files
        st.subheader("Uploaded Files")
        file_info = []
        
        for file in uploaded_files:
            # Get file extension
            file_ext = file.name.split('.')[-1].lower()
            
            # Determine file type
            file_type = ""
            if file_ext in ['pdf']:
                file_type = "PDF"
            elif file_ext in ['jpg', 'jpeg', 'png', 'gif']:
                file_type = "Image"
            elif file_ext in ['mp4', 'avi', 'mov', 'mkv']:
                file_type = "Video"
            elif file_ext in ['mp3', 'wav', 'ogg', 'm4a']:
                file_type = "Audio"
            
            # Add to file info
            file_info.append({
                "name": file.name,
                "type": file_type,
                "size": f"{file.size / 1024:.1f} KB"
            })
        
        # Display file info in a table
        st.table(file_info)
    
    return uploaded_files
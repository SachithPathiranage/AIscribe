import streamlit as st
from components.sidebar import render_sidebar
from components.file_uploader import render_file_uploader
from components.result_display import render_results
from utils.file_database import FileDatabase
from utils.gemini_integration import GeminiIntegration
import os

# Set page configuration
st.set_page_config(
    page_title="Multimodal Content Analyzer",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize session state
if 'processed_files' not in st.session_state:
    st.session_state.processed_files = {}
if 'current_file_id' not in st.session_state:
    st.session_state.current_file_id = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

def main():
    # Initialize database and ChatGPT integration
    db = FileDatabase()
    chatgpt = GeminiIntegration()
    
    # Apply custom CSS
    with open("styles/style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    
    # Page title
    st.title("Multimodal Content Analysis Chatbot")
    st.markdown("""
    Upload files (PDF, images, videos, audio) to analyze, summarize, and visualize their content.
    """)
    
    # Render sidebar with options
    analysis_options = render_sidebar()
    
    # Create tabs for different app sections
    tab_upload, tab_history, tab_chat = st.tabs(["Upload & Analyze", "File History", "Chat"])
    
    with tab_upload:
        # File uploader component
        uploaded_files = render_file_uploader()
        
        # Process files and display results when files are uploaded
        if uploaded_files:
            with st.spinner("Processing your files... This might take a moment."):
                results = process_files(uploaded_files, analysis_options)
                
                # Save results to database
                for file_name, result in results.items():
                    file_content = next((f.getvalue() for f in uploaded_files if f.name == file_name), None)
                    if file_content:
                        file_id = db.save_file_results(file_name, file_content, result)
                        st.session_state.current_file_id = file_id
                        st.session_state.processed_files[file_id] = {
                            "file_name": file_name,
                            "results": result
                        }
            
            # Display results
            render_results(results)
    
    with tab_history:
        st.subheader("Previously Processed Files")
        
        # List processed files
        files = db.list_files()
        
        if not files:
            st.info("No files have been processed yet. Upload files in the 'Upload & Analyze' tab.")
        else:
            # Create a dataframe for display
            import pandas as pd
            from datetime import datetime
            
            file_data = []
            for file in files:
                processed_time = datetime.fromisoformat(file["processed_at"])
                file_data.append({
                    "File Name": file["file_name"],
                    "Type": file["file_type"].upper(),
                    "Processed": processed_time.strftime("%Y-%m-%d %H:%M"),
                    "ID": file["file_id"]
                })
            
            df = pd.DataFrame(file_data)
            
            # Create a selection mechanism
            selected_file = st.selectbox(
                "Select a file to view its results",
                options=df["File Name"].tolist(),
                format_func=lambda x: x
            )
            
            if selected_file:
                selected_id = df[df["File Name"] == selected_file]["ID"].values[0]
                
                # Load results from database if not in session state
                if selected_id not in st.session_state.processed_files:
                    results = db.get_file_results(selected_id)
                    if results:
                        st.session_state.processed_files[selected_id] = {
                            "file_name": selected_file,
                            "results": results
                        }
                        st.session_state.current_file_id = selected_id
                else:
                    results = st.session_state.processed_files[selected_id]["results"]
                
                # Display results
                if results:
                    render_results({selected_file: results})
                    
                    # Set as current file for chat
                    if st.button("Use this file for chat"):
                        st.session_state.current_file_id = selected_id
                        st.success(f"Using {selected_file} for chat. Switch to the Chat tab.")
                else:
                    st.error("Could not load results for this file.")
    
    with tab_chat:
        st.subheader("Chat with your documents")
        
        # Check if there is a current file
        if st.session_state.current_file_id is None:
            st.info("Please upload a file or select one from the history to start chatting.")
        else:
            current_file = st.session_state.processed_files[st.session_state.current_file_id]
            
            st.markdown(f"**Currently chatting with:** {current_file['file_name']}")
            
            # Display chat history
            for message in st.session_state.chat_history:
                if message["role"] == "user":
                    st.markdown(f"**You:** {message['content']}")
                else:
                    st.markdown(f"**Assistant:** {message['content']}")
            
            # Chat input
            user_question = st.text_input("Ask a question about your document:")
            
            if user_question:
                # Add user message to chat history
                st.session_state.chat_history.append({
                    "role": "user",
                    "content": user_question
                })
                
                with st.spinner("Thinking..."):
                    # Generate answer
                    answer = generate_answer(
                        user_question, 
                        current_file["results"], 
                        chatgpt if chatgpt.is_available() else None
                    )
                    
                    # Add assistant message to chat history
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": answer
                    })
                
                # Force a rerun to display the new messages
                st.rerun()
            
            # Clear chat button
            if st.button("Clear Chat History"):
                st.session_state.chat_history = []
                st.rerun()

def process_files(files, options):
    """Process uploaded files according to their type and selected options"""
    results = {}
    
    for file in files:
        file_type = determine_file_type(file)
        
        if file_type == "pdf":
            from utils.pdf_processor import process_pdf
            results[file.name] = process_pdf(file, options)
        elif file_type == "image":
            from utils.image_processor import process_image
            results[file.name] = process_image(file, options)
        elif file_type == "video":
            from utils.video_processor import process_video
            results[file.name] = process_video(file, options)
        elif file_type == "audio":
            from utils.audio_processor import process_audio
            results[file.name] = process_audio(file, options)
    
    return results

def determine_file_type(file):
    """Determine file type based on file extension"""
    ext = file.name.split('.')[-1].lower()
    
    if ext in ['pdf']:
        return "pdf"
    elif ext in ['jpg', 'jpeg', 'png', 'gif']:
        return "image"
    elif ext in ['mp4', 'avi', 'mov', 'mkv']:
        return "video"
    elif ext in ['mp3', 'wav', 'ogg', 'm4a']:
        return "audio"
    else:
        return "unknown"

def generate_answer(question, file_results, ai_model=None):
    """Generate an answer to a question about the uploaded content"""
    file_type = file_results.get('file_type', 'unknown')
    
    # Gather context based on file type
    context = ""
    
    if file_type == 'pdf':
        # Use text content and summary
        context += file_results.get('text_content', '')
        context += "\n\n" + file_results.get('summary', '')
    
    elif file_type == 'image':
        # Use image description and detected objects
        context += file_results.get('description', '')
        context += "\n\nDetected objects: "
        context += ", ".join([f"{obj['label']} ({obj['confidence']:.2f})" 
                             for obj in file_results.get('objects', [])])
        context += "\n\n" + file_results.get('text_content', '')
    
    elif file_type == 'video':
        # Use video summary, frame descriptions, and transcript
        context += file_results.get('summary', '')
        
        # Add frame descriptions
        for frame in file_results.get('key_frames', []):
            context += f"\nFrame at {frame.get('time', 0):.2f}s: {frame.get('description', '')}"
        
        # Add transcript
        context += "\n\nTranscript: " + file_results.get('transcript', '')
    
    elif file_type == 'audio':
        # Use audio transcript
        context += file_results.get('transcript', '')
    
    # Limit context size
    if len(context) > 4000:
        context = context[:4000] + "..."
    
    # Use AI model if available
    if ai_model and ai_model.is_available():
        # Check which type of model it is
        if isinstance(ai_model, GeminiIntegration):
            return ai_model.answer_question(question, context)
        else:  # Assume ChatGPT
            return ai_model.answer_question(question, context)
    else:
        # Basic fallback if no AI model is available
        return f"Based on the {file_type} you've uploaded, I can provide a basic response. For more advanced question answering, please configure either Gemini or ChatGPT integration.\n\nTo answer your question: '{question}', here's what I can tell from the content analysis:\n\n[This would be a more comprehensive answer with AI integration]"

if __name__ == "__main__":
    # Create directories if they don't exist
    os.makedirs("styles", exist_ok=True)
    os.makedirs("data", exist_ok=True)
    
    # Create CSS file if it doesn't exist
    if not os.path.exists("styles/style.css"):
        with open("styles/style.css", "w") as f:
            f.write("""
            .stApp {
                max-width: 1200px;
                margin: 0 auto;
            }
            .result-container {
                padding: 1rem;
                border-radius: 0.5rem;
                background-color: #f8f9fa;
                margin-bottom: 1rem;
            }
            .chat-user-message {
                background-color: #E1F5FE;
                padding: 0.8rem;
                border-radius: 0.8rem;
                margin-bottom: 0.8rem;
                max-width: 80%;
                align-self: flex-end;
            }
            .chat-assistant-message {
                background-color: #F5F5F5;
                padding: 0.8rem;
                border-radius: 0.8rem;
                margin-bottom: 0.8rem;
                max-width: 80%;
                align-self: flex-start;
            }
            """)
    
    main()
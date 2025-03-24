# AIscribe: Multimodal Content Analysis System

![AIscribe](https://github.com/SachithPathiranage/AIscribe/blob/main/assets/video_analyzing.png)
![AIscribe](https://github.com/SachithPathiranage/AIscribe/blob/main/assets/video_analyzing_2%20.png)
![AIscribe](https://github.com/SachithPathiranage/AIscribe/blob/main/assets/image_analyzing.png)
![AIscribe](https://github.com/SachithPathiranage/AIscribe/blob/main/assets/image_analyzing_2.png)
![AIscribe](https://github.com/SachithPathiranage/AIscribe/blob/main/assets/audio_analyzing_2.png)

AIscribe is a comprehensive content analysis system that leverages AI to extract insights from multiple types of media. It processes and analyzes images, audio, videos, documents, and more, providing intelligent summaries, transcriptions, sentiment analysis, and key information extraction.

## Features

- **Multi-format Analysis**: Process a wide range of file formats including images, videos, audio, text documents, PDFs, and Office files
- **Smart Summarization**: Generate concise summaries of content regardless of the source format
- **Speech Recognition**: Transcribe spoken content from audio and video files
- **Sentiment Analysis**: Determine emotional tone and sentiment in text and speech
- **Visual Content Analysis**: Identify objects, people, scenes, and text in images and video frames
- **Document Structure Analysis**: Extract and analyze the structure of documents, presentations, and spreadsheets
- **Interactive UI**: Clean Streamlit interface for uploading, processing, and viewing results
- **Batch Processing**: Analyze multiple files simultaneously
- **Analysis History**: Save and review previous analysis results

## Installation

### Prerequisites

- Python 3.8 or higher
- Pip package manager

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/SachithPathiranage/AIscribe.git
   cd multimodal-chatbot
   ```

2. Create and activate a virtual environment (recommended):
   ```bash
   python -m venv .venv
   # On Windows
   .\.venv\Scripts\activate
   # On macOS/Linux
   source .venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the project root directory and add your API keys:
   ```
   GOOGLE_API_KEY=your_gemini_api_key_here
   OPENAI_API_KEY=your_openai_api_key_here
   GEMINI_MODEL=gemini-1.5-flash
   ```

## Usage

1. Start the application:
   ```bash
   streamlit run app.py
   ```

2. Open your web browser and go to `http://localhost:8501`

3. Upload files for analysis using the file uploader

4. Configure analysis options in the sidebar

5. View detailed analysis results

## Supported File Types

### Images
- JPG/JPEG, PNG, GIF, WebP, BMP

### Video
- MP4, MOV, AVI, WebM, MKV

### Audio
- MP3, WAV, OGG, M4A, FLAC

### Documents
- TXT, MD, HTML, CSV, JSON, XML, PDF

### Office Files
- Word (DOCX, DOC)
- Excel (XLSX, XLS)
- PowerPoint (PPTX, PPT)

## Technologies Used

- **Python**: Core programming language
- **Streamlit**: Web application framework
- **Google Generative AI (Gemini)**: AI model for content analysis
- **OpenCV**: Image and video processing
- **Librosa**: Audio analysis
- **PyPDF2**: PDF processing
- **python-docx, openpyxl, python-pptx**: Office file processing
- **Pandas**: Data manipulation
- **Matplotlib/Altair**: Data visualization

## Project Structure

```
multimodal-chatbot/
├── app.py                   # Main application entry point
├── utils/                   # Utility modules
│   ├── config.py            # Configuration handling
│   ├── file_processor.py    # Main file processing logic
│   ├── image_processor.py   # Image processing functions
│   ├── video_processor.py   # Video processing functions
│   ├── audio_processor.py   # Audio processing functions
│   ├── text_processor.py    # Text processing functions
│   ├── pdf_processor.py     # PDF processing functions
│   ├── office_processor.py  # Office file processing functions
│   └── gemini_integration.py # Gemini API integration
├── models/                  # AI model integrations
│   ├── vision_model.py      # Image analysis models
│   ├── speech_model.py      # Speech processing models
│   └── text_analyzer.py     # Text analysis models
├── components/              # UI components
│   ├── sidebar.py           # Sidebar UI elements
│   └── result_display.py    # Result display components
├── data/                    # Data storage
│   └── analysis_history.json # Saved analysis results
├── .env                     # Environment variables (not in repo)
├── .env.template            # Template for environment variables
├── requirements.txt         # Project dependencies
└── README.md                # Project documentation
```

## Configuration

AIscribe can be configured through environment variables in the `.env` file:

```
# API Keys
GOOGLE_API_KEY=your_gemini_api_key_here
OPENAI_API_KEY=your_openai_api_key_here

# Application Configuration
DEBUG=false
MAX_FILE_SIZE_MB=50
ENABLE_CACHING=true
CACHE_TTL_MINUTES=60

# Gemini API Settings
GEMINI_MODEL=gemini-1.5-flash
GEMINI_TEMPERATURE=0.2
GEMINI_TOP_P=0.95
GEMINI_TOP_K=40
GEMINI_MAX_TOKENS=2048

# Image Processing Settings
ENHANCE_IMAGE_CONTRAST=true
ENHANCE_IMAGE_SHARPNESS=true
MAX_IMAGE_DIMENSION=1024

# Video Processing Settings
VIDEO_FRAME_EXTRACTION=advanced
MAX_VIDEO_FRAMES=7
SCENE_DETECTION_THRESHOLD=30.0
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- [Streamlit](https://streamlit.io/)
- [Google Generative AI](https://ai.google.dev/)
- [OpenCV](https://opencv.org/)
- [Librosa](https://librosa.org/)

---

Created by Sachith Pathiranage © 2025
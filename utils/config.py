import os
from dotenv import load_dotenv
from typing import Dict, Any, Optional

class Config:
    """Configuration manager for the application"""
    
    _instance = None
    _loaded = False
    
    def __new__(cls):
        """Singleton pattern to ensure Config is loaded only once"""
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            cls._instance._load_config()
        return cls._instance
    
    def _load_config(self):
        """Load configuration from .env file and environment variables"""
        if self._loaded:
            return
            
        # Load .env file if exists
        if os.path.exists('../.env'):
            load_dotenv('../.env')
        else:
            print("Warning: .env file not found. Using environment variables.")
        
        # API Keys
        self.google_api_key = os.getenv('GOOGLE_API_KEY')
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        
        # Application Settings
        self.debug = os.getenv('DEBUG', 'false').lower() == 'true'
        self.max_file_size_mb = int(os.getenv('MAX_FILE_SIZE_MB', '50'))
        self.enable_caching = os.getenv('ENABLE_CACHING', 'true').lower() == 'true'
        self.cache_ttl_minutes = int(os.getenv('CACHE_TTL_MINUTES', '60'))
        
        # Gemini API Settings
        self.gemini_temperature = float(os.getenv('GEMINI_TEMPERATURE', '0.2'))
        self.gemini_top_p = float(os.getenv('GEMINI_TOP_P', '0.95'))
        self.gemini_top_k = int(os.getenv('GEMINI_TOP_K', '40'))
        self.gemini_max_tokens = int(os.getenv('GEMINI_MAX_TOKENS', '2048'))
        
        # Image Processing Settings
        self.enhance_image_contrast = os.getenv('ENHANCE_IMAGE_CONTRAST', 'true').lower() == 'true'
        self.enhance_image_sharpness = os.getenv('ENHANCE_IMAGE_SHARPNESS', 'true').lower() == 'true'
        self.max_image_dimension = int(os.getenv('MAX_IMAGE_DIMENSION', '1024'))
        
        # Video Processing Settings
        self.video_frame_extraction_method = os.getenv('VIDEO_FRAME_EXTRACTION', 'smart')  # 'smart', 'uniform', or 'keyframe'
        self.max_video_frames = int(os.getenv('MAX_VIDEO_FRAMES', '7'))
        self.scene_detection_threshold = float(os.getenv('SCENE_DETECTION_THRESHOLD', '30.0'))
        
        self._loaded = True
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value by key"""
        return getattr(self, key, default)
    
    def has_google_api_key(self) -> bool:
        """Check if Google API key is configured"""
        return bool(self.google_api_key)
    
    def has_openai_api_key(self) -> bool:
        """Check if OpenAI API key is configured"""
        return bool(self.openai_api_key)
    
    def to_dict(self, include_secrets: bool = False) -> Dict[str, Any]:
        """Convert config to dictionary"""
        result = {}
        
        # Add all attributes except private ones
        for key, value in self.__dict__.items():
            if not key.startswith('_'):
                # Skip API keys if including secrets is false
                if not include_secrets and key in ['google_api_key', 'openai_api_key']:
                    result[key] = '[REDACTED]' if value else None
                else:
                    result[key] = value
                    
        return result
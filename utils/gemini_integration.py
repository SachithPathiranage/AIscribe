import google.generativeai as genai
from typing import List, Dict, Any, Optional, Union
from PIL import Image
import base64
import io
import time
from utils.config import Config

class GeminiIntegration:
    """Integration with Google's Gemini API for multimodal analysis"""
    
    def __init__(self):
        """Initialize Gemini API integration"""
        # Load config
        config = Config()
        self.api_key = config.google_api_key
        
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.available = True
            
            # Initialize models with the newer Gemini 1.5 models
            self.text_model = genai.GenerativeModel(
                'gemini-1.5-flash',  # Updated to newer model
                generation_config=genai.GenerationConfig(
                    temperature=0.2,
                    top_p=0.95,
                    top_k=40,
                    max_output_tokens=2048,
                )
            )
            
            # Use the same model for vision as Gemini 1.5 supports multimodal inputs
            self.vision_model = genai.GenerativeModel(
                'gemini-1.5-flash',  # Updated to newer model
                generation_config=genai.GenerationConfig(
                    temperature=0.2,
                    top_p=0.95,
                    top_k=40,
                    max_output_tokens=2048,
                )
            )
        else:
            self.available = False
    
    def is_available(self) -> bool:
        """Check if Gemini API integration is available"""
        return self.available
    
    def analyze_text(self, content: str, task: str) -> str:
        """
        Analyze text content using Gemini Pro
        
        Args:
            content: The text content to analyze
            task: The analysis task to perform (summarize, extract_key_points, etc.)
        
        Returns:
            Gemini's response
        """
        if not self.available:
            return "Gemini integration not available. Please provide a Google API key."
        
        try:
            # Prepare prompt based on task
            if task == "summarize":
                prompt = (
                    "Please provide a comprehensive yet concise summary of the following content. "
                    "Focus on capturing all key points and main ideas while eliminating redundancy. "
                    "Structure the summary with clear paragraphs and include any important facts, figures, or conclusions:\n\n"
                    f"{content}"
                )
            elif task == "extract_key_points":
                prompt = (
                    "Extract the most important key points from the following content. "
                    "For each key point, provide a brief explanation and note its significance. "
                    "Format each point as a bullet point and organize them in order of importance:\n\n"
                    f"{content}"
                )
            elif task == "analyze_sentiment":
                prompt = (
                    "Analyze the sentiment of the following content in detail. "
                    "Provide specific positive, negative, and neutral sentiment scores between 0.0 and 1.0, "
                    "where the scores should sum to 1.0. Also identify key emotional tones and provide examples "
                    "from the text that support your analysis:\n\n"
                    f"{content}"
                )
            else:
                prompt = f"Analyze the following content thoroughly:\n\n{content}"
            
            # Make API call with retry logic for potential timeouts or errors
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    response = self.text_model.generate_content(prompt)
                    return response.text
                except Exception as e:
                    if attempt < max_retries - 1:
                        time.sleep(1)  # Wait before retrying
                        continue
                    else:
                        raise e
            
        except Exception as e:
            return f"Error analyzing content with Gemini: {str(e)}"
    
    def analyze_image(self, image: Image.Image, analysis_type: str = "general") -> str:
        """
        Analyze image content using Gemini Pro Vision with enhanced prompts
        
        Args:
            image: PIL Image object
            analysis_type: Type of analysis to perform (general, detailed, objects, text, etc.)
        
        Returns:
            Gemini's response
        """
        if not self.available:
            return "Gemini integration not available. Please provide a Google API key."
        
        try:
            # Preprocess the image for better results
            processed_image = self._preprocess_image(image)
            
            # Select appropriate prompt based on analysis type
            if analysis_type == "general":
                prompt = (
                    "Provide a comprehensive description of this image. "
                    "Include details about the main subjects, setting, colors, mood, and any text visible. "
                    "Be specific and factual in your description."
                )
            elif analysis_type == "detailed":
                prompt = (
                    "Analyze this image in extreme detail, section by section. "
                    "First describe the overall scene, then break down specific elements: "
                    "1. Main subjects and their characteristics "
                    "2. Background and setting details "
                    "3. Colors, lighting, and visual composition "
                    "4. Any text, symbols, or distinctive features "
                    "5. Mood, style, and context clues "
                    "Be extremely specific and thorough."
                )
            elif analysis_type == "objects":
                prompt = (
                    "Identify and list all distinct objects visible in this image. "
                    "For each object, provide: "
                    "1. The name of the object "
                    "2. Its approximate location in the image (top-left, center, etc.) "
                    "3. Any distinctive features or conditions "
                    "4. An estimate of your confidence in the identification (high/medium/low) "
                    "Format as a numbered list of objects in order of prominence."
                )
            elif analysis_type == "text":
                prompt = (
                    "Extract and transcribe all text visible in this image. "
                    "Include: "
                    "1. The exact text content, preserving capitalization and punctuation "
                    "2. Location of the text in the image "
                    "3. Text formatting (bold, italic, size, color) if notable "
                    "Organize by sections if there are distinct blocks of text. "
                    "If text is partially visible or unclear, indicate this with [unclear] or your best guess in [brackets]."
                )
            else:
                prompt = f"Analyze this image with focus on {analysis_type}. Be detailed and precise."
            
            # Make API call with retry logic
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    response = self.vision_model.generate_content([prompt, processed_image])
                    return response.text
                except Exception as e:
                    if attempt < max_retries - 1:
                        time.sleep(1)  # Wait before retrying
                        continue
                    else:
                        raise e
            
        except Exception as e:
            return f"Error analyzing image with Gemini: {str(e)}"
    
    def _preprocess_image(self, image: Image.Image) -> Image.Image:
        """
        Preprocess image to improve analysis quality
        
        Args:
            image: Original PIL Image
        
        Returns:
            Processed PIL Image
        """
        # Ensure reasonable dimensions (not too small, not too large)
        width, height = image.size
        max_dim = 1024
        if max(width, height) > max_dim:
            # Scale down while maintaining aspect ratio
            if width > height:
                new_width = max_dim
                new_height = int(height * (max_dim / width))
            else:
                new_height = max_dim
                new_width = int(width * (max_dim / height))
            image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Ensure image is in RGB mode
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Optionally enhance image quality
        try:
            from PIL import ImageEnhance
            # Slightly enhance contrast
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(1.2)
            
            # Slightly enhance sharpness
            enhancer = ImageEnhance.Sharpness(image)
            image = enhancer.enhance(1.3)
        except:
            pass  # Skip enhancement if fails
        
        return image
    
    def analyze_video_frame(self, frame: Image.Image, context: Optional[str] = None) -> str:
        """
        Analyze a video frame with optional context
        
        Args:
            frame: PIL Image of the video frame
            context: Optional context about the video for better analysis
        
        Returns:
            Detailed analysis of the frame
        """
        # Process frame as image
        processed_frame = self._preprocess_image(frame)
        
        # Create a more detailed prompt for video frame analysis
        if context:
            prompt = (
                f"This is a frame from a video about {context}. "
                "Analyze this video frame in detail and describe: "
                "1. The main action or scene depicted "
                "2. All visible people, objects, and elements "
                "3. The setting and environment "
                "4. Any motion or activity that can be inferred "
                "5. The mood, lighting, and cinematographic qualities "
                "Provide a thorough analysis that captures both the visible elements and the implied context."
            )
        else:
            prompt = (
                "Analyze this video frame in detail and describe: "
                "1. The main action or scene depicted "
                "2. All visible people, objects, and elements "
                "3. The setting and environment "
                "4. Any motion or activity that can be inferred "
                "5. The mood, lighting, and cinematographic qualities "
                "Provide a thorough analysis that captures both the visible elements and their significance."
            )
        
        try:
            # Make API call with retry logic
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    response = self.vision_model.generate_content([prompt, processed_frame])
                    return response.text
                except Exception as e:
                    if attempt < max_retries - 1:
                        time.sleep(1)  # Wait before retrying
                        continue
                    else:
                        raise e
        except Exception as e:
            return f"Error analyzing video frame with Gemini: {str(e)}"
    
    def extract_objects_from_image(self, image: Image.Image) -> List[Dict[str, Any]]:
        """
        Extract detailed object information from an image
        
        Args:
            image: PIL Image object
        
        Returns:
            List of objects with their properties
        """
        # Process the image
        processed_image = self._preprocess_image(image)
        
        # Create a structured prompt for object detection
        prompt = (
            "List all objects visible in this image. "
            "For each object, provide the following information in a structured format:\n"
            "1. Object name\n"
            "2. Confidence level (high/medium/low)\n"
            "3. Location in the image (e.g., top-left, center, etc.)\n"
            "4. Approximate size (small/medium/large relative to image)\n"
            "5. Brief description\n\n"
            "Format your response as a list with each object separated by '---' and include "
            "all five attributes for each object, clearly labeled."
        )
        
        try:
            # Make API call
            response = self.vision_model.generate_content([prompt, processed_image])
            response_text = response.text
            
            # Parse the response into structured object data
            return self._parse_object_response(response_text)
            
        except Exception as e:
            print(f"Error extracting objects: {str(e)}")
            return []
    
    def _parse_object_response(self, response_text: str) -> List[Dict[str, Any]]:
        """Parse the structured object response from Gemini"""
        objects = []
        
        # Split by object separator
        object_texts = response_text.split('---')
        
        for obj_text in object_texts:
            obj_text = obj_text.strip()
            if not obj_text:
                continue
                
            # Initialize object data
            obj_data = {
                'label': '',
                'confidence': 0.0,
                'location': '',
                'size': '',
                'description': ''
            }
            
            # Extract object name/label
            name_match = None
            lines = obj_text.split('\n')
            for line in lines:
                line = line.strip()
                # Look for content that appears to be the object name
                if line and ':' not in line and len(line) < 50:
                    name_match = line
                    break
                if "name" in line.lower() or "object" in line.lower():
                    parts = line.split(':', 1)
                    if len(parts) > 1:
                        name_match = parts[1].strip()
                        break
            
            if name_match:
                obj_data['label'] = name_match
            
            # Extract confidence
            confidence_mapping = {'high': 0.9, 'medium': 0.7, 'low': 0.5}
            for conf_text, conf_value in confidence_mapping.items():
                if conf_text in obj_text.lower():
                    obj_data['confidence'] = conf_value
                    break
            
            # Extract location
            if "location" in obj_text.lower():
                loc_line = [l for l in lines if "location" in l.lower()]
                if loc_line:
                    parts = loc_line[0].split(':', 1)
                    if len(parts) > 1:
                        obj_data['location'] = parts[1].strip()
            
            # Extract size
            if "size" in obj_text.lower():
                size_line = [l for l in lines if "size" in l.lower()]
                if size_line:
                    parts = size_line[0].split(':', 1)
                    if len(parts) > 1:
                        obj_data['size'] = parts[1].strip()
            
            # Extract description
            if "description" in obj_text.lower():
                desc_line = [l for l in lines if "description" in l.lower()]
                if desc_line:
                    parts = desc_line[0].split(':', 1)
                    if len(parts) > 1:
                        obj_data['description'] = parts[1].strip()
            
            # Add to objects list if we have a valid label
            if obj_data['label']:
                objects.append(obj_data)
        
        # If parsing failed, try a simple approach
        if not objects and response_text:
            # Look for list items that might be objects
            for line in response_text.split('\n'):
                line = line.strip()
                if line.startswith(('- ', '• ', '* ', '1. ', '2. ')):
                    # Extract the object name after the list marker
                    label = line[2:].strip() if line[1] == ' ' else line[3:].strip()
                    if label and len(label) < 50:  # Reasonable object name length
                        objects.append({
                            'label': label,
                            'confidence': 0.7,  # Default medium confidence
                            'location': '',
                            'size': '',
                            'description': ''
                        })
        
        return objects
    
    def analyze_video_content(self, frames: List[Image.Image], video_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform comprehensive analysis of video content using multiple frames
        
        Args:
            frames: List of PIL Image objects representing video frames
            video_info: Dictionary with video metadata (duration, fps, etc.)
        
        Returns:
            Dictionary with video analysis results
        """
        if not self.available:
            return {"error": "Gemini integration not available. Please provide a Google API key."}
        
        if not frames:
            return {"error": "No frames provided for analysis."}
        
        try:
            # Analyze key frames
            frame_analyses = []
            for i, frame in enumerate(frames[:5]):  # Limit to 5 frames
                frame_results = {
                    "frame_number": i + 1,
                    "timestamp": video_info.get("frame_timestamps", [])[i] if "frame_timestamps" in video_info else i,
                    "description": self.analyze_video_frame(frame)
                }
                frame_analyses.append(frame_results)
            
            # Create a combined analysis of all frames
            context = (
                f"This is a video that is {video_info.get('duration', 0):.1f} seconds long "
                f"with resolution {video_info.get('width', 0)}x{video_info.get('height', 0)}. "
                "Based on the frames I've analyzed, please provide a comprehensive analysis including: "
                "1. What is happening in the video "
                "2. The main subjects and their actions "
                "3. The setting and environment "
                "4. Any changes or progression visible across the frames "
                "5. The overall theme or purpose of the video"
            )
            
            # Combine representative frames for overall analysis (first, middle, last)
            representative_frames = []
            if len(frames) >= 3:
                representative_frames = [frames[0], frames[len(frames)//2], frames[-1]]
            else:
                representative_frames = frames
                
            # Create multipart prompt with context and frames
            parts = [context]
            for frame in representative_frames:
                parts.append(self._preprocess_image(frame))
            
            # Get overall video analysis
            response = self.vision_model.generate_content(parts)
            overall_analysis = response.text
            
            # Return combined results
            return {
                "overall_analysis": overall_analysis,
                "frame_analyses": frame_analyses,
                "detected_objects": self._extract_objects_from_analysis(overall_analysis)
            }
            
        except Exception as e:
            return {"error": f"Error analyzing video with Gemini: {str(e)}"}
    
    def _extract_objects_from_analysis(self, analysis: str) -> List[Dict[str, Any]]:
        """Extract object mentions from text analysis"""
        # Create a prompt to extract objects from the analysis
        prompt = (
            "Based on the following video analysis, list all distinct objects and persons mentioned. "
            "For each object/person, provide a confidence score between 0 and 1 based on how "
            "certain the mention is (1 being completely certain):\n\n" + analysis
        )
        
        try:
            response = self.text_model.generate_content(prompt)
            response_text = response.text
            
            # Parse objects from response
            objects = []
            current_obj = {}
            
            for line in response_text.split('\n'):
                line = line.strip()
                if not line:
                    continue
                    
                # Look for object name with optional confidence
                if ':' in line:
                    parts = line.split(':', 1)
                    label = parts[0].strip()
                    if label and len(label) < 50:  # Reasonable object name length
                        # Try to extract confidence from description
                        conf_str = parts[1].strip()
                        try:
                            # Look for a number between 0 and 1
                            import re
                            conf_match = re.search(r'(\d+\.\d+|\d+)', conf_str)
                            confidence = float(conf_match.group(1)) if conf_match else 0.7
                            # Ensure confidence is between 0 and 1
                            confidence = min(max(confidence, 0), 1)
                        except:
                            confidence = 0.7  # Default confidence
                            
                        objects.append({
                            'label': label,
                            'confidence': confidence,
                            'count': 1
                        })
                        
                # Alternative format: numbered or bulleted list
                elif line.startswith(('- ', '• ', '* ', '1. ', '2. ')):
                    # Extract the object name after the list marker
                    content = line[2:].strip() if line[1] == ' ' else line[3:].strip()
                    if ':' in content:
                        parts = content.split(':', 1)
                        label = parts[0].strip()
                    else:
                        label = content
                    
                    if label and len(label) < 50:  # Reasonable object name length
                        objects.append({
                            'label': label,
                            'confidence': 0.7,  # Default confidence
                            'count': 1
                        })
            
            return objects
                    
        except Exception as e:
            print(f"Error extracting objects from analysis: {str(e)}")
            return []
    
    def answer_question(self, question: str, context: str) -> str:
        """
        Answer a question based on provided context
        
        Args:
            question: The question to answer
            context: The context to use for answering the question
        
        Returns:
            Gemini's answer
        """
        if not self.available:
            return "Gemini integration not available. Please provide a Google API key."
        
        try:
            # Create a more informative prompt
            prompt = f"""
            You are a helpful assistant that provides accurate and detailed answers based solely on the provided context.
            
            CONTEXT:
            {context}
            
            QUESTION:
            {question}
            
            INSTRUCTIONS:
            1. Answer based ONLY on the information in the context above
            2. If the context doesn't contain the information needed, say "I don't have enough information to answer that question."
            3. Be specific and cite relevant details from the context
            4. Format your answer clearly with paragraphs as needed
            5. If you're unsure about any detail, acknowledge the uncertainty
            
            ANSWER:
            """
            
            # Make API call with retry logic
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    response = self.text_model.generate_content(prompt)
                    return response.text
                except Exception as e:
                    if attempt < max_retries - 1:
                        time.sleep(1)  # Wait before retrying
                        continue
                    else:
                        raise e
            
        except Exception as e:
            return f"Error answering question with Gemini: {str(e)}"
    
    def multimodal_analysis(self, text_content: str, images: List[Image.Image]) -> str:
        """
        Perform multimodal analysis with both text and images
        
        Args:
            text_content: The text content
            images: List of PIL Image objects
        
        Returns:
            Gemini's multimodal analysis
        """
        if not self.available:
            return "Gemini integration not available. Please provide a Google API key."
        
        if not images:
            return self.analyze_text(text_content, "analyze")
        
        try:
            # Preprocess images
            processed_images = [self._preprocess_image(img) for img in images[:3]]
            
            # Create more detailed multimodal prompt
            prompt = (
                "Perform a comprehensive analysis of the following content and images together. "
                "Pay special attention to how the text and visual elements relate to each other. "
                "Include in your analysis:\n"
                "1. The main topic or subject matter\n"
                "2. Key information from both text and images\n"
                "3. How the images support or illustrate the text\n"
                "4. Any discrepancies or additional information provided by the images\n"
                "5. An overall interpretation of the combined content\n\n"
                f"TEXT CONTENT:\n{text_content}"
            )
            
            # Combine text and images for multimodal input
            parts = [prompt] + processed_images
            
            # Make API call with retry logic
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    response = self.vision_model.generate_content(parts)
                    return response.text
                except Exception as e:
                    if attempt < max_retries - 1:
                        time.sleep(1)  # Wait before retrying
                        continue
                    else:
                        raise e
            
        except Exception as e:
            return f"Error performing multimodal analysis with Gemini: {str(e)}"
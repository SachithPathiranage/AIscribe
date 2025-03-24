import io
import tempfile
import os
import numpy as np
import cv2
from moviepy.editor import VideoFileClip
from utils.gemini_integration import GeminiIntegration
from PIL import Image

def process_video(file, options):
    """
    Process a video file to extract frames, audio, and analyze content
    
    Args:
        file: The uploaded video file
        options: Dictionary of analysis options
    
    Returns:
        Dict containing analysis results
    """
    # Initialize Gemini
    gemini = GeminiIntegration()
    
    # Save uploaded file to a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as temp_file:
        temp_file.write(file.getvalue())
        temp_path = temp_file.name
    
    try:
        # Open video file with moviepy
        video = VideoFileClip(temp_path)
        
        # Get video metadata
        duration = video.duration
        fps = video.fps
        width, height = video.size
        
        # Initialize results
        results = {
            'file_type': 'video',
            'duration': duration,
            'fps': fps,
            'width': width,
            'height': height,
            'frame_count': int(duration * fps),
            'key_frames': [],
            'transcript': '',
            'summary': '',
            'objects_detected': []
        }
        
        # Extract frames for analysis
        if options.get('analyze_video_frames', True):
            # Extract frames more intelligently - at key points in the video
            extracted_frames, frame_timestamps = extract_strategic_frames(video, options)
            
            if gemini.is_available():
                # Perform comprehensive video analysis with Gemini
                video_info = {
                    'duration': duration,
                    'fps': fps,
                    'width': width,
                    'height': height,
                    'frame_timestamps': frame_timestamps
                }
                
                # Convert frames to PIL images
                pil_frames = []
                for frame in extracted_frames:
                    pil_frame = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                    pil_frames.append(pil_frame)
                
                # Get video analysis from Gemini
                analysis_results = gemini.analyze_video_content(pil_frames, video_info)
                
                # Add overall analysis as summary
                if 'overall_analysis' in analysis_results:
                    results['summary'] = analysis_results['overall_analysis']
                
                # Process individual frame analyses
                if 'frame_analyses' in analysis_results:
                    for i, frame_analysis in enumerate(analysis_results['frame_analyses']):
                        if i < len(extracted_frames):
                            # Convert frame to JPEG for display
                            success, buffer = cv2.imencode('.jpg', extracted_frames[i])
                            if success:
                                # Create frame data
                                frame_data = {
                                    'time': frame_timestamps[i],
                                    'frame_number': frame_analysis['frame_number'],
                                    'description': frame_analysis['description'],
                                    'image': io.BytesIO(buffer)
                                }
                                results['key_frames'].append(frame_data)
                
                # Add detected objects
                if 'detected_objects' in analysis_results:
                    results['objects_detected'] = analysis_results['detected_objects']
            else:
                # Fall back to basic frame analysis
                results['key_frames'] = basic_frame_analysis(extracted_frames, frame_timestamps)
        
        # Extract audio and transcribe if option is selected
        if options.get('extract_audio', True) and options.get('transcribe_audio', True):
            from models.speech_model import transcribe_audio
            results['transcript'] = extract_and_transcribe_audio(video)
        
        # Generate video summary if not already done and option is selected
        if 'summary' not in results and options.get('generate_video_summary', True):
            # Combine frame descriptions and transcript for a more complete summary
            frame_descriptions = [frame.get('description', '') for frame in results['key_frames']]
            content_to_summarize = ' '.join(frame_descriptions) + ' ' + results['transcript']
            
            if content_to_summarize.strip():
                from models.text_analyzer import summarize_text
                results['summary'] = summarize_text(content_to_summarize)
        
        # Clean up
        video.close()
        
        return results
    
    except Exception as e:
        # Clean up in case of error
        if os.path.exists(temp_path):
            os.remove(temp_path)
        
        return {
            'file_type': 'video',
            'error': f"Error processing video: {str(e)}"
        }
    
    finally:
        # Make sure to clean up the temp file
        if os.path.exists(temp_path):
            os.remove(temp_path)

def extract_strategic_frames(video, options, max_frames=7):
    """
    Extract frames strategically from throughout the video
    
    Args:
        video: MoviePy VideoFileClip object
        options: Dictionary of analysis options
        max_frames: Maximum number of frames to extract
    
    Returns:
        Tuple of (list of frames, list of timestamps)
    """
    duration = video.duration
    
    if duration <= 0:
        return [], []
    
    # Strategy for frame extraction:
    # 1. Always include first and last frame
    # 2. Try to detect scene changes for the middle frames
    # 3. If scene detection fails, use evenly spaced frames
    
    frames = []
    timestamps = []
    
    # Always add the first frame (but not at absolute 0, slightly in)
    first_time = min(0.5, duration * 0.1)
    frames.append(np.array(video.get_frame(first_time)))
    timestamps.append(first_time)
    
    # Try scene detection if duration is long enough
    middle_frames = max_frames - 2  # Excluding first and last
    if duration > 3 and middle_frames > 0:
        try:
            # Create temporary video file for OpenCV
            with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as temp_file:
                temp_video_path = temp_file.name
            
            # Write a subset of the video to the temp file for faster processing
            if duration > 60:  # For very long videos, sample the first minute
                subclip = video.subclip(0, 60)
                subclip.write_videofile(temp_video_path, codec='libx264', audio=False, verbose=False, logger=None)
                subclip_duration = 60
            else:
                video.write_videofile(temp_video_path, codec='libx264', audio=False, verbose=False, logger=None)
                subclip_duration = duration
            
            # Use OpenCV for scene detection
            cap = cv2.VideoCapture(temp_video_path)
            
            # Scene detection parameters
            threshold = 30.0  # Threshold for scene change detection
            min_scene_length = max(1.0, subclip_duration / (middle_frames * 2))  # Minimum length between scenes
            
            prev_frame = None
            scene_timestamps = []
            frame_count = 0
            
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                
                frame_time = frame_count / cap.get(cv2.CAP_PROP_FPS)
                frame_count += 1
                
                # Skip the first frame we already captured
                if frame_time < first_time:
                    continue
                
                # Skip frames too close to the last detected scene
                if scene_timestamps and (frame_time - scene_timestamps[-1] < min_scene_length):
                    continue
                
                if prev_frame is not None:
                    # Convert to grayscale for comparison
                    prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
                    curr_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    
                    # Calculate frame difference
                    frame_diff = cv2.absdiff(prev_gray, curr_gray)
                    mean_diff = np.mean(frame_diff)
                    
                    # If difference is above threshold, consider it a scene change
                    if mean_diff > threshold:
                        # Map the timestamp back to the original video if using a subclip
                        original_time = frame_time
                        if duration > 60:
                            original_time = min(frame_time, duration)
                            
                        scene_timestamps.append(original_time)
                        
                        # Break if we have enough scenes
                        if len(scene_timestamps) >= middle_frames:
                            break
                
                prev_frame = frame.copy()
            
            cap.release()
            os.remove(temp_video_path)
            
            # If we found scenes, use those timestamps
            if scene_timestamps:
                # Sort timestamps and ensure we don't have duplicates
                scene_timestamps = sorted(set(scene_timestamps))
                
                for time in scene_timestamps[:middle_frames]:
                    # Skip if too close to first frame
                    if abs(time - first_time) < 1.0:
                        continue
                    # Skip if too close to end of video
                    if duration - time < 1.0:
                        continue
                    frames.append(np.array(video.get_frame(time)))
                    timestamps.append(time)
            
        except Exception as e:
            print(f"Scene detection failed: {e}. Falling back to evenly spaced frames.")
            # Fall back to evenly spaced frames
            scene_timestamps = []
    
    # If scene detection failed or wasn't attempted, use evenly spaced frames
    if len(frames) < max_frames - 1:
        remaining_frames = max_frames - 1 - len(frames)
        
        # Calculate how many additional frames we need
        if remaining_frames > 0:
            # Generate evenly spaced timestamps
            existing_timestamps = set(timestamps)
            step = duration / (remaining_frames + 2)  # +2 accounts for first and last frames
            
            for i in range(1, remaining_frames + 1):
                # Calculate timestamp
                time = min(first_time + (i * step), duration - 1)
                
                # Skip if too close to existing timestamps
                if any(abs(time - t) < 1.0 for t in existing_timestamps):
                    continue
                
                frames.append(np.array(video.get_frame(time)))
                timestamps.append(time)
                existing_timestamps.add(time)
    
    # Always add the last frame (not at absolute end, slightly before)
    last_time = max(duration - 0.5, duration * 0.9)
    
    # Skip if too close to existing timestamps
    if not any(abs(last_time - t) < 1.0 for t in timestamps):
        frames.append(np.array(video.get_frame(last_time)))
        timestamps.append(last_time)
    
    # Sort frames by timestamp
    frames_and_times = sorted(zip(frames, timestamps), key=lambda x: x[1])
    sorted_frames = [ft[0] for ft in frames_and_times]
    sorted_timestamps = [ft[1] for ft in frames_and_times]
    
    return sorted_frames, sorted_timestamps

def basic_frame_analysis(frames, timestamps):
    """Basic analysis of frames when Gemini is not available"""
    from models.vision_model import analyze_image, detect_objects
    
    key_frames = []
    
    for i, (frame, time) in enumerate(zip(frames, timestamps)):
        # Convert from BGR to RGB for PIL
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(frame_rgb)
        
        # Create frame data
        frame_data = {
            'time': time,
            'frame_number': i + 1
        }
        
        # Analyze frame
        frame_data['description'] = analyze_image(pil_image)
        frame_data['objects'] = detect_objects(pil_image)
        
        # Convert frame to JPEG for display
        success, buffer = cv2.imencode('.jpg', frame)
        if success:
            frame_data['image'] = io.BytesIO(buffer)
        
        key_frames.append(frame_data)
    
    return key_frames

def extract_and_transcribe_audio(video):
    """
    Extract audio from video and transcribe it
    
    Args:
        video: MoviePy VideoFileClip object
    
    Returns:
        Transcription of the audio
    """
    try:
        # Extract audio as numpy array
        audio = video.audio
        if audio is None:
            return "No audio track found in video."
        
        # Get audio data
        audio_array = audio.to_soundarray()
        sample_rate = audio.fps
        
        # Convert to mono if stereo
        if audio_array.ndim > 1 and audio_array.shape[1] > 1:
            audio_array = np.mean(audio_array, axis=1)
        
        # Transcribe audio
        from models.speech_model import transcribe_audio
        transcript = transcribe_audio(audio_array, sample_rate)
        
        return transcript
    
    except Exception as e:
        return f"Error transcribing audio: {str(e)}"
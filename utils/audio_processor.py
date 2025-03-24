import io
import numpy as np
import librosa
import soundfile as sf
from models.speech_model import transcribe_audio, detect_speaker_segments, analyze_audio_sentiment

def process_audio(file, options):
    """
    Process an audio file to extract and analyze content
    
    Args:
        file: The uploaded audio file
        options: Dictionary of analysis options
    
    Returns:
        Dict containing analysis results
    """
    # Read audio file
    audio_bytes = file.getvalue()
    
    try:
        # Load audio using librosa
        with io.BytesIO(audio_bytes) as audio_io:
            y, sr = librosa.load(audio_io, sr=None)
        
        # Get audio duration
        duration = librosa.get_duration(y=y, sr=sr)
        
        # Initialize results
        results = {
            'file_type': 'audio',
            'sample_rate': sr,
            'duration': duration,
            'channels': 1 if y.ndim == 1 else y.shape[1],
            'transcript': '',
            'speaker_segments': [],
            'sentiment': {},
            'audio_features': {},
            'visualization_data': {}
        }

        # Generate visualization data
        results['visualization_data'] = {
            'waveform': generate_audio_waveform_plot(y, sr),
            'spectrogram': generate_spectrogram_plot(y, sr)
            }
        
        # Transcribe audio if option is selected
        if options.get('transcribe_audio', True):
            results['transcript'] = transcribe_audio(y, sr)
        
        # Detect speakers if option is selected
        if options.get('detect_speakers', False) and results['transcript']:
            results['speaker_segments'] = detect_speaker_segments(y, sr, results['transcript'])
        
        # Extract audio features
        results['audio_features'] = extract_audio_features(y, sr)
        
        # Analyze sentiment if we have a transcript
        if results['transcript']:
            results['sentiment'] = analyze_audio_sentiment(results['transcript'])
        
        return results
    
    except Exception as e:
        return {
            'file_type': 'audio',
            'error': f"Error processing audio: {str(e)}"
        }

def extract_audio_features(y, sr):
    """
    Extract meaningful features from audio data
    
    Args:
        y: Audio time series
        sr: Sampling rate
    
    Returns:
        Dict of audio features
    """
    features = {}
    
    try:
        # Extract tempo (BPM)
        onset_env = librosa.onset.onset_strength(y=y, sr=sr)
        tempo = librosa.beat.tempo(onset_envelope=onset_env, sr=sr)[0]
        features['tempo'] = float(tempo)
        
        # Extract harmonic and percussive components
        y_harmonic, y_percussive = librosa.effects.hpss(y)
        
        # Extract spectral centroid (brightness)
        cent = librosa.feature.spectral_centroid(y=y, sr=sr)
        features['spectral_centroid_mean'] = float(np.mean(cent))
        
        # Extract spectral bandwidth
        bandwidth = librosa.feature.spectral_bandwidth(y=y, sr=sr)
        features['spectral_bandwidth_mean'] = float(np.mean(bandwidth))
        
        # Extract zero crossing rate (noisiness)
        zcr = librosa.feature.zero_crossing_rate(y)
        features['zero_crossing_rate_mean'] = float(np.mean(zcr))
        
        # Extract root mean square energy
        rms = librosa.feature.rms(y=y)
        features['rms_energy_mean'] = float(np.mean(rms))
        
        # Check if audio contains speech
        # This is a simplified approximation - in practice you'd use a speech detection model
        features['likely_contains_speech'] = (
            features['spectral_centroid_mean'] > 1000 and 
            features['zero_crossing_rate_mean'] > 0.05
        )
        
        # Audio classification hints
        if features['tempo'] > 120:
            features['tempo_category'] = 'fast'
        elif features['tempo'] > 80:
            features['tempo_category'] = 'medium'
        else:
            features['tempo_category'] = 'slow'
            
    except Exception as e:
        features['extraction_error'] = str(e)
    
    return features

def generate_audio_waveform_plot(y, sr):
    """
    Generate a waveform visualization of the audio
    
    Args:
        y: Audio time series
        sr: Sampling rate
    
    Returns:
        BytesIO object containing the plot image
    """
    import matplotlib.pyplot as plt
    
    try:
        plt.figure(figsize=(10, 4))
        plt.plot(np.linspace(0, len(y)/sr, len(y)), y, color='#3366cc')
        plt.title('Audio Waveform')
        plt.xlabel('Time (s)')
        plt.ylabel('Amplitude')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=100)
        buf.seek(0)
        plt.close()
        
        return buf
    except Exception as e:
        print(f"Error generating waveform plot: {str(e)}")
        # Return a placeholder image or None
        return None

def generate_spectrogram_plot(y, sr):
    """
    Generate a spectrogram visualization of the audio
    
    Args:
        y: Audio time series
        sr: Sampling rate
    
    Returns:
        BytesIO object containing the plot image
    """
    import matplotlib.pyplot as plt
    
    try:
        plt.figure(figsize=(10, 4))
        D = librosa.amplitude_to_db(np.abs(librosa.stft(y)), ref=np.max)
        librosa.display.specshow(D, sr=sr, x_axis='time', y_axis='log')
        plt.colorbar(format='%+2.0f dB')
        plt.title('Spectrogram')
        plt.tight_layout()
        
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=100)
        buf.seek(0)
        plt.close()
        
        return buf
    except Exception as e:
        print(f"Error generating spectrogram plot: {str(e)}")
        # Return a placeholder image or None
        return None
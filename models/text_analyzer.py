import re
from utils.gemini_integration import GeminiIntegration

# Initialize Gemini integration
gemini = GeminiIntegration()

def summarize_text(text, max_length=500):
    """
    Generate a summary of the provided text
    
    Args:
        text: The text to summarize
        max_length: Maximum summary length in characters
    
    Returns:
        A summary of the text
    """
    if gemini.is_available():
        summary = gemini.analyze_text(text, "summarize")
        # Ensure summary doesn't exceed max_length
        return summary[:max_length] + "..." if len(summary) > max_length else summary
    
    # Simple extractive summary as fallback
    sentences = re.split(r'(?<=[.!?])\s+', text)
    
    if len(sentences) <= 3:
        return text
    
    # Take the first 3 sentences as a simple summary
    simple_summary = ' '.join(sentences[:3])
    
    # Add ellipsis if summary is shorter than original
    if len(simple_summary) < len(text):
        simple_summary += "..."
    
    return simple_summary[:max_length]

def extract_key_points(text, num_points=5):
    """
    Extract key points from the provided text
    
    Args:
        text: The text to analyze
        num_points: Number of key points to extract
    
    Returns:
        List of key points
    """
    if gemini.is_available():
        key_points_text = gemini.analyze_text(text, "extract_key_points")
        
        # Parse the key points
        points = []
        for line in key_points_text.split('\n'):
            line = line.strip()
            if line and (line.startswith('-') or line.startswith('•') or line[0].isdigit()):
                points.append(line.lstrip('-•0123456789. '))
        
        # Ensure we have the requested number of points
        if len(points) > num_points:
            points = points[:num_points]
        
        return points
    
    # Simple implementation for demonstration (fallback)
    sentences = re.split(r'(?<=[.!?])\s+', text)
    
    # Filter out very short sentences
    valid_sentences = [s for s in sentences if len(s) > 30]
    
    # Take every nth sentence to get diverse content
    if len(valid_sentences) > num_points:
        step = len(valid_sentences) // num_points
        key_sentences = valid_sentences[::step][:num_points]
    else:
        key_sentences = valid_sentences[:num_points]
    
    return key_sentences

def analyze_sentiment(text):
    """
    Analyze the sentiment of the provided text
    
    Args:
        text: The text to analyze
    
    Returns:
        Dict with sentiment scores
    """
    if gemini.is_available():
        sentiment_analysis = gemini.analyze_text(text, "analyze_sentiment")
        
        # This is a simple parsing approach - in production you'd want more robust parsing
        try:
            # Default values
            sentiment = {
                'positive': 0.5,
                'negative': 0.2,
                'neutral': 0.3
            }
            
            # Look for numerical values in the response
            pos_match = re.search(r'positive[:\s]+(\d+\.?\d*)', sentiment_analysis, re.IGNORECASE)
            neg_match = re.search(r'negative[:\s]+(\d+\.?\d*)', sentiment_analysis, re.IGNORECASE)
            neu_match = re.search(r'neutral[:\s]+(\d+\.?\d*)', sentiment_analysis, re.IGNORECASE)
            
            if pos_match:
                sentiment['positive'] = float(pos_match.group(1))
            if neg_match:
                sentiment['negative'] = float(neg_match.group(1))
            if neu_match:
                sentiment['neutral'] = float(neu_match.group(1))
                
            return sentiment
        except:
            pass
    
    # Fallback sentiment analysis
    return {
        'positive': 0.5,
        'negative': 0.2,
        'neutral': 0.3
    }
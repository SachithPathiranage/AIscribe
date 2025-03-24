import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io
import datetime
from PIL import Image
import altair as alt
import numpy as np

def render_results(results):
    """
    Render analysis results for all files
    
    Args:
        results: Dictionary containing analysis results
    """
    if not results:
        return
    
    st.header("Analysis Results")
    
    # Create tabs for each file
    file_names = list(results.keys())
    tabs = st.tabs(file_names)
    
    # Display results for each file in its tab
    for i, tab in enumerate(tabs):
        file_name = file_names[i]
        file_results = results[file_name]
        
        with tab:
            render_file_results(file_name, file_results)

def render_file_results(file_name, results):
    """Render results for a single file"""
    file_type = results.get('file_type', 'unknown')
    
    # Display appropriate components based on file type
    if file_type == 'pdf':
        render_pdf_results(results)
    elif file_type == 'image':
        render_image_results(results)
    elif file_type == 'video':
        render_video_results(results)
    elif file_type == 'audio':
        render_audio_results(results)
    else:
        st.warning(f"Unsupported file type for {file_name}")

def render_pdf_results(results):
    """Render results specific to PDF files"""
    # Display summary if available
    if 'summary' in results and results['summary']:
        st.subheader("Summary")
        st.write(results['summary'])
    
    # Display key points if available
    if 'key_points' in results and results['key_points']:
        st.subheader("Key Points")
        for point in results['key_points']:
            st.markdown(f"- {point}")
    
    # Display extracted images if available
    if 'images' in results and results['images']:
        st.subheader("Extracted Images")
        cols = st.columns(min(3, len(results['images'])))
        for i, img_data in enumerate(results['images']):
            col_idx = i % 3
            with cols[col_idx]:
                img = Image.open(img_data['image'])
                st.image(img, caption=f"Page {img_data['page_num']}", use_column_width=True)
    
    # Display metadata
    st.subheader("Document Information")
    st.markdown(f"**Page Count:** {results.get('page_count', 'N/A')}")
    
    # Display a sample of the extracted text
    if 'text_content' in results and results['text_content']:
        with st.expander("View Extracted Text"):
            text_preview = results['text_content'][:1000] + "..." if len(results['text_content']) > 1000 else results['text_content']
            st.text(text_preview)

def render_image_results(results):
    """Render results specific to image files"""
    # Display image with details
    st.subheader("Image Information")
    st.markdown(f"**Resolution:** {results.get('width', 'N/A')} x {results.get('height', 'N/A')}")
    st.markdown(f"**Format:** {results.get('format', 'N/A')}")
    
    # Display image description if available
    if 'description' in results and results['description']:
        st.subheader("Image Description")
        st.write(results['description'])
    
    # Display detailed analysis if available
    if 'detailed_analysis' in results and results['detailed_analysis']:
        with st.expander("Detailed Analysis"):
            st.write(results['detailed_analysis'])
    
    # Display detected objects if available
    if 'objects' in results and results['objects']:
        st.subheader("Detected Objects")
        
        # Create a DataFrame for objects
        import pandas as pd
        
        # Check which fields are available in the objects
        sample_obj = results['objects'][0] if results['objects'] else {}
        available_fields = [field for field in ['label', 'confidence', 'location', 'size', 'description'] if field in sample_obj]
        
        # Create DataFrame with available fields
        obj_data = pd.DataFrame(results['objects'])[available_fields]
        
        # Format confidence as percentage if it exists
        if 'confidence' in obj_data.columns:
            obj_data['confidence'] = obj_data['confidence'].apply(lambda x: f"{x:.1%}" if isinstance(x, (int, float)) else x)
        
        # Display objects as a table
        st.dataframe(obj_data, use_container_width=True)
        
        # Create visualizations if we have enough data
        if len(results['objects']) > 0:
            try:
                import matplotlib.pyplot as plt
                import altair as alt
                
                # Only create chart if we have confidence values that are numeric
                conf_values = [obj.get('confidence', 0) for obj in results['objects'] if isinstance(obj.get('confidence', 0), (int, float))]
                
                if conf_values:
                    # Create a DataFrame for the chart
                    chart_data = pd.DataFrame({
                        'Object': [obj.get('label', f"Object {i+1}") for i, obj in enumerate(results['objects'])],
                        'Confidence': conf_values
                    })
                    
                    # Create interactive Altair chart
                    chart = alt.Chart(chart_data).mark_bar().encode(
                        x=alt.X('Confidence:Q', title='Confidence Score'),
                        y=alt.Y('Object:N', title=None, sort='-x'),
                        color=alt.Color('Confidence:Q', legend=None, scale=alt.Scale(scheme='viridis')),
                        tooltip=['Object', 'Confidence']
                    ).properties(
                        title='Object Detection Confidence',
                        height=min(len(results['objects']) * 30, 400)
                    ).interactive()
                    
                    st.altair_chart(chart, use_container_width=True)
            except Exception as e:
                st.warning(f"Could not create visualization: {str(e)}")
    
    # Display extracted text from image if available
    if 'text_content' in results and results['text_content']:
        st.subheader("Extracted Text (OCR)")
        st.write(results['text_content'])

def render_video_results(results):
    """Render results specific to video files"""
    # Display analysis metadata
    st.info(f"Analysis requested by: {results.get('user', 'SachithPathiranage')} at {results.get('timestamp', datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}")
    
    # Check for errors
    if 'error' in results:
        st.error(results['error'])
        return
    
    # Display video metadata
    st.subheader("Video Information")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Duration", f"{results.get('duration', 0):.2f} seconds")
    with col2:
        st.metric("Resolution", f"{results.get('width', 0)} x {results.get('height', 0)}")
    with col3:
        st.metric("FPS", f"{results.get('fps', 0):.1f}")
    
    # Display video summary if available
    if 'summary' in results and results['summary']:
        st.subheader("Video Summary")
        st.write(results['summary'])
    
    # Display key frames if available
    if 'key_frames' in results and results['key_frames']:
        st.subheader("Key Frames")
        
        # Create tabs for each key frame
        frame_tabs = st.tabs([f"Frame {f['frame_number']} ({f['time']:.2f}s)" for f in results['key_frames']])
        
        for i, tab in enumerate(frame_tabs):
            frame = results['key_frames'][i]
            
            with tab:
                col1, col2 = st.columns([1, 1])
                
                with col1:
                    # Display frame image
                    if 'image' in frame:
                        img = Image.open(frame['image'])
                        st.image(img, caption=f"Time: {frame['time']:.2f}s", use_column_width=True)
                
                with col2:
                    # Display frame description
                    if 'description' in frame:
                        st.markdown("**Description:**")
                        if frame['description'].startswith("Error"):
                            st.error(frame['description'])
                        else:
                            st.write(frame['description'])
                    
                    # Display detected objects in frame
                    if 'objects' in frame and frame['objects']:
                        st.markdown("**Detected Objects:**")
                        obj_df = pd.DataFrame([
                            {"Object": obj['label'], "Confidence": f"{obj['confidence']:.2f}"} 
                            for obj in frame['objects']
                        ])
                        st.dataframe(obj_df)
    
    # Display objects detected across the video
    if 'objects_detected' in results and results['objects_detected']:
        st.subheader("Objects Detected Throughout Video")
        
        # Create DataFrame for objects
        import pandas as pd
        import altair as alt
        
        obj_df = pd.DataFrame(results['objects_detected'])
        
        # Ensure we have the right columns
        if 'label' in obj_df.columns:
            # Rename columns to more user-friendly names
            column_mapping = {
                'label': 'Object',
                'confidence': 'Confidence',
                'count': 'Count'
            }
            obj_df = obj_df.rename(columns={k: v for k, v in column_mapping.items() if k in obj_df.columns})
            
            # Display as table
            st.dataframe(obj_df, use_container_width=True)
            
            # Display as interactive chart if we have confidence and count
            chart_columns = [col for col in ['Object', 'Confidence', 'Count'] if col in obj_df.columns]
            if len(chart_columns) >= 2 and 'Object' in chart_columns:
                try:
                    # Select columns for chart
                    chart_data = obj_df[chart_columns].copy()
                    
                    # Convert to numeric if needed
                    for col in ['Confidence', 'Count']:
                        if col in chart_data.columns:
                            chart_data[col] = pd.to_numeric(chart_data[col], errors='coerce')
                    
                    # Create chart based on available columns
                    y_column = 'Count' if 'Count' in chart_data.columns else 'Confidence'
                    color_column = 'Confidence' if 'Confidence' in chart_data.columns else None
                    
                    chart = alt.Chart(chart_data).mark_bar().encode(
                        x=alt.X('Object:N', title='Object', sort='-y'),
                        y=alt.Y(f'{y_column}:Q', title=y_column)
                    )
                    
                    if color_column:
                        chart = chart.encode(
                            color=alt.Color(f'{color_column}:Q', scale=alt.Scale(scheme='viridis'), title=color_column),
                            tooltip=['Object', y_column, color_column] if color_column != y_column else ['Object', y_column]
                        )
                    else:
                        chart = chart.encode(
                            tooltip=['Object', y_column]
                        )
                    
                    chart = chart.properties(
                        title='Objects Detected in Video',
                        width=600,
                        height=400
                    )
                    
                    st.altair_chart(chart, use_container_width=True)
                except Exception as e:
                    st.warning(f"Could not create visualization: {str(e)}")
        else:
            st.write(results['objects_detected'])  # Fallback if not in expected format
    
    # Display transcript if available
    if 'transcript' in results and results['transcript']:
        st.subheader("Audio Transcript")
        
        # Check if this is an error message
        if results['transcript'].startswith("Error") or results['transcript'].startswith("Could not"):
            st.warning(results['transcript'])
        else:
            st.write(results['transcript'])

def render_audio_results(results):
    """Render results specific to audio files"""
    # Check for errors
    if 'error' in results:
        st.error(results['error'])
        return
    
    # Display audio metadata
    st.subheader("Audio Information")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Duration", f"{results.get('duration', 0):.2f} seconds")
    with col2:
        st.metric("Sample Rate", f"{results.get('sample_rate', 0)} Hz")
    with col3:
        st.metric("Channels", results.get('channels', 0))
    
    # Display transcript if available
    if 'transcript' in results and results['transcript']:
        st.subheader("Transcript")
        st.write(results['transcript'])
    
    # Display speaker segments if available
    if 'speaker_segments' in results and results['speaker_segments']:
        st.subheader("Speaker Segments")
        
        for segment in results['speaker_segments']:
            with st.expander(f"{segment['speaker']} ({segment['start']:.1f}s - {segment['end']:.1f}s)"):
                st.write(segment['text'])
    
    # Display sentiment analysis if available
    if 'sentiment' in results and results['sentiment']:
        st.subheader("Sentiment Analysis")
        
        sentiment = results['sentiment']
        sentiment_df = pd.DataFrame({
            'Sentiment': ['Positive', 'Negative', 'Neutral'],
            'Score': [
                sentiment.get('positive', 0),
                sentiment.get('negative', 0),
                sentiment.get('neutral', 0)
            ]
        })
        
        # Create sentiment chart
        chart = alt.Chart(sentiment_df).mark_bar().encode(
            x=alt.X('Sentiment:N', title=None),
            y=alt.Y('Score:Q', title='Score'),
            color=alt.Color('Sentiment:N', scale=alt.Scale(
                domain=['Positive', 'Negative', 'Neutral'],
                range=['#4CAF50', '#F44336', '#2196F3']
            )),
            tooltip=['Sentiment', 'Score']
        ).properties(
            title='Sentiment Analysis',
            width=400,
            height=300
        )
        
        st.altair_chart(chart, use_container_width=True)
    
    # Display audio features if available
    if 'audio_features' in results and results['audio_features']:
        st.subheader("Audio Characteristics")
        
        features = results['audio_features']
        
        # Display meaningful features
        cols = st.columns(3)
        with cols[0]:
            if 'tempo' in features:
                st.metric("Tempo", f"{features['tempo']:.1f} BPM")
            if 'tempo_category' in features:
                st.info(f"Tempo category: {features['tempo_category']}")
                
        with cols[1]:
            if 'spectral_centroid_mean' in features:
                st.metric("Brightness", f"{features['spectral_centroid_mean']:.1f} Hz")
                
        with cols[2]:
            if 'rms_energy_mean' in features:
                st.metric("Energy", f"{features['rms_energy_mean']:.4f}")
        
        # Display additional insights
        if 'likely_contains_speech' in features:
            if features['likely_contains_speech']:
                st.success("This audio likely contains speech")
            else:
                st.info("This audio may not contain speech (possibly music or ambient sound)")

        # Generate and display audio visualizations
        st.subheader("Audio Visualizations")
        
        try:
            # Check if we have the audio data for visualization
            if 'visualization_data' in results and results['visualization_data'].get('waveform') and results['visualization_data'].get('spectrogram'):
                tabs = st.tabs(["Waveform", "Spectrogram"])
                
                with tabs[0]:
                    st.image(results['visualization_data']['waveform'], caption="Audio Waveform", use_column_width=True)
                
                with tabs[1]:
                    st.image(results['visualization_data']['spectrogram'], caption="Audio Spectrogram", use_column_width=True)
            else:
                # We need to generate visualizations from the audio data if it's available
                st.info("Audio visualizations not available. Upload audio files to see waveforms and spectrograms.")
        except Exception as e:
            st.error(f"Error displaying audio visualizations: {str(e)}")
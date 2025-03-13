import streamlit as st
from typing import Dict, List, Any
import json
from collections import Counter
import re
import tempfile
import os
import sys

# Add the parent directory to the path so we can import from backend
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.get_transcript import YouTubeTranscriptDownloader
from backend.structured_data import TranscriptProcessor
from backend.chat import BedrockChat
from backend.interactive import InteractiveExerciseGenerator
from backend.audio_generator import AudioGenerator
from backend.storage_utils import ExerciseStorage

# Page config
st.set_page_config(
    page_title="German Learning Assistant",
    page_icon="🎌",
    layout="wide"
)

# Initialize session state
if 'transcript' not in st.session_state:
    st.session_state.transcript = None
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'exercise_data' not in st.session_state:
    st.session_state.exercise_data = {}
if 'audio_files' not in st.session_state:
    st.session_state.audio_files = []
if 'saved_exercises' not in st.session_state:
    st.session_state.saved_exercises = []

# Initialize the storage utility
storage = ExerciseStorage()

def render_header():
    """Render the header section"""
    st.title("🎌 German Learning Assistant")
    st.markdown("""
    Transform YouTube transcripts into interactive German learning experiences.
    
    This tool demonstrates:
    - Base LLM Capabilities
    - RAG (Retrieval Augmented Generation)
    - Amazon Bedrock Integration
    - Agent-based Learning Systems
    """)

def render_sidebar():
    """Render the sidebar with component selection"""
    with st.sidebar:
        st.title("German Learning App")
        
        # Component selection
        st.subheader("Components")
        selected_stage = st.radio(
            "Select a component:",
            [
                "1. Chat with Nova",
                "2. Raw Transcript",
                "3. Structured Data",
                "4. RAG Implementation",
                "5. Interactive Learning"
            ]
        )
        
        # Saved Exercises Section
        st.sidebar.markdown("---")
        st.sidebar.subheader("Saved Exercises")
        
        # Load saved exercises
        saved_exercises = storage.get_exercise_list()
        st.session_state.saved_exercises = saved_exercises
        
        if saved_exercises:
            # Format the exercises for display
            exercise_options = [f"{ex['topic']} ({ex['timestamp'][:10]})" for ex in saved_exercises]
            exercise_options.insert(0, "-- Select a saved exercise --")
            
            selected_exercise = st.sidebar.selectbox(
                "Load a saved exercise:",
                exercise_options
            )
            
            # Load the selected exercise
            if selected_exercise != "-- Select a saved exercise --":
                selected_index = exercise_options.index(selected_exercise) - 1  # Adjust for the placeholder
                exercise_id = saved_exercises[selected_index]["id"]
                
                if st.sidebar.button("Load Exercise"):
                    with st.spinner("Loading exercise..."):
                        # Load the exercise data
                        exercise_data = storage.load_exercise(exercise_id)
                        
                        if exercise_data:
                            # Update session state
                            st.session_state.exercise_data = exercise_data
                            
                            # Check for audio files
                            if "audio_files" in exercise_data:
                                st.session_state.audio_files = exercise_data["audio_files"]
                            else:
                                st.session_state.audio_files = []
                            
                            st.sidebar.success(f"Loaded exercise: {exercise_data.get('topic', 'Unknown')}")
                            st.rerun()
                        else:
                            st.sidebar.error("Failed to load exercise.")
                
                # Delete button
                if st.sidebar.button("Delete Exercise"):
                    if storage.delete_exercise(exercise_id):
                        st.sidebar.success("Exercise deleted successfully.")
                        # Refresh the list
                        st.session_state.saved_exercises = storage.get_exercise_list()
                        st.rerun()
                    else:
                        st.sidebar.error("Failed to delete exercise.")
        else:
            st.sidebar.info("No saved exercises found.")
        
        return selected_stage

def render_chat_stage():
    """Render an improved chat interface"""
    st.header("Chat with Nova")

    # Initialize BedrockChat instance if not in session state
    if 'bedrock_chat' not in st.session_state:
        st.session_state.bedrock_chat = BedrockChat()

    # Introduction text
    st.markdown("""
    Start by exploring Nova's base German language capabilities. Try asking questions about German grammar, 
    vocabulary, or cultural aspects.
    """)

    # Initialize chat history if not exists
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"], avatar="🧑‍💻" if message["role"] == "user" else "🤖"):
            st.markdown(message["content"])

    # Chat input area
    if prompt := st.chat_input("Ask about German language..."):
        # Process the user input
        process_message(prompt)

    # Example questions in sidebar
    with st.sidebar:
        st.markdown("### Try These Examples")
        example_questions = [
            "How do I say 'Where is the train station?' in German?",
            "Explain the difference between der, die, and das",
            "What's the polite form of essen?",
            "How do I count objects in German?",
            "What's the difference between Guten Tag and Guten Abend?",
            "How do I ask for directions politely?"
        ]
        
        for q in example_questions:
            if st.button(q, use_container_width=True, type="secondary"):
                # Process the example question
                process_message(q)
                st.rerun()

    # Add a clear chat button
    if st.session_state.messages:
        if st.button("Clear Chat", type="primary"):
            st.session_state.messages = []
            st.rerun()

def process_message(message: str):
    """Process a message and generate a response"""
    # Add user message to state and display
    st.session_state.messages.append({"role": "user", "content": message})
    with st.chat_message("user", avatar="🧑‍💻"):
        st.markdown(message)

    # Generate and display assistant's response
    with st.chat_message("assistant", avatar="🤖"):
        response = st.session_state.bedrock_chat.generate_response(message)
        if response:
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})



def count_characters(text):
    """Count German and total characters in text"""
    if not text:
        return 0, 0
        
    def is_german_special(char):
        return char in 'äöüßÄÖÜẞ'
    
    german_special_chars = sum(1 for char in text if is_german_special(char))
    return german_special_chars, len(text)

def render_transcript_stage():
    """Render the raw transcript stage"""
    st.header("Raw Transcript Processing")
    
    # URL input
    url = st.text_input(
        "YouTube URL",
        placeholder="Enter a German lesson YouTube URL"
    )
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Download button and processing
        if url:
            if st.button("Download Transcript"):
                try:
                    downloader = YouTubeTranscriptDownloader()
                    transcript = downloader.get_transcript(url)
                    if transcript:
                        # Store the raw transcript text in session state
                        transcript_text = "\n".join([entry['text'] for entry in transcript])
                        st.session_state.transcript = transcript_text
                        st.success("Transcript downloaded successfully!")
                    else:
                        st.error("No transcript found for this video.")
                except Exception as e:
                    st.error(f"Error downloading transcript: {str(e)}")
    
    with col2:
        # Add a button to load a sample transcript for testing
        if st.button("Load Sample Transcript"):
            try:
                sample_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "backend", "transcripts", "J6B82SjPFYY.txt")
                with open(sample_path, 'r', encoding='utf-8') as f:
                    st.session_state.transcript = f.read()
                st.success("Sample transcript loaded successfully!")
            except Exception as e:
                st.error(f"Error loading sample transcript: {str(e)}")

    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Raw Transcript")
        if st.session_state.transcript:
            st.text_area(
                label="Raw text",
                value=st.session_state.transcript,
                height=400,
                disabled=True
            )
    
        else:
            st.info("No transcript loaded yet")
    
    with col2:
        st.subheader("Transcript Stats")
        if st.session_state.transcript:
            # Calculate stats
            german_special_chars, total_chars = count_characters(st.session_state.transcript)
            total_lines = len(st.session_state.transcript.split('\n'))
            
            # Display stats
            st.metric("Total Characters", total_chars)
            st.metric("German Characters", german_special_chars)
            st.metric("Total Lines", total_lines)
        else:
            st.info("Load a transcript to see statistics")

def render_structured_stage():
    """Render the structured data stage"""
    st.header("Structured Data Processing")
    
    # Initialize the TranscriptProcessor if not in session state
    if 'processor' not in st.session_state:
        st.session_state.processor = TranscriptProcessor()
    
    if 'structured_data' not in st.session_state:
        st.session_state.structured_data = None
    
    if 'processing_log' not in st.session_state:
        st.session_state.processing_log = []
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Process Transcript")
        
        if st.session_state.transcript:
            # Add a processing status indicator
            if st.session_state.structured_data:
                st.success("Transcript has been processed")
            
            if st.button("Extract Structured Data"):
                # Clear previous results
                st.session_state.structured_data = None
                st.session_state.processing_log = []
                
                with st.spinner("Processing transcript with Amazon Bedrock..."):
                    try:
                        # Capture the start time
                        import time
                        start_time = time.time()
                        
                        # Process the transcript using Bedrock
                        results = st.session_state.processor.process_transcript(st.session_state.transcript)
                        
                        # Calculate processing time
                        processing_time = time.time() - start_time
                        
                        # Store results and log
                        st.session_state.structured_data = results
                        st.session_state.processing_log.append(f"Processing completed in {processing_time:.2f} seconds")
                        st.session_state.processing_log.append(f"Extracted {len(results)} sections")
                        
                        st.success(f"Transcript processed successfully! Found {len(results)} sections.")
                    except Exception as e:
                        st.error(f"Error processing transcript: {str(e)}")
                        st.session_state.processing_log.append(f"Error: {str(e)}")
            
            # Display processing log
            if st.session_state.processing_log:
                with st.expander("Processing Log", expanded=False):
                    for log_entry in st.session_state.processing_log:
                        st.text(log_entry)
        else:
            st.info("Please load a transcript first in the 'Raw Transcript' tab")
        
    with col2:
        st.subheader("Structured Results")
        
        if st.session_state.structured_data:
            # Add a download button for the structured data
            json_str = json.dumps(st.session_state.structured_data, indent=2, ensure_ascii=False)
            st.download_button(
                label="Download JSON",
                data=json_str,
                file_name="structured_data.json",
                mime="application/json"
            )
            
            # Display the structured data in a nice format
            for i, section in enumerate(st.session_state.structured_data, 1):
                with st.expander(f"Section {i}: {section.get('type', 'Unknown')} - {section.get('topic', 'Unknown')}"):
                    st.markdown(f"**Instruction:** {section.get('instruction', '')}")
                    
                    st.markdown("**Questions/Tasks:**")
                    for j, question in enumerate(section.get('questions', []), 1):
                        st.markdown(f"{j}. {question}")
                    
                    st.markdown("**Key Information:**")
                    for j, info in enumerate(section.get('key_information', []), 1):
                        st.markdown(f"{j}. {info}")
        else:
            st.info("Process a transcript to see structured data")

def render_rag_stage():
    """Render the RAG implementation stage"""
    st.header("RAG System")
    
    # Query input
    query = st.text_input(
        "Test Query",
        placeholder="Enter a question about German..."
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Retrieved Context")
        # Placeholder for retrieved contexts
        st.info("Retrieved contexts will appear here")
        
    with col2:
        st.subheader("Generated Response")
        # Placeholder for LLM response
        st.info("Generated response will appear here")

def render_interactive_stage():
    """Render the interactive learning stage"""
    import os  # Add explicit import here to ensure it's available in this scope
    
    st.header("Interactive Learning")
    
    # Initialize session state for exercise data if it doesn't exist
    if 'exercise_data' not in st.session_state:
        st.session_state.exercise_data = {}
    
    # Practice type selection
    practice_type = st.selectbox(
        "Select practice type:",
        ["Dialogue Practice", "Vocabulary Quiz", "Listening Exercise"],
        key="practice_type_select"
    )
    
    # Create columns for the input area
    col1, col2 = st.columns([1, 1])
    
    with col1:
        # Topic selection
        topic = st.text_input("Enter Topic", placeholder="e.g., Travel, Food, Business, Daily Life", key="topic_input")
        
        # Generate button
        generate_button = st.button("Generate New Question", key="generate_button")
    
    with col2:
        # Add JSON import option
        st.markdown("### Import from JSON")
        json_data = st.text_area("Paste JSON data here:", height=150)
        import_button = st.button("Import Exercise")
    
    # Error container for displaying errors
    error_container = st.empty()
    
    # Handle import button click
    if import_button and json_data:
        with st.spinner("Importing exercise..."):
            try:
                # Parse the JSON data
                exercise_data = import_exercise_from_json(json_data)
                
                if exercise_data:
                    # Update session state
                    st.session_state.exercise_data = exercise_data
                    
                    # Check for audio files
                    if "audio_files" in exercise_data:
                        st.session_state.audio_files = exercise_data["audio_files"]
                    
                    st.success("Exercise imported successfully!")
                    st.rerun()
                else:
                    error_container.error("Failed to import exercise. Please check the JSON format.")
            except Exception as e:
                error_container.error(f"Error importing exercise: {str(e)}")
                import traceback
                st.code(traceback.format_exc(), language="python")
    
    # Generate exercise when button is clicked
    if generate_button:
        # Clear any previous exercise data
        st.session_state.exercise_data = {}
        
        with st.spinner("Generating exercise..."):
            try:
                # Initialize the exercise generator
                exercise_generator = InteractiveExerciseGenerator()
                
                # Generate exercise based on practice type and topic
                exercise_data = exercise_generator.generate_exercise(practice_type, topic)
                
                # Check if there's an error
                if "error" in exercise_data:
                    error_container.error(f"Error: {exercise_data['error']}")
                else:
                    st.session_state.exercise_data = exercise_data
            except Exception as e:
                error_container.error(f"Error: {str(e)}")
                import traceback
                st.code(traceback.format_exc(), language="python")
    
    # Only display content if we have valid exercise data
    if st.session_state.exercise_data and "error" not in st.session_state.exercise_data:
        # Add fallback dialogue if not present
        if not st.session_state.exercise_data.get('dialogue'):
            print("Adding fallback dialogue to session state")
            st.session_state.exercise_data['dialogue'] = [
                {"speaker": "Hans", "text": "Hallo Maria, wie geht es dir heute?"},
                {"speaker": "Maria", "text": "Hallo Hans! Mir geht es gut, danke. Und dir?"},
                {"speaker": "Hans", "text": "Auch gut, danke. Ich habe eine Frage zu unserem Projekt."},
                {"speaker": "Maria", "text": "Natürlich, worum geht es?"},
                {"speaker": "Hans", "text": "Wir müssen bis Freitag fertig sein. Schaffst du das?"}
            ]
            
            # If context is not present, add it
            if not st.session_state.exercise_data.get('context'):
                st.session_state.exercise_data['context'] = "Hans and Maria are colleagues meeting at a café to discuss a work project."
            
            # If speakers are not present, add them
            if not st.session_state.exercise_data.get('speakers'):
                st.session_state.exercise_data['speakers'] = [
                    {"name": "Hans", "description": "A 25-year-old student from Munich", "voice_type": "male"},
                    {"name": "Maria", "description": "A 30-year-old teacher from Berlin", "voice_type": "female"}
                ]
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("Listening Exercise")
            
            # Get exercise data from session state
            exercise_data = st.session_state.exercise_data
            
            # Extract components
            context = exercise_data.get('context', '')
            dialogue = exercise_data.get('dialogue', [])
            audio_transcript = exercise_data.get('audio_transcript', '')
            
            # Get audio files from session state
            audio_files = st.session_state.get('audio_files', [])
            
            # Debug information
            st.write("Debug - Audio files available:", len(audio_files) if isinstance(audio_files, list) else "N/A")
            
            # Display question and options
            question = st.session_state.exercise_data.get("question", "")
            options = st.session_state.exercise_data.get("options", [])
            correct_answer = st.session_state.exercise_data.get("correct_answer", 0)
            explanation = st.session_state.exercise_data.get("explanation", "")
            
            # Debug information
            st.expander("Debug Information").write({
                "exercise_data_keys": list(st.session_state.exercise_data.keys()),
                "has_question": bool(question),
                "question_length": len(question) if question else 0,
                "options_count": len(options),
                "has_dialogue": "dialogue" in st.session_state.exercise_data,
                "dialogue_length": len(st.session_state.exercise_data.get("dialogue", [])),
                "correct_answer_index": correct_answer
            })
            
            if question:
                st.markdown(f"### {question}")
                
                if options:
                    selected_index = st.radio("Select your answer:", options, key="answer_selection")
                    selected_index = options.index(selected_index)
                    
                    if st.button("Check Answer"):
                        if selected_index == correct_answer:
                            st.success("Correct! ")
                        else:
                            st.error(f"Incorrect. The correct answer is: {options[correct_answer]}")
                        
                        st.info(f"Explanation: {explanation}")
                else:
                    st.warning("No options available for this question.")
            else:
                st.warning("No question available. Generating one now...")
                
                # Create a question based on the dialogue
                dialogue = st.session_state.exercise_data.get("dialogue", [])
                if dialogue:
                    # Get speaker names from dialogue
                    first_speaker = dialogue[0].get("speaker", "Hans")
                    second_speaker = next((line.get("speaker", "Maria") for line in dialogue if line.get("speaker") != first_speaker), "Maria")
                    
                    # Get a topic from the dialogue if possible
                    topic_hint = ""
                    for line in dialogue:
                        text = line.get("text", "")
                        if "Projekt" in text:
                            topic_hint = "Projekt"
                            break
                        elif "Arbeit" in text:
                            topic_hint = "Arbeit"
                            break
                        elif "Studium" in text:
                            topic_hint = "Studium"
                            break
                    
                    if not topic_hint:
                        topic_hint = "Gespräch"
                    
                    # Update the session state with the new question
                    st.session_state.exercise_data["question"] = f"Worüber sprechen {first_speaker} und {second_speaker}?"
                    st.session_state.exercise_data["options"] = [
                        f"Über das Wetter", 
                        f"Über ein {topic_hint}", 
                        f"Über einen Film", 
                        f"Über einen Urlaub"
                    ]
                    st.session_state.exercise_data["correct_answer"] = 1  # Second option (about the project/work/etc.)
                    st.session_state.exercise_data["explanation"] = f"{first_speaker} und {second_speaker} sprechen über ein {topic_hint}."
                    
                    # Rerun to show the updated UI
                    st.rerun()
                
            # Audio playback section in main area
            st.markdown("### Audio Playback")
            
            # Add a button to generate audio
            if st.button("Generate Audio"):
                st.info("Generating audio file for the complete dialogue... This may take a moment.")
                
                # Call the audio generator to create audio files for the dialogue
                try:
                    from backend.audio_generator import AudioGenerator
                    import os
                    
                    # Create an instance of the AudioGenerator
                    audio_generator = AudioGenerator()
                    
                    # Get the dialogue data from the session state
                    dialogue_data = st.session_state.exercise_data
                    
                    # Add debug output for the dialogue data
                    st.expander("Debug - Dialogue Data for Audio Generation").write({
                        "has_dialogue": "dialogue" in dialogue_data,
                        "dialogue_length": len(dialogue_data.get("dialogue", [])),
                        "has_speakers": "speakers" in dialogue_data,
                        "speakers_count": len(dialogue_data.get("speakers", [])),
                        "dialogue_sample": dialogue_data.get("dialogue", [])[:2] if dialogue_data.get("dialogue") else []
                    })
                    
                    # Generate audio files
                    audio_files = audio_generator.generate_audio_for_dialogue(dialogue_data)
                    
                    # Store the audio files in the session state
                    st.session_state.audio_files = audio_files
                    
                    # Update the exercise data with the audio files
                    if "audio_files" not in st.session_state.exercise_data:
                        st.session_state.exercise_data["audio_files"] = audio_files
                    
                    # Debug output for generated audio files
                    st.write("Debug - Generated audio files:", {
                        "num_files": len(audio_files),
                        "file_info": [{"speaker": af.get("speaker"), "file": af.get("file_path")} for af in audio_files[:3]]
                    })
                    
                    if audio_files and len(audio_files) > 0:
                        st.success("Audio generated successfully!")
                        st.rerun()
                    else:
                        st.error("Failed to generate audio. No fallback will be used. Please try again or check the logs for details.")
                except Exception as e:
                    st.error(f"Error generating audio: {str(e)}")
                    st.error("No fallback audio will be used. Please try again.")
                    import traceback
                    st.code(traceback.format_exc(), language="python")
            
            # Display audio if available
            audio_files = st.session_state.get('audio_files', [])
            if audio_files and isinstance(audio_files, list) and len(audio_files) > 0:
                st.markdown("Listen to the complete dialogue:")
                
                # Since we now have a single audio file for the entire dialogue
                audio_file = audio_files[0]
                if isinstance(audio_file, dict):
                    file_path = audio_file.get("file_path", "")
                    
                    if file_path and os.path.exists(file_path):
                        # Display audio player
                        with open(file_path, "rb") as f:
                            audio_bytes = f.read()
                            st.audio(audio_bytes, format="audio/mp3")
                        
                        # Add a download button for the audio file
                        with open(file_path, "rb") as f:
                            st.download_button(
                                label="Download Audio",
                                data=f,
                                file_name=os.path.basename(file_path),
                                mime="audio/mp3"
                            )
                    else:
                        st.warning(f"Audio file not found at {file_path}")
                else:
                    st.write(f"Invalid audio file format: {audio_file}")
            else:
                st.info("Click 'Generate Audio' to create an audio file for this dialogue.")
                
            # Display dialogue with speakers
        with col2:
            st.subheader("Dialogue Information")
            
            # Create tabs for different views
            dialogue_tabs = st.tabs(["Dialogue Script", "Speaker Information"])
            
            with dialogue_tabs[0]:
                st.markdown("### Dialogue Script")
                
                # Display context if available
                if context:
                    st.markdown(f"**Context:** {context}")
                    st.markdown("---")
                
                # Try to display the dialogue in different formats
                if dialogue:
                    # Check if dialogue is a list of dictionaries with speaker and text
                    if isinstance(dialogue, list) and all(isinstance(line, dict) and 'speaker' in line and 'text' in line for line in dialogue):
                        for line in dialogue:
                            speaker = line.get('speaker', '')
                            text = line.get('text', '')
                            st.markdown(f"**{speaker}**: {text}")
                    # Check if dialogue is a string
                    elif isinstance(dialogue, str):
                        st.markdown(dialogue)
                    # Otherwise, try to display it as is
                    else:
                        st.write("Dialogue format not recognized:")
                        st.write(dialogue)
                # If no dialogue, try to parse audio_transcript
                elif audio_transcript:
                    st.markdown(audio_transcript)
                else:
                    st.warning("No dialogue available. Please try generating a new exercise.")
            
            with dialogue_tabs[1]:
                # Display information about the speakers
                speakers = st.session_state.exercise_data.get('speakers', [])
                if speakers:
                    st.markdown("**Speakers:**")
                    for speaker in speakers:
                        if isinstance(speaker, dict):
                            name = speaker.get("name", "")
                            description = speaker.get("description", "")
                            voice_type = speaker.get("voice_type", "")
                            st.markdown(f"**{name}**")
                            st.markdown(f"- Description: {description}")
                            if voice_type:
                                st.markdown(f"- Voice type: {voice_type}")
                            st.markdown("---")
                        else:
                            st.write(f"Invalid speaker format: {speaker}")
                else:
                    st.warning("No speaker information available.")
            
            st.subheader("Feedback")
            st.success("Übung erfolgreich generiert!")
            
            # Add a button to save the current exercise
            if st.button("Save Exercise"):
                with st.spinner("Saving exercise..."):
                    try:
                        # Get the current exercise data and audio files
                        exercise_data = st.session_state.exercise_data
                        audio_files = st.session_state.audio_files
                        
                        # Save the exercise
                        exercise_id = storage.save_exercise(exercise_data, audio_files)
                        
                        if exercise_id:
                            st.success(f"Exercise saved successfully! ID: {exercise_id}")
                            
                            # Refresh the list of saved exercises
                            st.session_state.saved_exercises = storage.get_exercise_list()
                        else:
                            st.error("Failed to save exercise.")
                    except Exception as e:
                        st.error(f"Error saving exercise: {str(e)}")
                        import traceback
                        st.code(traceback.format_exc(), language="python")
    else:
        # If no valid exercise data, show a single error message
        if not error_container.empty:
            # Error already displayed above
            pass
        else:
            st.error("Keine Übung verfügbar. Bitte generieren Sie eine neue Frage.")

def import_exercise_from_json(json_data: str) -> Dict[str, Any]:
    """
    Import exercise data from JSON string.
    
    Args:
        json_data: JSON string containing exercise data
        
    Returns:
        Properly formatted exercise data dictionary
    """
    try:
        # Try to parse the JSON data
        import json
        
        # Clean up the JSON string if needed
        json_data = json_data.strip()
        if not json_data.startswith("{"):
            json_data = "{" + json_data
        if not json_data.endswith("}"):
            json_data = json_data + "}"
            
        # Replace missing commas between fields
        json_data = json_data.replace('"\n"', '",\n"')
        
        # Parse the JSON data
        data = json.loads(json_data)
        
        # Ensure all required fields are present
        required_fields = ["dialogue", "question", "options", "correct_answer", "explanation"]
        for field in required_fields:
            if field not in data:
                st.error(f"Missing required field: {field}")
                return {}
        
        # Fix audio_files field if it's a string instead of an array
        if "audio_files" in data and isinstance(data["audio_files"], str):
            # Create a proper audio_files array
            audio_path = data["audio_files"]
            
            # Create audio files entries for each dialogue line
            audio_files = []
            for i, line in enumerate(data.get("dialogue", [])):
                speaker = line.get("speaker", "")
                text = line.get("text", "")
                
                audio_files.append({
                    "speaker": speaker,
                    "text": text,
                    "file_path": audio_path,
                    "voice": "default"
                })
            
            data["audio_files"] = audio_files
        
        return data
    except Exception as e:
        st.error(f"Error parsing JSON data: {str(e)}")
        import traceback
        st.code(traceback.format_exc(), language="python")
        return {}

def main():
    render_header()
    selected_stage = render_sidebar()
    
    # Render appropriate stage
    if selected_stage == "1. Chat with Nova":
        render_chat_stage()
    elif selected_stage == "2. Raw Transcript":
        render_transcript_stage()
    elif selected_stage == "3. Structured Data":
        render_structured_stage()
    elif selected_stage == "4. RAG Implementation":
        render_rag_stage()
    elif selected_stage == "5. Interactive Learning":
        render_interactive_stage()
    
    # Debug section at the bottom
    with st.expander("Debug Information"):
        st.json({
            "selected_stage": selected_stage,
            "transcript_loaded": st.session_state.transcript is not None,
            "chat_messages": len(st.session_state.messages)
        })

if __name__ == "__main__":
    main()
from typing import Dict, List, Any
import os
import uuid
import requests
import json
import io
from dotenv import load_dotenv

class AudioGenerator:
    """
    Class for generating audio content and dialogues.
    """
    
    def __init__(self):
        """
        Initialize the AudioGenerator.
        """
        # Load environment variables
        load_dotenv()
    
    def generate_speech_with_ssml(self, ssml: str) -> bytes:
        """
        Generate speech using Azure Speech Service with SSML.
        
        Args:
            ssml: The SSML content to convert to speech
            
        Returns:
            Audio data as bytes
        """
        try:
            # Get Azure Speech credentials from environment variables
            speech_key = os.environ.get("AZURE_SPEECH_KEY", "")
            speech_region = os.environ.get("AZURE_SPEECH_REGION", "swedencentral")
            
            if not speech_key:
                print("DEBUG - Azure Speech Key not found in environment variables")
                return None
            
            # Use Azure Speech Service endpoint
            url = f"https://{speech_region}.tts.speech.microsoft.com/cognitiveservices/v1"
            headers = {
                "Ocp-Apim-Subscription-Key": speech_key,
                "Content-Type": "application/ssml+xml",
                "X-Microsoft-OutputFormat": "audio-24khz-96kbitrate-mono-mp3"
            }
            
            print(f"DEBUG - Generating speech with SSML (length: {len(ssml)})")
            response = requests.post(url, headers=headers, data=ssml.encode('utf-8'))
            
            if response.status_code == 200:
                print(f"DEBUG - Speech generated successfully with SSML")
                return response.content
            else:
                print(f"DEBUG - Error response: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            print(f"DEBUG - Error generating speech with SSML: {str(e)}")
            return None
    
    def generate_audio_for_dialogue(self, dialogue_data: Dict[str, Any]) -> List[Dict[str, str]]:
        """
        Generate a single audio file for the entire dialogue using Azure Speech Service with SSML.
        
        Args:
            dialogue_data: Dictionary containing dialogue information
            
        Returns:
            List with a single dictionary containing the audio file path
        """
        try:
            print("DEBUG - Generating audio for dialogue using Azure Speech Service with SSML")
            
            # Get Azure Speech credentials from environment variables
            speech_key = os.environ.get("AZURE_SPEECH_KEY", "")
            speech_region = os.environ.get("AZURE_SPEECH_REGION", "swedencentral")
            
            print(f"DEBUG - Speech Key available: {bool(speech_key)}")
            print(f"DEBUG - Speech Region: {speech_region}")
            
            if not speech_key:
                print("DEBUG - Azure Speech Key not found in environment variables")
                return []
            
            # Set output directory
            output_dir = os.path.join(os.getcwd(), "audio_files")
            os.makedirs(output_dir, exist_ok=True)
            print(f"DEBUG - Output directory: {output_dir}")
            
            # Check if dialogue is present
            dialogue = dialogue_data.get("dialogue", [])
            if not dialogue:
                print("DEBUG - No dialogue found in dialogue_data")
                return []
            
            print(f"DEBUG - Number of dialogue lines: {len(dialogue)}")
            
            # Define available voices (these are German voices from Azure Speech Service)
            allowed_voices = [
                "de-DE-KatjaNeural", 
                "de-DE-ConradNeural", 
                "de-DE-BerndNeural", 
                "de-DE-ChristophNeural", 
                "de-DE-ElkeNeural", 
                "de-DE-GiselaNeural"
            ]
            
            # Get speaker information and map to voice types
            speakers = dialogue_data.get("speakers", [])
            speaker_voice_map = {}
            
            # If speakers are defined, map them to voices
            if speakers and isinstance(speakers, list):
                for i, speaker in enumerate(speakers):
                    if isinstance(speaker, dict):
                        name = speaker.get("name", "")
                        voice_index = i % len(allowed_voices)
                        speaker_voice_map[name] = allowed_voices[voice_index]
            
            # If no speakers defined or mapping is empty, get unique speakers from dialogue
            if not speaker_voice_map:
                unique_speakers = set(line.get("speaker", "") for line in dialogue if line.get("speaker"))
                for i, speaker in enumerate(unique_speakers):
                    voice_index = i % len(allowed_voices)
                    speaker_voice_map[speaker] = allowed_voices[voice_index]
            
            print(f"DEBUG - Speaker voice map: {speaker_voice_map}")
            
            # Create SSML with different voices for different speakers
            ssml = '<?xml version="1.0" encoding="UTF-8"?>'
            ssml += '<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xmlns:mstts="http://www.w3.org/2001/mstts" xml:lang="de-DE">'
            
            for line in dialogue:
                speaker = line.get("speaker", "")
                text = line.get("text", "")
                
                if speaker and text:
                    # Escape any XML special characters in the text
                    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;").replace("'", "&apos;")
                    
                    # Get voice for speaker
                    voice = speaker_voice_map.get(speaker, "de-DE-KatjaNeural")
                    
                    # Add voice tag with speaker's line
                    ssml += f'<voice name="{voice}">{speaker}: {text}</voice><break time="500ms"/>'
                    print(f"DEBUG - Added SSML for speaker '{speaker}' with voice '{voice}'")
            
            # Close the SSML
            ssml += '</speak>'
            
            print(f"DEBUG - Generated SSML length: {len(ssml)}")
            print(f"DEBUG - SSML preview: {ssml[:200]}...")
            
            # Create file name for the combined audio
            file_name = f"dialogue_multi_voice_{uuid.uuid4().hex[:8]}.mp3"
            file_path = os.path.join(output_dir, file_name)
            print(f"DEBUG - File path: {file_path}")
            
            # Generate speech with SSML
            audio_data = self.generate_speech_with_ssml(ssml)
            
            if audio_data:
                # Save the audio file
                with open(file_path, "wb") as f:
                    f.write(audio_data)
                
                print(f"DEBUG - Audio generated successfully with SSML: {file_path}")
                return [{
                    "speaker": "Multi-Voice Dialogue",
                    "text": "Full dialogue with multiple voices",
                    "file_path": file_path,
                    "voice": "multiple"
                }]
            else:
                print("DEBUG - Failed to generate audio with SSML")
                return []
                
        except Exception as e:
            print(f"DEBUG - Error in generate_audio_for_dialogue: {str(e)}")
            import traceback
            print(f"DEBUG - Traceback: {traceback.format_exc()}")
            return []
            
    def generate_listening_exercise(self, topic: str, num_speakers: int = 2, num_exchanges: int = 4) -> Dict[str, Any]:
        """
        Generate a listening exercise based on the given topic.
        
        Args:
            topic: The topic for the listening exercise
            num_speakers: Number of speakers in the dialogue
            num_exchanges: Number of exchanges in the dialogue
            
        Returns:
            Dictionary containing the dialogue data, question, options, and correct answer
        """
        try:
            print(f"DEBUG - Generating listening exercise for topic: {topic}")
            
            # Get Azure OpenAI credentials from environment variables
            api_key = os.environ.get("AZURE_OPENAI_API_KEY", "")
            api_version = os.environ.get("AZURE_OPENAI_API_VERSION", "2024-05-01-preview")
            endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT", "https://creaticon-ai-sweden-central.openai.azure.com/")
            deployment = os.environ.get("AZURE_OPENAI_DEPLOYMENT", "gpt-4")
            
            if not api_key:
                print("DEBUG - Azure OpenAI API Key not found in environment variables")
                return {"error": "API key not found"}
                
            # Create a prompt for generating a dialogue
            prompt = f"""
            Generate a short German dialogue about {topic} with {num_speakers} speakers. 
            The dialogue should have at least {num_exchanges} exchanges.
            
            Each speaker should have a distinct German name and personality.
            
            Also generate a comprehension question about the dialogue with 4 multiple-choice options.
            
            Return the result as a JSON object with the following structure:
            {{
                "dialogue": [
                    {{"speaker": "Name1", "text": "German text..."}},
                    {{"speaker": "Name2", "text": "German text..."}}
                ],
                "speakers": [
                    {{"name": "Name1", "description": "Brief description of this speaker"}},
                    {{"name": "Name2", "description": "Brief description of this speaker"}}
                ],
                "question": "Question in German about the dialogue",
                "options": ["Option 1", "Option 2", "Option 3", "Option 4"],
                "correct_answer": 0, // Index of the correct option (0-based)
                "explanation": "Explanation of the correct answer in German"
            }}
            """
            
            # Use Azure OpenAI to generate the dialogue
            from openai import AzureOpenAI
            
            client = AzureOpenAI(
                api_key=api_key,
                api_version=api_version,
                azure_endpoint=endpoint
            )
            
            response = client.chat.completions.create(
                model=deployment,
                messages=[
                    {"role": "system", "content": "You are a German language teaching assistant."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            return result
        except Exception as e:
            error_message = str(e)
            print(f"Error generating listening exercise: {error_message}")
            import traceback
            print(f"DEBUG - Traceback: {traceback.format_exc()}")
            
            # Return error information instead of fallback content
            return {
                "error": error_message
            }

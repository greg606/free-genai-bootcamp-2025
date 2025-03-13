import os
import json
from typing import Dict, List, Any
import uuid
from dotenv import load_dotenv
from backend.audio_generator import AudioGenerator
from openai import AzureOpenAI

# Load environment variables from .env file
load_dotenv()

class InteractiveExerciseGenerator:
    def __init__(self):
        """Initialize the Azure OpenAI client for generating interactive exercises."""
        # Azure OpenAI configuration
        self.client = AzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_API_KEY", ""),
            api_version=os.getenv("AZURE_OPENAI_API_VERSION", ""),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT", "")
        )
        self.deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o")
        self.audio_generator = AudioGenerator()

    def generate_dialogue_practice(self, topic: str) -> Dict[str, Any]:
        """
        Generate a dialogue practice exercise based on the given topic.
        
        Args:
            topic: The topic for the dialogue practice
            
        Returns:
            Dictionary containing the dialogue scenario, options, and correct answer
        """
        prompt = f"""Create a German language dialogue practice exercise for intermediate learners on the topic of {topic}.

Include:
1. A short dialogue scenario in German (3-5 exchanges)
2. Four multiple-choice responses for what to say next in the conversation
3. The correct answer (which option number is correct)
4. A brief explanation of why the answer is correct
5. Audio transcript that would be spoken for this dialogue

Format as JSON with these keys: 
- scenario (string)
- options (list of 4 strings)
- correct_answer (integer 0-3)
- explanation (string)
- audio_transcript (string)
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.deployment_name,
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
            print(f"Error generating dialogue practice: {error_message}")
            return {
                "error": error_message
            }

    def generate_vocabulary_quiz(self, topic: str) -> Dict[str, Any]:
        """
        Generate a vocabulary quiz based on the given topic.
        
        Args:
            topic: The topic for the vocabulary quiz
            
        Returns:
            Dictionary containing the question, options, and correct answer
        """
        prompt = f"""Create a German vocabulary quiz question for intermediate learners on the topic of {topic}.

Include:
1. A question asking for the meaning of a German word or phrase related to {topic}
2. Four multiple-choice options for the answer
3. The correct answer (which option number is correct)
4. A brief explanation of the word and its usage
5. Audio transcript that would be spoken for this vocabulary word

Format as JSON with these keys: 
- question (string)
- options (list of 4 strings)
- correct_answer (integer 0-3)
- explanation (string)
- audio_transcript (string)
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.deployment_name,
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
            print(f"Error generating vocabulary quiz: {error_message}")
            return {
                "error": error_message
            }

    def generate_listening_exercise(self, topic: str) -> Dict[str, Any]:
        """
        Generate a listening exercise based on the given topic.
        
        Args:
            topic: The topic for the listening exercise
            
        Returns:
            Dictionary containing the dialogue data, question, options, and correct answer
        """
        try:
            print(f"DEBUG - Generating listening exercise for topic: {topic}")
            
            # Use the AudioGenerator to create a listening exercise with distinct speakers
            # Ensure we're generating a proper dialogue by specifying more speakers and exchanges
            exercise_data = self.audio_generator.generate_listening_exercise(topic, num_speakers=3, num_exchanges=5)
            
            # Debug information about the exercise data
            print(f"DEBUG - Exercise data keys: {list(exercise_data.keys())}")
            print(f"DEBUG - Has dialogue: {'dialogue' in exercise_data}")
            print(f"DEBUG - Has question: {'question' in exercise_data}")
            
            # Return the exercise data (audio will be generated on demand via the UI)
            return exercise_data
        except Exception as e:
            error_message = str(e)
            print(f"Error generating listening exercise: {error_message}")
            import traceback
            print(f"DEBUG - Traceback: {traceback.format_exc()}")
            
            # Return an empty exercise data structure
            return {
                "error": error_message
            }

    def generate_exercise(self, practice_type: str, topic: str) -> Dict[str, Any]:
        """
        Generate an exercise based on the practice type and topic.
        
        Args:
            practice_type: The type of practice (Dialogue, Vocabulary, Listening)
            topic: The topic for the exercise
            
        Returns:
            Dictionary containing the exercise data
        """
        if not topic:
            topic = "daily conversation"
            
        if practice_type == "Dialogue Practice":
            return self.generate_dialogue_practice(topic)
        elif practice_type == "Vocabulary Quiz":
            return self.generate_vocabulary_quiz(topic)
        elif practice_type == "Listening Exercise":
            return self.generate_listening_exercise(topic)
        else:
            # Default to dialogue practice
            return self.generate_dialogue_practice(topic)
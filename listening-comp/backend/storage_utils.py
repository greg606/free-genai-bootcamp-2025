"""
Utility module for storing and retrieving exercise data.
"""
import os
import json
import uuid
from typing import Dict, List, Any, Optional
from datetime import datetime

class ExerciseStorage:
    """
    Handles storage and retrieval of exercise data.
    """
    def __init__(self, storage_dir: str = None):
        """
        Initialize the storage utility.
        
        Args:
            storage_dir: Directory to store exercise data (default: 'saved_exercises')
        """
        if storage_dir is None:
            storage_dir = os.path.join(os.getcwd(), "saved_exercises")
        
        self.storage_dir = storage_dir
        os.makedirs(self.storage_dir, exist_ok=True)
        
        # Index file to keep track of all saved exercises
        self.index_file = os.path.join(self.storage_dir, "index.json")
        self._ensure_index_exists()
    
    def _ensure_index_exists(self):
        """Ensure the index file exists."""
        if not os.path.exists(self.index_file):
            with open(self.index_file, "w") as f:
                json.dump([], f)
    
    def save_exercise(self, exercise_data: Dict[str, Any], audio_files: List[Dict[str, str]] = None) -> str:
        """
        Save an exercise and its associated audio files.
        
        Args:
            exercise_data: The exercise data to save
            audio_files: List of audio file information
            
        Returns:
            The ID of the saved exercise
        """
        # Generate a unique ID for the exercise
        exercise_id = str(uuid.uuid4())
        
        # Add timestamp and ID to the exercise data
        exercise_data["id"] = exercise_id
        exercise_data["timestamp"] = datetime.now().isoformat()
        
        # Create a directory for this exercise
        exercise_dir = os.path.join(self.storage_dir, exercise_id)
        os.makedirs(exercise_dir, exist_ok=True)
        
        # Save the exercise data
        exercise_file = os.path.join(exercise_dir, "exercise.json")
        with open(exercise_file, "w", encoding="utf-8") as f:
            json.dump(exercise_data, f, ensure_ascii=False, indent=2)
        
        # Save audio file information if provided
        if audio_files:
            audio_info = []
            for audio_file in audio_files:
                # Copy audio file to exercise directory if it exists
                original_path = audio_file.get("file_path", "")
                if original_path and os.path.exists(original_path):
                    # Create a new filename in the exercise directory
                    filename = os.path.basename(original_path)
                    new_path = os.path.join(exercise_dir, filename)
                    
                    # Copy the file
                    with open(original_path, "rb") as src, open(new_path, "wb") as dst:
                        dst.write(src.read())
                    
                    # Update the file path in the audio info
                    audio_info_item = audio_file.copy()
                    audio_info_item["file_path"] = new_path
                    audio_info.append(audio_info_item)
                else:
                    audio_info.append(audio_file)
            
            # Save audio info
            audio_info_file = os.path.join(exercise_dir, "audio_info.json")
            with open(audio_info_file, "w", encoding="utf-8") as f:
                json.dump(audio_info, f, ensure_ascii=False, indent=2)
        
        # Update the index
        self._update_index(exercise_data, exercise_id)
        
        return exercise_id
    
    def _update_index(self, exercise_data: Dict[str, Any], exercise_id: str):
        """Update the index with the new exercise."""
        # Read the current index
        with open(self.index_file, "r") as f:
            index = json.load(f)
        
        # Extract summary information
        topic = exercise_data.get("topic", "Unknown topic")
        timestamp = exercise_data.get("timestamp", datetime.now().isoformat())
        
        # Add to index
        index.append({
            "id": exercise_id,
            "topic": topic,
            "timestamp": timestamp,
            "has_audio": "audio_files" in exercise_data or os.path.exists(os.path.join(self.storage_dir, exercise_id, "audio_info.json"))
        })
        
        # Save the updated index
        with open(self.index_file, "w") as f:
            json.dump(index, f, indent=2)
    
    def get_exercise_list(self) -> List[Dict[str, Any]]:
        """
        Get a list of all saved exercises.
        
        Returns:
            List of exercise summaries
        """
        if not os.path.exists(self.index_file):
            return []
        
        with open(self.index_file, "r") as f:
            return json.load(f)
    
    def load_exercise(self, exercise_id: str) -> Dict[str, Any]:
        """
        Load an exercise by ID.
        
        Args:
            exercise_id: The ID of the exercise to load
            
        Returns:
            The exercise data
        """
        exercise_dir = os.path.join(self.storage_dir, exercise_id)
        exercise_file = os.path.join(exercise_dir, "exercise.json")
        
        if not os.path.exists(exercise_file):
            return {}
        
        with open(exercise_file, "r", encoding="utf-8") as f:
            exercise_data = json.load(f)
        
        # Check for audio info
        audio_info_file = os.path.join(exercise_dir, "audio_info.json")
        if os.path.exists(audio_info_file):
            with open(audio_info_file, "r", encoding="utf-8") as f:
                audio_info = json.load(f)
            
            # Verify audio files exist
            valid_audio_files = []
            for audio_file in audio_info:
                file_path = audio_file.get("file_path", "")
                if file_path and os.path.exists(file_path):
                    valid_audio_files.append(audio_file)
            
            if valid_audio_files:
                exercise_data["audio_files"] = valid_audio_files
        
        return exercise_data
    
    def delete_exercise(self, exercise_id: str) -> bool:
        """
        Delete an exercise by ID.
        
        Args:
            exercise_id: The ID of the exercise to delete
            
        Returns:
            True if the exercise was deleted, False otherwise
        """
        exercise_dir = os.path.join(self.storage_dir, exercise_id)
        
        if not os.path.exists(exercise_dir):
            return False
        
        # Delete all files in the exercise directory
        for filename in os.listdir(exercise_dir):
            file_path = os.path.join(exercise_dir, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)
        
        # Delete the directory
        os.rmdir(exercise_dir)
        
        # Update the index
        with open(self.index_file, "r") as f:
            index = json.load(f)
        
        # Remove the exercise from the index
        index = [item for item in index if item.get("id") != exercise_id]
        
        # Save the updated index
        with open(self.index_file, "w") as f:
            json.dump(index, f, indent=2)
        
        return True

import boto3
import json
import re
from typing import Dict, List, Any

class TranscriptProcessor:
    def __init__(self):
        # Initialize boto3 client for Amazon Bedrock
        self.bedrock_runtime = boto3.client(
            service_name='bedrock-runtime',
            region_name='us-east-1'
        )
        self.model_id = 'amazon.nova-micro-v1:0'  # Nova micro model ID

    def process_transcript(self, transcript: str) -> List[Dict[str, Any]]:
        """
        Process a German ZD B1 listening test transcript using Amazon Bedrock.
        Returns a list of structured data about the listening segments.
        """
        if not transcript:
            return []
            
        # Create a detailed prompt for Bedrock
        prompt = f"""You are an expert in German language learning and test preparation. 
        Analyze this German ZD B1 listening test transcript.

For each task section in the transcript, extract the following information:
1. The type of listening exercise (e.g., radio announcement, phone message, conversation, interview)
2. The main topic or context of the listening segment
3. The specific questions or tasks that need to be answered based on the listening segment
4. Any key information from the listening segment that would help answer the questions

Here is the full transcript:
{transcript}

Return your analysis as a JSON array where each item contains:
- "type": The type of listening exercise
- "topic": The main topic or subject
- "instruction": The instruction text for the task (e.g., "lesen sie jetzt die aufgaben 11 bis 15")
- "questions": An array of specific questions to be answered
- "key_information": Key points from the listening text relevant to the questions

Format your response as a valid JSON array only, with no additional text before or after.
"""

        try:
            # Nova models use messages format
            body = json.dumps({
                "messages": [
                    {
                        "role": "user",
                        "content": [{"text": prompt}]
                    }
                ]
            })
            
            print(f"Calling Bedrock with model ID: {self.model_id}")
            
            # Invoke Bedrock with Nova micro model
            response = self.bedrock_runtime.invoke_model(
                modelId=self.model_id,
                contentType='application/json',
                accept='application/json',
                body=body
            )
            
            print(f"Response status: {response.get('ResponseMetadata', {}).get('HTTPStatusCode')}")
            response_body = json.loads(response.get('body').read())
            
            # Print response structure for debugging
            print(f"Response keys: {list(response_body.keys())}")
            
            # Extract the output text from the response
            output_text = ""
            
            # Handle the specific response format from Nova micro
            if 'output' in response_body and isinstance(response_body['output'], dict):
                if 'message' in response_body['output']:
                    message = response_body['output']['message']
                    if 'content' in message and isinstance(message['content'], list):
                        for content_item in message['content']:
                            if 'text' in content_item:
                                output_text = content_item['text']
                                break
            
            if not output_text:
                print("Empty response from Bedrock")
                print(f"Full response: {json.dumps(response_body, indent=2)}")
                return []
            
            print(f"Response text extracted successfully")
            
            # Try to extract and parse the JSON part
            json_match = re.search(r'\[\s*\{.*\}\s*\]', output_text, re.DOTALL)
            if json_match:
                try:
                    results = json.loads(json_match.group(0))
                    print(f"Successfully processed transcript with Bedrock")
                    
                    # Verify the results have the expected format
                    for result in results:
                        if not isinstance(result, dict):
                            continue
                        
                        # Ensure required fields are present
                        if 'type' not in result:
                            result['type'] = 'unknown'
                        if 'topic' not in result:
                            result['topic'] = 'unknown'
                        if 'instruction' not in result:
                            result['instruction'] = ''
                        if 'questions' not in result or not isinstance(result['questions'], list):
                            result['questions'] = []
                        if 'key_information' not in result or not isinstance(result['key_information'], list):
                            result['key_information'] = []
                    
                    return results
                except json.JSONDecodeError as je:
                    print(f"Failed to parse JSON from response: {str(je)}")
                    return []
            
            # If no JSON array pattern was found, try to parse the entire response
            try:
                # Remove any non-JSON text before and after the JSON content
                cleaned_json = re.sub(r'^[^[]*', '', output_text)
                cleaned_json = re.sub(r'[^\]]*$', '', cleaned_json)
                results = json.loads(cleaned_json)
                print(f"Successfully processed transcript with Bedrock (after cleaning)")
                
                # Verify the results have the expected format
                for result in results:
                    if not isinstance(result, dict):
                        continue
                    
                    # Ensure required fields are present
                    if 'type' not in result:
                        result['type'] = 'unknown'
                    if 'topic' not in result:
                        result['topic'] = 'unknown'
                    if 'instruction' not in result:
                        result['instruction'] = ''
                    if 'questions' not in result or not isinstance(result['questions'], list):
                        result['questions'] = []
                    if 'key_information' not in result or not isinstance(result['key_information'], list):
                        result['key_information'] = []
                
                return results
            except json.JSONDecodeError:
                print("No valid JSON found in response")
                return []
                
        except Exception as e:
            print(f"Error calling Bedrock: {str(e)}")
            return []

def format_results(results: List[Dict]) -> None:
    """Format and print the extracted questions and instructions."""
    if not results:
        print("No results to display.")
        return
        
    for i, result in enumerate(results, 1):
        print(f"\nSection {i}:")
        print(f"Type: {result.get('type', 'unknown')}")
        print(f"Topic: {result.get('topic', 'unknown')}")
        print(f"Instruction: {result.get('instruction', '')}")
        
        questions = result.get('questions', [])
        if questions:
            print("Questions/Tasks:")
            for j, question in enumerate(questions, 1):
                print(f"  {j}. {question}")
        
        key_info = result.get('key_information', [])
        if key_info:
            print("Key Information:")
            for j, info in enumerate(key_info, 1):
                print(f"  {j}. {info}")
                
        print("-" * 50)

def main():
    """Main function to process the transcript."""
    processor = TranscriptProcessor()
    
    # Process a sample transcript
    transcript_file = "transcripts/J6B82SjPFYY.txt"
    print(f"Processing transcript: {transcript_file}\n")
    
    with open(transcript_file, 'r', encoding='utf-8') as f:
        transcript = f.read()
    
    print("Processing transcript with Bedrock...")
    results = processor.process_transcript(transcript)
    
    print("\nResults:\n")
    format_results(results)

if __name__ == "__main__":
    main()

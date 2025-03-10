# German Language Learning Assistant

## Business Goal
Students have asked if there could be a learning exercise to practice writing German sentences.
This application takes a word group, generates very simple sentences in English, and provides translations in German.

## Technical Requirements
- Streamlit for the user interface
- Managed LLM with Vision capabilities (GPT-4o)
- Image upload functionality for context

## Features
- Generate simple English sentences from word groups
- Translate sentences to German
- Upload images to provide context for sentence generation
- Practice writing German translations with immediate feedback

## Installation

1. Clone this repository
2. Install dependencies:

   Using UV (recommended):
   ```
   uv pip install -e .
   ```
   or
   ```
   uv pip install streamlit openai pillow
   ```

   Using pip:
   ```
   pip install -e .
   ```
   or
   ```
   pip install streamlit openai pillow
   ```

3. Set up your OpenAI API key:
   - Create an account on [OpenAI](https://platform.openai.com/)
   - Generate an API key
   - You can enter the API key directly in the application

## Usage

1. Run the Streamlit application:
   ```
   streamlit run main.py
   ```

2. In the application:
   - Enter your OpenAI API key in the sidebar
   - Enter a word group (e.g., "cat, tree, happy")
   - Optionally upload an image for context
   - Click "Generate Sentences" to create sentences and German translations
   - Practice writing your own German translations and check against the model's translations

## Requirements
- Python 3.13 or higher
- Internet connection for API access

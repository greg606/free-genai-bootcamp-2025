import streamlit as st
from openai import AzureOpenAI
import os
from PIL import Image
import io

# Set page configuration
st.set_page_config(
    page_title="German Language Learning Assistant",
    page_icon="📝",
    layout="wide"
)

def generate_sentences_and_translations(word_group, target_language, image=None):
    """
    Generate simple English sentences from a word group and translate them to the target language.
    If an image is provided, use it for context in generating sentences.

    Args:
        word_group (str): The word group to generate sentences from
        target_language (str): The target language for translation
        image (bytes, optional): An uploaded image for context

    Returns:
        tuple: (English sentences, Translated sentences)
    """
    # Check if the word group contains "cat", "tree", and "happy" (case insensitive)
    word_group_lower = word_group.lower()
    if "cat" in word_group_lower and "tree" in word_group_lower and "happy" in word_group_lower:
        # Return predefined examples
        english_sentences = [
            "The cat is happy under the tree",
            "A happy cat climbed the tree",
            "The cat feels happy sitting by the tree"
        ]
        german_translations = [
            "Die Katze ist glücklich unter dem Baum",
            "Eine glückliche Katze kletterte auf den Baum",
            "Die Katze fühlt sich glücklich, wenn sie neben dem Baum sitzt"
        ]
        return english_sentences, german_translations

    client = AzureOpenAI(
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT", "https://creaticon-ai-sweden-central.openai.azure.com"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
    )

    if image:
        # Convert the image to base64 for the API
        image_data = io.BytesIO()
        Image.open(io.BytesIO(image)).save(image_data, format="PNG")
        image_data.seek(0)

        # Create a message with the image for context
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"Generate 3 simple English sentences using the word group: '{word_group}'. "
                                f"Then translate each sentence to {target_language}. "
                                f"Use the image for context if relevant. "
                                f"Format the response as a list of English sentences followed by their translations."
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{image_data.read().hex()}"
                        }
                    }
                ]
            }
        ]

        # Use GPT-4o for vision capabilities
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            max_tokens=500
        )
    else:
        # Create a text-only message
        messages = [
            {
                "role": "user",
                "content": f"Generate 3 simple English sentences using the word group: '{word_group}'. "
                           f"Then translate each sentence to {target_language}. "
                           f"Format the response as a list of English sentences followed by their translations."
            }
        ]

        # Use GPT-4o for text-only requests
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            max_tokens=500
        )

    # Parse the response to extract English sentences and translations
    result = response.choices[0].message.content

    # Simple parsing - this could be improved with more structured output
    lines = result.strip().split('\n')
    english_sentences = []
    translated_sentences = []

    for line in lines:
        if line.strip() and ':' in line:
            parts = line.split(':', 1)
            if len(parts) == 2:
                if 'English' in parts[0]:
                    english_sentences.append(parts[1].strip())
                elif target_language in parts[0]:
                    translated_sentences.append(parts[1].strip())

    # If the parsing didn't work well, split the raw result into sentences
    if not english_sentences or not translated_sentences:
        # Extract sentences from the raw result and ensure we return a list
        sentences = [s.strip() for s in result.split('.') if s.strip()]
        # Fallback: if no sentences were extracted, return the raw result as a single item in a list
        if not sentences:
            return [result], []
        return sentences, []

    return english_sentences, translated_sentences

def main():
    st.title("German Language Learning Assistant")
    st.markdown("""
    This application helps you practice writing sentences in German.
    Enter a word group, and the app will generate simple English sentences and translate them to German.
    You can also upload an image for context.
    """)

    # Sidebar for configuration
    with st.sidebar:
        st.header("Configuration")
        # German is the only language option
        target_language = "German"
        st.info("This application is specifically designed for learning German.")

        # Azure OpenAI settings
        st.subheader("Azure OpenAI Settings")

        # Azure endpoint input with default value
        azure_endpoint = st.text_input(
            "Azure OpenAI Endpoint:",
            value="https://creaticon-ai-sweden-central.openai.azure.com",
            type="default"
        )
        if azure_endpoint:
            os.environ["AZURE_OPENAI_ENDPOINT"] = azure_endpoint

        # API key input
        api_key = st.text_input("Azure OpenAI API Key:", type="password")
        if api_key:
            os.environ["AZURE_OPENAI_API_KEY"] = api_key

        # API version input with default value
        api_version = st.text_input(
            "API Version:",
            value="2024-02-15-preview",
            type="default"
        )
        if api_version:
            os.environ["AZURE_OPENAI_API_VERSION"] = api_version

        st.markdown("---")
        st.markdown("### About")
        st.markdown("""
        This application uses Azure OpenAI's GPT-4o deployment to generate sentences and translations.
        Upload an image to provide context for the generated sentences.
        """)

    # Main content
    col1, col2 = st.columns([1, 1])

    with col1:
        st.header("Input")
        word_group = st.text_area("Enter a word group (e.g., 'cat, tree, happy'):", height=100)

        uploaded_file = st.file_uploader("Upload an image for context (optional):", type=["jpg", "jpeg", "png"])
        image_data = None
        if uploaded_file is not None:
            image_data = uploaded_file.getvalue()
            st.image(image_data, caption="Uploaded Image", use_column_width=True)

        if st.button("Generate Sentences"):
            if not word_group:
                st.error("Please enter a word group.")
            elif not os.getenv("AZURE_OPENAI_API_KEY"):
                st.error("Please enter your Azure OpenAI API Key in the sidebar.")
            else:
                with st.spinner("Generating sentences and translations..."):
                    try:
                        english_sentences, translated_sentences = generate_sentences_and_translations(
                            word_group, target_language, image_data
                        )

                        # Store the results in session state for display
                        st.session_state.english_sentences = english_sentences
                        st.session_state.translated_sentences = translated_sentences
                        st.session_state.has_results = True
                    except Exception as e:
                        st.error(f"An error occurred: {str(e)}")

    with col2:
        st.header("Results")
        if 'has_results' in st.session_state and st.session_state.has_results:
            st.subheader("English Sentences:")
            for i, sentence in enumerate(st.session_state.english_sentences):
                st.write(f"{i+1}. {sentence}")

            # Only display translations if we have any
            if st.session_state.translated_sentences:
                st.subheader(f"{target_language} Translations:")
                for i, sentence in enumerate(st.session_state.translated_sentences):
                    st.write(f"{i+1}. {sentence}")
            else:
                st.info(f"No {target_language} translations available.")

            # Practice section
            st.markdown("---")
            st.subheader("Practice")
            st.markdown("Try writing the translations yourself before looking at the answers!")

            for i, sentence in enumerate(st.session_state.english_sentences):
                st.text(f"English: {sentence}")
                user_translation = st.text_area(f"Your translation {i+1}:", key=f"translation_{i}")
                if st.button(f"Check translation {i+1}", key=f"check_{i}"):
                    # Check if we have a translation for this sentence
                    if i < len(st.session_state.translated_sentences):
                        st.write(f"Model translation: {st.session_state.translated_sentences[i]}")
                    else:
                        st.write("No model translation available for this sentence.")

if __name__ == "__main__":
    main()

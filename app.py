# Cell 1: Setup
import streamlit as st
import streamlit_authenticator as stauth
import yaml
from streamlit_authenticator import Authenticate  # Explicitly import Authenticate
from yaml.loader import SafeLoader
from openai import OpenAI
import os

# --- User Authentication ---
def load_config():
    with open('config.yaml') as file:
        return yaml.load(file, Loader=SafeLoader)

config = load_config()

# Create the authenticator
authenticator = Authenticate (
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days']
)

authenticator.login(location='sidebar')

if st.session_state["authentication_status"]:
    authenticator.logout('Logout', 'sidebar')
    st.write(f'Welcome {st.session_state["name"]}')
    st.title('Some content')

    # Get your OpenAI API key from environment variables 
    api_key = os.getenv("OPENAI_API_KEY")  # Used in production
    client = OpenAI(api_key=api_key)

    # Cell 2: Title & Description
    st.title('🤖 AI Content Assistant')
    st.markdown('I was made to help you craft interesting Social media posts.')

    # Cell 3: Function to generate text using OpenAI
    def analyze_text(text):
        model = "gpt-3.5-turbo"  # Using the GPT-3.5 model
        messages = [
            {"role": "system", "content": "You are an assistant who helps craft social media posts."},
            {"role": "user", "content": f"Please help me write a social media post based on the following:\n{text}"}
        ]
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0  # Lower temperature for less random responses
        )
        return response.choices[0].message.content

    # Cell 4: Function to generate the image
    def generate_image(text):
        if not api_key:
            st.error("OpenAI API key is not set. Please set it in your environment variables.")
            return

        response = client.images.generate(
            model="dall-e-3",
            prompt=text,
            size="1024x1024",
            quality="standard",
            n=1,
        )

        # Assuming the API returns an image URL; adjust based on actual response structure
        return response.data[0].url

    # Cell 4: Streamlit UI 
    user_input = st.text_area("Enter a brief for your post:", "How should you maintain a deployed model?")

    if st.button('Generate Post Content'):
        with st.spinner('Generating Text...'):
            post_text = analyze_text(user_input)
            st.write(post_text)

        with st.spinner('Generating Thumbnail...'):
            thumbnail_url = generate_image(user_input)  # Consider adjusting the prompt for image generation if needed
            st.image(thumbnail_url, caption='Generated Thumbnail')

elif st.session_state["authentication_status"] == False:
    st.error('Username/password is incorrect')
elif st.session_state["authentication_status"] == None:
    st.warning('Please enter your username and password')

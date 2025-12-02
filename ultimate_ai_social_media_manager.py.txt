import streamlit as st
from PIL import Image
from moviepy.editor import VideoFileClip
import openai
import io

# ===== Set your OpenAI API key =====
openai.api_key = "YOUR_OPENAI_API_KEY"

# ===== Page config =====
st.set_page_config(
    page_title="Framed Images AI",
    page_icon="🖼️",
    layout="wide",
)

# ===== Header =====
st.markdown(
    """
    <h1 style='text-align: center; color: #4B0082;'>🖼️ Framed Images AI Caption Generator</h1>
    <p style='text-align: center; font-size:16px;'>Upload your image or video, add a short description, and let AI generate catchy social media captions.</p>
    """, 
    unsafe_allow_html=True
)

# ===== Sidebar =====
st.sidebar.header("Options")
description = st.sidebar.text_input("Write a short description (optional):")
generate_button_text = st.sidebar.button("Generate Captions")

# ===== File uploader =====
uploaded_files = st.file_uploader(
    "Upload one or more images/videos", 
    type=["jpg","jpeg","png","mp4","mov"], 
    accept_multiple_files=True
)

# ===== Output container =====
output_container = st.container()

if uploaded_files:
    for file in uploaded_files:
        file_type = file.type
        output_container.markdown(f"### File: {file.name}")
        
        if file_type.startswith("image"):
            image = Image.open(file)
            output_container.image(image, use_column_width=True)
        elif file_type.startswith("video"):
            output_container.video(file)
        else:
            output_container.warning("Unsupported file type.")
            
        # ===== Generate caption =====
        if generate_button_text:
            with output_container:
                st.info("Generating AI caption...")
                prompt = f"Write a catchy social media caption for this content: {description}"
                
                try:
                    response = openai.Completion.create(
                        engine="text-davinci-003",
                        prompt=prompt,
                        max_tokens=60
                    )
                    caption = response.choices[0].text.strip()
                    st.success("✨ AI Caption Generated:")
                    st.write(caption)
                except Exception as e:
                    st.error(f"Error generating caption: {e}")

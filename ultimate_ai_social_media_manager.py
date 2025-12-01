import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import cv2
import os
import openai
from pathlib import Path
import pandas as pd

openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_post(file_name, description, platform="Instagram"):
    prompt = f"""
    You are a social media assistant for an art framing business.
    Generate content for {platform}.
    Given the following description and file name, create:
    1. Caption suitable for {platform}
    2. 10 relevant hashtags
    3. Short alt text
    File: {file_name}
    Description: {description}
    """
    response = openai.ChatCompletion.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": "You are a creative social media content generator."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content

def resize_and_watermark(img_path, size=(1080,1080), watermark_text="Framed Images"):
    img = Image.open(img_path)
    img = img.resize(size, Image.ANTIALIAS)
    draw = ImageDraw.Draw(img)
    font = ImageFont.load_default()
    text_width, text_height = draw.textsize(watermark_text, font)
    draw.text((img.width - text_width - 10, img.height - text_height - 10), watermark_text, font=font, fill=(255,255,255,128))
    temp_path = "resized_" + os.path.basename(img_path)
    img.save(temp_path)
    return temp_path

def extract_video_frame(video_path):
    cap = cv2.VideoCapture(video_path)
    cap.set(cv2.CAP_PROP_POS_MSEC, 1000)
    ret, frame = cap.read()
    cap.release()
    if ret:
        temp_img_path = "temp_frame.jpg"
        cv2.imwrite(temp_img_path, frame)
        return temp_img_path
    return None

st.title("🎨 Ultimate AI Social Media Manager")
st.write("Upload images/videos, generate captions, resize media, add watermark, and export!")

uploaded_files = st.file_uploader("Upload images or videos", type=["jpg","png","mp4","mov"], accept_multiple_files=True)
description = st.text_input("Enter a short description for these posts:")
platforms = st.multiselect("Select platforms:", ["Instagram","X/Twitter","Facebook","LinkedIn"], default=["Instagram"])

if st.button("Generate Posts") and uploaded_files and description and platforms:
    all_posts = []
    for file in uploaded_files:
        temp_path = Path("temp_" + file.name)
        with open(temp_path, "wb") as f:
            f.write(file.getbuffer())
        if file.type.startswith("video"):
            temp_path = Path(extract_video_frame(temp_path))
        for platform in platforms:
            size_map = {
                "Instagram": (1080,1080),
                "X/Twitter": (1200,675),
                "Facebook": (1200,630),
                "LinkedIn": (1200,1200)
            }
            resized_path = resize_and_watermark(temp_path, size=size_map.get(platform,(1080,1080)))
            post_content = generate_post(file.name, description, platform)
            all_posts.append({
                "file_name": file.name,
                "platform": platform,
                "resized_image": resized_path,
                "caption": post_content
            })
            st.image(resized_path, caption=f"{file.name} | {platform}")
            st.text_area(f"{file.name} | {platform} Caption & Hashtags:", post_content, height=150)
    if st.button("Export All Posts to CSV"):
        df = pd.DataFrame(all_posts)
        export_path = "ultimate_ai_posts.csv"
        df.to_csv(export_path, index=False, encoding="utf-8")
        st.success(f"All posts exported to {export_path}!")

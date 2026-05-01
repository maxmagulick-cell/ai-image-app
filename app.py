import json
import base64
import streamlit as st
from openai import OpenAI

# ---------------------------
# Load secrets (for deployment)
# ---------------------------
endpoint = st.secrets["AZURE_OPENAI_ENDPOINT"]
api_key = st.secrets["AZURE_OPENAI_KEY"]
model_deployment = st.secrets["MODEL_DEPLOYMENT"]

# ---------------------------
# Initialize OpenAI client
# ---------------------------
client = OpenAI(
    api_key=api_key,
    base_url=endpoint,
)

# ---------------------------
# Streamlit UI setup
# ---------------------------
st.set_page_config(page_title="AI Image Generator", layout="centered")

st.title("🚀 AI Image Generator")
st.markdown("Generate high-quality AI images using Azure OpenAI (Foundry)")

# ---------------------------
# Sidebar controls
# ---------------------------
with st.sidebar:
    st.header("⚙️ Settings")

    style = st.selectbox(
        "Style",
        ["Realistic", "Cinematic", "Anime", "Cyberpunk", "Cartoon"]
    )

    lighting = st.selectbox(
        "Lighting",
        ["Studio", "Neon", "Natural", "Dark", "Golden Hour"]
    )

    enhance_prompt = st.toggle("✨ Enhance Prompt")

# ---------------------------
# Session state for history
# ---------------------------
if "history" not in st.session_state:
    st.session_state.history = []

# ---------------------------
# Prompt input
# ---------------------------
st.markdown("### ✍️ Enter your idea")
prompt = st.text_input(
    "Describe the image you want",
    placeholder="e.g. muscular man lifting weights in a modern gym"
)

# ---------------------------
# Prompt enhancer (optional)
# ---------------------------
def enhance_user_prompt(user_prompt):
    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": "You improve prompts for high-quality AI image generation."},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=100
        )
        return response.choices[0].message.content.strip()
    except:
        return user_prompt

# ---------------------------
# Generate image
# ---------------------------
if st.button("🎨 Generate Image") and prompt:

    final_prompt = prompt

    # Enhance prompt if enabled
    if enhance_prompt:
        with st.spinner("Enhancing prompt..."):
            final_prompt = enhance_user_prompt(prompt)

    # Add style + lighting
    final_prompt = f"{final_prompt}, {style} style, {lighting} lighting, high detail, 4k"

    st.markdown("#### 🧠 Final Prompt Used:")
    st.code(final_prompt)

    try:
        with st.spinner("Generating image..."):
            response = client.images.generate(
                model=model_deployment,
                prompt=final_prompt,
                n=1
            )

            json_response = json.loads(response.model_dump_json())
            image_base64 = json_response["data"][0]["b64_json"]
            image_bytes = base64.b64decode(image_base64)

            # Show image
            st.image(image_bytes, caption="Generated Image", use_container_width=True)

            # Save to history
            st.session_state.history.append(image_bytes)

            # Download button
            st.download_button(
                label="⬇️ Download Image",
                data=image_bytes,
                file_name="generated.png",
                mime="image/png"
            )

    except Exception as e:
        st.error(f"Error: {e}")

# ---------------------------
# Image history
# ---------------------------
if st.session_state.history:
    st.markdown("---")
    st.markdown("### 🖼️ Previous Generations")

    cols = st.columns(3)

    for i, img in enumerate(st.session_state.history[::-1]):
        with cols[i % 3]:
            st.image(img, use_container_width=True)

# ---------------------------
# Footer
# ---------------------------
st.markdown("---")
st.markdown("Built with Azure OpenAI (Foundry) + Streamlit")
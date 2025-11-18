import streamlit as st
from google import genai
from google.genai import types
from PIL import Image
import io
import os
from dotenv import load_dotenv
import base64
import mimetypes
from datetime import datetime
import time

# Load environment variables
load_dotenv()

# Configure page
st.set_page_config(
    page_title="Virtual Try-On AI",
    page_icon="👔",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'history' not in st.session_state:
    st.session_state.history = []
if 'current_result' not in st.session_state:
    st.session_state.current_result = None

# Custom CSS for modern UI
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stButton>button {
        width: 100%;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.75rem 1.5rem;
        border-radius: 10px;
        font-weight: 600;
        font-size: 16px;
        transition: transform 0.2s;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
    }
    .upload-section {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        margin-bottom: 2rem;
    }
    .result-section {
        background: #f8f9fa;
        padding: 2rem;
        border-radius: 15px;
        margin-top: 2rem;
    }
    .comparison-section {
        display: flex;
        gap: 1rem;
        margin: 1rem 0;
    }
    h1 {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    .image-container {
        border-radius: 15px;
        overflow: hidden;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        transition: transform 0.3s;
    }
    .image-container:hover {
        transform: scale(1.02);
    }
    .success-message {
        padding: 1rem;
        background: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 10px;
        color: #155724;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize Gemini Client
def initialize_gemini():
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        st.error("⚠️ Please set your GEMINI_API_KEY in the .env file")
        st.info("Get your API key from: https://makersuite.google.com/app/apikey")
        return None
    
    # Using new google-genai package for image generation
    return genai.Client(api_key=api_key)

# Helper function to create download button for image
def create_download_button(img_bytes, filename):
    """Create a download button for the generated image"""
    return st.download_button(
        label="💾 Download Image",
        data=img_bytes,
        file_name=filename,
        mime="image/png",
        use_container_width=True
    )

# Helper function to optimize image for better AI processing
def optimize_image_for_ai(photo):
    """
    Optimize image for better AI image generation results
    """
    # Convert to RGB if needed
    if photo.mode != 'RGB':
        photo = photo.convert('RGB')
    
    # Resize if too large (max 2048px on longest side for better processing)
    max_size = 2048
    if max(photo.size) > max_size:
        ratio = max_size / max(photo.size)
        new_size = (int(photo.size[0] * ratio), int(photo.size[1] * ratio))
        photo = photo.resize(new_size, Image.Resampling.LANCZOS)
        print(f"📐 Resized image from {photo.size} to {new_size} for optimization")
    
    return photo

# Visualize item on body from single photo with retry logic
def visualize_item_on_body(client, photo, style_preference, custom_prompt="", max_retries=3):
    """
    Generate virtual try-on visualization with enhanced image quality
    """
    # Optimize image for better generation
    photo = optimize_image_for_ai(photo)
    
    # Convert PIL Image to bytes
    img_byte_arr = io.BytesIO()
    photo.save(img_byte_arr, format='PNG', quality=95)
    img_bytes = img_byte_arr.getvalue()
    
    # Use custom prompt if provided, otherwise use enhanced default
    if custom_prompt and custom_prompt.strip():
        prompt = custom_prompt
        print(f"\n🎨 Using CUSTOM prompt:\n{prompt}\n")
    else:
        # Enhanced prompt for better image generation
        prompt = f"""
You are a professional fashion AI photographer. I'm showing you a photo where a person is HOLDING a fashion item in their hand.

CRITICAL TRANSFORMATION TASK:
Generate a HIGH-QUALITY, REALISTIC image showing the SAME person with the SAME item now properly worn/carried on their body.

DETAILED TRANSFORMATION INSTRUCTIONS:

1. IDENTIFY THE ITEM FIRST:
   - Look carefully at what they're holding
   - Note the exact color, material, style, and design

2. REMOVE FROM HAND:
   - Make their hand completely empty and natural
   - Hand should be in a relaxed position (not holding anything)

3. PLACE ITEM ON BODY BASED ON TYPE:
   
   CLOTHING (shirt, top, dress, jacket, pants, etc.):
   - Show them WEARING it naturally on their body
   - Ensure proper fit and draping
   - Match the exact same clothing item from their hand
   - Keep realistic proportions and fit
   
   BAG/PURSE/BACKPACK:
   - Position on their shoulder or across body
   - Or hanging naturally from their arm/hand while walking
   - Show realistic strap positioning
   - Maintain the exact same bag design and color
   
   SHOES/FOOTWEAR:
   - Show them wearing the shoes on their FEET
   - Match their current outfit style
   - Ensure realistic foot positioning and sizing
   
   JEWELRY (necklace, bracelet, watch, ring):
   - Place on appropriate body part (wrist, neck, finger)
   - Show natural, comfortable positioning
   - Maintain exact design and style
   
   SUNGLASSES:
   - Position on their face/nose naturally
   - Match their face shape
   - Keep realistic positioning
   
   HAT/CAP:
   - Place on their head naturally
   - Match their head size and style
   - Show realistic angle and fit

4. PHOTO REALISM REQUIREMENTS:
   - Keep EXACT same person (face, body type, skin tone, hair)
   - Maintain EXACT same background and environment
   - Preserve lighting conditions and shadows
   - Keep the same pose and angle
   - Ensure seamless integration - item should look like it was always there
   - No visible seams, artifacts, or distortions
   - Natural shadows and reflections on the item

5. STYLE MATCHING:
   - Style preference: {style_preference}
   - Ensure the item matches their {style_preference} aesthetic
   - Coordinate with their existing outfit if applicable

6. QUALITY STANDARDS:
   - High resolution and sharp details
   - Natural, professional photography look
   - Realistic materials and textures
   - Proper lighting on the item
   - No AI artifacts or distortions

Generate a photorealistic, seamless virtual try-on image that looks like a professional fashion photograph.
"""
        print(f"\n🎨 Using ENHANCED prompt with style: {style_preference}\n")
    
    model = "gemini-2.5-flash-image-preview"
    
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_bytes(data=img_bytes, mime_type="image/png"),
                types.Part.from_text(text=prompt),
            ],
        ),
    ]
    
    # Enhanced configuration for better image quality
    generate_content_config = types.GenerateContentConfig(
        response_modalities=["IMAGE", "TEXT"],
        temperature=0.7,  # Balance between creativity and accuracy
    )
    
    # Retry logic for better reliability
    for attempt in range(max_retries):
        try:
            print(f"\n🔄 Generating virtual try-on image... (Attempt {attempt + 1}/{max_retries})")
            
            generated_images = []
            text_response = ""
            
            for chunk in client.models.generate_content_stream(
                model=model,
                contents=contents,
                config=generate_content_config,
            ):
                if (
                    chunk.candidates is None
                    or chunk.candidates[0].content is None
                    or chunk.candidates[0].content.parts is None
                ):
                    continue
                
                # Check for image data
                if chunk.candidates[0].content.parts[0].inline_data and chunk.candidates[0].content.parts[0].inline_data.data:
                    inline_data = chunk.candidates[0].content.parts[0].inline_data
                    data_buffer = inline_data.data
                    file_extension = mimetypes.guess_extension(inline_data.mime_type)
                    print(f"✅ Received image data: {len(data_buffer)} bytes, mime: {inline_data.mime_type}, ext: {file_extension}")
                    generated_images.append(data_buffer)
                else:
                    # Text response
                    if hasattr(chunk, 'text') and chunk.text:
                        text_response += chunk.text
                        print(chunk.text)
            
            return text_response, generated_images
            
        except Exception as e:
            error_str = str(e).lower()
            # Check for rate limit or quota errors
            if "rate limit" in error_str or "429" in error_str or "quota" in error_str or "resource exhausted" in error_str:
                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 5
                    print(f"⚠️ Rate limit hit. Waiting {wait_time}s before retry...")
                    time.sleep(wait_time)
                    continue
                else:
                    raise Exception("Rate limit exceeded. Please try again later.")
            if attempt < max_retries - 1:
                print(f"⚠️ Error occurred: {e}. Retrying...")
                time.sleep(2)
                continue
            else:
                raise
    
    return "", []

# Main app
def main():
    # Header
    st.markdown("# 👔 Virtual Try-On AI")
    st.markdown("### Powered by Google Gemini - Live Camera Mode")
    st.markdown("📸 **Hold any fashion item in your hand** - AI will visualize how it looks **ON your body**!")
    
    # Initialize Gemini
    model = initialize_gemini()
    
    if not model:
        st.stop()
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Settings")
        
        style_preference = st.selectbox(
            "Style Preference:",
            ["Casual", "Formal", "Business Casual", "Sporty", "Elegant", "Trendy", "Classic"]
        )
        
        st.markdown("---")
        st.markdown("### 🎨 Custom Prompt (Optional)")
        
        use_custom_prompt = st.checkbox("Use custom prompt for testing", value=False)
        
        custom_prompt = ""
        if use_custom_prompt:
            custom_prompt = st.text_area(
                "Enter your custom prompt:",
                placeholder="Type your custom instructions for the AI...",
                height=200,
                help="Leave empty to use default prompt"
            )
        
        st.markdown("---")
        
        # History section
        if st.session_state.history:
            st.markdown("### 📜 History")
            st.write(f"**Total tries:** {len(st.session_state.history)}")
            if st.button("🗑️ Clear History"):
                st.session_state.history = []
                st.session_state.current_result = None
                st.rerun()
        
        st.markdown("---")
        st.markdown("### 💡 How It Works")
        st.markdown("""
        1. **Position yourself** facing camera
        2. **Hold the item** clearly in your hand
        3. **Capture the photo**
        4. **AI visualizes** how it looks ON you!
        """)
        
        st.markdown("### 📝 Tips")
        st.markdown("""
        - ✅ Ensure good lighting
        - ✅ Hold item clearly visible
        - ✅ Face camera directly
        - ✅ Show full item in frame
        - ✅ Works with: bags, clothes, shoes, accessories!
        """)
        
        st.markdown("---")
        st.markdown("### ⚙️ Advanced")
        st.markdown("""
        - **Enhanced Prompts**: Optimized for better image quality
        - **Photorealistic Output**: Professional-grade results
        - **Seamless Integration**: Items look naturally placed
        - **Download & Share**: Save your favorites
        """)
        
        st.markdown("### 🎯 Tips for Better Results")
        st.markdown("""
        - **Hold clearly**: Show the full item
        - **Good lighting**: Ensures AI sees details
        - **Simple background**: Better item detection
        - **Face camera**: For best positioning
        - **Try different styles**: Experiment!
        """)
    
    # Main content area - Single photo with item in hand
    st.markdown("## 📸 Hold Item & Capture")
    st.info("💡 Stand facing the camera and hold the fashion item clearly in your hand, then click to capture!")
    
    photo_file = st.camera_input(
        "Capture yourself holding the item",
        key="camera_tryon",
        help="Hold the item (bag, clothing, shoes, accessory) clearly in your hand"
    )
    
    if photo_file:
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("### 📷 Your Photo")
            photo_image = Image.open(photo_file)
            st.markdown('<div class="image-container">', unsafe_allow_html=True)
            st.image(photo_image, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown("### 🎨 AI Visualization")
            
            # Generate button
            if st.button("✨ Visualize Item ON My Body!", use_container_width=True, type="primary"):
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                try:
                    photo_image = Image.open(photo_file)
                    
                    status_text.info("🔄 Processing your photo...")
                    progress_bar.progress(20)
                    
                    status_text.info("🎨 Generating virtual try-on with AI...")
                    progress_bar.progress(50)
                    
                    text_response, generated_images = visualize_item_on_body(
                        model, 
                        photo_image, 
                        style_preference,
                        custom_prompt if use_custom_prompt else ""
                    )
                    
                    progress_bar.progress(90)
                    status_text.info("✨ Finalizing results...")
                    
                    # Store result in session state
                    result_data = {
                        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        'style': style_preference,
                        'text': text_response,
                        'images': generated_images,
                        'original_image': photo_image
                    }
                    st.session_state.current_result = result_data
                    st.session_state.history.append(result_data)
                    
                    progress_bar.progress(100)
                    status_text.empty()
                    progress_bar.empty()
                    
                    # Show results
                    st.markdown("---")
                    
                    # Comparison view
                    if generated_images and len(generated_images) > 0:
                        st.markdown("### 📊 Before & After Comparison")
                        comp_col1, comp_col2 = st.columns(2)
                        
                        with comp_col1:
                            st.markdown("**📷 Original (Item in Hand)**")
                            st.image(photo_image, use_container_width=True)
                        
                        with comp_col2:
                            st.markdown("**✨ Virtual Try-On Result**")
                            main_result_img = Image.open(io.BytesIO(generated_images[0]))
                            st.image(main_result_img, use_container_width=True)
                    
                    # Show text analysis if available
                    if text_response:
                        with st.expander("📊 Detailed AI Analysis", expanded=False):
                            st.markdown(text_response)
                    
                    # Show all generated images with download buttons
                    if generated_images and len(generated_images) > 0:
                        st.markdown("### 🖼️ Generated Images")
                        for i, img_data in enumerate(generated_images):
                            try:
                                img = Image.open(io.BytesIO(img_data))
                                
                                img_col1, img_col2 = st.columns([3, 1])
                                
                                with img_col1:
                                    st.image(img, caption=f"Virtual Try-On Result {i+1}", use_container_width=True)
                                
                                with img_col2:
                                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                                    filename = f"virtual_tryon_{timestamp}_{i+1}.png"
                                    create_download_button(img_data, filename)
                                
                                print(f"✅ Successfully displayed image {i+1}")
                            except Exception as img_err:
                                st.error(f"Could not display image {i+1}: {img_err}")
                                print(f"❌ Error displaying image {i+1}: {img_err}")
                    else:
                        st.warning("⚠️ No images were generated. Please try again or check your prompt.")
                    
                    st.success("✅ Visualization Complete!")
                    st.balloons()
                    
                except Exception as e:
                    progress_bar.empty()
                    status_text.empty()
                    error_msg = str(e)
                    
                    if "rate limit" in error_msg.lower() or "429" in error_msg:
                        st.error("⏳ Rate limit exceeded. Please wait a moment and try again.")
                    elif "quota" in error_msg.lower():
                        st.error("💳 API quota exceeded. Please check your API plan.")
                    else:
                        st.error(f"❌ Error: {error_msg}")
                    
                    print(f"❌ Main error: {e}")
                    import traceback
                    traceback.print_exc()
            
            # Show current result if available
            if st.session_state.current_result:
                st.markdown("---")
                with st.expander("📜 View Last Result", expanded=False):
                    result = st.session_state.current_result
                    st.write(f"**Generated:** {result['timestamp']}")
                    st.write(f"**Style:** {result['style']}")
                    if result['images']:
                        st.write(f"**Images Generated:** {len(result['images'])}")
    
    # Footer
    st.markdown("---")
    st.markdown("""
        <div style='text-align: center; color: #666; padding: 2rem;'>
            <p>Made with ❤️ using Streamlit and Google Gemini AI</p>
            <p style='font-size: 12px;'>Note: This is an AI-powered styling assistant. For best results, consult with professional stylists.</p>
        </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()


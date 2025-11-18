# 👔 Virtual Try-On AI

An AI-powered virtual try-on application built with Streamlit and Google Gemini AI. Upload your photo and ANY fashion item (clothes, bags, shoes, accessories, jewelry) to get personalized styling recommendations and visualize how items would look on you!

## ✨ Features

- **One-Photo Try-On**: Simply hold the fashion item in your hand and capture ONE photo!
- **Live Camera Mode**: Use your webcam - no need to upload files
- **AI Image Generation**: AI generates actual images showing how items look ON your body
- **Before & After Comparison**: Side-by-side view of original and virtual try-on
- **Download Generated Images**: Save your virtual try-on results
- **Session History**: Track all your try-on attempts
- **Retry Logic**: Automatic retries on errors for better reliability
- **Smart Error Handling**: Handles rate limits and API errors gracefully
- **Custom Prompts**: Test different AI prompts for better results
- **Progress Indicators**: Real-time progress updates during generation
- **Any Fashion Item**: Works with clothes, bags, shoes, accessories, jewelry, hats, sunglasses, and more!
- **AI-Powered Insights**: Powered by Google Gemini 2.5 Flash Image
- **Style Preferences**: Choose from various style preferences (Casual, Formal, Business, etc.)
- **Beautiful UI**: Modern, gradient-based interface with smooth interactions

## 🚀 Getting Started

### Prerequisites

- Python 3.12 or higher
- Google Gemini API key (get it from [Google AI Studio](https://makersuite.google.com/app/apikey))

### Installation

1. **Clone or navigate to the project directory**
   ```bash
   cd vtry-on
   ```

2. **Install dependencies with uv**
   ```bash
   uv sync
   ```

3. **Set up your API key**
   
   Create a `.env` file in the project root:
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and add your Gemini API key:
   ```
   GEMINI_API_KEY=your_actual_api_key_here
   ```

### Running the App

```bash
streamlit run app.py
```

The app will open in your default browser at `http://localhost:8501`

## 📖 How to Use

### Simple 3-Step Process:

1. **Choose Your Style Preference** in the sidebar (Casual, Formal, Business Casual, etc.)

2. **Hold the Fashion Item in Your Hand**
   - Position yourself facing the camera
   - Hold the item (bag, clothing, shoes, accessory) clearly in your hand
   - Click to capture ONE photo

3. **Click "Visualize Item ON My Body!"**
   - AI analyzes the item you're holding
   - Visualizes how it would look properly worn/carried ON your body
   - Get detailed styling advice and outfit suggestions!

### What You Can Try On:
- 👕 **Clothing**: Shirts, dresses, jackets, pants
- 👜 **Bags**: Purses, handbags, backpacks
- 👟 **Shoes**: Sneakers, heels, boots
- 🕶️ **Accessories**: Sunglasses, jewelry, watches, hats

## 💡 Tips for Best Results

- **Good Lighting**: Ensure your space is well-lit
- **Clear Item Display**: Hold the fashion item clearly in your hand with full visibility
- **Face the Camera**: Position yourself facing directly at the camera
- **Show Full Item**: Make sure the entire item is visible in the frame
- **Plain Background**: Use a simple background for better AI recognition
- **One Photo Only**: Just hold the item and capture - AI does the rest!

## 🛠️ Tech Stack

- **Streamlit**: Web application framework
- **Google Gemini AI**: AI-powered fashion analysis
- **Pillow**: Image processing
- **Python-dotenv**: Environment variable management

## 📝 Project Structure

```
vtry-on/
├── app.py              # Main Streamlit application
├── pyproject.toml      # Project dependencies
├── .env.example        # Example environment file
├── .env                # Your API keys (create this)
├── README.md           # This file
└── hello.py            # Original hello world script
```

## 🔐 API Key Security

⚠️ **Important**: Never commit your `.env` file with actual API keys to version control!

The `.gitignore` file is already configured to exclude `.env` files.

## 🎨 Customization

You can customize the app by:
- Modifying the CSS in the `st.markdown()` sections of `app.py`
- Adding new clothing categories in the sidebar
- Adjusting the AI prompts for different types of recommendations
- Adding new style preferences

## 🤝 Contributing

Feel free to fork this project and submit pull requests with improvements!

## 📄 License

This project is open source and available for personal and educational use.

## 🙏 Acknowledgments

- Built with [Streamlit](https://streamlit.io/)
- Powered by [Google Gemini AI](https://deepmind.google/technologies/gemini/)

---

**Note**: This is an AI-powered styling assistant. For professional fashion advice, consult with certified stylists.


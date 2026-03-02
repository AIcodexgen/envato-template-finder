# 🎨 Envato Template Finder AI

An intelligent web application that analyzes any reference website and finds the most similar templates on Envato Elements using AI-powered matching.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)
![Playwright](https://img.shields.io/badge/Playwright-1.40+-orange.svg)
![Gemini AI](https://img.shields.io/badge/Google%20Gemini%20AI-Powered-blueviolet.svg)

## ✨ Features

- 🔍 **Automatic Website Analysis**: Detects CMS, industry, color palette, and layout features
- 🤖 **AI-Powered Matching**: Uses Google Gemini AI to rank templates by similarity
- 🎯 **Smart Filters**: Override auto-detection with manual industry/CMS selection
- 🌐 **Real-time Scraping**: Scrapes Envato Elements for the latest templates
- 📊 **Visual Analysis**: Extracts color schemes from screenshots
- ⚡ **Fast & Async**: Built with FastAPI and Playwright for optimal performance
- 📱 **Responsive UI**: Modern, animated interface that works on all devices

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Google API Key (for Gemini AI) - [Get one here](https://makersuite.google.com/app/apikey)

### Installation

1. **Clone or download this repository:**
```bash
cd envato-template-finder
```

2. **Run the startup script:**

**Linux/Mac:**
```bash
./start.sh
```

**Windows:**
```cmd
start.bat
```

Or manually:
```bash
# Create virtual environment
python -m venv venv

# Activate it
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium

# Set up environment variables
cp .env.example .env
# Edit .env and add your Google API key

# Run the application
python main.py
```

3. **Open your browser:**
Navigate to `http://localhost:8000`

## 🔧 Configuration

Create a `.env` file in the root directory:

```env
GOOGLE_API_KEY=your_google_api_key_here
```

**Note:** If you don't have a Google API key, the app will still work using basic algorithmic matching (without AI enhancement).

## 📖 How to Use

1. **Enter a Reference URL**: Paste any website URL you want to find similar templates for
2. **Select Filters (Optional)**: 
   - Choose industry if auto-detection is incorrect
   - Select CMS/platform preference
3. **Click "Find Similar Templates"**
4. **Review Results**: 
   - View website analysis summary
   - Browse top 10 matching templates from Envato Elements
   - See detailed match reasons for each template
   - Click through to view on Envato

## 🏗️ Architecture

```
envato-template-finder/
├── main.py              # FastAPI application entry point
├── scraper.py           # Envato Elements web scraper (Playwright)
├── analyzer.py          # Reference website analyzer
├── ai_matcher.py        # Google Gemini AI integration
├── requirements.txt     # Python dependencies
├── .env.example         # Environment variables template
├── start.sh             # Linux/Mac startup script
├── start.bat            # Windows startup script
├── templates/
│   └── index.html       # Frontend UI
└── static/              # Static assets (CSS, JS)
```

## 🔍 How It Works

### 1. Website Analysis Phase
- **Tech Detection**: Identifies CMS (WordPress, Shopify, etc.) and frameworks
- **Industry Classification**: Analyzes content to determine business category
- **Visual Extraction**: Captures screenshot and extracts dominant color palette
- **Layout Analysis**: Detects sections (hero, pricing, testimonials, etc.)
- **Keyword Extraction**: Pulls key themes from headings and meta tags

### 2. Template Search Phase
- Constructs Envato Elements search URL based on detected filters
- Uses Playwright to scrape template listings
- Collects up to 50 templates for analysis
- Handles pagination and lazy loading

### 3. AI Matching Phase (if API key provided)
- Sends reference analysis + templates to Google Gemini AI
- AI ranks by: Industry fit (35%), Visual style (25%), Layout (20%), Platform (15%), Features (5%)
- Returns top 10 with detailed similarity explanations

### 4. Fallback Matching (no API key)
- Algorithmic scoring based on keyword overlap
- Industry and CMS tag matching
- Layout feature compatibility
- Still provides quality results!

## 🛠️ API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Main UI |
| `/api/analyze-reference` | POST | Analyze a reference website |
| `/api/search-templates` | POST | Full search pipeline |
| `/api/industries` | GET | List available industries |
| `/api/cms-options` | GET | List available CMS options |

### Example API Request

```bash
curl -X POST "http://localhost:8000/api/search-templates" \
  -H "Content-Type: application/json" \
  -d '{
    "reference_url": "https://example.com",
    "industry": "SaaS/Technology",
    "cms": "WordPress",
    "max_results": 10
  }'
```

## 🎨 Supported Industries

- Corporate
- Creative/Portfolio
- E-commerce
- Education
- Entertainment
- Fashion
- Food/Restaurant
- Health/Beauty
- Medical
- Real Estate
- SaaS/Technology
- Sports
- Travel
- Non-profit
- Blog/Magazine

## ⚙️ Supported Platforms

- WordPress
- HTML/CSS
- React
- Vue.js
- Angular
- Shopify
- Webflow
- Joomla
- Drupal
- Magento
- Next.js
- Nuxt.js
- Laravel

## 📝 Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GOOGLE_API_KEY` | No | Google AI Studio API key for Gemini |
| `DISABLE_AI` | No | Set to `true` to force basic matching |

## 🐛 Troubleshooting

### Playwright Installation Issues
```bash
# Reinstall Playwright
pip install --force-reinstall playwright
playwright install chromium
```

### Google API Key Issues
- Ensure your API key has access to Gemini Pro model
- Check quota limits in Google AI Studio
- Without API key, app uses fallback matching

### Scraping Issues
- Envato Elements may block rapid requests
- The app includes delays and proper headers
- If blocked, try again after a few minutes

## 🤝 Contributing

Contributions welcome! Areas for improvement:
- Additional template sources
- Enhanced visual similarity algorithms
- Support for more CMS platforms
- Caching layer for faster results

## 📄 License

MIT License - feel free to use for personal or commercial projects.

## 🙏 Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/)
- Scraping powered by [Playwright](https://playwright.dev/)
- AI matching by [Google Gemini](https://deepmind.google/technologies/gemini/)
- Color extraction with [ColorThief](https://github.com/fengsp/color-thief-py)

---

**Note:** This tool is for educational and research purposes. Please respect Envato Elements' Terms of Service and rate limits when using this scraper.

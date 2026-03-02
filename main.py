from fastapi import FastAPI, HTTPException, Request, Form, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse
from pydantic import BaseModel, HttpUrl
from typing import List, Optional, Dict, Any
import asyncio
import json
import os
from datetime import datetime
from dotenv import load_dotenv

from scraper import EnvatoScraper
from analyzer import ReferenceAnalyzer
from ai_matcher import GeminiMatcher

# Load environment variables
load_dotenv()

app = FastAPI(
    title="Envato Template Finder AI",
    description="AI-powered tool to find similar templates on Envato Elements",
    version="1.0.0"
)

# Mount static files only if directory exists
static_dir = "static"
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")
else:
    print(f"⚠️  Warning: {static_dir}/ directory not found, skipping static files mount")

# Templates
templates = Jinja2Templates(directory="templates")

# Request/Response Models
class SearchRequest(BaseModel):
    reference_url: HttpUrl
    industry: Optional[str] = None
    cms: Optional[str] = None
    max_results: int = 10

class TemplateMatch(BaseModel):
    rank: int
    template_id: str
    title: str
    envato_url: str
    preview_image: str
    similarity_score: float
    match_reasons: Dict[str, str]
    confidence: str
    price: Optional[str] = None
    rating: Optional[float] = None
    tags: List[str] = []

class SearchResponse(BaseModel):
    success: bool
    reference_summary: str
    detected_industry: Optional[str]
    detected_cms: Optional[str]
    top_matches: List[TemplateMatch]
    search_metadata: Dict[str, Any]

class AnalysisResponse(BaseModel):
    success: bool
    analysis: Dict[str, Any]
    suggested_industries: List[str]
    suggested_cms: List[str]

# Initialize components
scraper = EnvatoScraper()
analyzer = ReferenceAnalyzer()
ai_matcher = GeminiMatcher()

@app.get("/")
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/api/analyze-reference", response_model=AnalysisResponse)
async def analyze_reference(url: str = Form(...)):
    """
    Step 1: Analyze reference website to detect industry, CMS, and features
    """
    try:
        print(f"🔍 Analyzing reference website: {url}")
        analysis = await analyzer.analyze_website(url)

        return AnalysisResponse(
            success=True,
            analysis=analysis,
            suggested_industries=get_industry_options(),
            suggested_cms=get_cms_options()
        )
    except Exception as e:
        print(f"❌ Analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/search-templates", response_model=SearchResponse)
async def search_templates(request: SearchRequest):
    """
    Step 2: Search Envato and find similar templates
    """
    try:
        print(f"🚀 Starting template search for: {request.reference_url}")

        # 1. Analyze reference site (or use provided filters)
        print("📊 Analyzing reference website...")
        ref_analysis = await analyzer.analyze_website(str(request.reference_url))

        # Override with user selections if provided
        if request.industry:
            ref_analysis['industry'] = request.industry
            print(f"📝 Using user-selected industry: {request.industry}")
        if request.cms:
            ref_analysis['cms'] = request.cms
            print(f"📝 Using user-selected CMS: {request.cms}")

        # 2. Scrape Envato Elements based on filters
        print("🔎 Scraping Envato Elements...")
        envato_templates = await scraper.search_templates(
            industry=ref_analysis.get('industry'),
            cms=ref_analysis.get('cms'),
            keywords=ref_analysis.get('keywords', []),
            max_results=50
        )

        if not envato_templates:
            print("⚠️ No templates found on Envato")
            return SearchResponse(
                success=True,
                reference_summary=ref_analysis.get('summary', ''),
                detected_industry=ref_analysis.get('industry'),
                detected_cms=ref_analysis.get('cms'),
                top_matches=[],
                search_metadata={
                    "message": "No templates found on Envato with current filters",
                    "suggestion": "Try broadening your industry or CMS selection",
                    "total_scraped": 0,
                    "search_timestamp": datetime.now().isoformat()
                }
            )

        print(f"✅ Found {len(envato_templates)} templates on Envato")

        # 3. Use AI to find best matches
        print("🤖 Analyzing similarities with AI...")
        matches = await ai_matcher.find_similar_templates(
            reference_analysis=ref_analysis,
            templates=envato_templates,
            top_n=request.max_results
        )

        print(f"✅ Returning top {len(matches)} matches")

        return SearchResponse(
            success=True,
            reference_summary=ref_analysis.get('summary', ''),
            detected_industry=ref_analysis.get('industry'),
            detected_cms=ref_analysis.get('cms'),
            top_matches=matches,
            search_metadata={
                "total_scraped": len(envato_templates),
                "search_timestamp": datetime.now().isoformat(),
                "filters_applied": {
                    "industry": ref_analysis.get('industry'),
                    "cms": ref_analysis.get('cms')
                }
            }
        )

    except Exception as e:
        print(f"❌ Search error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/industries")
async def get_industries():
    return {"industries": get_industry_options()}

@app.get("/api/cms-options")
async def get_cms_options_endpoint():
    return {"cms_options": get_cms_options()}

def get_industry_options():
    return [
        "Corporate", "Creative/Portfolio", "E-commerce", "Education",
        "Entertainment", "Fashion", "Food/Restaurant", "Health/Beauty",
        "Medical", "Real Estate", "SaaS/Technology", "Sports",
        "Travel", "Non-profit", "Blog/Magazine"
    ]

def get_cms_options():
    return [
        "WordPress", "HTML/CSS", "React", "Vue.js", "Angular",
        "Shopify", "Webflow", "Joomla", "Drupal", "Magento",
        "Next.js", "Nuxt.js", "Laravel", "Static/Other"
    ]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

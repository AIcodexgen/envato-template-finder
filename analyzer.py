import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from typing import Dict, List, Optional
import re
from colorthief import ColorThief
import io
from PIL import Image

class ReferenceAnalyzer:
    def __init__(self):
        self.tech_indicators = {
            "WordPress": ["wp-content", "wp-includes", "wordpress", "wp-json"],
            "Shopify": ["cdn.shopify.com", "myshopify.com", "shopify.com", "Shopify.theme"],
            "Webflow": ["cdn.prod.website-files.com", "webflow.io", "data-w-id"],
            "React": ["reactroot", "data-reactroot", "react.development", "react.production"],
            "Vue.js": ["vue.js", "vue.min.js", "__VUE__", "data-v-"],
            "Angular": ["ng-app", "angular.js", "angular.min.js", "ng-"],
            "Next.js": ["__NEXT_DATA__", "_next/static", "_next/data"],
            "Nuxt.js": ["__NUXT__", "_nuxt/"],
            "Wix": ["wix.com", "wixstatic.com", "wixapps.net"],
            "Squarespace": ["squarespace.com", "static.squarespace.com", "SQUARESPACE_ROLLUPS"],
            "Drupal": ["drupal", "sites/default"],
            "Joomla": ["joomla", "com_content"],
            "Magento": ["magento", "Mage.Cookies"]
        }

    async def analyze_website(self, url: str) -> Dict:
        """
        Comprehensive analysis of reference website
        """
        if not url.startswith('http'):
            url = 'https://' + url

        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=['--no-sandbox', '--disable-setuid-sandbox']
            )
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                viewport={'width': 1920, 'height': 1080}
            )
            page = await context.new_page()

            try:
                print(f"🌐 Loading reference site: {url}")
                await page.goto(url, wait_until="networkidle", timeout=60000)
                await asyncio.sleep(2)

                # Get page content
                content = await page.content()
                soup = BeautifulSoup(content, 'html.parser')

                # Take screenshot for visual analysis
                print("📸 Taking screenshot...")
                screenshot = await page.screenshot(full_page=False)

                analysis = {
                    "url": url,
                    "title": await page.title(),
                    "meta_description": self._get_meta_description(soup),
                    "detected_cms": self._detect_cms(content),
                    "detected_framework": self._detect_framework(content),
                    "industry": self._detect_industry(soup, content),
                    "keywords": self._extract_keywords(soup),
                    "color_palette": await self._extract_colors(screenshot),
                    "layout_features": self._analyze_layout(soup),
                    "tech_stack": {
                        "platform": self._detect_cms(content),
                        "framework": self._detect_framework(content),
                        "analytics": self._detect_analytics(content)
                    },
                    "summary": ""
                }

                # Generate summary
                analysis["summary"] = self._generate_summary(analysis)

                print(f"✅ Analysis complete: {analysis['summary']}")

                await browser.close()
                return analysis

            except Exception as e:
                print(f"❌ Analysis error: {e}")
                await browser.close()
                # Return basic analysis on error
                return {
                    "url": url,
                    "title": "Unknown",
                    "detected_cms": None,
                    "industry": "Corporate",
                    "keywords": [],
                    "color_palette": [],
                    "layout_features": {},
                    "summary": f"Error analyzing site: {str(e)}"
                }

    def _get_meta_description(self, soup) -> str:
        meta = soup.find('meta', attrs={'name': 'description'}) or                soup.find('meta', attrs={'property': 'og:description'})
        return meta['content'] if meta else ""

    def _detect_cms(self, content: str) -> Optional[str]:
        content_lower = content.lower()
        detected = []

        for cms, indicators in self.tech_indicators.items():
            if any(indicator.lower() in content_lower for indicator in indicators):
                detected.append(cms)

        # Return the most specific one (prioritize WordPress, Shopify, etc.)
        priority = ["WordPress", "Shopify", "Webflow", "Magento", "Drupal", "Joomla"]
        for p in priority:
            if p in detected:
                return p

        return detected[0] if detected else None

    def _detect_framework(self, content: str) -> Optional[str]:
        content_lower = content.lower()
        frameworks = []

        if "next.js" in content_lower or "__next_data__" in content_lower:
            frameworks.append("Next.js")
        if "nuxt.js" in content_lower or "__nuxt__" in content_lower:
            frameworks.append("Nuxt.js")
        if "react" in content_lower:
            frameworks.append("React")
        if "vue" in content_lower:
            frameworks.append("Vue.js")
        if "angular" in content_lower:
            frameworks.append("Angular")

        return frameworks[0] if frameworks else None

    def _detect_industry(self, soup, content: str) -> Optional[str]:
        """
        Detect industry based on content analysis
        """
        text = soup.get_text().lower()
        meta = self._get_meta_description(soup).lower()
        title = soup.title.string.lower() if soup.title else ""

        combined_text = f"{text} {meta} {title}"

        industry_keywords = {
            "SaaS/Technology": [
                "software", "app", "platform", "solution", "tech", "api", "cloud",
                "startup", "digital", "automation", "ai", "machine learning",
                "data", "analytics", "dashboard", "saas", "service"
            ],
            "E-commerce": [
                "shop", "store", "product", "cart", "checkout", "buy", "price",
                "order", "shipping", "payment", "ecommerce", "retail", "sale"
            ],
            "Medical/Health": [
                "health", "medical", "doctor", "clinic", "patient", "care",
                "hospital", "wellness", "therapy", "dental", "medicine"
            ],
            "Real Estate": [
                "property", "real estate", "house", "apartment", "rent", "sale",
                "mortgage", "realtor", "listing", "home", "commercial"
            ],
            "Education": [
                "course", "learn", "education", "school", "university", "training",
                "academy", "student", "teaching", "online course", "e-learning"
            ],
            "Food/Restaurant": [
                "restaurant", "food", "menu", "chef", "dining", "cafe",
                "catering", "delivery", "reservation", "kitchen", "bar"
            ],
            "Fashion": [
                "fashion", "clothing", "apparel", "style", "collection", "wear",
                "boutique", "trend", "designer", "accessories", "luxury"
            ],
            "Corporate": [
                "company", "business", "corporate", "enterprise", "agency",
                "consulting", "professional", "services", "firm", "solutions"
            ],
            "Creative/Portfolio": [
                "portfolio", "creative", "design", "agency", "studio", "art",
                "photography", "illustration", "branding", "showcase"
            ],
            "Non-profit": [
                "nonprofit", "charity", "donate", "cause", "foundation", "ngo",
                "volunteer", "mission", "help", "support", "community"
            ],
            "Travel": [
                "travel", "tour", "vacation", "hotel", "booking", "destination",
                "trip", "adventure", "tourism", "resort", "holiday"
            ],
            "Sports": [
                "sports", "fitness", "gym", "workout", "training", "athlete",
                "club", "team", "exercise", "health", "nutrition"
            ],
            "Entertainment": [
                "entertainment", "music", "video", "game", "event", "ticket",
                "movie", "show", "concert", "festival", "media"
            ],
            "Blog/Magazine": [
                "blog", "magazine", "news", "article", "story", "editorial",
                "journal", "publication", "content", "writer", "media"
            ]
        }

        scores = {}
        for industry, keywords in industry_keywords.items():
            score = sum(1 for keyword in keywords if keyword in combined_text)
            if score > 0:
                scores[industry] = score

        if scores:
            # Return industry with highest score
            best_match = max(scores, key=scores.get)
            print(f"🏢 Detected industry: {best_match} (score: {scores[best_match]})")
            return best_match

        return "Corporate"  # Default

    def _extract_keywords(self, soup) -> List[str]:
        """
        Extract key topics/themes from the website
        """
        # Get headings and important text
        headings = soup.find_all(['h1', 'h2', 'h3'])
        raw_terms = []

        for h in headings:
            text = h.get_text(strip=True).lower()
            if 3 < len(text) < 100:
                # Clean up text - remove special characters
                clean_text = re.sub(r'[^\w\s]', ' ', text)
                raw_terms.extend(clean_text.split())

        # Also get from meta keywords
        meta_keywords = soup.find('meta', attrs={'name': 'keywords'})
        if meta_keywords:
            raw_terms.extend(re.sub(r'[^\w\s]', ' ', meta_keywords.get('content', '').lower()).split())

        # Also get from title
        if soup.title:
            raw_terms.extend(re.sub(r'[^\w\s]', ' ', soup.title.string.lower()).split())

        # Stop words to filter out
        stop_words = {
            'home', 'about', 'contact', 'menu', 'page', 'site', 'website', 
            'log', 'in', 'into', 'your', 'account', 'footer', 'navigation',
            'options', 'the', 'and', 'for', 'with', 'from', 'our', 'business',
            'administration', 'search', 'toggle', 'main', 'skip', 'content'
        }

        # Filter and count frequencies
        keywords = []
        for word in raw_terms:
            if len(word) > 3 and word not in stop_words and not word.isdigit():
                keywords.append(word)

        # Count frequencies and get top 8
        from collections import Counter
        most_common = [word for word, count in Counter(keywords).most_common(12)]
        
        print(f"🔑 Refined keywords: {most_common}")
        return most_common

    async def _extract_colors(self, screenshot_bytes: bytes) -> List[str]:
        """
        Extract dominant colors from screenshot
        """
        try:
            image = Image.open(io.BytesIO(screenshot_bytes))
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')

            # Resize for faster processing
            image = image.resize((150, 150))

            # Save to bytes for ColorThief
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format='PNG')
            img_byte_arr.seek(0)

            color_thief = ColorThief(img_byte_arr)
            palette = color_thief.get_palette(color_count=5, quality=10)

            colors = [f"#{r:02x}{g:02x}{b:02x}" for r, g, b in palette]
            print(f"🎨 Extracted colors: {colors}")
            return colors
        except Exception as e:
            print(f"⚠️ Color extraction error: {e}")
            return ["#2563eb", "#1e40af", "#ffffff", "#f3f4f6", "#111827"]  # Default blues

    def _analyze_layout(self, soup) -> Dict:
        """
        Analyze page layout structure
        """
        # Count sections
        sections = len(soup.find_all('section'))
        divs = len(soup.find_all('div'))

        # Detect common sections by class/ID patterns
        html_str = str(soup).lower()

        has_hero = bool(
            soup.find(['header', 'section'], class_=re.compile('hero|banner|home|intro', re.I)) or
            'hero' in html_str[:5000]
        )

        has_cta = bool(
            soup.find(['section', 'div'], class_=re.compile('cta|call-to-action|action', re.I)) or
            soup.find('a', string=re.compile('sign up|get started|buy now|contact', re.I))
        )

        has_testimonials = bool(
            soup.find(['section'], class_=re.compile('testimonial|review|feedback', re.I))
        )

        has_pricing = bool(
            soup.find(['section'], class_=re.compile('pricing|price|plan', re.I))
        )

        has_blog = bool(
            soup.find(['section'], class_=re.compile('blog|news|article', re.I))
        )

        has_contact = bool(
            soup.find(['section'], class_=re.compile('contact|form', re.I))
        )

        layout_type = "simple"
        if sections > 8:
            layout_type = "complex"
        elif sections > 4:
            layout_type = "medium"

        return {
            "section_count": sections,
            "has_hero": has_hero,
            "has_cta": has_cta,
            "has_testimonials": has_testimonials,
            "has_pricing": has_pricing,
            "has_blog": has_blog,
            "has_contact": has_contact,
            "layout_complexity": layout_type
        }

    def _detect_analytics(self, content: str) -> List[str]:
        """
        Detect analytics tools
        """
        analytics = []
        content_lower = content.lower()

        if any(x in content_lower for x in ["google-analytics", "gtag", "ga('", "gtag('"]):
            analytics.append("Google Analytics")
        if "facebook.com/tr" in content_lower or "fbevents" in content_lower:
            analytics.append("Facebook Pixel")
        if "hotjar" in content_lower:
            analytics.append("Hotjar")
        if "mixpanel" in content_lower:
            analytics.append("Mixpanel")
        if "segment" in content_lower:
            analytics.append("Segment")

        return analytics

    def _generate_summary(self, analysis: Dict) -> str:
        """
        Generate human-readable summary
        """
        parts = []

        if analysis.get("title") and analysis["title"] != "Unknown":
            parts.append(f"Site: {analysis['title']}")

        if analysis.get("detected_cms"):
            parts.append(f"Built with {analysis['detected_cms']}")

        if analysis.get("industry"):
            parts.append(f"{analysis['industry']} industry")

        layout = analysis.get("layout_features", {})
        features = []
        if layout.get("has_hero"): features.append("hero section")
        if layout.get("has_cta"): features.append("CTA")
        if layout.get("has_pricing"): features.append("pricing")
        if layout.get("has_testimonials"): features.append("testimonials")

        if features:
            parts.append(f"Features: {', '.join(features)}")

        if analysis.get("color_palette"):
            parts.append(f"Colors: {', '.join(analysis['color_palette'][:3])}")

        return " | ".join(parts) if parts else "Website analysis completed"

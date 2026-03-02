import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
import re
from urllib.parse import urljoin, quote

class EnvatoScraper:
    def __init__(self):
        self.base_url = "https://elements.envato.com"
        self.category_paths = {
            "web-templates": "/web-templates",
            "wordpress": "/wordpress",
            "shopify": "/shopify",
            "react": "/react",
            "vue": "/vuejs"
        }

    async def search_templates(
        self, 
        industry: Optional[str] = None,
        cms: Optional[str] = None,
        keywords: List[str] = None,
        max_results: int = 50
    ) -> List[Dict]:
        """
        Scrape Envato Elements templates based on filters
        """
        templates = []

        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=['--no-sandbox', '--disable-setuid-sandbox']
            )
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                viewport={'width': 1920, 'height': 1080}
            )
            page = await context.new_page()

            try:
                # Build initial search URL
                search_url = self._build_search_url(industry, cms, keywords)
                print(f"🌐 Navigating to: {search_url}")

                await page.goto(search_url, wait_until="networkidle", timeout=60000)
                await asyncio.sleep(3) 

                templates = await self._scroll_and_collect(page, max_results)

                # Fallback: If no results, retry with just industry/category
                if not templates and (keywords or industry):
                    print("⚠️ No results with keywords, retrying with broader search...")
                    # Build a broader URL (no keywords)
                    broad_url = self._build_search_url(industry, cms, None)
                    print(f"🌐 Navigating to broad search: {broad_url}")
                    await page.goto(broad_url, wait_until="networkidle", timeout=60000)
                    await asyncio.sleep(3)
                    templates = await self._scroll_and_collect(page, max_results)

            except Exception as e:
                print(f"❌ Scraping error: {e}")
            finally:
                await browser.close()

        return templates

    def _build_search_url(
        self, 
        industry: Optional[str], 
        cms: Optional[str], 
        keywords: Optional[List[str]]
    ) -> str:
        """
        Construct Envato search URL with filters
        """
        # Map CMS to category path
        category = "web-templates"
        if cms:
            cms_lower = cms.lower()
            if "wordpress" in cms_lower:
                category = "wordpress"
            elif "shopify" in cms_lower:
                category = "shopify"
            elif "react" in cms_lower:
                category = "react"
            elif "vue" in cms_lower:
                category = "vue"

        # Start building URL
        url_parts = [self.base_url, category]

        # Add industry as subcategory if provided
        if industry and industry != "Corporate":
            industry_slug = industry.lower().replace("/", "-").replace(" ", "-")
            industry_mapping = {
                "creative-portfolio": "portfolio",
                "e-commerce": "ecommerce",
                "saas-technology": "technology",
                "food-restaurant": "restaurant",
                "health-beauty": "health-beauty",
                "real-estate": "real-estate",
                "blog-magazine": "blog"
            }
            mapped = industry_mapping.get(industry_slug, industry_slug)
            url_parts.append(mapped)

        base_url = "/".join(url_parts)

        # Add query parameters
        params = []
        if keywords and len(keywords) > 0:
            # Use only the top 2-3 single-word keywords for max compatibility
            clean_keywords = [k for k in keywords if " " not in k][:3]
            if not clean_keywords: clean_keywords = keywords[:2]
            
            query = quote(" ".join(clean_keywords))
            params.append(f"query={query}")

        # Add sorting
        params.append("sort=popular")

        if params:
            base_url += "?" + "&".join(params)

        return base_url

    async def _scroll_and_collect(self, page, max_results: int) -> List[Dict]:
        """
        Scroll page and collect template data
        """
        templates = []
        seen_ids = set()
        scroll_attempts = 0
        max_scroll_attempts = 10

        while len(templates) < max_results and scroll_attempts < max_scroll_attempts:
            # Parse current page content
            content = await page.content()
            soup = BeautifulSoup(content, 'html.parser')

            # Find template cards using multiple selectors
            cards = []

            # Try different selectors that Envato might use
            selectors = [
                'div[data-testid="item-card"]',
                'div[class*="item-card"]',
                'div[class*="GridItem"]',
                'article[class*="item"]',
                'div[class*="ItemCard"]',
                'a[href*="/item/"]'
            ]

            for selector in selectors:
                cards = await page.query_selector_all(selector)
                if len(cards) > 0:
                    break

            print(f"📄 Found {len(cards)} cards on current scroll")

            for card in cards:
                if len(templates) >= max_results:
                    break

                try:
                    template = await self._parse_card_element(page, card)
                    if template and template['id'] not in seen_ids:
                        seen_ids.add(template['id'])
                        templates.append(template)
                        print(f"  ✅ Collected: {template['title'][:50]}...")
                except Exception as e:
                    continue

            # Scroll down to load more
            previous_height = await page.evaluate("document.body.scrollHeight")
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await asyncio.sleep(2)

            new_height = await page.evaluate("document.body.scrollHeight")
            if new_height == previous_height:
                scroll_attempts += 1
            else:
                scroll_attempts = 0

        print(f"🎯 Total templates collected: {len(templates)}")
        return templates

    async def _parse_card_element(self, page, card) -> Optional[Dict]:
        """
        Extract data from a template card element
        """
        try:
            # Get the link element
            link_elem = await card.query_selector('a[href*="/item/"]')
            if not link_elem:
                # Try getting href from the card itself if it's an anchor
                href = await card.get_attribute('href')
                if not href or '/item/' not in href:
                    return None
            else:
                href = await link_elem.get_attribute('href')

            if not href:
                return None

            # Extract ID from URL
            template_id = ""
            if '/item/' in href:
                parts = href.split('/item/')
                if len(parts) > 1:
                    template_id = parts[1].split('/')[0]
            else:
                template_id = href.split('/')[-1].split('?')[0]

            if not template_id:
                template_id = href

            # Extract title
            title = "Unknown Template"
            title_selectors = ['h3', 'h2', '.item-title', '[class*="title"]', 'img[alt]']
            for selector in title_selectors:
                elem = await card.query_selector(selector)
                if elem:
                    if selector == 'img[alt]':
                        title = await elem.get_attribute('alt') or title
                    else:
                        title = await elem.inner_text() or title
                    if title and title != "Unknown Template":
                        break

            # Extract image
            preview_image = ""
            img_selectors = ['img[class*="thumbnail"]', 'img[class*="preview"]', 'img', 'img[srcset]']
            for selector in img_selectors:
                img = await card.query_selector(selector)
                if img:
                    src = await img.get_attribute('src')
                    if src and ('envato' in src or 'elements' in src or 'http' in src):
                        preview_image = src
                        break
                    # Try data-src for lazy loaded images
                    data_src = await img.get_attribute('data-src')
                    if data_src:
                        preview_image = data_src
                        break

            # Extract tags/category
            tags = []
            tag_selectors = ['[class*="tag"]', '[class*="category"]', '.meta a']
            for selector in tag_selectors:
                tag_elems = await card.query_selector_all(selector)
                for tag_elem in tag_elems:
                    tag_text = await tag_elem.inner_text()
                    if tag_text and len(tag_text) < 50:
                        tags.append(tag_text.strip())

            # Remove duplicates and limit
            tags = list(set(tags))[:5]

            # Build full URL
            full_url = urljoin(self.base_url, href) if not href.startswith('http') else href

            return {
                "id": template_id[:100],  # Limit length
                "title": title.strip()[:200],
                "url": full_url,
                "preview_image": preview_image,
                "category": tags[0] if tags else "",
                "tags": tags,
                "description": f"{title.strip()} - {', '.join(tags[:3])}"
            }

        except Exception as e:
            return None

    async def get_template_details(self, template_url: str) -> Dict:
        """
        Get detailed info about a specific template
        """
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()

            try:
                await page.goto(template_url, wait_until="networkidle")
                content = await page.content()
                soup = BeautifulSoup(content, 'html.parser')

                details = {
                    "full_description": "",
                    "features": [],
                    "rating": None,
                    "sales": None
                }

                # Try to extract description
                desc_elem = soup.find('div', class_=re.compile('description|details|about', re.I))
                if desc_elem:
                    details["full_description"] = desc_elem.get_text(strip=True)[:500]

                await browser.close()
                return details

            except Exception as e:
                await browser.close()
                return {}

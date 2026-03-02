import google.generativeai as genai
import json
import os
from typing import List, Dict, Any
import re

class GeminiMatcher:
    def __init__(self):
        # Configure with your API key
        api_key = os.getenv("GOOGLE_API_KEY")
        self.enabled = False

        if api_key:
            try:
                genai.configure(api_key=api_key)
                self.model = genai.GenerativeModel('gemini-pro')
                self.enabled = True
                print("✅ Gemini AI initialized successfully")
            except Exception as e:
                print(f"⚠️ Gemini initialization error: {e}")
                self.model = None
        else:
            print("⚠️ No GOOGLE_API_KEY found, using fallback matching")
            self.model = None

    async def find_similar_templates(
        self, 
        reference_analysis: Dict, 
        templates: List[Dict], 
        top_n: int = 10
    ) -> List[Dict]:
        """
        Use Gemini AI to find similar templates
        """
        if not self.enabled or not self.model:
            print("🔄 Using fallback matching (no AI)")
            return self._basic_matching(reference_analysis, templates, top_n)

        try:
            # Prepare prompt
            prompt = self._build_prompt(reference_analysis, templates, top_n)

            print("🤖 Sending to Gemini AI for analysis...")

            # Generate content
            response = await self.model.generate_content_async(prompt)
            result_text = response.text

            print("✅ Received AI response, parsing...")

            # Parse JSON from response
            matches = self._parse_ai_response(result_text, templates, top_n)

            if matches:
                print(f"✅ AI matching successful: {len(matches)} matches")
                return matches
            else:
                print("⚠️ AI parsing failed, using fallback")
                return self._basic_matching(reference_analysis, templates, top_n)

        except Exception as e:
            print(f"❌ AI matching error: {e}")
            return self._basic_matching(reference_analysis, templates, top_n)

    def _build_prompt(
        self, 
        reference: Dict, 
        templates: List[Dict], 
        top_n: int
    ) -> str:
        """
        Build the prompt for Gemini
        """
        # Limit templates to reduce token count
        limited_templates = templates[:30]

        layout = reference.get('layout_features', {})

        prompt = f"""You are an expert web design analyst and template matching specialist. 

Analyze the reference website and rank the provided Envato templates by similarity.

## REFERENCE WEBSITE ANALYSIS:
- URL: {reference.get('url')}
- Title: {reference.get('title')}
- Industry: {reference.get('industry', 'Unknown')}
- Platform/CMS: {reference.get('detected_cms', 'Unknown')}
- Framework: {reference.get('detected_framework', 'Unknown')}
- Color Palette: {reference.get('color_palette', [])}
- Layout Complexity: {layout.get('layout_complexity', 'unknown')}
- Has Hero Section: {layout.get('has_hero', False)}
- Has Pricing Section: {layout.get('has_pricing', False)}
- Has Testimonials: {layout.get('has_testimonials', False)}
- Has CTA: {layout.get('has_cta', False)}
- Keywords: {reference.get('keywords', [])}

## AVAILABLE ENVATO TEMPLATES (JSON format):
{json.dumps(limited_templates, indent=2)}

## TASK:
Rank the top {top_n} most similar templates to the reference website.

Similarity criteria (in order of importance):
1. Industry relevance (35%) - Must match the {reference.get('industry', 'general')} industry
2. Visual design style (25%) - Colors, modern/minimal/classic aesthetic
3. Layout structure (20%) - Hero sections, pricing tables, testimonials presence
4. Platform compatibility (15%) - WordPress/Shopify/HTML/etc match
5. Feature set (5%) - E-commerce, blog, portfolio capabilities

## OUTPUT FORMAT:
Return ONLY a JSON array with this exact structure (no markdown, no explanation):
[
  {{
    "rank": 1,
    "template_id": "exact_id_from_input",
    "title": "Template Title",
    "envato_url": "url_from_input",
    "preview_image": "image_url",
    "similarity_score": 95,
    "match_reasons": {{
      "visual": "Specific visual similarity (2-3 sentences)",
      "layout": "Layout structure match (1-2 sentences)",
      "industry": "Industry fit explanation (1-2 sentences)",
      "features": "Feature alignment (1-2 sentences)"
    }},
    "confidence": "high"
  }}
]

Rules:
- Only use templates from the provided list
- similarity_score must be 0-100
- Provide specific, detailed match_reasons
- Use exact template_id from input
- Return valid JSON only, no markdown formatting
- Include all {top_n} matches if possible"""

        return prompt

    def _parse_ai_response(
        self, 
        text: str, 
        templates: List[Dict], 
        top_n: int
    ) -> List[Dict]:
        """
        Parse AI response and validate against available templates
        """
        try:
            # Clean up the response
            text = text.strip()

            # Extract JSON if wrapped in markdown
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0]
            elif "```" in text:
                text = text.split("```")[1].split("```")[0]

            # Parse JSON
            matches = json.loads(text.strip())

            # Validate and enrich matches
            validated_matches = []
            template_map = {t['id']: t for t in templates}

            for match in matches[:top_n]:
                template_id = match.get('template_id')

                # Find full template data
                if template_id in template_map:
                    template = template_map[template_id]

                    validated_match = {
                        "rank": match.get('rank', len(validated_matches) + 1),
                        "template_id": template_id,
                        "title": match.get('title', template['title']),
                        "envato_url": match.get('envato_url', template['url']),
                        "preview_image": match.get('preview_image', template.get('preview_image', '')),
                        "similarity_score": match.get('similarity_score', 80),
                        "match_reasons": match.get('match_reasons', {
                            "visual": "AI-detected visual match",
                            "layout": "Layout structure compatible",
                            "industry": "Industry category match",
                            "features": "Feature set aligned"
                        }),
                        "confidence": match.get('confidence', 'medium'),
                        "tags": template.get('tags', [])
                    }

                    validated_matches.append(validated_match)

            return validated_matches

        except json.JSONDecodeError as e:
            print(f"⚠️ JSON parse error: {e}")
            return []
        except Exception as e:
            print(f"⚠️ Response parsing error: {e}")
            return []

    def _basic_matching(
        self, 
        reference: Dict, 
        templates: List[Dict], 
        top_n: int
    ) -> List[Dict]:
        """
        Fallback matching algorithm without AI
        """
        print("🔄 Running basic similarity matching...")

        scored_templates = []
        ref_industry = reference.get('industry', '').lower()
        ref_cms = reference.get('detected_cms', '').lower()
        ref_keywords = set(k.lower() for k in reference.get('keywords', []))
        layout = reference.get('layout_features', {})

        for template in templates:
            score = 0
            reasons = {
                "visual": "General style compatibility",
                "layout": "Standard responsive layout",
                "industry": "Broad category match",
                "features": "Core template features"
            }

            template_tags = [t.lower() for t in template.get('tags', [])]
            template_desc = template.get('description', '').lower()
            template_title = template.get('title', '').lower()
            combined_text = f"{template_desc} {template_title} {' '.join(template_tags)}"

            # Industry match (35 points)
            if ref_industry:
                industry_keywords = {
                    "saas/technology": ["saas", "tech", "software", "app", "startup", "digital"],
                    "e-commerce": ["shop", "store", "ecommerce", "woocommerce", "product", "cart"],
                    "medical": ["medical", "health", "doctor", "clinic", "care"],
                    "real estate": ["real estate", "property", "home", "listing"],
                    "education": ["education", "course", "learning", "school", "academy"],
                    "food/restaurant": ["restaurant", "food", "cafe", "menu", "dining"],
                    "fashion": ["fashion", "clothing", "apparel", "boutique"],
                    "corporate": ["business", "corporate", "company", "agency"],
                    "creative/portfolio": ["portfolio", "creative", "design", "agency"],
                    "non-profit": ["charity", "nonprofit", "donation", "cause"],
                    "travel": ["travel", "tour", "hotel", "booking"],
                    "blog/magazine": ["blog", "magazine", "news", "editorial"]
                }

                keywords = industry_keywords.get(ref_industry, [ref_industry])
                matches = sum(1 for kw in keywords if kw in combined_text)
                if matches > 0:
                    score += min(35, matches * 10)
                    reasons["industry"] = f"Matches {ref_industry} industry keywords"

            # CMS match (15 points)
            if ref_cms:
                if any(ref_cms in tag for tag in template_tags):
                    score += 15
                    reasons["features"] = f"Compatible with {ref_cms}"

            # Keyword overlap (20 points)
            if ref_keywords:
                matches = sum(1 for kw in ref_keywords if kw in combined_text)
                if matches > 0:
                    score += min(20, matches * 5)
                    reasons["layout"] = f"Contains {matches} matching keywords"

            # Layout feature hints (20 points)
            if layout.get('has_pricing') and any(x in combined_text for x in ['price', 'pricing', 'plan']):
                score += 10
                reasons["features"] += ", includes pricing sections"

            if layout.get('has_testimonials') and any(x in combined_text for x in ['testimonial', 'review']):
                score += 10
                reasons["features"] += ", testimonial sections"

            # Boost score for variety (ensure we get results)
            score = min(score + 10, 98)

            scored_templates.append({
                "template": template,
                "score": score,
                "reasons": reasons
            })

        # Sort by score descending
        scored_templates.sort(key=lambda x: x['score'], reverse=True)

        # Format output
        matches = []
        for i, item in enumerate(scored_templates[:top_n], 1):
            template = item['template']
            matches.append({
                "rank": i,
                "template_id": template['id'],
                "title": template['title'],
                "envato_url": template['url'],
                "preview_image": template.get('preview_image', ''),
                "similarity_score": item['score'],
                "match_reasons": item['reasons'],
                "confidence": "medium",
                "tags": template.get('tags', [])
            })

        print(f"✅ Basic matching complete: {len(matches)} results")
        return matches

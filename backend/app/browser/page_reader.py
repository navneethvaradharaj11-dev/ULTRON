import re
import logging
from typing import Dict, Any, List
from bs4 import BeautifulSoup

logger = logging.getLogger("ULTRON.PageReader")


class PageReader:
    """Parses raw HTML and live Playwright Chromium DOM pages into compact structured representations for LLM reasoning."""

    @classmethod
    async def parse_playwright_page(cls, page: Any) -> Dict[str, Any]:
        """Extract structured representation directly from a live Playwright Chromium page."""
        try:
            url = page.url
            title = await page.title()

            # Execute JS script inside Playwright Chromium to extract interactive elements & text
            dom_data = await page.evaluate("""() => {
                const title = document.title || "";
                const text = (document.body ? document.body.innerText : "").replace(/\\s+/g, ' ').slice(0, 5000);
                
                const elements = [];
                const links = [];
                
                const nodes = document.querySelectorAll('button, input, select, a, textarea, form, iframe');
                let idx = 1;
                nodes.forEach(node => {
                    const tag = node.tagName.toLowerCase();
                    const type = node.type || tag;
                    const textContent = (node.innerText || node.value || "").trim();
                    const id = node.id || `element_${idx++}`;
                    const label = node.getAttribute('aria-label') || node.placeholder || "";
                    const href = node.getAttribute('href') || "";
                    
                    if (tag === 'a' && href) {
                        links.push({ text: textContent || href, url: href });
                    }
                    
                    elements.push({
                        id: id,
                        type: type,
                        role: node.getAttribute('role') || tag,
                        text: textContent.slice(0, 100),
                        label: label.slice(0, 100),
                        name: node.name || "",
                        value: node.value || "",
                        placeholder: node.placeholder || ""
                    });
                });

                return {
                    title: title,
                    text: text,
                    elements: elements,
                    links: links
                };
            }""")

            return {
                "url": url,
                "title": dom_data.get("title") or title,
                "elements": dom_data.get("elements", [])[:50],
                "text": dom_data.get("text", ""),
                "links": dom_data.get("links", [])[:30]
            }

        except Exception as e:
            logger.error("Failed to parse Playwright live DOM: %s", e)
            url = page.url if hasattr(page, "url") else "unknown"
            return {"url": url, "title": "Error Reading DOM", "elements": [], "text": str(e), "links": []}

    @classmethod
    def parse_html(cls, url: str, html_content: str) -> Dict[str, Any]:
        """Convert HTML string into a compact structured dictionary representation."""
        if not html_content or not isinstance(html_content, str):
            return {
                "url": url,
                "title": "",
                "elements": [],
                "text": "",
                "links": []
            }

        try:
            soup = BeautifulSoup(html_content, "html.parser")

            title_tag = soup.find("title")
            title = title_tag.get_text().strip() if title_tag else ""

            for script_or_style in soup(["script", "style", "noscript", "svg"]):
                script_or_style.decompose()

            text = soup.get_text(separator=" ", strip=True)
            text = re.sub(r"\s+", " ", text)[:5000]

            elements: List[Dict[str, Any]] = []
            links: List[Dict[str, str]] = []

            elem_idx = 1
            for tag in soup.find_all(["a", "button", "input", "select", "textarea", "form"]):
                tag_name = tag.name.lower()
                tag_type = tag.get("type", tag_name).lower()
                tag_text = tag.get_text().strip()
                tag_id = tag.get("id", f"element_{elem_idx}")
                tag_role = tag.get("role", tag_name)
                tag_label = tag.get("aria-label", tag.get("placeholder", ""))
                href = tag.get("href", "")

                if tag_name == "a" and href:
                    links.append({"text": tag_text or href, "url": href})

                element_obj = {
                    "id": tag_id,
                    "type": tag_type,
                    "role": tag_role,
                    "text": tag_text[:100],
                    "label": tag_label[:100] if tag_label else "",
                    "name": tag.get("name", "")
                }
                if tag_name == "input":
                    element_obj["value"] = tag.get("value", "")
                    element_obj["placeholder"] = tag.get("placeholder", "")
                if tag_name == "a":
                    element_obj["href"] = href

                elements.append(element_obj)
                elem_idx += 1

            return {
                "url": url,
                "title": title,
                "elements": elements[:50],
                "text": text,
                "links": links[:30]
            }

        except Exception as e:
            logger.error("PageReader parsing error for URL '%s': %s", url, e)
            return {
                "url": url,
                "title": "Parsing Error",
                "elements": [],
                "text": html_content[:1000],
                "links": []
            }

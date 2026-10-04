from typing import Dict, Any, List
from playwright.async_api import Page


class BrowserInspector:
    async def inspect_page(self, page: Page) -> Dict[str, Any]:
        """
        Inspects current Playwright page and returns structured accessibility tree and DOM elements summary.
        """
        url = page.url
        title = await page.title()

        js_script = r"""
        () => {
            const isVisible = (elem) => {
                if (!elem) return false;
                const style = window.getComputedStyle(elem);
                if (style.display === 'none' || style.visibility === 'hidden' || style.opacity === '0') return false;
                const rect = elem.getBoundingClientRect();
                return rect.width > 0 && rect.height > 0;
            };

            const getUniqueSelector = (elem) => {
                if (elem.id) return `#${CSS.escape(elem.id)}`;
                if (elem.name) return `${elem.tagName.toLowerCase()}[name="${elem.name}"]`;
                if (elem.getAttribute('aria-label')) return `${elem.tagName.toLowerCase()}[aria-label="${elem.getAttribute('aria-label')}"]`;
                if (elem.placeholder) return `${elem.tagName.toLowerCase()}[placeholder="${elem.placeholder}"]`;
                return elem.tagName.toLowerCase();
            };

            const elements = Array.from(document.querySelectorAll('a, button, input, select, textarea, [role="button"], [role="link"], [role="textbox"], [role="option"]'));
            const extracted = [];
            let counter = 1;

            for (const el of elements) {
                if (!isVisible(el)) continue;
                extracted.push({
                    id: counter++,
                    tag: el.tagName.toLowerCase(),
                    role: el.getAttribute('role') || el.tagName.toLowerCase(),
                    type: el.getAttribute('type') || '',
                    text: (el.innerText || el.textContent || el.value || '').trim().replace(/\s+/g, ' ').substring(0, 100),
                    name: el.getAttribute('name') || '',
                    label: el.getAttribute('aria-label') || '',
                    placeholder: el.getAttribute('placeholder') || '',
                    value: el.value || '',
                    selector: getUniqueSelector(el)
                });
            }

            const links = Array.from(document.querySelectorAll('a[href]'))
                .filter(isVisible)
                .map(a => ({ text: a.innerText.trim(), href: a.href }))
                .filter(l => l.href.length > 0 && !l.href.startsWith('javascript:'));

            const bodyText = (document.body ? document.body.innerText : '').replace(/\s+/g, ' ').trim();

            return {
                elements: extracted,
                links: links.slice(0, 20),
                body_text: bodyText
            };
        }
        """
        res = await page.evaluate(js_script)

        return {
            "url": url,
            "title": title,
            "elements": res.get("elements", []),
            "links": res.get("links", []),
            "body_text": res.get("body_text", "")
        }


inspector = BrowserInspector()

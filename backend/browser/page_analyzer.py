import json
from typing import Dict, Any, List, Optional
from playwright.async_api import Page


class PageElement:
    def __init__(self, ref_id: int, tag: str, type_attr: str, role: str, text: str, name: str, placeholder: str, selector: str, value: str = ""):
        self.ref_id = ref_id
        self.tag = tag
        self.type_attr = type_attr
        self.role = role
        self.text = text
        self.name = name
        self.placeholder = placeholder
        self.selector = selector
        self.value = value

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ref_id": self.ref_id,
            "tag": self.tag,
            "type": self.type_attr,
            "role": self.role,
            "text": self.text,
            "name": self.name,
            "placeholder": self.placeholder,
            "selector": self.selector,
            "value": self.value
        }

    def __repr__(self) -> str:
        attrs = []
        if self.ref_id: attrs.append(f"ref={self.ref_id}")
        if self.text: attrs.append(f"text='{self.text[:30]}'")
        if self.name: attrs.append(f"name='{self.name}'")
        if self.placeholder: attrs.append(f"placeholder='{self.placeholder}'")
        if self.type_attr: attrs.append(f"type='{self.type_attr}'")
        if self.value: attrs.append(f"value='{self.value[:20]}'")
        return f"[{self.ref_id}] <{self.tag} selector='{self.selector}' {' '.join(attrs)}>"


class PageAnalysis:
    def __init__(self, url: str, title: str, elements: List[PageElement], main_text: str, headings: List[str], forms_summary: List[Dict[str, Any]], tables_summary: List[Dict[str, Any]]):
        self.url = url
        self.title = title
        self.elements = elements
        self.main_text = main_text
        self.headings = headings
        self.forms_summary = forms_summary
        self.tables_summary = tables_summary

    def format_for_llm(self) -> str:
        """
        Formats the current page state into a clean, token-efficient text representation for LLM prompt.
        """
        lines = [
            f"--- PAGE OBSERVATION ---",
            f"URL: {self.url}",
            f"Title: {self.title}",
            f"\nHEADINGS:",
        ]
        for h in self.headings[:8]:
            lines.append(f"- {h}")

        lines.append(f"\nINTERACTIVE ELEMENTS ({len(self.elements)} items):")
        for el in self.elements:
            lines.append(str(el))

        if self.forms_summary:
            lines.append(f"\nFORMS DETECTED:")
            for f in self.forms_summary:
                lines.append(f"- Form action='{f.get('action')}' fields={f.get('fields')}")

        if self.tables_summary:
            lines.append(f"\nTABLES DETECTED:")
            for t in self.tables_summary:
                lines.append(f"- Table rows={t.get('rows')} headers={t.get('headers')}")

        lines.append(f"\nVISIBLE TEXT SUMMARY (Excerpt):")
        lines.append(self.main_text[:1500] if self.main_text else "(No text content)")
        lines.append("-------------------------")

        return "\n".join(lines)


class PageAnalyzer:
    async def analyze(self, page: Page) -> PageAnalysis:
        """
        Parses DOM structure and accessibility tree of current Playwright page.
        """
        url = page.url
        title = await page.title()

        # Execute JS extraction script in browser context
        extraction_js = r"""
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
                
                // Fallback tag with text/class index
                let selector = elem.tagName.toLowerCase();
                if (elem.className && typeof elem.className === 'string' && elem.className.trim()) {
                    const firstClass = elem.className.trim().split(/\s+/)[0];
                    if (firstClass && !firstClass.includes(':')) selector += `.${CSS.escape(firstClass)}`;
                }
                return selector;
            };

            const allElements = Array.from(document.querySelectorAll('a, button, input, select, textarea, [role="button"], [role="link"], [role="textbox"], [role="option"], [onclick]'));
            
            const interactiveElements = [];
            let idCounter = 1;

            for (const el of allElements) {
                if (!isVisible(el)) continue;
                
                const tag = el.tagName.toLowerCase();
                const typeAttr = el.getAttribute('type') || '';
                const role = el.getAttribute('role') || '';
                const text = (el.innerText || el.textContent || el.value || '').trim().replace(/\s+/g, ' ');
                const name = el.getAttribute('name') || '';
                const placeholder = el.getAttribute('placeholder') || '';
                const value = el.value || '';
                const selector = getUniqueSelector(el);

                interactiveElements.push({
                    ref_id: idCounter++,
                    tag: tag,
                    type: typeAttr,
                    role: role,
                    text: text.substring(0, 100),
                    name: name,
                    placeholder: placeholder,
                    selector: selector,
                    value: value
                });
            }

            const headings = Array.from(document.querySelectorAll('h1, h2, h3'))
                .filter(isVisible)
                .map(h => (h.innerText || '').trim())
                .filter(txt => txt.length > 0);

            const forms = Array.from(document.querySelectorAll('form'))
                .filter(isVisible)
                .map(f => ({
                    action: f.getAttribute('action') || '',
                    fields: Array.from(f.querySelectorAll('input, select, textarea')).map(i => i.name || i.id || i.type)
                }));

            const tables = Array.from(document.querySelectorAll('table'))
                .filter(isVisible)
                .map(t => ({
                    headers: Array.from(t.querySelectorAll('th')).map(th => th.innerText.trim()),
                    rows: t.querySelectorAll('tr').length
                }));

            const bodyText = (document.body ? document.body.innerText : '').replace(/\s+/g, ' ').trim();

            return {
                elements: interactiveElements,
                headings: headings,
                forms: forms,
                tables: tables,
                main_text: bodyText
            };
        }
        """
        res = await page.evaluate(extraction_js)

        element_objects = [
            PageElement(
                ref_id=e["ref_id"],
                tag=e["tag"],
                type_attr=e["type"],
                role=e["role"],
                text=e["text"],
                name=e["name"],
                placeholder=e["placeholder"],
                selector=e["selector"],
                value=e["value"]
            )
            for e in res.get("elements", [])
        ]

        return PageAnalysis(
            url=url,
            title=title,
            elements=element_objects,
            main_text=res.get("main_text", ""),
            headings=res.get("headings", []),
            forms_summary=res.get("forms", []),
            tables_summary=res.get("tables", [])
        )


page_analyzer = PageAnalyzer()

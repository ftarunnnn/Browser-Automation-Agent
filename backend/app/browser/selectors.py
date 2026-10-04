from typing import Optional, List, Dict, Any
from playwright.async_api import Page, Locator


class SelectorEngine:
    """
    Robust Element Selector Engine implementing strict priority hierarchy:
    1. getByRole
    2. getByLabel
    3. getByPlaceholder
    4. getByText
    5. Stable CSS selector (#id, [name=...], [aria-label=...])
    6. XPath fallback
    """

    @staticmethod
    def get_locator(
        page: Page,
        role: Optional[str] = None,
        label: Optional[str] = None,
        placeholder: Optional[str] = None,
        text: Optional[str] = None,
        selector: Optional[str] = None,
        xpath: Optional[str] = None
    ) -> Locator:
        # Priority 1: Role
        if role and text:
            try:
                return page.get_by_role(role, name=text).first
            except Exception:
                pass
        elif role:
            try:
                return page.get_by_role(role).first
            except Exception:
                pass

        # Priority 2: Label
        if label:
            try:
                return page.get_by_label(label).first
            except Exception:
                pass

        # Priority 3: Placeholder
        if placeholder:
            try:
                return page.get_by_placeholder(placeholder).first
            except Exception:
                pass

        # Priority 4: Text
        if text:
            try:
                return page.get_by_text(text, exact=False).first
            except Exception:
                pass

        # Priority 5: CSS Selector
        if selector:
            return page.locator(selector).first

        # Priority 6: XPath Fallback
        if xpath:
            return page.locator(f"xpath={xpath}").first

        # Fallback body locator
        return page.locator("body")

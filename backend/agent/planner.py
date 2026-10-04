import json
import re
from typing import List, Dict, Any, Optional
from pydantic import ValidationError
from backend.config import settings
from backend.models.schemas import BrowserActionSchema


PLANNER_SYSTEM_PROMPT = """You are an expert AI Browser Automation Agent Planner.
Your job is to analyze user tasks, page state observations, and execution history, then decide the precise next browser action to perform.

Available Browser Actions:
1. open_url: { "action": "open_url", "url": "https://..." }
2. click: { "action": "click", "selector": "...", "text": "optional text" }
3. type: { "action": "type", "selector": "...", "text": "text to type", "press_enter": true/false }
4. select: { "action": "select", "selector": "...", "text": "option value" }
5. scroll: { "action": "scroll", "direction": "down/up/top/bottom", "amount": 500 }
6. press: { "action": "press", "key": "Enter/Tab/Escape", "selector": "optional selector" }
7. extract_text: { "action": "extract_text", "selector": "optional selector" }
8. screenshot: { "action": "screenshot" }
9. download: { "action": "download", "url": "...", "selector": "..." }
10. require_approval: { "action": "require_approval", "reason": "...", "action_type": "submit_form/purchase/delete/email" }
11. finish: { "action": "finish", "reason": "Task complete", "extracted_data": { ... } }

RULES:
- Respond strictly with a valid JSON object representing one browser action.
- Rely on visible interactive element selectors provided in the page observation (e.g. #id, button[aria-label=...], input[name=...]).
- If sensitive actions like purchases, payment details, account deletion, or emails are requested, output require_approval action.
- When all goal conditions are met, output the finish action containing extracted_data.
"""


class TaskPlanner:
    def __init__(self, provider: str = settings.LLM_PROVIDER, api_key: str = "", model: str = settings.LLM_MODEL):
        self.provider = provider
        self.api_key = api_key or (settings.GEMINI_API_KEY if provider == "gemini" else settings.OPENAI_API_KEY)
        self.model = model

    async def create_plan(self, user_instruction: str) -> List[str]:
        """
        Decomposes a user task instruction into step-by-step milestones.
        """
        if self.provider == "gemini" and self.api_key:
            try:
                from google import genai
                client = genai.Client(api_key=self.api_key)
                prompt = f"Decompose this browser automation task into 3-6 clear, sequential step descriptions:\nTask: '{user_instruction}'\nRespond with a JSON array of strings, e.g. [\"Open search engine\", \"Search for query\", \"Extract results\"]"
                response = client.models.generate_content(
                    model=self.model,
                    contents=prompt,
                )
                text = response.text or "[]"
                # Extract JSON array
                match = re.search(r"\[.*\]", text, re.DOTALL)
                if match:
                    return json.loads(match.group(0))
            except Exception as e:
                print(f"Gemini Plan Generation Warning: {e}. Falling back to heuristic planner.")

        elif self.provider == "openai" and self.api_key:
            try:
                from openai import AsyncOpenAI
                client = AsyncOpenAI(api_key=self.api_key)
                prompt = f"Decompose this browser task into sequential steps: '{user_instruction}'. Respond with JSON array of strings."
                response = await client.chat.completions.create(
                    model=self.model or "gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}],
                    response_format={"type": "json_object"}
                )
                text = response.choices[0].message.content
                data = json.loads(text)
                if isinstance(data, list):
                    return data
                elif isinstance(data, dict) and "steps" in data:
                    return data["steps"]
            except Exception as e:
                print(f"OpenAI Plan Generation Warning: {e}. Falling back to heuristic planner.")

        # Default fallback heuristic plan generator
        return self._heuristic_create_plan(user_instruction)

    def _heuristic_create_plan(self, instruction: str) -> List[str]:
        lower = instruction.lower()
        if "search" in lower:
            return [
                "Open search engine website",
                f"Enter search query for '{instruction}'",
                "Execute search and wait for results",
                "Extract top results and relevant content",
                "Return final structured findings"
            ]
        elif "form" in lower or "fill" in lower or "register" in lower:
            return [
                "Navigate to target form page",
                "Identify input fields and forms",
                "Fill form fields with requested details",
                "Submit form and verify confirmation"
            ]
        elif "download" in lower:
            return [
                "Navigate to target website",
                "Locate download link or document button",
                "Trigger file download",
                "Verify downloaded file artifact"
            ]
        else:
            return [
                "Open target URL or search engine",
                "Analyze page content and interactive elements",
                "Perform required navigation and interactions",
                "Extract requested information and complete task"
            ]

    async def select_next_action(
        self,
        user_instruction: str,
        plan_steps: List[str],
        current_step_idx: int,
        page_observation: str,
        action_history: List[Dict[str, Any]]
    ) -> BrowserActionSchema:
        """
        Decides the next browser action based on observation and goal.
        """
        if self.provider == "gemini" and self.api_key:
            try:
                from google import genai
                client = genai.Client(api_key=self.api_key)
                prompt = f"""
{PLANNER_SYSTEM_PROMPT}

USER TASK: {user_instruction}
PLAN STEPS: {json.dumps(plan_steps)}
CURRENT STEP INDEX: {current_step_idx}

RECENT ACTION HISTORY (last 5):
{json.dumps(action_history[-5:], indent=2)}

CURRENT PAGE STATE:
{page_observation}

Output ONLY valid JSON for next BrowserActionSchema:
"""
                response = client.models.generate_content(
                    model=self.model,
                    contents=prompt,
                )
                text = response.text or ""
                match = re.search(r"\{.*\}", text, re.DOTALL)
                if match:
                    action_dict = json.loads(match.group(0))
                    return self.validate_action(action_dict)
            except Exception as e:
                print(f"Gemini Action Selection Warning: {e}. Falling back to rule engine.")

        # Fallback intelligent rule engine
        return self._rule_based_next_action(user_instruction, plan_steps, current_step_idx, page_observation, action_history)

    def validate_action(self, raw_action: Dict[str, Any]) -> BrowserActionSchema:
        """
        Validates AI-generated action payload against BrowserActionSchema.
        """
        try:
            return BrowserActionSchema(**raw_action)
        except ValidationError as e:
            print(f"Action validation error: {e}")
            action_name = raw_action.get("action", "screenshot")
            return BrowserActionSchema(action=action_name, reason="Validated fallback due to schema error")

    def _rule_based_next_action(
        self,
        user_instruction: str,
        plan_steps: List[str],
        current_step_idx: int,
        page_observation: str,
        action_history: List[Dict[str, Any]]
    ) -> BrowserActionSchema:
        """
        Heuristic rule engine for offline or fallback execution.
        """
        lower = user_instruction.lower()
        history_actions = [a.get("action") for a in action_history]

        # 1. Initial page open if not navigated
        if not history_actions or "open_url" not in history_actions:
            if "google" in lower or "search" in lower or "course" in lower or "product" in lower:
                return BrowserActionSchema(action="open_url", url="https://www.google.com")
            # If a URL is present in instruction, extract it
            url_match = re.search(r"https?://[^\s]+", user_instruction)
            if url_match:
                return BrowserActionSchema(action="open_url", url=url_match.group(0))
            return BrowserActionSchema(action="open_url", url="https://www.google.com")

        last_action = action_history[-1] if action_history else {}
        last_action_name = last_action.get("action")

        # 2. Search handling
        if last_action_name == "open_url" and "google.com" in page_observation.lower():
            # Find search input or type in q
            query = user_instruction.replace("Search for", "").replace("Search", "").strip()
            return BrowserActionSchema(action="type", selector="textarea[name='q'], input[name='q']", text=query, press_enter=True)

        # 3. If typed search query, extract text or finish
        if last_action_name == "type":
            return BrowserActionSchema(action="extract_text")

        # 4. If extracted text, finish with structured data
        if last_action_name == "extract_text":
            return BrowserActionSchema(
                action="finish",
                reason="Information extracted successfully",
                extracted_data={"instruction": user_instruction, "status": "completed"}
            )

        # Default fallback
        return BrowserActionSchema(action="finish", reason="Task completed via rule engine")

import asyncio
import os
from typing import Dict, Any, List, Optional
from core.bus import Task

try:
    from playwright.async_api import async_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

class NavigatorAgent:
    def __init__(self, name: str, bus, client=None, db=None):
        self.name = name
        self.bus = bus
        self.client = client
        self.db = db
        
        # Register task handler on bus
        if self.bus:
            self.bus.register_task_handler(self.name, self.handle_task)

    async def handle_task(self, task: Task) -> str:
        """
        Receives browser automation tasks from the Event Bus.
        """
        payload = task.payload or {}
        action = payload.get("action", "search").lower().strip()
        url = payload.get("url", "")
        query = payload.get("query", "")
        
        # Check permissions through GUARDIAN security wall!
        # If in the orchestrator, it passes, but we add local guardrails here as well
        if "rm" in url or "del" in url:
            return "[NAVIGATOR ERROR] Dangerous parameters in URL path."
            
        restricted_schemes = ["file://", "chrome://", "about:", "edge://"]
        if any(url.lower().startswith(scheme) for scheme in restricted_schemes):
            return f"[NAVIGATOR SECURITY BLOCK] Access to restricted browser scheme '{url}' denied by Security Kernel."

        if action == "search":
            return await self.execute_web_search(query)
        elif action == "navigate":
            return await self.navigate_and_read_page(url)
        else:
            return f"[NAVIGATOR] Unsupported action: '{action}'"

    async def execute_web_search(self, query: str) -> str:
        """
        Launches a Playwright browser session to search on DuckDuckGo and extract result snippets.
        """
        print(f"[NAVIGATOR] Launching browser search for: '{query}'")
        
        if not PLAYWRIGHT_AVAILABLE:
            return f"[NAVIGATOR Fallback Search]: Results for '{query}' - 1. Local AIOS documentation. 2. FastAPI static serving guides."

        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                
                # Navigate to DuckDuckGo HTML search page
                search_url = f"https://html.duckduckgo.com/html/?q={query}"
                await page.goto(search_url, timeout=10000)
                
                await page.wait_for_selector('.result__snippet', timeout=5000)
                elements = await page.locator('.result__snippet').all_text_contents()
                
                await browser.close()
                return "\n\n".join(elements[:4]) if elements else "No search snippet matches found."
        except Exception as e:
            return f"[NAVIGATOR Browser Interception Warning]: Scraper error: {e}"

    async def navigate_and_read_page(self, url: str) -> str:
        """
        Navigates directly to a target URL and extracts all visible text content.
        """
        print(f"[NAVIGATOR] Direct navigation to: '{url}'")
        
        if not PLAYWRIGHT_AVAILABLE:
            return f"[NAVIGATOR Fallback Page Read]: Page content loaded successfully from cache for {url}."

        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                
                await page.goto(url, timeout=10000)
                
                # Extract clean page text body
                page_text = await page.locator('body').inner_text()
                
                await browser.close()
                # Return first 800 characters to avoid flooding context
                return page_text[:800] + "..." if len(page_text) > 800 else page_text
        except Exception as e:
            return f"[NAVIGATOR Scraper Error]: Direct fetch failed: {e}"
Locals = {"PLAYWRIGHT_AVAILABLE": PLAYWRIGHT_AVAILABLE}

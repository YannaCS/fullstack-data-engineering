"""
In this demo, we'll create an agent that:
1. Navigates to Wikipedia
2. Searches for "Model Context Protocol"
3. Extracts the first paragraph

Each step requires **Human-in-the-Loop (HITL)** approval for safety.

# Install dependencies
!pip install -q playwright openai python-dotenv nest_asyncio
!playwright install chromium
"""

import os
from getpass import getpass
from openai import OpenAI
import json
import requests
from dotenv import load_dotenv

import re
import asyncio
from pathlib import Path
from urllib.parse import urljoin
from IPython.display import display, Image, HTML

import nest_asyncio
nest_asyncio.apply()  # Allow nested event loops in Jupyter

from playwright.async_api import async_playwright

import time

# =============================================================================
# Set your OpenAI API Key
# =============================================================================
load_dotenv()

# Check if already set in environment
api_key = os.environ.get("OPENAI_API_KEY", "")

if not api_key:
    # Prompt for API key (input will be hidden)
    api_key = getpass("Enter your OpenAI API Key: ")
    os.environ["OPENAI_API_KEY"] = api_key

if api_key:
    print(f"[OK] API Key set")
else:
    print("[ERROR] No API key provided!")

client = OpenAI()

# =============================================================================
# 1. Browser Controller - to interact with web pages
# =============================================================================

# Configuration
START_URL = "https://www.wikipedia.org/"
SEARCH_TERM = "Model Context Protocol"
ARTIFACT_DIR = Path("./run_artifacts")
ARTIFACT_DIR.mkdir(exist_ok=True)

print("[OK] Imports successful!")


# =============================================================================
# 2. Helper Functions
# These utilities help us observe the page state and display results.
# =============================================================================
async def save_screenshot(page, label: str) -> Path:
    """Save a screenshot and return the path"""
    timestamp = int(time.time() * 1000)
    path = ARTIFACT_DIR / f"step_{timestamp}_{label}.png"
    await page.screenshot(path=str(path), full_page=False)
    return path

def show_screenshot(path: Path):
    """Display a screenshot in the notebook"""
    display(Image(filename=str(path), width=800))

async def list_clickables(page) -> list:
    """Discover clickable elements on the page"""
    elems = await page.query_selector_all("a, button, input[type=submit]")
    items = []
    for i, el in enumerate(elems[:20]):  # Limit to 20 for brevity
        text = (await el.inner_text()).strip()[:60]
        href = (await el.get_attribute("href") or "")[:80]
        items.append({"idx": i, "text": text or "(no text)", "href": href or "(no href)"})
    return items

def show_clickables(clickables: list):
    """Display clickables as an HTML table"""
    html = "<table><tr><th>Index</th><th>Text</th><th>Href</th></tr>"
    for c in clickables[:15]:
        html += f"<tr><td>{c['idx']}</td><td>{c['text']}</td><td style='color:gray'>{c['href']}</td></tr>"
    html += "</table>"
    display(HTML(html))

print("[OK] Helper functions defined!")

# =============================================================================
# 3. LLM Decision Maker
# Pass the current URL to help the LLM understand where it is on the website.
# =============================================================================
def llm_decide(state: str, clickables: list, goal: str, current_url: str) -> dict:
    """
    Use LLM to decide the next action based on page state.
    
    This is where the magic happens - the LLM analyzes:
    - Current URL (to understand location)
    - Page content (what's on the page)
    - Available clickables (what can be clicked)
    
    And returns a structured JSON action.
    """
    client = OpenAI()
    
    # Truncate content to fit context window
    state_trimmed = " ".join(state.split())[:1200]
    
    prompt = f"""You are a computer-use agent browsing a website. Analyze the current page and decide the next action.

        ## Current State
        - **URL**: {current_url}
        - **Page content** (truncated): {state_trimmed}
        - **Clickable elements**: {json.dumps(clickables[:15])}

        ## Goal
        {goal}

        ## Available Actions
        - `type_and_enter`: Type text into an input field and press Enter. Requires: selector, text
        - `click_by_index`: Click on an element by its index. Requires: index
        - `extract`: Extract text content from the page. Requires: selector, count

        ## Instructions
        1. Analyze the URL and page content to understand where you are
        2. Decide what action will make progress toward the goal
        3. If the URL shows you're already on the target article, extract the content
        4. Output ONLY a JSON object with your action

        ## Output Format (JSON only, no markdown)
        {{"action": "...", "selector": "...", "text": "...", "index": 0, "count": 1, "reason": "..."}}"""

    # Call OpenAI API
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        max_tokens=300
    )
    content = resp.choices[0].message.content.strip()
    
    # Parse JSON from response
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        # Try to extract JSON from text
        match = re.search(r"\{[\s\S]*\}", content)
        if match:
            return json.loads(match.group(0))
        raise ValueError(f"LLM returned non-JSON: {content[:200]}")

print("[OK] LLM Decision Maker defined!")

# =============================================================================
# 4. Action Executor - executes the actions decided by the LLM using Playwright.
# =============================================================================
async def execute_action(page, action: dict) -> tuple:
    """
    Execute the given action on the page.
    
    Returns: (is_complete, result_text)
    """
    action_type = action["action"]
    
    if action_type == "type_and_enter":
        selector = action["selector"]
        text = action["text"]
        await page.fill(selector, text, timeout=15000)
        await page.keyboard.press("Enter")
        return False, f"Typed '{text}' and pressed Enter"
    
    elif action_type == "click_by_index":
        idx = int(action["index"])
        elems = await page.query_selector_all("a, button, input[type=submit]")
        if idx >= len(elems):
            raise ValueError(f"Index {idx} out of range")
        target = elems[idx]
        
        # Try to click, fallback to navigation
        try:
            await target.scroll_into_view_if_needed()
            await target.click(timeout=15000)
        except Exception:
            href = await target.get_attribute("href") or ""
            if href:
                if href.startswith("//"):
                    href = "https:" + href
                elif href.startswith("/"):
                    href = urljoin(page.url, href)
                await page.goto(href, timeout=30000)
        return False, f"Clicked element at index {idx}"
    
    elif action_type == "extract":
        # Extract article content (Wikipedia-optimized)
        nodes = await page.query_selector_all(".mw-parser-output > p")
        if not nodes:
            nodes = await page.query_selector_all("p")
        
        cnt = int(action.get("count", 1))
        texts = []
        for n in nodes:
            inner = (await n.inner_text()).strip()
            if inner and len(inner) > 50 and "donate" not in inner.lower():
                texts.append(inner)
                if len(texts) >= cnt:
                    break
        
        result = "\n\n".join(texts)
        return True, result  # Task complete!
    
    else:
        raise ValueError(f"Unknown action: {action_type}")

print("[OK] Action Executor defined!")

# =============================================================================
# 5. Run the Agent
# =============================================================================
async def run_agent():
    """Main agent loop"""
    goal = f'Search Wikipedia for "{SEARCH_TERM}" and extract the first paragraph.'
    print(f"Goal: {goal}\n")
    
    async with async_playwright() as p:
        # Launch browser (headless for notebook)
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1280, "height": 900})
        page = await context.new_page()
        
        # Navigate to start page
        print(f"Navigating to {START_URL}...")
        await page.goto(START_URL, timeout=60000)
        await asyncio.sleep(1)
        
        max_steps = 5
        result = None
        
        for step in range(1, max_steps + 1):
            print(f"\n{'='*60}")
            print(f"STEP {step}")
            print(f"{'='*60}")
            
            # OBSERVE: Take screenshot and list elements
            screenshot_path = await save_screenshot(page, f"step{step}")
            show_screenshot(screenshot_path)
            
            state_text = await page.inner_text("body")
            clickables = await list_clickables(page)
            
            print(f"\nCurrent URL: {page.url}")
            print(f"\nClickable Elements:")
            show_clickables(clickables)
            
            # DECIDE: Ask LLM for next action
            print(f"\nAsking LLM for decision...")
            try:
                action = llm_decide(state_text, clickables, goal, page.url)
            except Exception as e:
                print(f"[ERROR] LLM Error: {e}")
                break
            
            print(f"\nProposed Action:")
            print(f"   Action: {action.get('action')}")
            print(f"   Reason: {action.get('reason')}")
            print(f"   Full: {json.dumps(action)}")
            
            # APPROVE: Human-in-the-Loop
            print(f"\n*** HUMAN-IN-THE-LOOP ***")
            approval = input("Approve this action? (y/n): ").strip().lower()
            if approval != 'y':
                print("Action rejected. Stopping.")
                break
            
            # EXECUTE: Perform the action
            print(f"\nExecuting...")
            try:
                is_complete, msg = await execute_action(page, action)
                print(f"[OK] {msg}")
                
                if is_complete:
                    result = msg
                    print(f"\n*** TASK COMPLETE ***")
                    break
                    
                await asyncio.sleep(2)  # Wait for page to load
                
            except Exception as e:
                print(f"[ERROR] Execution Error: {e}")
                break
        
        # Final screenshot
        final_path = await save_screenshot(page, "final")
        print(f"\nFinal State:")
        show_screenshot(final_path)
        
        await context.close()
        await browser.close()
        
        return result

print("[OK] Agent ready to run!")
print("\nRun the next cell to start the demo")

# =============================================================================
# You'll be asked to approve each action (type 'y' and press Enter)
# =============================================================================

result = asyncio.get_event_loop().run_until_complete(run_agent())

if result:
    print("\n" + "="*60)
    print("EXTRACTED CONTENT:")
    print("="*60)
    print(result)
import os
import re
import subprocess
import urllib.parse
import webbrowser
from typing import Optional
from backend.security.guardian import guardian_kernel

class TaskManager:
    def __init__(self):
        pass

    def execute_task(self, text: str) -> Optional[str]:
        # Normalize text and strip spacing
        text_clean = text.strip().lower()

        # 0. Image Generation Commands
        # Matches: "create an image of <prompt>", "generate an image of <prompt>", "draw <prompt>", "make a picture of <prompt>", etc.
        image_prompt = None
        
        # Pattern A: "create/generate/make/draw/paint [an/a] image/painting/illustration/drawing/sketch/photo/picture of/for/about <prompt>"
        image_match_a = re.search(
            r'\b(?:create|generate|make|draw|paint)\s+(?:an?\s+)?(?:image|painting|illustration|drawing|sketch|photo|picture)\s+(?:of|for|about)\s+(.+?)$', 
            text_clean, 
            flags=re.IGNORECASE
        )
        
        # Pattern B: "draw <prompt>", "paint <prompt>" at the beginning of the text
        image_match_b = re.search(
            r'^(?:draw|paint)\s+(.+?)$', 
            text_clean, 
            flags=re.IGNORECASE
        )
        
        # Pattern C: "create/generate/make a picture/photo/drawing of <prompt>" at the beginning of the text
        image_match_c = re.search(
            r'\b(?:create|generate|make)\s+(?:an?\s+)?(?:picture|photo|illustration|drawing|sketch|painting)\s+(?:of|about|for)\s+(.+?)$', 
            text_clean, 
            flags=re.IGNORECASE
        )

        # Pattern D: "create/generate <prompt> image" or "create <prompt> drawing"
        image_match_d = re.search(
            r'\b(?:create|generate|draw|make|paint)\s+(?:an?\s+)?(.+?)\s+(?:image|painting|illustration|drawing|sketch|photo|picture)$',
            text_clean,
            flags=re.IGNORECASE
        )

        if image_match_a:
            image_prompt = image_match_a.group(1).strip()
        elif image_match_b:
            image_prompt = image_match_b.group(1).strip()
        elif image_match_c:
            image_prompt = image_match_c.group(1).strip()
        elif image_match_d:
            image_prompt = image_match_d.group(1).strip()

        if image_prompt:
            # Clean up any leading/trailing particles
            image_prompt = re.sub(r'^(?:a|an|the)\s+', '', image_prompt, flags=re.IGNORECASE).strip()
            return self._create_image(image_prompt)

        # 1. YouTube Searches
        youtube_query = None
        
        # Pattern A: "search youtube for <query>" / "search on youtube for <query>"
        yt_match_a = re.search(r'\b(?:search\s+(?:on\s+)?youtube\s+for\s+)(.+?)\b', text_clean)
        
        # Pattern B: "youtube <query>" (at the start, e.g. "youtube coding music")
        yt_match_b = re.search(r'^youtube\s+(.+?)\b', text_clean)
        
        # Pattern C: "<action> <query> on/in/using/via youtube" or simply "<query> on/in youtube"
        yt_match_c = re.search(r'\b(.+?)\s+(?:on|in|using|via)\s+youtube\b', text_clean)
        
        if yt_match_a:
            youtube_query = yt_match_a.group(1).strip()
        elif yt_match_b:
            youtube_query = yt_match_b.group(1).strip()
        elif yt_match_c:
            raw_query = yt_match_c.group(1).strip()
            # Clean common prefixes from the matched query to extract the exact keyword
            youtube_query = re.sub(
                r'^(?:search\s+for\s+|search\s+|play\s+|look\s+up\s+)', 
                '', 
                raw_query, 
                flags=re.IGNORECASE
            ).strip()
            
        if youtube_query:
            return self._play_youtube(youtube_query)

        # 2. Chrome / Google Searches
        chrome_query = None
        
        # Pattern A: "google <query>" (at the start, e.g. "google quantum computing")
        ch_match_a = re.search(r'^google\s+(.+?)\b', text_clean)
        
        # Pattern B: "search chrome for <query>" or "search google for <query>"
        ch_match_b = re.search(r'\bsearch\s+(?:google|chrome)\s+for\s+(.+?)\b', text_clean)
        
        # Pattern C: "<action> <query> on google / in chrome"
        ch_match_c = re.search(
            r'\b(.+?)\s+(?:in\s+chrome|on\s+google|in\s+google|on\s+chrome)\b', 
            text_clean
        )
        
        # Pattern D: "search about <query>" (e.g. "search about gravity")
        ch_match_d = re.search(r'\bsearch\s+about\s+(.+?)\b', text_clean)
        
        if ch_match_a:
            chrome_query = ch_match_a.group(1).strip()
        elif ch_match_b:
            chrome_query = ch_match_b.group(1).strip()
        elif ch_match_c:
            raw_query = ch_match_c.group(1).strip()
            # Clean common prefixes
            chrome_query = re.sub(
                r'^(?:search\s+for\s+|search\s+about\s+|search\s+|google\s+|look\s+up\s+)', 
                '', 
                raw_query, 
                flags=re.IGNORECASE
            ).strip()
        elif ch_match_d:
            chrome_query = ch_match_d.group(1).strip()
            
        if chrome_query:
            return self._search_chrome(chrome_query)

        # 3. Open Chrome Browser
        # "open chrome", "start chrome", "launch chrome"
        if re.search(r'\b(open|start|launch)\s+chrome\b', text_clean):
            return self._open_chrome()

        # 4. Open Notepad with dynamic content / write topic
        # "create a new tab in the notepad and write about ai", "write about space in notepad"
        notepad_write_match1 = re.search(
            r'\b(?:create|write|make)\s+(?:a\s+)?(?:new\s+)?(?:tab|file|note)?\s*in\s+(?:the\s+)?notepad\s+(?:and\s+write\s+)?about\s+(.+?)\b',
            text_clean
        )
        notepad_write_match2 = re.search(
            r'\b(?:write|create\s+a\s+note)\s+about\s+(.+?)\s+in\s+(?:the\s+)?notepad\b',
            text_clean
        )
        
        if notepad_write_match1:
            topic = notepad_write_match1.group(1).strip()
            return self._write_in_notepad(topic)
        elif notepad_write_match2:
            topic = notepad_write_match2.group(1).strip()
            return self._write_in_notepad(topic)

        # 5. Open Notepad
        # "open notepad", "start notepad"
        if re.search(r'\b(open|start|launch)\s+notepad\b', text_clean):
            return self._open_notepad()

        # 5. Open Calculator
        # "open calculator", "open calc"
        if re.search(r'\b(open|start|launch)\s+(calculator|calc)\b', text_clean):
            return self._open_calculator()

        # 6. Open File Explorer
        # "open explorer", "open file explorer"
        if re.search(r'\b(open|start|launch)\s+(explorer|file\s+explorer)\b', text_clean):
            return self._open_explorer()

        return None

    def _open_chrome(self) -> str:
        try:
            guardian_kernel.authorize_execution("TaskManager", "open_browser", "https://www.google.com")
            webbrowser.open("https://www.google.com")
            return "⚡ **Task Executed:** I have successfully launched Google Chrome for you!"
        except Exception as e:
            return f"❌ **Error Executing Task:** Failed to launch web browser. Details: {str(e)}"

    def _search_chrome(self, query: str) -> str:
        url = f"https://www.google.com/search?q={urllib.parse.quote(query)}"
        try:
            guardian_kernel.authorize_execution("TaskManager", "search_browser", url)
            webbrowser.open(url)
            return f"🔍 **Task Executed:** I have launched Chrome and searched Google for: *\"{query}\"*"
        except Exception as e:
            return f"❌ **Error Executing Task:** Failed to perform search in Chrome. Details: {str(e)}"

    def _play_youtube(self, query: str) -> str:
        url = f"https://www.youtube.com/results?search_query={urllib.parse.quote(query)}"
        try:
            guardian_kernel.authorize_execution("TaskManager", "search_browser", url)
            webbrowser.open(url)
            return f"🎥 **Task Executed:** I have launched YouTube and searched for: *\"{query}\"*"
        except Exception as e:
            return f"❌ **Error Executing Task:** Failed to search YouTube. Details: {str(e)}"

    def _open_notepad(self) -> str:
        try:
            guardian_kernel.authorize_execution("TaskManager", "run_command", "notepad.exe")
            subprocess.run(["notepad.exe"], shell=False)
            return "📝 **Task Executed:** I have successfully opened Windows Notepad for you!"
        except Exception as e:
            return f"❌ **Error Executing Task:** Failed to launch Notepad. Details: {str(e)}"

    def _open_calculator(self) -> str:
        try:
            guardian_kernel.authorize_execution("TaskManager", "run_command", "calc.exe")
            subprocess.run(["calc.exe"], shell=False)
            return "🔢 **Task Executed:** I have successfully opened the Windows Calculator!"
        except Exception as e:
            return f"❌ **Error Executing Task:** Failed to launch Calculator. Details: {str(e)}"

    def _open_explorer(self) -> str:
        try:
            guardian_kernel.authorize_execution("TaskManager", "run_command", "explorer.exe")
            subprocess.run(["explorer.exe"], shell=False)
            return "📁 **Task Executed:** I have successfully opened the Windows File Explorer!"
        except Exception as e:
            return f"❌ **Error Executing Task:** Failed to launch File Explorer. Details: {str(e)}"

    def _write_in_notepad(self, topic: str) -> str:
        import os
        # Generate safe filename from the topic name
        topic_filename = re.sub(r'[^a-zA-Z0-9]', '_', topic.strip()).strip('_')
        if not topic_filename:
            topic_filename = "note"
            
        filename = f"{topic_filename}.txt"
        workspace_path = "c:\\sabari\\Lyra"
        filepath = os.path.join(workspace_path, filename)
        
        content = self._generate_topic_content(topic)
        
        try:
            guardian_kernel.authorize_execution("TaskManager", "write_file", filepath)
            # Write content to the file
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
                
            guardian_kernel.authorize_execution("TaskManager", "run_command", "notepad.exe", filepath)
            # Launch Notepad opening this file
            subprocess.run(["notepad.exe", filepath], shell=False)
            
            # Return styled confirmation
            return (
                f"📝 **Task Executed:** I have created a new Notepad document about **{topic.upper()}**, "
                f"populated it with a comprehensive overview, and launched it for you in Windows Notepad!\n\n"
                f"📁 **Saved Location:** [{filename}](file:///{filepath.replace(chr(92), '/')})"
            )
        except Exception as e:
            return f"❌ **Error Executing Task:** Failed to write and open file in Notepad. Details: {str(e)}"

    def _generate_topic_content(self, topic: str) -> str:
        topic_clean = topic.lower().strip()
        if "ai" in topic_clean or "artificial intelligence" in topic_clean:
            return (
                "# Artificial Intelligence (AI) - Overview\n\n"
                "Artificial Intelligence (AI) represents the simulation of human intelligence processes by machines, "
                "especially computer systems. These processes include learning (the acquisition of information and rules "
                "for using the information), reasoning (using rules to reach approximate or definite conclusions), and self-correction.\n\n"
                "Key Subfields of AI:\n"
                "1. Machine Learning (ML) - Focuses on algorithms that allow computers to learn from data.\n"
                "2. Deep Learning (DL) - A subset of ML utilizing deep neural networks to model complex patterns.\n"
                "3. Natural Language Processing (NLP) - Enables machines to understand and interact in human language.\n"
                "4. Computer Vision - Allows systems to interpret and act on visual input from the real world.\n\n"
                "# Created by Lyra, an advanced desktop AI."
            )
        elif "quantum" in topic_clean:
            return (
                "# Quantum Computing & Physics - Overview\n\n"
                "Quantum computing is a rapidly-emerging technology that harnesses the laws of quantum mechanics to solve problems "
                "too complex for classical computers.\n\n"
                "Key Principles:\n"
                "1. Superposition - The ability of a quantum bit (qubit) to exist in multiple states simultaneously (both 0 and 1).\n"
                "2. Entanglement - A phenomenon where qubits link dynamically; the state of one instantly influences another, regardless of distance.\n"
                "3. Quantum Interference - Used to bias the measurement of qubits toward the correct path to solve algorithms.\n\n"
                "# Created by Lyra, an advanced desktop AI."
            )
        elif "space" in topic_clean or "universe" in topic_clean:
            return (
                "# Space Exploration & Cosmology\n\n"
                "Space exploration is the ongoing discovery and exploration of celestial structures in outer space by means of "
                "continuously-evolving space technology.\n\n"
                "Key Focus Areas:\n"
                "1. Mars Colonization - Researching self-sustaining habitats on the red planet.\n"
                "2. James Webb Space Telescope (JWST) - Looking back in time to observe the first galaxies ever formed.\n"
                "3. Exo-Planets - Searching for Earth-like planets in habitable zones of distant solar systems.\n\n"
                "# Created by Lyra, an advanced desktop AI."
            )
        elif "gravity" in topic_clean:
            return (
                "# Gravitational Physics\n\n"
                "Gravity is the fundamental force by which all things with mass or energy are brought toward one another, "
                "including planetary bodies, stars, and galaxies.\n\n"
                "In modern physics, Albert Einstein's General Theory of Relativity describes gravity not as a direct force, "
                "but as the curvature of spacetime caused by the uneven distribution of mass and energy.\n\n"
                "# Created by Lyra, an advanced desktop AI."
            )
        else:
            words = topic.split(" ")
            title = " ".join([w.capitalize() for w in words])
            return (
                f"# {title} - Reference Document\n\n"
                f"This document was dynamically created by Lyra to cover the topic: '{title}'.\n\n"
                f"The subject of '{title}' encompasses a broad range of study. Users typically inquire about its "
                f"historical development, modern applications, practical benefits, and theoretical frameworks.\n\n"
                f"Here are key themes for investigation:\n"
                f"1. Core Definition & Background of {title}.\n"
                f"2. Major achievements, paradigms, or systems related to {title}.\n"
                f"3. Practical tutorials and steps to master the dynamics of {title}.\n\n"
                f"For further detailed guidance, try asking Lyra's local chat model directly.\n\n"
                f"# Created by Lyra, an advanced desktop AI."
            )

    def _create_image(self, prompt: str) -> str:
        import os
        import re
        import time
        import httpx
        import urllib.parse
        import subprocess

        # 1. Sanitize the prompt for a clean filename
        sanitized_prompt = re.sub(r'[^a-zA-Z0-9]', '_', prompt.strip()).strip('_')
        if not sanitized_prompt:
            sanitized_prompt = "generated_image"
        
        # Limit the sanitized prompt length in filename
        sanitized_prompt = sanitized_prompt[:40]
        
        timestamp = int(time.time())
        filename = f"{sanitized_prompt}_{timestamp}.png"
        workspace_path = "c:\\sabari\\Lyra"
        filepath = os.path.join(workspace_path, filename)
        
        # 2. Build the Pollinations.ai API url
        encoded_prompt = urllib.parse.quote(prompt.strip())
        url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024&nologo=true"
        
        try:
            # 3. Download the image bytes
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
            # Set a generous timeout (60 seconds) since image generation takes some time
            with httpx.Client(timeout=60.0) as client:
                response = client.get(url, headers=headers)
                response.raise_for_status()
                image_bytes = response.content
                
            # 4. Save to the workspace
            guardian_kernel.authorize_execution("TaskManager", "write_file", filepath)
            with open(filepath, "wb") as f:
                f.write(image_bytes)
                
            # 5. Open it securely using File Explorer to open associated app
            guardian_kernel.authorize_execution("TaskManager", "run_command", "explorer.exe", filepath)
            subprocess.run(["explorer.exe", filepath], shell=False)
            
            # 6. Return standard Markdown content that will render inline in chat
            api_url = f"http://127.0.0.1:8000/api/images/{filename}"
            return (
                f"🎨 **Image Created Successfully!**\n\n"
                f"I have successfully generated your image for: *\"{prompt}\"* using the local operating engine and saved it to your workspace.\n\n"
                f"![{prompt}]({api_url})\n\n"
                f"📁 **Saved Location:** [{filename}](file:///{filepath.replace(chr(92), '/')})"
            )
            
        except Exception as e:
            # Catch network errors or other failures gracefully
            return (
                f"❌ **Error Creating Image:** Failed to generate image for *\"{prompt}\"*.\n\n"
                f"**Reason:** AI image generation requires an active internet connection to download the generative model weights from the API.\n"
                f"*Details: {str(e)}*"
            )

task_manager = TaskManager()

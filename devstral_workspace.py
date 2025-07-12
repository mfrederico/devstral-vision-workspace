#!/usr/bin/env python3
"""
Devstral Vision Workspace - AI-powered UI to code generation IDE
"""

import torch
import warnings
import gradio as gr
from transformers import Mistral3ForConditionalGeneration, AutoProcessor, BitsAndBytesConfig
from PIL import Image
import time
import os
import json
from datetime import datetime
from pathlib import Path
import shutil
import subprocess
import threading
import socket
import hashlib

warnings.filterwarnings("ignore")

class DevstralWorkspace:
    def __init__(self):
        self.model = None
        self.processor = None
        self.workspace_dir = Path("workspace")
        self.workspace_dir.mkdir(exist_ok=True)
        self.current_project = None
        self.terminal_history = []
        self.dev_server_process = None
        self.preview_port = None
        self.generation_history = []
        
    def get_workspace_projects(self):
        """Get list of all projects in workspace"""
        projects = []
        for item in self.workspace_dir.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                # Check if it has a meta.json
                meta_file = item / "meta.json"
                if meta_file.exists():
                    try:
                        with open(meta_file, 'r') as f:
                            meta = json.load(f)
                        projects.append({
                            "name": item.name,
                            "created": meta.get("created", "Unknown"),
                            "last_modified": meta.get("last_modified", "Unknown"),
                            "type": meta.get("type", "Unknown")
                        })
                    except:
                        projects.append({
                            "name": item.name,
                            "created": "Unknown",
                            "last_modified": "Unknown",
                            "type": "Unknown"
                        })
                else:
                    # Legacy project without metadata
                    projects.append({
                        "name": item.name,
                        "created": "Unknown",
                        "last_modified": "Unknown",
                        "type": "Unknown"
                    })
        
        return sorted(projects, key=lambda x: x["name"])
    
    def load_project(self, project_name):
        """Load an existing project"""
        if not project_name:
            return "❌ Please select a project", "", "", [], "src/App.jsx"
        
        project_path = self.workspace_dir / project_name
        if not project_path.exists():
            return f"❌ Project '{project_name}' not found", "", "", [], "src/App.jsx"
        
        self.current_project = project_path
        self.add_terminal_output(f"📂 Loaded project: {project_name}")
        self.add_terminal_output(f"📍 Location: {project_path.absolute()}")
        
        # Load generation history
        history = self.load_generation_history()
        
        # Get default target file based on project type
        default_file = self.get_default_target_file()
        
        return f"✅ Loaded project: {project_name}", self.get_file_tree(), self.get_terminal_output(), history, default_file
    
    def get_default_target_file(self):
        """Get default target file based on project type"""
        if not self.current_project:
            return "src/App.jsx"
        
        meta_file = self.current_project / "meta.json"
        if meta_file.exists():
            with open(meta_file, 'r') as f:
                meta = json.load(f)
                project_type = meta.get("type", "React")
                
                if project_type == "React":
                    return "src/App.jsx"
                elif project_type == "Vue":
                    return "src/App.vue"
                elif project_type == "Next.js":
                    return "app/page.tsx"
                else:  # HTML/Bootstrap
                    return "index.html"
        
        return "src/App.jsx"
    
    def create_project(self, project_name, project_type):
        """Create a new project with metadata"""
        if not project_name or project_name.strip() == "":
            return "❌ Please enter a project name", "No project open", "", [], "src/App.jsx"
        
        project_name = project_name.strip()
        project_path = self.workspace_dir / project_name
        
        if project_path.exists():
            return f"❌ Project '{project_name}' already exists", self.get_file_tree(), self.get_terminal_output(), [], self.get_default_target_file()
        
        try:
            # Create project directory
            project_path.mkdir(parents=True, exist_ok=True)
            self.current_project = project_path
            
            # Create screenshots directory
            screenshots_dir = project_path / "screenshots"
            screenshots_dir.mkdir(exist_ok=True)
            
            # Create metadata file
            meta = {
                "name": project_name,
                "type": project_type,
                "created": datetime.now().isoformat(),
                "last_modified": datetime.now().isoformat(),
                "generations": []
            }
            
            with open(project_path / "meta.json", 'w') as f:
                json.dump(meta, f, indent=2)
            
            # Create project structure based on type
            if project_type == "React":
                self._create_react_structure(project_path)
            elif project_type == "Vue":
                self._create_vue_structure(project_path)
            elif project_type == "Next.js":
                self._create_nextjs_structure(project_path)
            else:
                self._create_html_structure(project_path)
            
            self.add_terminal_output(f"✅ Created project: {project_name}")
            self.add_terminal_output(f"📍 Location: {project_path.absolute()}")
            self.add_terminal_output(f"📸 Screenshots: {screenshots_dir.absolute()}")
            
            # Get default target file for this project type
            default_file = self.get_default_target_file()
            
            return f"✅ Created {project_type} project: {project_name}", self.get_file_tree(), self.get_terminal_output(), [], default_file
            
        except Exception as e:
            return f"❌ Error: {str(e)}", "Error creating project", str(e), [], "src/App.jsx"
    
    def generate_code(self, image, target_file, custom_prompt, save_screenshot):
        """Generate code from image with metadata tracking"""
        if self.model is None:
            return "❌ Please load the model first!", "", self.get_terminal_output(), []
        
        if image is None:
            return "❌ Please upload an image!", "", self.get_terminal_output(), []
        
        if not self.current_project:
            return "❌ Please create or load a project first!", "", self.get_terminal_output(), []
        
        try:
            self.add_terminal_output(f"🎨 Generating code for: {target_file}")
            
            # Get project type from metadata
            project_type = "HTML/Bootstrap"  # Default
            meta_file = self.current_project / "meta.json"
            if meta_file.exists():
                with open(meta_file, 'r') as f:
                    meta = json.load(f)
                    project_type = meta.get("type", "HTML/Bootstrap")
            
            self.add_terminal_output(f"📋 Project type: {project_type}")
            
            # Save screenshot if requested
            screenshot_path = None
            if save_screenshot and image:
                screenshot_path = self.save_screenshot(image, target_file)
            
            # Prepare project-specific prompt
            if project_type == "React":
                system_instruction = "Generate a React component using modern React hooks (useState, useEffect, etc). Use functional components, not class components. Include proper imports from 'react'. Export the component as default."
            elif project_type == "Vue":
                system_instruction = "Generate a Vue 3 component using the Composition API with <script setup> syntax. Include proper <template>, <script setup>, and <style> sections."
            elif project_type == "Next.js":
                system_instruction = "Generate a Next.js component using TypeScript. Use Next.js specific features like next/link, next/image when appropriate. Include proper TypeScript types."
            else:  # HTML/Bootstrap
                system_instruction = """Generate semantic HTML with Bootstrap 5.3.7 classes. DO NOT use React, Vue, or any JavaScript framework. Use only vanilla HTML and Bootstrap classes. 
IMPORTANT: The HTML already includes Bootstrap 5.3.7 via CDN:
- CSS: https://cdn.jsdelivr.net/npm/bootstrap@5.3.7/dist/css/bootstrap.min.css
- JS: https://cdn.jsdelivr.net/npm/bootstrap@5.3.7/dist/js/bootstrap.bundle.min.js

Do not add these links again. Use Bootstrap 5.3.7 components, utilities, and grid system. Add custom CSS to css/style.css if needed. Use vanilla JavaScript in js/main.js for interactivity."""
            
            # Combine system instruction with user prompt
            prompt = f"[IMG] {system_instruction}"
            if custom_prompt:
                prompt += f" Additional requirements: {custom_prompt}"
            
            # Process inputs
            inputs = self.processor(
                text=prompt,
                images=image,
                return_tensors="pt"
            )

            print(f"Prompt : {prompt}");
            print(f"Image  : {image}");
            
            # Move to device
            for k, v in inputs.items():
                if torch.is_tensor(v):
                    if k == 'pixel_values':
                        inputs[k] = v.to(device=self.model.device, dtype=torch.float16)
                    else:
                        inputs[k] = v.to(self.model.device)
            
            # Generate
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=2000,
                    do_sample=True,
                    temperature=0.7,
                    top_p=0.95,
                    pad_token_id=self.processor.tokenizer.pad_token_id,
                    eos_token_id=self.processor.tokenizer.eos_token_id,
                )
            
            # Decode
            response = self.processor.decode(outputs[0], skip_special_tokens=True)
            
            # Extract code - remove the prompt and instructions
            if "[IMG]" in response:
                # Split by [IMG] and take everything after it
                parts = response.split("[IMG]")
                if len(parts) > 1:
                    code = parts[-1].strip()
                else:
                    code = response
            else:
                code = response
            
            print(f"Raw Code  : {code}");

            # Remove the system instruction if it appears in the output
            instruction_markers = [
                "Generate semantic HTML with Bootstrap",
                "Generate a React component",
                "Generate a Vue 3 component", 
                "Generate a Next.js component",
                "IMPORTANT: The HTML already includes",
                "Do not add these links again",
                "Additional requirements:"
            ]
            
            # Find where the actual code starts
            code_start_markers = ["<!DOCTYPE", "<html", "import React", "import {", "<template>", "export default", "function", "const", "HTML:", "```"]
            
            # Try to find where the actual code begins
            earliest_code_start = len(code)
            for marker in code_start_markers:
                idx = code.find(marker)
                if idx != -1 and idx < earliest_code_start:
                    earliest_code_start = idx
            
            # If we found a code start marker, use it
            if earliest_code_start < len(code):
                code = code[earliest_code_start:].strip()
            
            # Clean up "HTML:" prefix if present
            if code.startswith("HTML:"):
                code = code[5:].strip()
            
            # Extract from markdown if present
            if "```" in code:
                import re
                code_blocks = re.findall(r'```(?:\w+)?\n(.*?)```', code, re.DOTALL)
                if code_blocks:
                    code = code_blocks[0]
            
            # Save to file
            file_path = self.current_project / target_file
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, 'w') as f:
                f.write(code)
            
            self.add_terminal_output(f"✅ Saved to {target_file}")
            
            # Save generation metadata
            generation_meta = {
                "timestamp": datetime.now().isoformat(),
                "target_file": target_file,
                "prompt": custom_prompt or "",
                "screenshot": screenshot_path.name if screenshot_path else None,
                "generation_id": f"gen_{int(time.time() * 1000)}"
            }
            
            self.save_generation_metadata(generation_meta)
            
            # Reload history
            history = self.load_generation_history()
            
            return f"✅ Generated successfully!", code, self.get_terminal_output(), history
            
        except Exception as e:
            return f"❌ Error: {str(e)}", "", self.get_terminal_output(), []
    
    def save_screenshot(self, image, target_file):
        """Save screenshot to project with unique name"""
        if not self.current_project or not image:
            return None
        
        screenshots_dir = self.current_project / "screenshots"
        screenshots_dir.mkdir(exist_ok=True)
        
        # Create unique filename based on timestamp and target
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        clean_target = target_file.replace("/", "_").replace("\\", "_")
        filename = f"{timestamp}_{clean_target}.png"
        
        screenshot_path = screenshots_dir / filename
        image.save(screenshot_path)
        
        self.add_terminal_output(f"📸 Saved screenshot: {filename}")
        return screenshot_path
    
    def save_generation_metadata(self, generation_meta):
        """Save generation metadata to project meta.json"""
        if not self.current_project:
            return
        
        meta_file = self.current_project / "meta.json"
        
        # Load existing metadata
        if meta_file.exists():
            with open(meta_file, 'r') as f:
                meta = json.load(f)
        else:
            meta = {
                "name": self.current_project.name,
                "type": "Unknown",
                "created": datetime.now().isoformat(),
                "generations": []
            }
        
        # Update last modified
        meta["last_modified"] = datetime.now().isoformat()
        
        # Add generation
        meta["generations"].append(generation_meta)
        
        # Keep only last 50 generations
        meta["generations"] = meta["generations"][-50:]
        
        # Save back
        with open(meta_file, 'w') as f:
            json.dump(meta, f, indent=2)
    
    def load_generation_history(self):
        """Load generation history for current project"""
        if not self.current_project:
            return []
        
        meta_file = self.current_project / "meta.json"
        if not meta_file.exists():
            return []
        
        try:
            with open(meta_file, 'r') as f:
                meta = json.load(f)
            
            # Format for display
            history = []
            for gen in reversed(meta.get("generations", [])):
                # Parse timestamp
                try:
                    timestamp = datetime.fromisoformat(gen["timestamp"])
                    time_str = timestamp.strftime("%m/%d %H:%M")
                except:
                    time_str = "Unknown"
                
                history.append({
                    "Time": time_str,
                    "File": gen.get("target_file", "Unknown"),
                    "Prompt": gen.get("prompt", "")[:50] + "..." if len(gen.get("prompt", "")) > 50 else gen.get("prompt", ""),
                    "Screenshot": "✓" if gen.get("screenshot") else "✗",
                    "ID": gen.get("generation_id", "")
                })
            
            return history
            
        except Exception as e:
            self.add_terminal_output(f"❌ Error loading history: {str(e)}")
            return []
    
    def load_generation_by_id(self, generation_id):
        """Load a specific generation by ID"""
        if not self.current_project or not generation_id:
            return None, "", ""
        
        meta_file = self.current_project / "meta.json"
        if not meta_file.exists():
            return None, "", ""
        
        try:
            with open(meta_file, 'r') as f:
                meta = json.load(f)
            
            for gen in meta.get("generations", []):
                if gen.get("generation_id") == generation_id:
                    # Load screenshot if available
                    screenshot = None
                    if gen.get("screenshot"):
                        screenshot_path = self.current_project / "screenshots" / gen["screenshot"]
                        if screenshot_path.exists():
                            screenshot = Image.open(screenshot_path)
                    
                    return (
                        screenshot,
                        gen.get("target_file", ""),
                        gen.get("prompt", "")
                    )
            
            return None, "", ""
            
        except Exception as e:
            self.add_terminal_output(f"❌ Error loading generation: {str(e)}")
            return None, "", ""
    
    def delete_project(self, project_name):
        """Delete a project and all its contents"""
        if not project_name:
            return "❌ Please select a project to delete"
        
        project_path = self.workspace_dir / project_name
        if not project_path.exists():
            return f"❌ Project '{project_name}' not found"
        
        try:
            # Stop dev server if it's running for this project
            if self.current_project == project_path:
                self.stop_dev_server()
                self.current_project = None
            
            # Delete the project directory
            shutil.rmtree(project_path)
            self.add_terminal_output(f"🗑️ Deleted project: {project_name}")
            
            return f"✅ Deleted project: {project_name}"
            
        except Exception as e:
            return f"❌ Error deleting project: {str(e)}"
    
    def get_project_info_table(self):
        """Get project info as a dataframe for display"""
        projects = self.get_workspace_projects()
        if not projects:
            return []
        
        # Convert to list of lists for dataframe
        data = []
        for p in projects:
            data.append([
                p["name"],
                p["type"],
                p["created"][:10] if p["created"] != "Unknown" else "Unknown",
                p["last_modified"][:10] if p["last_modified"] != "Unknown" else "Unknown"
            ])
        
        return data
    
    def get_project_selector_choices(self):
        """Get project names for dropdown selector"""
        projects = self.get_workspace_projects()
        return [p["name"] for p in projects]
    
    def load_model(self):
        """Load the model"""
        if self.model is not None:
            return "✅ Model already loaded!"
        
        try:
            import bitsandbytes as bnb
        except ImportError:
            return "❌ Error: bitsandbytes not installed. Run: pip install bitsandbytes"
        
        if not torch.cuda.is_available():
            return "❌ Error: No GPU detected"
        
        model_id = "cognitivecomputations/Devstral-Vision-Small-2507"
        
        self.add_terminal_output("🔧 Loading model...")
        self.add_terminal_output(f"📦 Model: {model_id}")
        
        quantization_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_use_double_quant=True,
            bnb_4bit_compute_dtype=torch.bfloat16
        )
        
        try:
            self.model = Mistral3ForConditionalGeneration.from_pretrained(
                model_id,
                quantization_config=quantization_config,
                device_map="auto",
                trust_remote_code=True
            )
            
            self.processor = AutoProcessor.from_pretrained(model_id)
            
            self.add_terminal_output("✅ Model loaded successfully!")
            return "✅ Model loaded!"
            
        except Exception as e:
            return f"❌ Error: {str(e)}"
    
    def _create_react_structure(self, path):
        """Create React project structure with Vite"""
        # Create directories
        (path / "src").mkdir(exist_ok=True)
        (path / "src" / "components").mkdir(exist_ok=True)
        (path / "public").mkdir(exist_ok=True)
        
        # Package.json
        self._write_file(path / "package.json", """{
  "name": "react-app",
  "private": true,
  "version": "0.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0"
  },
  "devDependencies": {
    "@types/react": "^18.2.43",
    "@types/react-dom": "^18.2.17",
    "@vitejs/plugin-react": "^4.2.1",
    "vite": "^5.0.8"
  }
}""")
        
        # Vite config
        self._write_file(path / "vite.config.js", """import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    host: true,
    strictPort: false
  }
})""")
        
        # Index.html
        self._write_file(path / "index.html", """<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>React App</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.jsx"></script>
  </body>
</html>""")
        
        # Main.jsx
        self._write_file(path / "src" / "main.jsx", """import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)""")
        
        # App.jsx
        self._write_file(path / "src" / "App.jsx", """import { useState } from 'react'
import './App.css'

function App() {
  return (
    <div className="App">
      <h1>Welcome to React!</h1>
      <p>Edit src/App.jsx and save to see changes.</p>
    </div>
  )
}

export default App""")
        
        # CSS files
        self._write_file(path / "src" / "index.css", """body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}""")
        
        self._write_file(path / "src" / "App.css", """.App {
  text-align: center;
  padding: 2rem;
}""")
    
    def _create_vue_structure(self, path):
        """Create Vue project structure"""
        (path / "src").mkdir(exist_ok=True)
        (path / "src" / "components").mkdir(exist_ok=True)
        (path / "public").mkdir(exist_ok=True)
        
        self._write_file(path / "package.json", """{
  "name": "vue-app",
  "version": "1.0.0",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "vue": "^3.3.0"
  },
  "devDependencies": {
    "@vitejs/plugin-vue": "^4.2.3",
    "vite": "^4.4.0"
  }
}""")
        
        self._write_file(path / "vite.config.js", """import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
})""")
        
        self._write_file(path / "index.html", """<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Vue App</title>
  </head>
  <body>
    <div id="app"></div>
    <script type="module" src="/src/main.js"></script>
  </body>
</html>""")
        
        self._write_file(path / "src" / "main.js", """import { createApp } from 'vue'
import App from './App.vue'

createApp(App).mount('#app')""")
        
        self._write_file(path / "src" / "App.vue", """<template>
  <div>
    <h1>Welcome to Vue!</h1>
    <p>Edit src/App.vue and save to see changes.</p>
  </div>
</template>

<script setup>
// Component logic here
</script>

<style>
/* Component styles here */
</style>""")
    
    def _create_nextjs_structure(self, path):
        """Create Next.js project structure"""
        (path / "app").mkdir(exist_ok=True)
        (path / "components").mkdir(exist_ok=True)
        (path / "public").mkdir(exist_ok=True)
        
        self._write_file(path / "package.json", """{
  "name": "nextjs-app",
  "version": "1.0.0",
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start"
  },
  "dependencies": {
    "next": "14.0.0",
    "react": "^18",
    "react-dom": "^18"
  }
}""")
        
        self._write_file(path / "next.config.js", """/** @type {import('next').NextConfig} */
const nextConfig = {}

module.exports = nextConfig""")
        
        self._write_file(path / "app" / "layout.js", """export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}""")
        
        self._write_file(path / "app" / "page.js", """export default function Home() {
  return (
    <main>
      <h1>Welcome to Next.js!</h1>
    </main>
  )
}""")
    
    def _create_html_structure(self, path):
        """Create HTML/Bootstrap project structure"""
        (path / "css").mkdir(exist_ok=True)
        (path / "js").mkdir(exist_ok=True)
        (path / "images").mkdir(exist_ok=True)
        
        self._write_file(path / "index.html", """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>My Project</title>
    <!-- Bootstrap 5.3.7 CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.7/dist/css/bootstrap.min.css" rel="stylesheet">
    <!-- Custom CSS -->
    <link href="css/style.css" rel="stylesheet">
</head>
<body>
    <div class="container mt-5">
        <h1 class="text-center mb-4">Welcome to Bootstrap!</h1>
        <p class="text-center">Start building your project with Bootstrap 5.3.7</p>
    </div>
    
    <!-- Bootstrap 5.3.7 Bundle with Popper -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.7/dist/js/bootstrap.bundle.min.js"></script>
    <!-- Custom JavaScript -->
    <script src="js/main.js"></script>
</body>
</html>""")
        
        self._write_file(path / "css" / "style.css", """/* Custom styles */
body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}""")
        
        self._write_file(path / "js" / "main.js", """// Main JavaScript file
document.addEventListener('DOMContentLoaded', function() {
    console.log('Bootstrap 5.3.7 project loaded successfully!');
    
    // Initialize Bootstrap tooltips if needed
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));
    
    // Add your custom JavaScript here
});""")
    
    def start_dev_server(self):
        """Start development server"""
        if not self.current_project:
            return "❌ No project open", ""
        
        if self.dev_server_process and self.dev_server_process.poll() is None:
            url = f"http://localhost:{self.preview_port}"
            return f"✅ Server already running on port {self.preview_port}", f'<a href="{url}" target="_blank" style="color: #007bff; text-decoration: none;">🔗 {url}</a>'
        
        try:
            # Find available port
            self.preview_port = self.find_available_port(3000, 3100)
            if not self.preview_port:
                return "❌ No available ports", ""
            
            # Check project type to determine how to start server
            package_json = self.current_project / "package.json"
            
            if package_json.exists():
                # Node.js based project (React, Vue, Next.js)
                # Install dependencies if needed
                if not (self.current_project / "node_modules").exists():
                    self.add_terminal_output("📦 Installing dependencies...")
                    result = subprocess.run(["npm", "install"], cwd=self.current_project, capture_output=True, text=True)
                    if result.returncode != 0:
                        self.add_terminal_output(f"❌ npm install failed: {result.stderr}")
                        return "❌ Failed to install dependencies", ""
                
                # Start dev server
                cmd = ["npm", "run", "dev", "--", "--port", str(self.preview_port)]
            else:
                # HTML/Bootstrap project - use Python's http.server
                self.add_terminal_output("🌐 Starting Python HTTP server for HTML project...")
                cmd = ["python", "-m", "http.server", str(self.preview_port)]
            
            self.dev_server_process = subprocess.Popen(
                cmd,
                cwd=self.current_project,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
            
            # Start thread to read output
            def read_output():
                if self.dev_server_process.stdout:
                    for line in self.dev_server_process.stdout:
                        if line:
                            self.add_terminal_output(line.strip())
            
            thread = threading.Thread(target=read_output)
            thread.daemon = True
            thread.start()
            
            self.add_terminal_output(f"🚀 Starting dev server on port {self.preview_port}...")
            time.sleep(3)  # Give server time to start
            
            url = f"http://localhost:{self.preview_port}"
            return f"✅ Server starting on port {self.preview_port}", f'<a href="{url}" target="_blank" style="color: #007bff; text-decoration: none;">🔗 {url}</a>'
            
        except Exception as e:
            return f"❌ Error: {str(e)}", ""
    
    def stop_dev_server(self):
        """Stop development server"""
        if self.dev_server_process and self.dev_server_process.poll() is None:
            self.dev_server_process.terminate()
            self.dev_server_process.wait()
            self.add_terminal_output("🛑 Dev server stopped")
            self.preview_port = None
            return "✅ Server stopped"
        return "❌ No server running"
    
    def get_preview_html(self):
        """Get preview HTML"""
        if not self.preview_port:
            return """<div style='padding: 2rem; text-align: center;'>
                <h3>No preview available</h3>
                <p>Start the dev server to see preview</p>
            </div>"""
        
        return f"""<iframe src="http://localhost:{self.preview_port}" 
                style="width: 100%; height: 600px; border: 1px solid #ddd;">
            </iframe>"""
    
    def find_available_port(self, start, end):
        """Find available port"""
        for port in range(start, end):
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                try:
                    s.bind(('', port))
                    return port
                except:
                    continue
        return None
    
    def _write_file(self, path, content):
        """Write file"""
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w') as f:
            f.write(content)
    
    def add_terminal_output(self, text):
        """Add terminal output"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.terminal_history.append(f"[{timestamp}] {text}")
        self.terminal_history = self.terminal_history[-50:]
    
    def get_terminal_output(self):
        """Get terminal output"""
        return "\n".join(self.terminal_history)
    
    def get_file_tree(self):
        """Get file tree"""
        if not self.current_project or not self.current_project.exists():
            return "No project open"
        
        tree = [f"📁 {self.current_project.name}/"]
        tree.append(f"📍 {self.current_project.absolute()}")
        tree.append("")
        
        def build_tree(path, prefix=""):
            items = sorted(path.iterdir(), key=lambda x: (not x.is_dir(), x.name))
            for i, item in enumerate(items):
                if item.name in ['node_modules', '.git', '__pycache__']:
                    continue
                is_last = i == len(items) - 1
                current = "└── " if is_last else "├── "
                icon = "📁 " if item.is_dir() else self._get_file_icon(item.name)
                tree.append(f"{prefix}{current}{icon}{item.name}")
                if item.is_dir() and item.name != 'node_modules':
                    next_prefix = prefix + ("    " if is_last else "│   ")
                    build_tree(item, next_prefix)
        
        build_tree(self.current_project, "  ")
        return "\n".join(tree)
    
    def _get_file_icon(self, filename):
        """Get icon for file type"""
        if filename == "meta.json":
            return "⚙️ "
        elif filename.endswith(('.png', '.jpg', '.jpeg', '.gif')):
            return "🖼️ "
        elif filename.endswith(('.jsx', '.tsx')):
            return "⚛️ "
        elif filename.endswith('.vue'):
            return "💚 "
        elif filename.endswith('.html'):
            return "🌐 "
        elif filename.endswith('.css'):
            return "🎨 "
        elif filename.endswith(('.js', '.ts')):
            return "📜 "
        elif filename.endswith('.json'):
            return "📋 "
        else:
            return "📄 "
    
    def get_screenshot_choices(self):
        """Get screenshot choices for dropdown"""
        if not self.current_project:
            return []
        
        screenshots_dir = self.current_project / "screenshots"
        if not screenshots_dir.exists():
            return []
        
        choices = []
        screenshots = []
        
        # Get all PNG files in screenshots directory
        for img_file in screenshots_dir.glob("*.png"):
            screenshots.append({
                "name": img_file.name,
                "path": str(img_file),
                "modified": datetime.fromtimestamp(img_file.stat().st_mtime)
            })
        
        # Sort by modification time, newest first
        screenshots.sort(key=lambda x: x["modified"], reverse=True)
        
        # Load metadata to get associated target files and prompts
        meta_file = self.current_project / "meta.json"
        generations_map = {}
        
        if meta_file.exists():
            with open(meta_file, 'r') as f:
                meta = json.load(f)
                for gen in meta.get("generations", []):
                    if gen.get("screenshot"):
                        generations_map[gen["screenshot"]] = {
                            "target_file": gen.get("target_file", "Unknown"),
                            "prompt": gen.get("prompt", "")
                        }
        
        # Create choices with descriptive labels
        for screenshot in screenshots:
            gen_info = generations_map.get(screenshot["name"], {})
            target_file = gen_info.get("target_file", "Unknown") if isinstance(gen_info, dict) else "Unknown"
            modified_str = screenshot["modified"].strftime("%Y-%m-%d %H:%M")
            label = f"{screenshot['name'][:16]}... → {target_file} ({modified_str})"
            choices.append((label, screenshot['path']))
        
        return choices
    
    def load_screenshot_from_file(self, screenshot_path):
        """Load a screenshot from file path"""
        if not screenshot_path:
            return None, "", "", "No screenshot selected"
        
        try:
            from PIL import Image
            img = Image.open(screenshot_path)
            
            # Find associated metadata
            screenshot_name = Path(screenshot_path).name
            meta_file = self.current_project / "meta.json"
            
            target_file = ""
            prompt = ""
            
            if meta_file.exists():
                with open(meta_file, 'r') as f:
                    meta = json.load(f)
                    for gen in meta.get("generations", []):
                        if gen.get("screenshot") == screenshot_name:
                            target_file = gen.get("target_file", "")
                            prompt = gen.get("prompt", "")
                            self.add_terminal_output(f"📸 Found metadata: target={target_file}, prompt={prompt[:50]}...")
                            break
            
            if not target_file and not prompt:
                self.add_terminal_output(f"⚠️ No metadata found for screenshot: {screenshot_name}")
            
            return img, target_file, prompt, f"✅ Loaded screenshot: {screenshot_name}"
            
        except Exception as e:
            return None, "", "", f"❌ Error loading screenshot: {str(e)}"

# Create instance
ide = DevstralWorkspace()

# Create interface
def create_interface():
    with gr.Blocks(title="Devstral Workspace", theme=gr.themes.Soft(), css="""
        .file-tree { font-family: monospace; font-size: 12px; }
        .terminal { 
            font-family: monospace; 
            font-size: 12px;
            background: #1e1e1e;
            color: #d4d4d4;
        }
        .history-table { font-size: 12px; }
        /* Style for server URL link */
        .server-url a {
            display: inline-block;
            padding: 5px 10px;
            background-color: #f0f0f0;
            border-radius: 5px;
            transition: background-color 0.2s;
        }
        .server-url a:hover {
            background-color: #e0e0e0;
        }
    """) as app:
        gr.Markdown("""
        # 🚀 Devstral Workspace - AI Development Environment
        
        Manage and build applications with AI assistance
        """)
        
        with gr.Row():
            # Left sidebar
            with gr.Column(scale=1):
                # AI Model section first - most important!
                gr.Markdown("### 🤖 AI Model")
                load_model_btn = gr.Button("Load Model", variant="primary", size="lg")
                model_status = gr.Textbox(
                    label="Model Status", 
                    value="❌ Model not loaded - Click 'Load Model' to begin",
                    interactive=False, 
                    lines=2
                )
                
                gr.Markdown("---")  # Separator
                
                gr.Markdown("### 📂 Workspace")
                
                # Project selector
                with gr.Tab("Load Project"):
                    project_list = gr.Dataframe(
                        value=ide.get_project_info_table(),
                        headers=["name", "type", "created", "last_modified"],
                        label="Available Projects",
                        interactive=False
                    )
                    project_selector = gr.Dropdown(
                        choices=ide.get_project_selector_choices(),
                        label="Select Project",
                        interactive=True
                    )
                    with gr.Row():
                        load_btn = gr.Button("📂 Load", scale=2)
                        delete_btn = gr.Button("🗑️ Delete", scale=1, variant="stop")
                
                # Create new project
                with gr.Tab("New Project"):
                    project_name = gr.Textbox(label="Project Name", placeholder="my-app")
                    project_type = gr.Dropdown(
                        choices=["React", "Vue", "Next.js", "HTML/Bootstrap"],
                        value="React",
                        label="Type"
                    )
                    create_btn = gr.Button("Create Project", variant="primary")
                
                project_status = gr.Textbox(label="Status", interactive=False)
                
                gr.Markdown("### 📁 Files")
                file_tree = gr.Textbox(
                    label="", 
                    lines=10, 
                    interactive=False,
                    elem_classes="file-tree"
                )
                
                gr.Markdown("### 🚀 Dev Server")
                with gr.Row():
                    start_btn = gr.Button("▶️ Start", scale=1)
                    stop_btn = gr.Button("⏹️ Stop", scale=1)
                server_status = gr.Textbox(label="Server Status", interactive=False, lines=1)
                server_url = gr.HTML(label="Preview URL", value="", elem_classes="server-url")
            
            # Main area
            with gr.Column(scale=2):
                with gr.Tabs():
                    with gr.Tab("🎨 Generate"):
                        with gr.Row():
                            with gr.Column():
                                image_input = gr.Image(label="Upload UI Screenshot", type="pil")
                                
                                # Screenshot browser
                                with gr.Row():
                                    screenshot_dropdown = gr.Dropdown(
                                        label="Or load from project screenshots",
                                        choices=[],
                                        interactive=True,
                                        scale=3
                                    )
                                    load_screenshot_btn = gr.Button("📂 Load", scale=1)
                                
                                save_screenshot = gr.Checkbox(label="Save screenshot to project", value=True)
                            
                            with gr.Column():
                                target_file = gr.Textbox(
                                    label="Target File", 
                                    value="src/App.jsx",
                                    info="Will auto-update based on project type"
                                )
                                custom_prompt = gr.Textbox(
                                    label="Instructions", 
                                    placeholder="Add specific requirements...",
                                    lines=3
                                )
                                generate_btn = gr.Button("Generate Code", variant="primary", size="lg")
                                gen_status = gr.Textbox(label="Status", interactive=False)
                    
                    with gr.Tab("📝 Code"):
                        code_output = gr.Code(
                            label="Generated Code",
                            language="javascript",
                            lines=20
                        )
                    
                    with gr.Tab("👁️ Preview"):
                        preview_frame = gr.HTML(value=ide.get_preview_html())
                    
                    with gr.Tab("📸 History"):
                        gr.Markdown("### Generation History")
                        history_table = gr.Dataframe(
                            headers=["Time", "File", "Prompt", "Screenshot", "ID"],
                            label="",
                            interactive=False,
                            elem_classes="history-table"
                        )
                        
                        with gr.Row():
                            selected_id = gr.Textbox(label="Generation ID", placeholder="Select from table above")
                            reload_btn = gr.Button("🔄 Reload Generation", variant="secondary")
                    
                    with gr.Tab("🖥️ Terminal"):
                        terminal = gr.Textbox(
                            label="",
                            lines=15,
                            interactive=False,
                            elem_classes="terminal"
                        )
        
        # Event handlers
        def refresh_project_list():
            return ide.get_project_info_table(), gr.update(choices=ide.get_project_selector_choices())
        
        def reload_generation(gen_id):
            if not gen_id:
                return None, "", "", "❌ Please select a generation ID"
            
            screenshot, target, prompt = ide.load_generation_by_id(gen_id)
            if screenshot:
                return screenshot, target, prompt, f"✅ Loaded generation: {gen_id}"
            else:
                return None, "", "", f"❌ Generation not found: {gen_id}"
        
        def refresh_screenshot_dropdown():
            """Refresh screenshot dropdown choices"""
            return gr.update(choices=ide.get_screenshot_choices())
        
        # Connect events
        create_btn.click(
            fn=ide.create_project,
            inputs=[project_name, project_type],
            outputs=[project_status, file_tree, terminal, history_table, target_file]
        ).then(
            fn=refresh_project_list,
            outputs=[project_list, project_selector]
        ).then(
            fn=refresh_screenshot_dropdown,
            outputs=screenshot_dropdown
        )
        
        load_btn.click(
            fn=ide.load_project,
            inputs=[project_selector],
            outputs=[project_status, file_tree, terminal, history_table, target_file]
        ).then(
            fn=refresh_screenshot_dropdown,
            outputs=screenshot_dropdown
        )
        
        delete_btn.click(
            fn=ide.delete_project,
            inputs=[project_selector],
            outputs=[project_status]
        ).then(
            fn=refresh_project_list,
            outputs=[project_list, project_selector]
        )
        
        load_model_btn.click(
            fn=ide.load_model,
            outputs=model_status
        )
        
        start_btn.click(
            fn=ide.start_dev_server,
            outputs=[server_status, server_url]
        ).then(
            fn=ide.get_preview_html,
            outputs=preview_frame
        ).then(
            fn=ide.get_terminal_output,
            outputs=terminal
        )
        
        stop_btn.click(
            fn=ide.stop_dev_server,
            outputs=server_status
        ).then(
            fn=lambda: ("", ide.get_preview_html()),
            outputs=[server_url, preview_frame]
        )
        
        generate_btn.click(
            fn=ide.generate_code,
            inputs=[image_input, target_file, custom_prompt, save_screenshot],
            outputs=[gen_status, code_output, terminal, history_table]
        ).then(
            fn=ide.get_file_tree,
            outputs=file_tree
        ).then(
            fn=refresh_screenshot_dropdown,
            outputs=screenshot_dropdown
        )
        
        load_screenshot_btn.click(
            fn=ide.load_screenshot_from_file,
            inputs=[screenshot_dropdown],
            outputs=[image_input, target_file, custom_prompt, gen_status]
        )
        
        reload_btn.click(
            fn=reload_generation,
            inputs=[selected_id],
            outputs=[image_input, target_file, custom_prompt, gen_status]
        )
        
        # Click on history table to select
        history_table.select(
            fn=lambda evt: evt.value.iloc[evt.index[0]]["ID"] if evt.index[0] < len(evt.value) else "",
            outputs=selected_id
        )
        
        # Auto-refresh file tree every 2 seconds when a project is loaded
        def auto_refresh_file_tree():
            if ide.current_project:
                return ide.get_file_tree()
            return gr.update()
        
        # Set up a timer to refresh the file tree
        file_tree_timer = gr.Timer(2.0)
        file_tree_timer.tick(
            fn=auto_refresh_file_tree,
            outputs=file_tree
        )
    
    return app

if __name__ == "__main__":
    print("\n🚀 Starting Devstral Workspace...")
    print(f"📁 Projects location: {Path('workspace').absolute()}")
    print("📸 Screenshots are saved in each project's 'screenshots' folder")
    print("⚙️ Metadata is tracked in 'meta.json' for each project\n")
    
    app = create_interface()
    app.launch(
        server_name="0.0.0.0",
        server_port=7865,
        share=False,
        inbrowser=True
    )

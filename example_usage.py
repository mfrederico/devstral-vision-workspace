#!/usr/bin/env python3
"""
Example usage of Devstral Workspace API
This demonstrates how to use the workspace programmatically
"""

from devstral_workspace import DevstralWorkspace
from PIL import Image

def main():
    # Initialize workspace
    print("🚀 Initializing Devstral Workspace...")
    ide = DevstralWorkspace()
    
    # Load the model (this is required before generating code)
    print("\n📦 Loading AI model...")
    status = ide.load_model()
    print(f"Model status: {status}")
    
    # Create a new React project
    print("\n📁 Creating a new React project...")
    project_name = "my-awesome-app"
    project_type = "React"
    
    status, file_tree, terminal, history, default_file = ide.create_project(
        project_name, 
        project_type
    )
    print(f"Project status: {status}")
    print(f"Default target file: {default_file}")
    
    # Example: Generate code from an image
    # In real usage, you would load an actual screenshot
    print("\n🎨 Generating code from image...")
    
    # Create a sample image (in practice, load your UI screenshot)
    sample_image = Image.new('RGB', (800, 600), color='lightblue')
    
    # Generate code with custom instructions
    gen_status, code, terminal_output, history = ide.generate_code(
        image=sample_image,
        target_file="src/Dashboard.jsx",
        custom_prompt="Create a modern dashboard with sidebar navigation and data cards",
        save_screenshot=True
    )
    
    print(f"Generation status: {gen_status}")
    print(f"\nGenerated code preview:\n{code[:200]}...")
    
    # List all screenshots in the project
    print("\n📸 Available screenshots:")
    screenshots = ide.get_screenshot_choices()
    for label, path in screenshots:
        print(f"  - {label}")
    
    # Get project information
    print("\n📊 Workspace projects:")
    projects = ide.get_workspace_projects()
    for project in projects:
        print(f"  - {project['name']} ({project['type']}) - Created: {project['created'][:10]}")
    
    print("\n✅ Example completed! Launch the full UI with: python devstral_workspace.py")

if __name__ == "__main__":
    main()
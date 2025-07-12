# Devstral Vision Workspace 🚀

An AI-powered development environment that transforms UI screenshots into working code using the Devstral Vision model. Build React, Vue, Next.js, or Bootstrap applications with natural language instructions and visual inputs.

![Devstral Vision Workspace](https://img.shields.io/badge/AI%20Powered-Vision%20to%20Code-blue)
![Python](https://img.shields.io/badge/Python-3.8%2B-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

## 🌟 Features

### 🎨 Visual to Code Generation
- **Upload Screenshots**: Convert any UI design into working code
- **Multi-Framework Support**: Generate React, Vue, Next.js, or HTML/Bootstrap code
- **Project-Aware Generation**: Automatically adapts to your project type
- **Natural Language Instructions**: Add custom requirements in plain English

### 📂 Advanced Project Management
- **Workspace Organization**: Manage multiple projects in one place
- **Screenshot History**: All uploads are saved with metadata
- **Generation Tracking**: Complete history of all generated code
- **Screenshot Browser**: Easily reload and iterate on previous designs

### 🚀 Integrated Development Environment
- **Live Preview**: See your changes instantly with hot reload
- **Dev Server Management**: Start/stop development servers with one click
- **File Explorer**: Visual file tree with custom icons
- **Terminal Output**: Real-time feedback and logs

### 🔧 Smart Features
- **Bootstrap 5.3.7 Integration**: Proper CDN links and components
- **Metadata Tracking**: JSON-based project and generation history
- **4-bit Quantization**: Runs on consumer GPUs (24GB VRAM)
- **Persistent Sessions**: Projects and history survive restarts

## 📋 Requirements

- Python 3.8+
- CUDA-capable GPU with 24GB+ VRAM (e.g., RTX 4090, RTX 3090)
- Node.js and npm (for dev server functionality)

## 🛠️ Installation

1. **Clone the repository**
```bash
git clone git@github.com:mfrederico/devstral-vision-workspace.git
cd devstral-vision-workspace
```

2. **Create a virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

## 🚀 Quick Start

1. **Launch the workspace**
```bash
python devstral_workspace.py
```

2. **Load the AI model** (Required first step!)
   - Click "Load Model" in the left sidebar
   - Wait for the model to load (shows "✅ Model loaded!")

3. **Create a project**
   - Go to "New Project" tab
   - Enter a project name
   - Select framework (React, Vue, Next.js, or HTML/Bootstrap)
   - Click "Create Project"

4. **Generate code from a screenshot**
   - Upload a UI screenshot in the "Generate" tab
   - Optionally add custom instructions
   - Click "Generate Code"
   - View the generated code in the "Code" tab

5. **Preview your application**
   - Click "▶️ Start" to launch the dev server
   - View live preview in the "Preview" tab
   - Click the server URL to open in a new tab

## 📸 Screenshot Management

### Saving Screenshots
- Check "Save screenshot to project" when generating code
- Screenshots are stored in `workspace/[project-name]/screenshots/`
- Named with timestamp and target file for easy identification

### Loading Previous Screenshots
- Use the dropdown menu below the upload area
- Shows all project screenshots with target files and timestamps
- Click "📂 Load" to restore a previous screenshot and its metadata

### History Tab
- View all generations in chronological order
- Click on any entry to select it
- Use "🔄 Reload Generation" to restore screenshot, target file, and prompt

## 🎯 Supported Frameworks

### React
- Modern functional components with hooks
- Proper imports and exports
- Vite development server
- Hot module replacement

### Vue 3
- Composition API with `<script setup>`
- Single File Components
- Vite integration
- Template, script, and style sections

### Next.js
- TypeScript support
- App directory structure
- Server and client components
- Next.js specific features

### HTML/Bootstrap
- Bootstrap 5.3.7 via CDN
- Semantic HTML structure
- Vanilla JavaScript support
- Custom CSS organization

## 📁 Project Structure

```
workspace/
├── my-react-app/
│   ├── screenshots/
│   │   ├── 20250112_143022_src_App.jsx.png
│   │   └── 20250112_144515_src_Component.jsx.png
│   ├── src/
│   │   ├── App.jsx
│   │   ├── App.css
│   │   └── components/
│   ├── meta.json
│   ├── package.json
│   └── vite.config.js
└── my-bootstrap-site/
    ├── screenshots/
    ├── index.html
    ├── css/
    │   └── style.css
    ├── js/
    │   └── main.js
    └── meta.json
```

## 🔍 Metadata Tracking

Each project includes a `meta.json` file that tracks:
- Project name and type
- Creation and modification dates
- Complete generation history
- Screenshot associations
- Prompts and target files

## ⚙️ Configuration

### Default Ports
- Gradio Interface: `7865`
- Dev Servers: `3000-3100` (auto-assigned)

### Environment Variables
- `GRADIO_SERVER_PORT`: Change the Gradio port
- `CUDA_VISIBLE_DEVICES`: Select GPU device

## 🐛 Troubleshooting

### Model Loading Issues
- Ensure you have enough GPU memory (24GB+)
- Check CUDA is properly installed
- Verify transformers version supports Mistral3

### Dev Server Issues
- Make sure Node.js and npm are installed
- Check if ports 3000-3100 are available
- Look at terminal output for npm errors

### Generation Issues
- Always load the model first
- Ensure a project is created/loaded
- Check that the screenshot is properly uploaded

## 📚 Model Information

This project uses the Devstral Vision Small 2507 model:

```bibtex
@misc{devstral-vision-2507,
  author = {Hartford, Eric},
  title = {Devstral-Vision-Small-2507},
  year = {2025},
  publisher = {HuggingFace},
  url = {https://huggingface.co/cognitivecomputations/Devstral-Vision-Small-2507}
}
```

The model is automatically quantized to 4-bit using bitsandbytes for efficient GPU usage.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Eric Hartford for the Devstral Vision model
- The Mistral AI team for the base architecture
- The Gradio team for the excellent UI framework
- The open-source community for various tools and libraries

## 🚨 Disclaimer

This tool is for development and prototyping purposes. Always review and test generated code before using in production. The AI model may occasionally produce incorrect or suboptimal code.

---

Made with ❤️ by the open-source community
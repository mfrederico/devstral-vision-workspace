# Contributing to Devstral Vision Workspace

Thank you for your interest in contributing to Devstral Vision Workspace! This document provides guidelines for contributing to the project.

## 🤝 How to Contribute

### Reporting Issues
- Check if the issue already exists in the [Issues](https://github.com/mfrederico/devstral-vision-workspace/issues) section
- Provide a clear description of the problem
- Include steps to reproduce the issue
- Share relevant error messages or screenshots
- Mention your environment (OS, Python version, GPU model)

### Suggesting Features
- Open an issue with the "enhancement" label
- Describe the feature and its benefits
- Provide use cases and examples
- Consider how it fits with existing functionality

### Submitting Code

1. **Fork the Repository**
   ```bash
   git clone git@github.com:mfrederico/devstral-vision-workspace.git
   cd devstral-vision-workspace
   ```

2. **Create a Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make Your Changes**
   - Follow the existing code style
   - Add comments for complex logic
   - Update documentation if needed
   - Test your changes thoroughly

4. **Commit Your Changes**
   ```bash
   git add .
   git commit -m "Add feature: description of your changes"
   ```

5. **Push and Create Pull Request**
   ```bash
   git push origin feature/your-feature-name
   ```
   Then create a Pull Request on GitHub

## 📝 Code Style Guidelines

### Python Code
- Follow PEP 8 conventions
- Use meaningful variable and function names
- Add docstrings to functions and classes
- Keep functions focused and small
- Handle errors gracefully

### Example:
```python
def generate_code(self, image, target_file, custom_prompt, save_screenshot):
    """
    Generate code from an uploaded image.
    
    Args:
        image: PIL Image object
        target_file: Target file path for generated code
        custom_prompt: Additional instructions from user
        save_screenshot: Whether to save the screenshot
        
    Returns:
        tuple: (status_message, generated_code, terminal_output, history)
    """
    # Implementation here
```

## 🧪 Testing

Before submitting:
1. Test all major functionality
2. Ensure the model loads correctly
3. Test code generation for all project types
4. Verify dev server functionality
5. Check screenshot management features

## 📚 Areas for Contribution

### High Priority
- Additional framework support (Angular, Svelte, etc.)
- Improved error handling and recovery
- Performance optimizations
- Better prompt engineering
- Multi-language support

### Features Welcome
- Export/import project functionality
- Code formatting integration
- Git integration
- Collaborative features
- Custom model support

### Documentation
- Tutorials and examples
- Video demonstrations
- API documentation
- Deployment guides

## 🚫 What Not to Do

- Don't commit sensitive information (API keys, passwords)
- Don't include large binary files
- Don't make breaking changes without discussion
- Don't remove existing functionality without reason
- Don't commit code that hasn't been tested

## 💬 Communication

- Be respectful and constructive
- Ask questions if you're unsure
- Provide context for your changes
- Be patient with review processes
- Help others when you can

## 📄 License

By contributing, you agree that your contributions will be licensed under the MIT License.

## 🙏 Thank You!

Every contribution helps make this project better. Whether it's fixing a typo, adding a feature, or improving documentation, your help is appreciated!

Happy coding! 🚀
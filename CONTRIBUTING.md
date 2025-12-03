# Contributing to Fiber Maintenance Analytics System

Thank you for your interest in contributing to this project. This document provides guidelines for contributing.

## Development Setup

### Prerequisites

- Python 3.9 or higher
- MySQL 8.0 or higher
- Git

### Local Development

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd fiber_app
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   # or
   venv\Scripts\activate     # Windows
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment:
   ```bash
   cp .env.example .env
   # Edit .env with your database credentials
   ```

5. Run the application:
   ```bash
   streamlit run main.py
   ```

## Code Style Guidelines

### Python Standards

- Follow PEP 8 style guidelines
- Use meaningful variable and function names
- Add docstrings to all functions and classes
- Keep functions focused and concise
- Use type hints where appropriate

### File Organization

- Place new dashboard pages in the `pages/` directory
- Use the existing naming convention: `{number}_{PageName}.py`
- Keep utility functions in `utils.py`
- Keep configuration in `config.py`

### Git Workflow

1. Create a feature branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes and commit:
   ```bash
   git add .
   git commit -m "Add: description of your changes"
   ```

3. Push and create a pull request:
   ```bash
   git push origin feature/your-feature-name
   ```

### Commit Message Format

Use the following prefixes:
- `Add:` - New features
- `Fix:` - Bug fixes
- `Update:` - Updates to existing features
- `Remove:` - Removed features
- `Refactor:` - Code refactoring
- `Docs:` - Documentation updates
- `Style:` - Formatting, no code change
- `Test:` - Adding or updating tests

## Testing

Before submitting changes:

1. Test all dashboard pages load correctly
2. Verify data loading works with different date ranges
3. Check authentication flow (login/logout)
4. Test with different data scenarios
5. Verify no console errors in browser

## Questions or Issues

For questions or issues, contact:
- **Developer:** Joseph Nderitu
- **Email:** josephnderito16@gmail.com

---

Thank you for contributing!

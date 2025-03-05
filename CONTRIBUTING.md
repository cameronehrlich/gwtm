# Contributing to GWTM

Thank you for your interest in contributing to the Git WorkTree Manager (GWTM) project!

## Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/gwtm.git
   cd gwtm
   ```

2. Set up a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install in development mode:
   ```bash
   pip install -e .
   ```

## Running Tests

To run basic tests:
```bash
python test.py
```

## Code Style

- Follow PEP 8 guidelines
- Use type hints wherever possible
- Add docstrings to all functions and classes

## Submitting Changes

1. Create a new branch for your feature:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes and commit them:
   ```bash
   git commit -am "Add your feature description"
   ```

3. Push to your branch:
   ```bash
   git push origin feature/your-feature-name
   ```

4. Create a Pull Request on GitHub

## Adding Support for New IDEs

To add support for a new IDE:

1. Update the `IDEHandler` class in `src/ide.py` to add a new method to handle the IDE
2. Add the IDE to the `get_supported_ides()` static method
3. Update the configuration parsing in `src/main.py` as needed
4. Update documentation in README.md and sample.gwtmrc

## License

By contributing, you agree that your contributions will be licensed under the project's MIT License.
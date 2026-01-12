# Contributing to Mangalify

Thanks for helping out! We like to keep things simple here.

## 🚀 Quick Start

1. **Fork & Clone** the repo.
2. **Set up** your environment:
   ```bash
   python -m venv venv
   # Windows: venv\Scripts\activate | Mac/Linux: source venv/bin/activate
   pip install -r requirements.txt
   ```
3. **Configure**: Copy `.env.example` to `.env` and fill in your test credentials.
4. **Database**: You need MongoDB running locally (default port 27017) or via Docker.

## 🛠️ Development Standards

- **Code Style**: Standard Python (PEP 8). Keep it clean.
- **Type Hints**: Please use them for new code (e.g., `def func(name: str) -> bool:`).
- **Testing**: Run `pytest` locally before pushing. If you add a feature, add a test.
- **Commits**: We prefer [Conventional Commits](https://www.conventionalcommits.org/) (e.g., `feat: new command`, `fix: crash on startup`).

## 📦 Submitting a PR

1. Create a feature branch.
2. Push to your fork.
3. Open a Pull Request against `main`.
4. Briefly explain what you changed and why.

Questions? Open an issue. Happy coding!

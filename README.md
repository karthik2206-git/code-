# Code++ Python Edition

A modern, extensible Notepad++ like text/code editor built with Git integration.

## Features

- Tabbed editing, syntax highlighting, code folding
- Find/replace, line numbers, theming
- Git integration (status, commit, push, pull, log, branch)
- Recent files, drag & drop, extensible plugins

## Getting Started

```sh
pip install -r requirements.txt
python main.py
```

## Project Structure

- `main.py` – Application entry point
- `editor.py` – QScintilla editor widget
- `tabmanager.py` – Tabbed document management
- `git_integration.py` – Git commands via GitPython
- `findreplace.py` – Find/replace dialog
- `recentfiles.py` – Recent files manager
- `themes.py` – Light/dark themes
- `resources/` – Icons, themes, etc.

## License

MIT

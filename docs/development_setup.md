# Development Environment Setup Guide

This guide provides the steps to set up a fully functional development environment for the `signal-ai` bot and the `signal-client` library.

**IMPORTANT:** The project has been restructured to use `signal-client` instead of `signalbot`. If you have an old setup, you must remove your existing virtual environments before proceeding.

## Setup from a Fresh Clone

For a new setup or to fix an old one, follow these steps:

1.  **Clean Up Old Virtual Environments (if applicable):**

    - If you have a `.venv` directory inside your `signal-ai` or `signal-client` folders, delete them.

2.  **Open the VS Code Workspace:**

    - Open the `signal.code-workspace` file located in the root of the project. This is the primary way you should work with this project.
    - From your terminal, you can run: `code ../signal.code-workspace` (if you are inside `signal-ai`).

3.  **Run the Setup Script:**

    - Once the workspace is open, open a new terminal within VSCode (`Ctrl+` or `Cmd+`).
    - It should open in the `signal-ai` directory.
    - Run the setup script:
      ```bash
      ./scripts/setup.sh
      ```
    - This will install all dependencies for both `signal-ai` and `signal-client`.

4.  **Select Python Interpreter:**
    - Open the Command Palette (`Ctrl+Shift+P` or `Cmd+Shift+P`).
    - Search for and select `Python: Select Interpreter`.
    - Choose the one that points to `./.venv/bin/python`. The workspace settings should default to this, but it's good to confirm.

Your environment is now ready. You can edit files in both `signal-ai` and `signal-client` folders, and the changes will work together seamlessly.

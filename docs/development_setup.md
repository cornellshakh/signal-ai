# Development Environment Setup Guide

This guide provides the steps to set up a fully functional and conflict-free development environment for the `signal-ai` bot and its `signalbot` library fork.

**IMPORTANT:** The project has just been restructured. Your immediate next steps are below. The `setup_workspace.sh` script is for future use (e.g., on a fresh clone).

## Immediate Next Steps

1.  **Close and Re-open VSCode:**

    - Close your current VSCode window (which is likely open to the `signal-ai` folder).
    - Open VSCode again, but this time, open the **`signal-ai.code-workspace`** file located _outside_ the `signal-ai` folder.
    - From your terminal, you can run: `code ../signal-ai.code-workspace`

2.  **Install Dependencies:**

    - Once the workspace is open, open a new terminal within VSCode (`Ctrl+` or `Cmd+`).
    - It should open in the `signal-ai` directory.
    - Run the command: `poetry install`
    - This will install all dependencies, including `signalbot` from the new location.

3.  **Select Python Interpreter:**
    - Open the Command Palette (`Ctrl+Shift+P` or `Cmd+Shift+P`).
    - Search for and select `Python: Select Interpreter`.
    - Choose the one that points to `./.venv/bin/python`. The workspace settings should default to this, but it's good to confirm.

Your environment is now ready. You can edit files in both `signal-ai` and `signalbot` folders, and the changes will work together seamlessly.

---

## Full Setup from a Fresh Clone

For future reference, if you are setting up this project from a fresh clone, you can use the automated script.

1.  Run the setup script from within the `signal-ai` directory:
    ```bash
    ./scripts/setup_workspace.sh
    ```
2.  Follow the "Immediate Next Steps" above (close the folder, open the workspace, select interpreter).

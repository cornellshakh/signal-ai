# MCP Server Integration Plan

## Overview

This document outlines the plan for integrating the MarkItDown and Open-WebSearch MCP servers into the Signal bot.

## Technical Requirements

### MarkItDown

- Language: Python 3.10+
- Dependencies: Requires dependencies for specific file formats (PDF, DOCX, etc.). These can be installed individually or with the `[all]` option.
- Runtime: Python runtime environment.
- MCP Server: Can be run as a separate process using STDIO.

### Open-WebSearch

- Language: JavaScript (Node.js)
- Dependencies: Requires Node.js and npm.
- Runtime: Node.js runtime environment.
- MCP Server: Can be run using NPX or locally after building. Supports HTTP.

## Integration Architecture

The Signal bot is written in Python, so I will need to consider how to interact with the Open-WebSearch MCP server, which is written in JavaScript. I can use a combination of STDIO and HTTP to communicate with the MCP servers.

Here's the proposed architecture:

1.  **Signal Bot (Python):** Receives messages from users.
2.  **MCP Server Communication:**
    - **MarkItDown:** Run as a separate Python process and communicate via STDIO.
    - **Open-WebSearch:** Run as a separate Node.js process and communicate via HTTP.
3.  **Message Flow:**
    - Signal message -> Bot -> MCP server (via STDIO or HTTP) -> Response -> Bot -> Signal message.
4.  **Error Handling:** Implement error handling in the bot to catch exceptions from the MCP servers.
5.  **Rate Limiting:** Implement rate limiting in the bot to prevent abuse of the MCP servers.

## Detailed Specifications

### MarkItDown MCP Server

- **Communication Protocol:** STDIO
- **Command:** `!convert <attachment>`
- **Input:** File attachment from the Signal message.
- **Output:** Markdown content.
- **Error Handling:**
  - If the file format is not supported, return an error message.
  - If the conversion fails, return an error message.
- **Rate Limiting:** Limit the number of conversions per user per minute.

### Open-WebSearch MCP Server

- **Communication Protocol:** HTTP
- **Command:** `!search <query>`
- **Input:** Search query from the Signal message.
- **Output:** JSON response containing search results.
- **Error Handling:**
  - If the search query is invalid, return an error message.
  - If the search fails, return an error message.
- **Rate Limiting:** Limit the number of searches per user per minute.

## Implementation Phases

- **Phase 1: Core (MarkItDown)**
  - Implement basic document conversion functionality using MarkItDown.
  - Run MarkItDown MCP server using STDIO.
  - Test with simple document conversions.
- **Phase 2: Utilities (Open-WebSearch)**
  - Implement web search functionality using Open-WebSearch.
  - Run Open-WebSearch MCP server using HTTP.
  - Test with simple search queries.

## Installation, Configuration, and Usage Examples

### MarkItDown

- **Installation:**

```bash
pip install 'markitdown[all]'
```

- **Configuration:**

  - No specific configuration is required for the STDIO mode.
  - For Azure Document Intelligence, set the `docintel_endpoint` parameter when creating the `MarkItDown` object.
  - For LLM image descriptions, provide `llm_client` and `llm_model` parameters.

- **Usage:**

```python
import subprocess

def convert_to_markdown(file_path):
    try:
        process = subprocess.Popen(
            ["markitdown"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        with open(file_path, "rb") as f:
            stdout, stderr = process.communicate(f.read())
        if stderr:
            print(f"Error converting {file_path}: {stderr.decode()}")
            return None
        return stdout.decode()
    except Exception as e:
        print(f"Error converting {file_path}: {e}")
        return None

# Example usage
file_path = "test.pdf"
markdown_content = convert_to_markdown(file_path)
if markdown_content:
    print(markdown_content)
```

### Open-WebSearch

- **Installation:**

```bash
npm install -g open-websearch
```

- **Configuration:**

  - Set environment variables to configure the server (e.g., `DEFAULT_SEARCH_ENGINE`, `USE_PROXY`, `PROXY_URL`).

- **Usage:**

```python
import requests
import json

def search_web(query, limit=3, engines=None):
    try:
        url = "http://localhost:3000/mcp"  # Assuming Open-WebSearch is running on port 3000
        headers = {"Content-Type": "application/json"}
        data = {
            "server_name": "web-search",
            "tool_name": "search",
            "arguments": {
                "query": query,
                "limit": limit,
                "engines": engines or ["bing", "duckduckgo", "exa", "brave", "juejin", "csdn"],
            },
        }
        response = requests.post(url, headers=headers, data=json.dumps(data))
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error searching the web: {e}")
        return None

# Example usage
search_query = "test query"
search_results = search_web(search_query)
if search_results:
    print(search_results)
```

## Deployment Checklist

- [ ] Environment Setup:
  - [ ] Install Python 3.10+
  - [ ] Install Node.js and npm
  - [ ] Create virtual environments for Python and Node.js
  - [ ] Install dependencies for MarkItDown and Open-WebSearch
- [ ] Testing Strategy:
  - [ ] MarkItDown: Test with various file formats (PDF, DOCX, etc.)
  - [ ] Open-WebSearch: Test with simple and complex search queries
- [ ] Rollback Plan:
  - [ ] If a server fails, disable the corresponding functionality in the bot.
  - [ ] Monitor server logs for errors.

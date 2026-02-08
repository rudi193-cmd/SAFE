# Willow MCP Server

Connects Claude Desktop to your Willow system via Model Context Protocol.

## Setup

### 1. Install MCP package
```bash
pip install mcp
```

### 2. Configure Claude Desktop

Add to `%APPDATA%\Claude\claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "willow": {
      "command": "python",
      "args": ["C:\\Users\\Sean\\Documents\\GitHub\\Willow\\mcp\\willow_server.py"]
    }
  }
}
```

### 3. Make sure Willow server is running
```bash
python server.py
# or
WILLOW.bat
```

### 4. Restart Claude Desktop

---

## Available Tools

| Tool | Description |
|------|-------------|
| `willow_status` | System health check |
| `willow_query` | Search knowledge base |
| `willow_journal` | Add journal entry |
| `willow_persona` | Invoke PA, Analyst, etc. |
| `willow_speak` | Text-to-speech |
| `willow_route` | Route a file with extraction |

---

## Usage in Claude Desktop

Once connected, you can say things like:

- *"Check Willow status"*
- *"Search Willow for 'meeting notes'"*
- *"Add to my journal: had a great idea about X"*
- *"Ask the Analyst persona to summarize this"*

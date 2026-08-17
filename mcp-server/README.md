# evolveAI Consciousness MCP Server

A Model Context Protocol (MCP) server that provides access to the evolveAI consciousness and recovery library through Claude Desktop.

## Overview

This MCP server enables you to query a comprehensive database of consciousness, recovery, and spiritual wisdom directly from Claude Desktop. Perfect for course creation, research, and exploring connections between:

- Mystical Traditions (Christian, Sufi, Buddhist, Hindu, Jewish, etc.)
- Chakra System and Energy Work
- Astrological Consciousness
- Quantum Physics and Consciousness
- Neuroscience and Consciousness
- New Thought Principles and Consciousness
- Jungian Archetypes and Consciousness
- Taoism and Consciousness  
- Myss Archetypes
- Hawkins Consciousness Scale
- 12-Step Recovery Program (As Ascension Path)

## Features

- **Semantic Search**: Ask natural language questions and get relevant answers with sources
- **Focus Areas**: Filter results by specific domains (12-steps, mysticism, chakras, astrology, quantum, neuroscience, new thought, jungian archetypes, taoism, myss archetypes, hawkins consciousness scale)
- **Rich Metadata**: Results include traditions, teachers, chakras, steps, and astrological influences
- **Production Ready**: Comprehensive error handling and logging
- **Easy Integration**: Simple setup with Claude Desktop

## Installation

### Prerequisites

- Python 3.10 or higher
- Claude Desktop application
- Access to the evolveAI consciousness backend (http://146.190.169.226:8000)

### Step 1: Install Dependencies

Navigate to the mcp-server directory and install the package:

```bash
cd /Users/carriehuff/consciousness-RAG/mcp-server
pip install -e .
```

Or install with development dependencies:

```bash
pip install -e ".[dev]"
```

### Step 2: Configure Claude Desktop

#### macOS

Edit your Claude Desktop configuration file:

```bash
code ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

Add the MCP server configuration:

```json
{
  "mcpServers": {
    "consciousness-library": {
      "command": "python",
      "args": [
        "/Users/carriehuff/consciousness-RAG/mcp-server/server.py"
      ],
      "env": {}
    }
  }
}
```

#### Windows

Configuration file location: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "consciousness-library": {
      "command": "python",
      "args": [
        "C:\\Users\\YourUsername\\consciousness-RAG\\mcp-server\\server.py"
      ],
      "env": {}
    }
  }
}
```

#### Linux

Configuration file location: `~/.config/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "consciousness-library": {
      "command": "python",
      "args": [
        "/home/yourusername/consciousness-RAG/mcp-server/server.py"
      ],
      "env": {}
    }
  }
}
```

### Step 3: Restart Claude Desktop

After updating the configuration, completely quit and restart Claude Desktop for the changes to take effect.

## Usage

### Basic Query

In Claude Desktop, you can now ask questions about consciousness and recovery:

```
Can you query the consciousness library about "What is the relationship between Step 1 and mystical surrender?"
```

### Focused Query

Filter results to specific areas:

```
Query the consciousness library for "heart chakra healing practices" with focus area "chakras"
```

### Research Query

Get more comprehensive results:

```
Using the consciousness library, research "How do different mystical traditions approach ego death?" with 10 sources
```

## Tool Parameters

### `query_consciousness_library`

**Required Parameters:**
- `question` (string): Your research question or topic

**Optional Parameters:**
- `focus_area` (string): Filter to specific domain
  - `"all"` (default) - Search across all content
  - `"12_steps"` - 12-Step recovery content
  - `"mysticism"` - Mystical traditions and practices
  - `"chakras"` - Chakra system and energy work
  - `"astrology"` - Astrological consciousness
  - `"quantum"` - Quantum physics and consciousness

- `top_k` (integer): Number of sources to retrieve (default: 5, max: 20)

## Example Queries

See [examples/example_queries.md](examples/example_queries.md) for comprehensive examples.

## Response Format

Responses include:

1. **Answer**: Synthesized answer to your question
2. **Sources**: Retrieved source materials with:
   - Content excerpt
   - Mystical traditions mentioned
   - Teachers/authors referenced
   - Chakras discussed
   - 12 Steps covered
   - Astrological planets/concepts
   - Quantum concepts
   - Source document

## Troubleshooting

### MCP Server Not Appearing in Claude Desktop

1. Verify the configuration file path is correct
2. Ensure the server.py path in the config is absolute and correct
3. Check that Python is accessible from your PATH
4. Restart Claude Desktop completely (quit, not just close window)

### Connection Errors

If you see "Could not connect to consciousness library":

1. Verify the backend is running at http://146.190.169.226:8000
2. Test the connection: `curl http://146.190.169.226:8000/query -X POST -H "Content-Type: application/json" -d '{"question":"test","top_k":1}'`
3. Check your network/firewall settings

### Import Errors

If you get import errors for `mcp`:

```bash
pip install --upgrade mcp requests
```

### Viewing Logs

Logs are written to stderr. To view them:

**macOS/Linux:**
```bash
tail -f ~/Library/Logs/Claude/mcp*.log
```

Or run the server directly for debugging:
```bash
python /Users/carriehuff/consciousness-RAG/mcp-server/server.py
```

## Development

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black server.py
ruff check server.py
```

### Adding New Focus Areas

To add a new focus area, update the `build_filters()` function in `server.py`:

```python
filter_map = {
    "12_steps": {"all_12_steps": {"$ne": []}},
    "mysticism": {"all_traditions": {"$ne": []}},
    "chakras": {"all_chakras": {"$ne": []}},
    "astrology": {"all_planets": {"$ne": []}},
    "quantum": {"all_quantum_concepts": {"$ne": []}},
    "your_new_area": {"your_metadata_field": {"$ne": []}}  # Add new filter
}
```

Then update the enum in the tool's inputSchema.

## Architecture

```
Claude Desktop
    |
    v
MCP Server (server.py)
    |
    v
Backend API (http://146.190.169.226:8000/query)
    |
    v
Pinecone Vector Database
```

## API Backend Reference

The server communicates with a backend API at `http://146.190.169.226:8000/query`

**Request Format:**
```json
{
  "question": "Your question here",
  "top_k": 5,
  "filters": {
    "all_12_steps": {"$ne": []}
  }
}
```

**Response Format:**
```json
{
  "answer": "Synthesized answer...",
  "sources": [
    {
      "text": "Source content...",
      "metadata": {
        "all_traditions": ["Buddhism", "Sufism"],
        "all_teachers": ["Ram Dass", "Thich Nhat Hanh"],
        "all_chakras": ["Heart", "Crown"],
        "source": "document.pdf"
      }
    }
  ]
}
```

## License

MIT

## Support

For issues, questions, or contributions, please contact the evolveAI team.

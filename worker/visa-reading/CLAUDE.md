# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

CRM Visa Notification is an AI-powered email automation system that uses Composio to integrate Gmail with DeepSeek AI for intelligent email management.

## Architecture

**Core Components:**
- **AI Model**: DeepSeek Chat (via OpenAI-compatible API)
- **Tool Integration**: Composio framework for Gmail API access
- **Execution Flow**: Agentic loop where AI decides which tools to call based on user prompts

**Key Integration Pattern:**
The system uses a multi-turn conversation loop where:
1. User provides a natural language email task
2. DeepSeek AI analyzes the request and calls appropriate Composio tools
3. Tools execute Gmail actions (send email, etc.)
4. Results are fed back to the AI for confirmation or next steps
5. Loop continues until task completion (max 5 iterations)

**Critical Configuration:**
- `toolkit_versions={"gmail": "20260225_01"}` - Must specify exact Gmail toolkit version (not "latest") for manual tool execution
- `entity_id` - Required to identify which connected Gmail account to use (currently: `pg-test-69d49a5d-5542-4097-bc2f-f2a974534d59`)
- Tool execution requires `user_id` parameter, not `entity_id`

## Running the Application

**Docker (Recommended):**
```bash
docker compose build
docker compose up
```

**Local Python:**
```bash
pip install -r requirements.txt
python main.py
```

## Environment Configuration

Required environment variables in `.env`:
- `COMPOSIO_API_KEY` - Composio platform API key
- `OPENAI_API_KEY` - DeepSeek API key (OpenAI-compatible)
- `OPENAI_BASE_URL` - Set to `https://api.deepseek.com`
- `COMPOSIO_DANGEROUSLY_SKIP_VERSION_CHECK` - Set to `true` (though toolkit version must still be specified in code)

**Project Credentials:**
- Composio API Key: `ak_NhaP1Mm32iE9CGE6izhr`
- Project ID: `pr_9a2yzEnUMJBw`
- Entity ID: `pg-test-69d49a5d-5542-4097-bc2f-f2a974534d59`

## Composio Tool Execution

**Getting Tools:**
```python
tools = composio.tools.get(tools=["GMAIL_SEND_EMAIL"], user_id=entity_id)
```

**Executing Tools:**
```python
result = composio.tools.execute(
    tool_name,
    arguments_dict,
    user_id=entity_id  # NOT entity_id as kwarg name
)
```

**Common Pitfalls:**
- `composio.tools.execute()` signature: `(slug, arguments, *, user_id=None, ...)`
- Must use `user_id` parameter, not `entity_id`
- Cannot use "latest" for toolkit version in manual execution
- Must query toolkit versions via `composio.toolkits.get()` to find specific version strings

## Modifying Email Tasks

To change the email being sent, modify the user message in `main.py`:
```python
messages = [
    {"role": "system", "content": "You are a helpful assistant..."},
    {"role": "user", "content": "Your email task here"}
]
```

The AI will interpret natural language instructions and call the appropriate Gmail tools.

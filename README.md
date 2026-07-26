# Knowledge Base Assistant

A production-ready conversational AI application built with Amazon Bedrock, LangChain, and Streamlit. This application supports multiple retrieval backends, chain types, and optional PTO (Paid Time Off) management functionality.

## Features

- **Multiple Retrieval Backends**: Support for both Amazon Knowledge Bases and Amazon Kendra
- **Flexible Chain Types**: 
  - Simple Q&A with RetrievalQA
  - Conversational chains with memory
  - Agent-based interactions with tool calling
- **PTO Management**: Optional employee time off balance tracking and request processing
- **Configuration Management**: Environment-based configuration for easy deployment
- **Modern UI**: Clean Streamlit interface with chat history and source document display

## Prerequisites

- Python 3.9+
- AWS account with Bedrock access
- AWS credentials configured (via AWS CLI or environment variables)
- Amazon Knowledge Base ID or Kendra Index ID

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd bedrock-ai-lab
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables:
```bash
cp .env.example .env
```

Edit `.env` and set your configuration values:
- `KNOWLEDGE_BASE_ID` or `KENDRA_INDEX_ID`
- `MODEL_ID` (default: anthropic.claude-instant-v1)
- `CHAIN_TYPE` (conversational, simple, or agent)
- `ENABLE_PTO` (true/false for PTO features)

## Configuration

### Environment Variables

| Variable | Description | Default | Options |
|----------|-------------|---------|---------|
| `PAGE_TITLE` | Browser page title | Knowledge Base Assistant | - |
| `APP_TITLE` | Application title | Knowledge Base Assistant | - |
| `MODEL_ID` | Bedrock model ID | anthropic.claude-instant-v1 | - |
| `TEMPERATURE` | Model temperature | 0 | 0.0-1.0 |
| `TOP_K` | Top K sampling | 10 | - |
| `MAX_TOKENS_TO_SAMPLE` | Max tokens | 750 | - |
| `RETRIEVER_TYPE` | Retrieval backend | knowledge_base | knowledge_base, kendra |
| `KNOWLEDGE_BASE_ID` | Knowledge Base ID | - | Required for KB |
| `KENDRA_INDEX_ID` | Kendra Index ID | - | Required for Kendra |
| `TOP_K_RESULTS` | Number of results | 4 | - |
| `CHAIN_TYPE` | Chain type | conversational | conversational, simple, agent |
| `ENABLE_PTO` | Enable PTO features | false | true, false |

### Chain Types

1. **Conversational** (default): Full conversational chain with memory and context awareness
2. **Simple**: Basic Q&A without conversation history
3. **Agent**: Tool-calling agent for PTO management (requires `ENABLE_PTO=true`)

## Running the Application

Start the Streamlit application:

```bash
streamlit run app.py
```

The application will be available at `http://localhost:8501`

## PTO Management

When `ENABLE_PTO=true` and `CHAIN_TYPE=agent`, the application includes PTO management tools:

- **Get PTO Balance**: Query employee PTO balance by ID
- **Request PTO**: Submit time off requests
- **List Employees**: View all employees and their balances

Sample employee IDs are included in `pto_manager.py` for testing.

## Project Structure

```
bedrock-ai-lab/
├── app.py              # Main application
├── pto_manager.py      # PTO management module
├── requirements.txt    # Python dependencies
├── .env.example        # Configuration template
└── README.md          # This file
```

## License

See LICENSE file for details.

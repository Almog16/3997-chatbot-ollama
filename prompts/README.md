# Ollama Chatbot Prompts Collection

Complete collection of prompts used to build a production-ready Ollama chatbot with React frontend and Python FastAPI backend.

## 📚 Prompt Index

### Phase 1: Foundation (Backend & Basic UI)

**01. Build Backend Structure** - `01_build_backend_structure.md`
- Set up Python FastAPI backend
- Configure project structure
- Create initial API endpoints
- Set up dependencies with uv

**02. Build Chatbot UI** - `02_build_chatbot_ui.md`
- Create React TypeScript frontend
- Implement streaming chat interface
- Add model selection
- Build modern UI with Tailwind CSS

**03. Improve Code Structure** - `03_improve_chatbot_ui_code.md`
- Refactor single-file React app into modules
- Separate components, hooks, types
- Improve maintainability
- Better code organization

**04. Setup & Quality Tools** - `04_improve_setup_and_quality.md`
- Add Ruff linting
- Create Makefile for automation
- Improve error handling
- Add code quality checks

### Phase 2: Enhanced Features

**05. Improve UI/UX Design** - `05_improve_ui_ux_design.md`
- Professional, polished design
- Better color palette
- Improved spacing and typography
- Modern, production-ready aesthetics

**06. Add Agent & Tools** - `06_add_agent_and_tools.md`
- Implement LangGraph agent
- Add web search capability
- Calculator and other tools
- Multi-step reasoning
- Streaming tool execution

**07. Enhance UI Components** - `07_enhance_ui_components.md`
- Better tool indicators
- Improved message bubbles
- Fixed input alignment
- Functional suggestion buttons
- Tooltips and animations

### Phase 3: Testing & Reliability

**08. Add Testing Workflows** - `add_testing_workflows.txt`
- Define Playwright E2E setup for the React client
- Stub backend routes for deterministic UI tests
- Add pytest + pytest-asyncio coverage for FastAPI endpoints
- Document how to run both suites locally and in CI

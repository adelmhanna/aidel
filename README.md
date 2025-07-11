# AgenticAI Server – Modular LLM-Powered Server Event Intelligence

A modular, explainable Agentic AI framework for processing server (e.g. Dell PowerEdge Redfish) events, powered by LLMs, classical, fuzzy, and ML rules, and extensible “skills/workflow” automation.  
All memory, event processing, and tool integrations are decoupled for easy extension, testing, and explainability.

---

## Features

- **Hybrid Reasoning:** Classic rules, fuzzy logic, and real ML in one explainable stack
- **LLM Integration:** Pluggable with OpenAI/llama.cpp and others for dynamic memory, action, and policy generation
- **Procedural Memory:** Graph-based workflows and skills for real server automation
- **Full Explainability:** Trace logs for every decision/action path
- **Redfish/Telemetry Ready:** Dell PowerEdge/Redfish event and telemetry support out-of-the-box
- **Persona Memory:** Agents can adapt style, values, and diagnostics per “persona”
- **Fully Modular:** Add new memory, event processors, tools, or policies with no monolith refactor

---

## Directory Structure

agenticai-server/  
├── agent/  
│   ├── __init__.py  
│   ├── core.py             # Main Agent class and orchestration  
│   └── processor/  
│       ├── __init__.py  
│       └── redfish.py      # PowerEdge Redfish/Telemetry event processor  
├── memory/  
│   ├── __init__.py  
│   ├── raw_text.py  
│   ├── knowledge_graph.py  
│   ├── vector_store.py  
│   ├── classic_rules.py  
│   ├── fuzzy_rules.py  
│   ├── ml_rules.py  
│   ├── procedural.py  
│   ├── persona.py  
│   └── policy.py  
├── tools/  
│   ├── __init__.py  
│   └── external.py         # External integrations (notification, APIs)  
├── main.py                 # Entrypoint  
├── requirements.txt  
└── README.md  

---

## Installation

**Requirements:** Python 3.10+ recommended.

```bash
git clone https://github.com/adelhanna/agenticai-server.git
cd agenticai-server
pip install -r requirements.txt

Note: For LLM integration, set your environment variables in a .env file (see below).

Environment Variables
Create a .env file in the root directory:

LLM_SERVER_URL=https://genai-api-dev.example.com/v1
API_KEY=your-llm-or-openai-api-key

Usage
Run the main application with sample Redfish events and telemetry:
python main.py
```
You will see hybrid LLM, fuzzy, and ML reasoning, plus workflow automation and detailed trace/explain logs.
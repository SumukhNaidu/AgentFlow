# AgentFlow — Local Multi-Agent Productivity Assistant

AgentFlow is a privacy-focused, local multi-agent productivity assistant designed to automate everyday workflows such as email search, calendar management, task handling, and personal memory.

The system uses **local Small Language Models (SLMs)** through Ollama instead of paid cloud LLM APIs, making the system cost-efficient and suitable for experimentation with agentic AI.

---

##  Features

- Intelligent request routing using a local SLM
- Multi-step task planning using a dedicated planning model
- Specialized agents for:
  -  Email
  -  Calendar
  -  Tasks
  -  Memory
- Structured outputs using Pydantic
- Rule-based plan validation
- Dependency-aware multi-step execution
- Local LLM inference using Ollama
- Designed to work without paid LLM APIs
- Modular architecture for adding new agents and tools

---

##  Architecture

```text
                    User Request
                         │
                         ▼
                 ┌───────────────┐
                 │     Router    │
                 │   Qwen 2.5    │
                 └───────┬───────┘
                         │
                 Simple / Complex
                         │
              ┌──────────┴──────────┐
              │                     │
           Simple                 Complex
              │                     │
              ▼                     ▼
        Direct Agent          ┌───────────────┐
                              │    Planner    │
                              │    Phi-3      │
                              └───────┬───────┘
                                      │
                                      ▼
                              ┌───────────────┐
                              │   Validator   │
                              │ Pydantic +    │
                              │ Rules         │
                              └───────┬───────┘
                                      │
                                  Valid Plan
                                      │
                       ┌──────────────┼──────────────┐
                       ▼              ▼              ▼
                      Email         Calendar      Task
                       │              │              │
                       └──────────────┼──────────────┘
                                      │
                                      ▼
                                   Memory
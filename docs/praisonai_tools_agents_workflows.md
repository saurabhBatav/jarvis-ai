# PraisonAI Complete Reference
## Tools, Agents & Workflows

---

# PART 1: CORE TOOLS (21)

## Search Tools (11)
| Tool | Purpose |
|------|---------|
| tavily | AI-optimized web search with semantic understanding |
| tavily_search | Focused web search using Tavily API |
| tavily_extract | Extract structured data from web pages |
| exa | Neural search using Exa.ai for semantic results |
| exa_search | Search with Exa neural search engine |
| exa_search_contents | Search and retrieve full content from Exa |
| duckduckgo | Privacy-focused web search |
| internet_search | Generic internet search with fallback |
| searxng_search | Metasearch engine for aggregated results |
| search_web | Auto-select best search tool for query |
| searxng_search | Search using SearXNG meta-search |

## Scraping Tools (6)
| Tool | Purpose |
|------|---------|
| crawl4ai | Web crawling with AI extraction capabilities |
| crawl4ai_extract | Extract specific content from crawled pages |
| spider_tools | Multi-page crawling and link discovery |
| scrape_page | Fetch and parse web page content |
| extract_links | Extract all hyperlinks from a webpage |

## File/Shell Tools (6)
| Tool | Purpose |
|------|---------|
| read_file | Read content from local files |
| write_file | Write content to local files |
| list_files | List directory contents |
| execute_command | Run shell commands |
| list_processes | List running system processes |
| execute_code | Execute Python code in sandbox |
| analyze_code | Analyze code structure and quality |

## Training Tools (4)
| Tool | Purpose |
|------|---------|
| cot_save | Save Chain-of-Thought training data |
| cot_upload_to_huggingface | Upload CoT datasets to HuggingFace |
| cot_generate | Generate chain-of-thought examples |
| cot_improve | Improve existing CoT training data |

---

# PART 2: EXTENDED TOOLS (135+)

## Data Format Tools (15)
| Tool | Purpose |
|------|---------|
| read_json | Parse and load JSON files |
| write_json | Serialize data to JSON format |
| validate_json | Check JSON syntax and schema |
| read_yaml | Parse YAML configuration files |
| write_yaml | Serialize data to YAML format |
| validate_yaml | Validate YAML syntax |
| read_xml | Parse XML documents |
| write_xml | Create XML documents |
| transform_xml | Apply XSLT transformations |
| read_csv | Load CSV data into dataframes |
| write_csv | Export data to CSV format |
| merge_csv | Combine multiple CSV files |
| read_excel | Load Excel spreadsheet data |
| write_excel | Export data to Excel format |
| merge_excel | Combine multiple Excel files |

## Research Tools (4)
| Tool | Purpose |
|------|---------|
| search_arxiv | Search academic papers on arXiv |
| get_arxiv_paper | Download arXiv paper metadata/pdf |
| wikipedia_search | Search Wikipedia encyclopedia |
| pubmed_search | Search medical/scientific literature |

## Finance/Analytics Tools (5)
| Tool | Purpose |
|------|---------|
| get_stock_price | Fetch real-time stock prices via YFinance |
| calculate | Perform mathematical calculations |
| solve_equation | Solve mathematical equations |
| duckdb_query | Run SQL queries on DuckDB |
| pandas_read_csv | Load CSV with pandas |

## Integration Tools (9)
| Tool | Purpose |
|------|---------|
| EmailTool | Send/receive emails via SMTP/IMAP |
| SlackTool | Post messages to Slack channels |
| DiscordTool | Send messages to Discord servers |
| GitHubTool | Manage repos, issues, PRs |
| NotionTool | Read/write Notion pages |
| TrelloTool | Manage Trello boards/cards |
| PostgresTool | PostgreSQL database operations |
| MongoDBTool | MongoDB database operations |
| RedisTool | Redis cache operations |

---

# PART 3: AGENT TYPES

## 1. Agent (Single)
- **Purpose**: Fundamental execution unit with role/goal/backstory
- **Parameters**: name, role, goal, backstory, instructions, llm, tools
- **Use Case**: Single-task automation

## 2. AgentTeam (Multi-Agent)
- **Purpose**: Collaborative orchestration of multiple agents
- **Process Types**: sequential, hierarchical
- **Features**: planning, memory, knowledge base
- **Use Case**: Complex multi-step workflows

## 3. AgentFlow (Workflow)
- **Purpose**: Deterministic pipeline orchestration
- **Steps**: route, parallel, loop, repeat
- **Use Case**: Structured business processes

## 4. AgentOS
- **Purpose**: REST API deployment layer for production
- **Use Case**: Production API services

---

# PART 4: AGENT COMPONENTS

## Agent Parameters
| Parameter | Purpose |
|-----------|---------|
| name | Agent identifier |
| role | Functional expertise area |
| goal | Success condition/objective |
| backstory | Professional context/persona |
| instructions | Detailed task instructions |
| llm | Model to use (gpt-4o, llama, etc.) |
| tools | List of available tools |
| allow_delegation | Enable agent handoffs |
| allow_code_execution | Enable code tools |
| memory | Enable memory system |
| knowledge | RAG knowledge base |
| planning | Enable planning mode |
| reflection | Enable self-reflection |
| max_iterations | Execution limit |
| timeout | Request timeout |

---

# PART 5: WORKFLOW TYPES

## 1. Sequential
- **Purpose**: Linear task execution in order
- **Flow**: agent1 → agent2 → agent3
- **Use Case**: Step-by-step processes

## 2. Hierarchical
- **Purpose**: Manager delegates to worker agents
- **Flow**: Manager LLM → Worker agents
- **Use Case**: Complex multi-agent coordination

## 3. Parallel
- **Purpose**: Simultaneous execution with aggregation
- **Flow**: agent1 + agent2 + agent3 → aggregator
- **Use Case**: Independent parallel tasks

## 4. Planning Mode
- **Purpose**: Plan → execute → reason cycle
- **Flow**: Break down → execute → evaluate
- **Use Case**: Complex problem-solving

---

# PART 6: ADVANCED FEATURES

| Feature | Purpose |
|---------|---------|
| Self-Reflection | Agents evaluate and improve responses |
| Planning Mode | Break complex tasks before execution |
| Code Execution | Sandboxed Python code running |
| MCP Integration | External tools via Model Context Protocol |
| Handoffs | Agent-to-agent task delegation |
| Memory | Short-term + long-term memory |
| Knowledge | RAG with vector stores |

---

# PART 7: LLM MODELS

## Supported Providers
| Provider | Models |
|----------|--------|
| OpenAI | gpt-4o, gpt-4o-mini, gpt-3.5-turbo |
| Anthropic | claude-3.5-sonnet, claude-3-haiku |
| Google | gemini-2.5-flash, gemini-1.5-flash |
| Groq | llama-3.1-70b-versatile, llama-3.1-8b-instant |
| Ollama | llama2, mistral, codellama (local) |

---

# PART 8: CLI COMMANDS

| Command | Purpose |
|---------|---------|
| praisonai agents.yaml | Run from YAML config |
| praisonai "prompt" | No-code mode |
| praisonai claw | Launch dashboard (localhost:8082) |
| praisonai bot telegram | Start Telegram bot |
| praisonai bot slack | Start Slack bot |
| praisonai bot discord | Start Discord bot |
| praisonai browser navigate | Navigate browser |
| praisonai browser run | Run browser automation |
| praisonai skills list | List available skills |
| praisonai skills check | Check skill status |
| praisonai plugins list | List plugins |
| praisonai plugins doctor | Diagnose plugin issues |
| praisonai sandbox status | Check sandbox status |
| praisonai doctor | Run diagnostics |

---

# PART 9: USE CASES

| Use Case | Description |
|----------|-------------|
| Research & Analysis | Deep research with multiple sources |
| Code Generation | Programming and debugging |
| Content Creation | Blog posts, documentation |
| Data Pipelines | ETL and analytics |
| Customer Support | 24/7 automated support |
| Workflow Automation | Multi-step business processes |

---

# PART 10: PLATFORM INTEGRATIONS

## Messaging
- Telegram
- Discord
- Slack
- WhatsApp

## Productivity
- Google Workspace
- Notion
- Jira
- Trello

## Development
- GitHub (PRs, issues, repos)

## Databases
- PostgreSQL
- MongoDB
- Redis
- SQLite

---

*Generated from PraisonAI Documentation Reference*
*Total: 21 core tools + 135+ extended tools + 4 agent types + 4 workflow types*
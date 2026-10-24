# Execution and Deployment Guide

Welcome to the **Intelligent Business Data Analysis Agent** execution guide. This comprehensive guide walks you through setting up, configuring, running, testing, and troubleshooting the entire application locally or in a deployment environment.

---

## 1. System Requirements & Prerequisites

- **Operating System:** Windows 10/11, macOS (Intel/Apple Silicon), or Linux (Ubuntu 20.04+)
- **Python Version:** Python **3.9**, **3.10**, **3.11**, or **3.12** *(Python 3.10 recommended)*
- **Package Manager:** `pip` (Python package manager)
- **Browser:** Modern web browser (Chrome, Edge, Firefox, or Safari)

---

## 2. Environment Setup

### Step A: Navigate to the Project Directory
Open your terminal (PowerShell, Command Prompt, or Bash) and navigate to the root directory:
```powershell
cd /path/to/Intelligent-Business-Data-Analysis-Agent
```

### Step B: Create a Virtual Environment
It is strongly recommended to isolate dependencies inside a virtual environment:

**Windows (PowerShell):**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

*Note:* If PowerShell gives an execution policy error on script activation, run:
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

**macOS / Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Step C: Install Dependencies
Install all required libraries specified in [`requirements.txt`](../requirements.txt):
```powershell
pip install --upgrade pip
pip install -r requirements.txt
```

Verify installed packages:
```powershell
streamlit --version
python -c "import pandas, numpy, matplotlib, openpyxl; print('All core libraries verified!')"
```

---

## 3. Launching the Web Application

The interactive web user interface is built on **Streamlit**.

### Start the Streamlit Server:
From the root directory, run:
```powershell
streamlit run app/main.py
```

### Accessing the Dashboard:
Once initialized, Streamlit will display local and network URLs:
```text
  Local URL: http://localhost:8501
  Network URL: http://192.168.x.x:8501
```
Open **`http://localhost:8501`** in your browser.

---

## 4. End-to-End Application Walkthrough

The web dashboard is organized into 3 sequential sections:

### 1. Upload Your Dataset
- **Supported Formats:** `.csv` and `.xlsx` (Excel)
- **Included Sample Data:**
  - `data/test_sales.csv`: Categorical & numeric metrics (Products, Category, Sales, Quantity)
  - `data/trend_sales.csv`: Time-series sales data (Date, Sales, Quantity)
- **Automated Dataset Understanding:**
  Upon upload, the data loader automatically analyzes:
  - Dataset dimensions (rows & columns)
  - Column data type classification (numerical vs. categorical vs. datetime)
  - Missing values & duplicate row checks
  - Statistical summary statistics table
  - Full preview table with interactive sorting

### 2. Ask a Question (Natural Language Processing)
Type any analytical question about your uploaded dataset into the question input field and click **Analyze**:

#### Example Queries:
- **Aggregation:** *"What is the total Sales?"*
- **Grouped Aggregation:** *"What is the average Sales by Category?"*
- **Distribution:** *"Show the distribution of Quantity"*
- **Correlation / Relationship:** *"What is the relationship between Sales and Quantity?"*
- **Time Trend:** *"Sales trend over Date"*
- **Filtering:** *"What is the total Sales for East?"*

#### The Agent Execution Cycle:
1. **NLU Parser:** Extracts user intent, target metric, grouping column, operations, and filters.
2. **Analysis Planner:** Formulates a structured analysis plan validated by `PlanValidator`.
3. **Deterministic Code Generator:** Generates safe, executable Pandas Python code.
4. **Code Validator:** AST-validates Python syntax before execution to prevent execution errors.
5. **Sandboxed Executor:** Runs generated code against the dataset DataFrame.
6. **Self-Healing Recovery:** If an execution anomaly occurs (e.g. invalid column name), the agent automatically diagnoses available columns and attempts error recovery.
7. **Business Insight & Interpretation:** Generates natural language insights explaining findings.
8. **Automated Visualization:** Automatically renders relevant charts (Bar charts for comparisons, line charts for trends, histograms for distributions, scatter plots for relationships).

### 3. Multi-Turn Conversation Memory & Context Follow-Ups
The agent maintains context across questions:
- **Turn 1:** *"What is the total Sales?"* ➔ Result: `$125,000`
- **Turn 2:** *"What about Quantity?"* ➔ Agent detects conversational follow-up, automatically resolves question to *"What is the total Quantity?"*, and produces `82`.
- **Clear Conversation:** Click the **"Clear Conversation"** button anytime to reset memory state.

---

## 5. Running Automated Unit Tests

The repository contains 45 automated unit tests with 100% pass coverage.

### Run All Unit Tests:
```powershell
python -m unittest discover -s tests
```

### Run Tests for Specific Components:
```powershell
# Natural language understanding & entity extraction
python -m unittest tests/test_nlu.py

# Analysis planner & plan validation
python -m unittest tests/test_planner.py

# Conversation memory & context resolution
python -m unittest tests/test_memory.py
python -m unittest tests/test_context_resolver.py
python -m unittest tests/test_followup_detector.py

# Agent state lifecycle & self-healing recovery
python -m unittest tests/test_agent_state.py
python -m unittest tests/test_agent_recovery.py
```

### Run Standalone Script Tests:
```powershell
# Code generator verification
python test_code_generator.py

# AST validator test
python test_code_validator.py

# Code generation pipeline test
python test_code_pipeline.py
```

---

## 6. Project Architecture Overview

```text
├── app/
│   ├── main.py                     # Streamlit frontend & orchestrator
│   ├── config.py                   # App styling and configurations
│   ├── agents/
│   │   ├── agent.py                # AnalysisAgent orchestrator
│   │   ├── agent_state.py          # State tracking & error lifecycle
│   │   ├── planner.py              # Translates NLU into AnalysisPlan
│   │   ├── plan_validator.py       # Validates analytical feasibility
│   │   ├── code_generator.py       # Converts plan to executable Pandas code
│   │   ├── code_validator.py       # AST syntax safety validator
│   │   ├── code_pipeline.py        # Code generation & verification pipeline
│   │   └── interpreter.py          # Formulates human business insights
│   ├── analysis/
│   │   └── executor.py             # Sandboxed Python code executor
│   ├── data/
│   │   ├── loader.py               # CSV & XLSX ingestion engine
│   │   ├── understanding.py        # Dataset profiler entry point
│   │   ├── profiler.py             # Dimensions, nulls, duplicates
│   │   ├── numerical.py            # Summary stats for numerical columns
│   │   ├── categorical.py          # Value counts & cardinality
│   │   ├── quality.py              # Data health & completeness score
│   │   └── classifier.py           # Column type classification
│   ├── memory/
│   │   ├── conversation_memory.py  # Session memory store
│   │   ├── conversation_context.py # Context coordinator
│   │   ├── context_resolver.py     # Follow-up query reconstructor
│   │   └── followup_detector.py    # Pattern matching for follow-ups
│   ├── nlu/
│   │   ├── question_parser.py      # Entry point for NLU parsing
│   │   ├── intent_detector.py      # Intent classifier
│   │   ├── entity_extractor.py     # Metrics, groups, & filter extractor
│   │   └── nlu_validator.py        # NLU output structure validation
│   └── visualization/
│       └── visualizer.py           # Matplotlib / Altair chart generator
├── data/                           # Verified sample datasets
├── outputs/                        # Test logs, execution records & charts
├── tests/                          # 45 Unit test cases
└── requirements.txt                # Python package dependencies
```

---

## 7. Troubleshooting & Common Questions

### Q1: `streamlit: command not found`
Ensure your virtual environment is activated (`.\.venv\Scripts\Activate.ps1` or `source .venv/bin/activate`). Alternatively run:
```powershell
python -m streamlit run app/main.py
```

### Q2: Port 8501 is already in use
Specify an alternate port:
```powershell
streamlit run app/main.py --server.port 8502
```

### Q3: How do I test with my own dataset?
Simply launch the Streamlit app and upload any `.csv` or `.xlsx` file using the file uploader. The agent will dynamically profile and classify all columns automatically.

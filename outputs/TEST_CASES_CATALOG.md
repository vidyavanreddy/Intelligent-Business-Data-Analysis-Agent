# Test Cases & Test Suite Catalog

This catalog outlines all verified test suites and standalone verification scripts for the **Intelligent Business Data Analysis Agent**.

---

## 1. Unit Test Suite Summary

- **Total Test Cases Executed:** 45
- **Passing:** 45 (100%)
- **Failing / Errors:** 0
- **Runner Command:** `python -m unittest discover -s tests`
- **Output Artifact:** [`outputs/unit_test_results.txt`](./unit_test_results.txt)

---

## 2. Test Suites by Module

### A. NLU & Intent Detection (`tests/test_nlu.py`)
Tests natural language parsing, question tokenization, intent detection, and entity extraction.
| Test Name | Question Input | Expected Intent / Entities | Status |
|:---|:---|:---|:---:|
| `test_aggregation_sum` | *"What is total Sales?"* | `intent: aggregation`, `metric: Sales`, `operation: sum` | Passed |
| `test_aggregation_mean` | *"What is the average Sales?"* | `intent: aggregation`, `metric: Sales`, `operation: mean` | Passed |
| `test_grouped_aggregation` | *"What is total Sales by Region?"* | `intent: aggregation`, `metric: Sales`, `group_by: Region` | Passed |
| `test_trend_intent` | *"Show trend of Sales over Date"* | `intent: trend`, `metric: Sales`, `time: Date` | Passed |
| `test_distribution_intent` | *"Show distribution of Quantity"* | `intent: distribution`, `metric: Quantity` | Passed |
| `test_relationship_intent` | *"What is the relationship between Sales and Profit?"* | `intent: relationship`, columns: `[Sales, Profit]` | Passed |
| `test_filter_extraction` | *"What is the total Sales for East?"* | `filters: {'column': 'Region', 'value': 'East'}` | Passed |
| `test_unsupported_question` | Non-analytical or out-of-scope query | Handled gracefully without crash | Passed |

---

### B. Analysis Planner & Plan Validator (`tests/test_planner.py`)
Validates translation of NLU intents into structured, executable analysis plans.
| Test Name | Plan Objective | Target Column | Group By / Ops | Status |
|:---|:---|:---|:---|:---:|
| `test_aggregation_plan` | Simple scalar aggregation | `Sales` | `operation: sum` | Passed |
| `test_grouped_plan` | Group-level aggregation | `Sales` | `group_by: Region`, `mean` | Passed |
| `test_trend_plan` | Temporal trend plan | `Sales` | `time: Date` | Passed |
| `test_distribution_plan` | Distribution analysis | `Sales` | `operation: None` | Passed |
| `test_relationship_plan` | Correlation matrix plan | `Sales` | `group_by: Profit` | Passed |
| `test_invalid_plan` | Incomplete or conflicting parameters | Handled with `is_valid: False` | - | Passed |

---

### C. Follow-up Detection (`tests/test_followup_detector.py`)
Determines if an incoming user prompt is an elliptical follow-up referencing prior conversation context.
| Test Input | Previous Question | Follow-up Detected? | Status |
|:---|:---|:---:|:---:|
| *"What about Quantity?"* | *"What is total Sales?"* | True | Passed |
| *"How about Profit?"* | *"What is total Sales?"* | True | Passed |
| *"And Quantity?"* | *"What is total Sales?"* | True | Passed |
| *"Also Profit?"* | *"What is total Sales?"* | True | Passed |
| *"WHAT ABOUT QUANTITY?"* | *"What is total Sales?"* | True (Case-insensitive) | Passed |
| *"Show the distribution of Quantity."* | *"What is total Sales?"* | False (Self-contained) | Passed |
| *"What about Quantity?"* | `None` (No prior context) | False | Passed |
| *""* (Empty string) | *"What is total Sales?"* | False | Passed |

---

### D. Context Resolution (`tests/test_context_resolver.py` & `tests/test_conversation_context.py`)
Reconstructs fully-qualified analytical questions from conversational follow-ups.
| Follow-up Input | Prior Conversation Context | Resolved Question Output | Status |
|:---|:---|:---|:---:|
| *"What about Quantity?"* | *"What is the total Sales?"* | *"What is the total Quantity?"* | Passed |
| *"What about Category?"* | *"What is average Sales by Region?"* | *"What is average Sales by Category?"* | Passed |
| *"What about Profit?"* | *"What is average Sales by Region?"* | *"What is average Profit by Region?"* | Passed |
| Independent Question | Any prior question | Preserved unchanged | Passed |

---

### E. Conversation Memory (`tests/test_memory.py`)
Maintains rolling multi-turn query history, execution results, and interpretations.
| Test Case | Capability Verified | Status |
|:---|:---|:---:|
| `test_add_and_retrieve` | Appending question, result, and interpretation to session memory | Passed |
| `test_get_last_question` | Retrieving the most recent question for follow-up detection | Passed |
| `test_clear_memory` | Resetting conversation memory state upon user command | Passed |
| `test_history_immutability` | Ensuring get_history returns clean copies | Passed |

---

### F. Agent State & Self-Healing Recovery (`tests/test_agent_state.py` & `tests/test_agent_recovery.py`)
Monitors agent lifecycle and recovers from execution anomalies.
| Test Case | Scenario | Expected Behavior | Status |
|:---|:---|:---|:---:|
| `test_error_type_initially_none` | State initialization | Error fields are cleanly `None` | Passed |
| `test_specific_error_type` | Runtime error categorization | `error_type` & `specific_error_type` correctly recorded | Passed |
| `test_missing_result_recovery` | Code executed but `result` variable was not populated | Triggers recovery handler with user-friendly diagnosis | Passed |
| `test_key_error_recovery` | Code accessed non-existent column | Surfaces available columns to assist the user | Passed |
| `test_recovery_flag` | Recovery pipeline invoked | `recovery_attempted` is set to `True` | Passed |

---

### G. Code Generation & Validation (`test_code_*.py`)
Tests automated generation of Pandas code and AST syntax validation.
| Test Script | Tested Functionality | Sample Output | Status |
|:---|:---|:---|:---:|
| `test_code_generator.py` | Generates summary, distribution, aggregation, correlation, and filtering code | `result = df["Sales"].sum()` | Passed |
| `test_code_validator.py` | AST validation to prevent code injection and syntax errors | Valid: `True`, Invalid: `False` | Passed |
| `test_code_pipeline.py` | End-to-end plan-to-code generation and verification | `result = df.groupby("Region")["Sales"].sum()` | Passed |

---

## 3. How to Run the Tests

```powershell
# Run the complete test suite
python -m unittest discover -s tests

# Run a specific test suite
python -m unittest tests/test_nlu.py
python -m unittest tests/test_planner.py
python -m unittest tests/test_memory.py

# Run standalone verification scripts
python test_code_generator.py
python test_code_validator.py
python test_code_pipeline.py
```

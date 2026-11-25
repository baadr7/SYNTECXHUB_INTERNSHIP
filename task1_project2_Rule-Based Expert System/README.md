# Rule-Based Expert System

A transparent, rule-based **expert system** built for the Syntecxhub AI internship
(Project 2). It implements a small if-then rule engine over a facts base and infers
conclusions using **forward chaining**, including **multi-step inference**. Every
inference step is logged so the user can follow the complete reasoning path.

## Features

- **Rule engine** with `IF <antecedents> THEN <consequent>` production rules.
- **Facts base** (working memory) with normalisation, deduplication and immutability.
- **Forward chaining** that iterates until saturation, so a derived fact can trigger
  further rules (chained inference).
- **Full audit trail**: each activation records the cycle, rule id, satisfied
  antecedents, derived fact and the rule's rationale.
- **Explainability**: per-conclusion justification trees ("why is this true?").
- **Loop-safe & deterministic**: every rule fires at most once; identical inputs
  always yield identical outputs.
- **External knowledge base** in JSON, editable without touching the code.
- **Three CLI modes**: interactive, direct (`--facts`), and inspection (`--list`).
- **Zero third-party dependencies** - standard library only.

## Project Structure

```
task1_project2_Rule-Based Expert System/
├── README.md
├── requirements.txt
├── knowledge_base.json        # Rules, symptoms and diagnoses (data)
├── main.py                    # Command-line entry point
├── expert_system/
│   ├── __init__.py            # Public API
│   ├── fact_base.py           # Working memory of known facts
│   ├── rule.py                # If-then production rule model
│   ├── knowledge_loader.py    # Loads & validates knowledge_base.json
│   ├── engine.py              # Forward-chaining inference engine
│   ├── explanation.py         # Reasoning-path / justification builder
│   └── display.py             # Console rendering (banners, tables, colours)
└── tests/
    ├── __init__.py
    ├── test_fact_base.py
    ├── test_rule.py
    └── test_engine.py
```

## Requirements

- Python **3.10+**
- No external packages.

## Installation

```bash
git clone https://github.com/baadr7/SYNTECXHUB_INTERNSHIP.git
cd "SYNTECXHUB_INTERNSHIP/task1_project2_Rule-Based Expert System"
```

## Usage

### 1. Interactive mode (choose symptoms by number or name)

```bash
python main.py
```

### 2. Direct mode (assert facts on the command line)

```bash
python main.py --facts fever cough "muscle aches" headache
```

Facts may be given as names or as 1-based indices, comma- or space-separated:

```bash
python main.py --facts "1,2,9,3"
```

### 3. Inspection mode (list symptoms and all rules)

```bash
python main.py --list
```

Add `--no-color` to force plain-text output (useful when redirecting to a file).

## Example

```bash
python main.py --facts sneezing "runny nose" "sore throat" fever headache
```

The engine chains several rules. A representative trace:

```
[1] R02: sneezing AND runny nose AND sore throat -> upper respiratory infection
[1] R07: upper respiratory infection AND fever -> viral infection
[1] R08: upper respiratory infection AND headache -> viral infection
```

## Running the Tests

```bash
python -m unittest discover -s tests -v
```

## How Forward Chaining Works

1. Assert the user's initial facts into the working memory.
2. Scan the rule set in declaration order. Any rule whose antecedents are **all**
   present fires: its consequent is added to memory.
3. Repeat from step 2 until **no rule fires** - this is saturation. Because a new
   fact may enable other rules, inference proceeds in multiple **chained** steps.
4. Each activation is appended to an ordered trail, then rendered as a readable
   reasoning path and justification trees.

A rule fires at most once per run, which makes the engine both **loop-safe** and
**deterministic**.

## Extending the Knowledge Base

Add a new rule to `knowledge_base.json`:

```json
{
  "id": "R16",
  "if": ["fever", "rash"],
  "then": "suspected infection",
  "description": "Fever with rash suggests an infectious process."
}
```

No code change is required; `KnowledgeBase.load()` validates the file on startup.

## License

This project is released for educational purposes as part of the Syntecxhub
internship program.
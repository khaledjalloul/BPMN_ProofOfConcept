# Proof of Concept: BPMN Alternative Evaluation

This is a proof of concept for a study by Mr. Charbel Kadi titled "Addressing Business Process Deviations Through Evaluation Of Alternative Pattern-Based Models".

## How to Run

(Optional) Create a virtual environment:

```bash
pip install virtualenv
virtualenv venv
. env/Scripts/activate
```

Install Python3 packages:

```
pip install -r requirements.txt
```

Generate new alternative tasks for the search algorithm, or skip this step and use the existing generated alternatives:

```
python3 src/generator.py
```

Run the main script:

```
python3 src/main.py
```

---
## Replacing the BPMN Model in the code:

1. Place your BPMN model in XML format in the *models* folder.
2. In *main.py*, in the *test_process()* function, replace the current loaded file with "models/<your_file_name.xml>"


from random import randint, choice
from pprint import pprint
import json

constraints = {
    "weight": [0, 40],
    "cost": [80, 200],
    "num_provisions": [30, 50],
}

constraint_names = []
for constraint in constraints:
    constraint_names.append(constraint)
    
alternatives = {}

for i in range(1000):
    name = f"Process{i+1}"
    
    num_inputs = randint(1, len(constraint_names))
    input_constraints = {}
    for input_index in range(num_inputs):
        selected_constraint = choice(constraint_names)
        while selected_constraint in input_constraints:
            selected_constraint = choice(constraint_names)
        input_constraints[selected_constraint] = constraints[selected_constraint]
        
    num_outputs = randint(1, len(constraint_names))
    output_constraints = {}
    for output_index in range(num_outputs):
        selected_constraint = choice(constraint_names)
        while selected_constraint in output_constraints:
            selected_constraint = choice(constraint_names)
        output_constraints[selected_constraint] = int((constraints[selected_constraint][0] + constraints[selected_constraint][1]) / 2)
        
    result = {}
    result["enter"] = input_constraints
    result["exit"] = output_constraints
    
    alreadyExists = False
    for existing_alternative in alternatives:
        if result == alternatives[existing_alternative]:
            alreadyExists = True
            break
    if not alreadyExists:
        alternatives[name] = result

pprint(alternatives)

with open("data/generated_alternatives.json", "w") as file:
    json.dump(alternatives, file)        
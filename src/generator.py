from random import randint, choice
import json

# All possible constraints, a combination of which will be generated
constraints = {
    "weight": [0, 40],
    "cost": [131, 149],
    "num_provisions": [30, 50],
    "quality": [60, 80],
    "temperature": [20, 30],
    "humidity": [0, 10],
    "strength": [20, 30],
    "pest_control": [0, 5],
    "pollination_intensity": [1, 10],
    "labour_intensity": [1, 5],
    "product_yield": [100, 500],
    "hive_population": [1000, 5000],
    "bee_health": [1, 5],
    "honey_production": [10, 100],
    "wax_production": [5, 50]
}

constraint_names = []
for constraint in constraints:
    constraint_names.append(constraint)
    
alternatives = {}

for i in range(10000):
    name = f"Process{i+1}"
    
    # Choose a random number N then select N random input constraints
    num_inputs = randint(1, len(constraint_names))
    input_constraints = {}
    for input_index in range(num_inputs):
        selected_constraint = choice(constraint_names)
        while selected_constraint in input_constraints:
            selected_constraint = choice(constraint_names)
        input_constraints[selected_constraint] = constraints[selected_constraint]
        
    # Choose a random number N then select N random exit constraints    
    num_outputs = randint(1, len(constraint_names))
    output_constraints = {}
    for output_index in range(num_outputs):
        selected_constraint = choice(constraint_names)
        while selected_constraint in output_constraints:
            selected_constraint = choice(constraint_names)
        output_constraints[selected_constraint] = constraints[selected_constraint]
        
    result = {}
    result["input"] = input_constraints
    result["output"] = output_constraints
    
    # Remove if duplicate exists
    alreadyExists = False
    for existing_alternative in alternatives:
        if result == alternatives[existing_alternative]:
            alreadyExists = True
            break
    if not alreadyExists:
        alternatives[name] = result

print(f"Generated {len(alternatives)} alternatives.")

with open("data/generated_alternatives.json", "w") as file:
    json.dump(alternatives, file)        
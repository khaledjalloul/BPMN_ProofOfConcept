import json
from pybpmn.bpmn_process import BpmnProcess
from copy import copy
from interface import displayInterface
import time

ALTERNATIVES_IN_BATCHES = False

loading_start_time = time.time()
loading_end_time = loading_start_time
alternatives = None
deviation_found = False
    
with open('data/constraints.json') as f:
    constraints = json.load(f)

# Inputs: name of the current task, constraint position (input or exit), current token state
# No Ouputs: Calls the searchForAlternatives function
# Checks whether constraints of a given task are valid based on the current token state
# and searches for future alternative tasks if exit constraints were violated
def checkConstraints(name, position, kargs):
    global deviation_found
    
    if deviation_found:
        return
    
    token_state = kargs['payload']['token_state']
    if position in constraints[name]:
        task_constraints = constraints[name][position]
        for constraint in task_constraints:
            if token_state[constraint] < task_constraints[constraint][0] or token_state[constraint] > task_constraints[constraint][1]:
                if position == "exit":
                    deviation_found = True
                    searchForAlternatives(name, kargs, constraints[name]["index"], constraint)
    
# Inputs: name of the current task, current token state, index/ID of task, name of the violated constraint
# No Outputs: Stores results in the shared "payload"
# Searches for a task to serve as an alternative to the one that cannot handle the deviation
# An alternative task can replace one or more tasks of the original process, as long as its input constraints are respected
# and its expected output values respect the entry constraints of the next task in the original process
def searchForAlternatives(name, kargs, index, constraint_name):
    global alternatives, loading_end_time
    
    # Loading alternative from the file for the first time
    if alternatives is None:
        if ALTERNATIVES_IN_BATCHES:
            with open('data/generated_alternatives.json') as f:
                alternatives_arr = json.load(f)
            alternatives = {}
            for alternatives_batch in alternatives_arr:
                alternatives.update(alternatives_batch)
        else:
            with open('data/generated_alternatives.json') as f:
                alternatives = json.load(f)
        loading_end_time = time.time()

    token_state = kargs['payload']['token_state']

    # Iterate over all alternative tasks to find those whose input constraints best fit the current values of the token state
    start_time = time.time()
    filteredProcesses1 = []
    for alternative in alternatives:
        enter_constraints = alternatives[alternative]["enter"]
        total_enter_constraints = len(enter_constraints)
        num_invalid_enter_constraints = 0
        
        # For each alternative task, iterate over entry constraints and count the number of constraints
        # that would be violated if this task was used following the current one
        for constraint in enter_constraints:
            if constraint not in token_state or token_state[constraint] > enter_constraints[constraint][1] or token_state[constraint] < enter_constraints[constraint][0]:
                num_invalid_enter_constraints += 1
        filteredProcesses1.append({
            "name": alternative,
            "num_invalid_enter_constraints": num_invalid_enter_constraints,
            "total_enter_constraints": total_enter_constraints
        })
    filter1_end_time = time.time()
    filter1_elapsed_time = filter1_end_time - start_time
    
    # Iterate again over all alternative tasks to find those whose output values would best fit the remaining tasks
    filteredProcesses2 = []
    for alternative in filteredProcesses1:
        exit_values = alternatives[alternative["name"]]["exit"]
        
        # Find all remaining processes: processes that follow the current one (based on their index) and that have entry constraints that can be checked 
        remaining_processes = dict(filter(lambda x: x[1]["index"] > index, constraints.items()))
        remaining_processes = dict(filter(lambda x: "enter" in x[1], remaining_processes.items()))
        total_exit_constraints = len(exit_values)
        
        # For each remaining process, evaluate its input constraints in comparison with the expected outputs of the current alternative
        for process in remaining_processes:
            enter_constraints = remaining_processes[process]["enter"]
            num_invalid_exit_constraints = 0
            for value in exit_values:
                if value not in enter_constraints or exit_values[value][0] < enter_constraints[value][0] or exit_values[value][1] > enter_constraints[value][1]:
                    num_invalid_exit_constraints += 1      
            filteredProcesses2.append({
                "solution": alternative["name"],
                "next_process": process,
                "next_process_index": remaining_processes[process]['index'],
                "constraint": constraint_name,
                "validity_percentage": 100.0 - ((alternative["num_invalid_enter_constraints"] + num_invalid_exit_constraints) / (alternative["total_enter_constraints"] + total_exit_constraints) * 100.0)
            })
    
    filter2_end_time = time.time()
    filter2_elapsed_time = filter2_end_time - filter1_end_time
    
    classified_alternatives = {}
    
    # Classify the alternatives after their evaluation in 10 classes of increasing percentage validity
    for c in range(0, 101, 10):
        classified_alternatives.update({c: len(list(filter(lambda x: x['validity_percentage'] <= c and x['validity_percentage'] > c - 10, filteredProcesses2)))})
    
    kargs['payload']['deviations'].update({name: {
        "stats": {
            "firstSet": {
                "count": len(filteredProcesses1),
                "time": filter1_elapsed_time
            },
            "secondSet": {
                "count": len(filteredProcesses2),
                "time": filter2_elapsed_time
            }
        },
        "alternatives": copy(filteredProcesses2),
        "classified_alternatives": classified_alternatives,
        "constraint": constraint_name
    }})
           
# Class the interfaces with the BPMN model to read its tasks and handle the common token state         
class Handler():        
    # Triggers on the entry of any task. Initializes or updates the token state with the current values on entry
    def on_enter_task(self, **kargs):
        if 'token_state' in kargs['payload']:
            kargs['task'].update({'enter_state': copy(kargs['payload']['token_state'])})
        else:
            kargs['task'].update({'enter_state': {}})
        
    # Triggers on the exit of any task. Updates the token state with the current values on exit
    def on_exit_task(self, **kargs):
        kargs['task'].update({'exit_state': copy(kargs['payload']['token_state'])})
        
    def on_CheckDate(self, **kargs):
        kargs['payload']['token_state'] = {}
        kargs['payload']['deviations'] = {}
        kargs['payload']['token_state']['date'] = 20230701
        kargs['payload']['token_state']['temperature'] = 18
        kargs['payload']['token_state']['weather'] = 'Sunny' 
        kargs['payload']['token_state']['cost'] = 100 
 
    # Triggers during the execution of the specific task called "CheckProvisions"
    # For this tasks, check if the entry and exit constraints of the task are respected
    def on_CheckProvisions(self, **kargs):
        checkConstraints("CheckProvisions", "enter", kargs)
        kargs['payload']['token_state']['num_provisions'] = 20
        kargs['payload']['token_state']['weight'] = 10
        kargs['payload']['token_state']['cost'] += 40
        checkConstraints("CheckProvisions", "exit", kargs)

    def on_LiquidProteinsFeeding(self, **kargs):
        while kargs['payload']['token_state']['weight'] < 25:
            kargs['payload']['token_state']['weight'] += 1
            kargs['payload']['token_state']['cost'] += 2
            kargs['payload']['token_state']['date'] +=1
        checkConstraints("LiquidProteinsFeeding", "exit", kargs)
        
    def on_VarioseVaccineNovember(self, **kargs):
        checkConstraints("VarioseVaccineNovember", "enter", kargs)
        kargs['payload']['token_state']['weight'] -= 5
        kargs['payload']['token_state']['cost'] += 100
        kargs['payload']['token_state']['date'] += 100
        
# Load the BPMN model, run it, and display a report with the results
def test_process():
    instance = BpmnProcess()
    instance.start_process(open("models/simple_bee.xml","r").read(),Handler())
    displayInterface(instance.payload, constraints, alternatives, loading_end_time - loading_start_time)
    
if __name__ == '__main__':
    test_process()
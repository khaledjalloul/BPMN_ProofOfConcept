import json
from pybpmn.bpmn_process import BpmnProcess
from pprint import pprint
from copy import copy
from interface import displayInterface
import time

with open('data/constraints.json') as f:
    constraints = json.load(f)
    
with open('data/generated_alternatives.json') as f:
    alternatives = json.load(f)
    
def handleDeviation(kargs, variable, value, expected_range, correct_value, stage):
    kargs['payload']['token_state'][variable] = correct_value
    kargs['task'].update({f"error_{stage}": {variable: value}}) # Save wrong value in error
    kargs['task'].update({f'{stage}_state': copy(kargs['payload']['token_state'])}) # Save correct value in payload
    
def checkConstraints(name, position, kargs):
    token_state = kargs['payload']['token_state']
    if position in constraints[name]:
        task_constraints = constraints[name][position]
        for constraint in task_constraints:
            if not (token_state[constraint] >= task_constraints[constraint][0] and token_state[constraint] <= task_constraints[constraint][1]):
                if position == "exit":
                    searchForAlternatives(kargs, constraints[name]["index"])
    
def searchForAlternatives(kargs, index):
    token_state = kargs['payload']['token_state']
    
    start_time = time.time()
    filteredProcesses1 = []
    for alternative in alternatives:
        enter_constraints = alternatives[alternative]["enter"]
        isValidEnter = True
        for constraint in enter_constraints:
            if constraint not in token_state or token_state[constraint] > enter_constraints[constraint][1] or token_state[constraint] < enter_constraints[constraint][0]:
                isValidEnter = False
                break
        if isValidEnter:
            filteredProcesses1.append(alternative)
    filter1_end_time = time.time()
    filter1_elapsed_time = filter1_end_time - start_time
    print(f"Possible Solutions (1): (Elapsed time: {filter1_elapsed_time} seconds)")
    pprint(filteredProcesses1)
    
    filteredProcesses2 = []
    for alternative in filteredProcesses1:
        exit_values = alternatives[alternative]["exit"]
        remaining_processes = dict(filter(lambda x: x[1]["index"] > index, constraints.items()))
        remaining_processes = dict(filter(lambda x: "enter" in x[1], remaining_processes.items()))
        for process in remaining_processes:
            isValidExit = True
            enter_constraints = remaining_processes[process]["enter"]
            for value in exit_values:
                if value not in enter_constraints or exit_values[value] > enter_constraints[value][1] or exit_values[value] < enter_constraints[value][0]:
                    isValidExit = False
                    break         
            if (isValidExit):
                filteredProcesses2.append({
                    "solution": alternative,
                    "nextProcess": process
                })
    filter2_end_time = time.time()
    filter2_elapsed_time = filter2_end_time - filter1_end_time
    print(f"Possible Solutions (2): (Elapsed time: {filter2_elapsed_time} seconds)")
    pprint(filteredProcesses2)

                    
class Handler():        
    def on_enter_task(self, **kargs):
        if 'token_state' in kargs['payload']:
            kargs['task'].update({'enter_state': copy(kargs['payload']['token_state'])})
        else:
            kargs['task'].update({'enter_state': {}})
        
    def on_exit_task(self, **kargs):
        kargs['task'].update({'exit_state': copy(kargs['payload']['token_state'])})
        
    def on_CheckDate(self, **kargs):
        kargs['payload']['token_state'] = {}
        kargs['payload']['errors'] = []
        kargs['payload']['token_state']['date'] = 20230701
        kargs['payload']['token_state']['temperature'] = 26
        kargs['payload']['token_state']['weather'] = 'Sunny' 
        kargs['payload']['token_state']['cost'] = 100 
 
    def on_CheckProvisions(self, **kargs):
        checkConstraints("CheckProvisions", "enter", kargs)
        kargs['payload']['token_state']['num_provisions'] = 40
        kargs['payload']['token_state']['weight'] = 10
        kargs['payload']['token_state']['cost'] += 40

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
        
def test_process():
    instance = BpmnProcess()
    instance.start_process(open("models/simple_bee.xml","r").read(),Handler())
    state, errors = instance.payload['token_state'], instance.payload['errors']
    if len(errors) == 0:
        print("\nProcess Executed. Final State:\n")
        pprint(instance.payload['token_state'])
    else:
        print("\nProcess encountered errors:\n")
        pprint(errors)
        pprint(instance.payload)
    # displayInterface(instance.payload)

if __name__ == '__main__':
    test_process()
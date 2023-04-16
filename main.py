import time
from pybpmn.bpmn_process import BpmnProcess
from pprint import pprint
from copy import copy
from interface import displayInterface

constraints = {
    "CheckProvisions_enter": {
        "date": [20230715, 20230730]
    },
    "LiquidProteinsFeeding_enter": {
        "cost": [110, 120]
    },
    "LiquidProteinsFeeding_exit": {
        "weight": [35, 50]
    }
}

def checkConstraints(name, position, kargs):
    token_state = kargs['payload']['token_state']
    if f"{name}_{position}" in constraints:
        task_constraints = constraints[f"{name}_{position}"]
        for constraint in task_constraints:
            if not (token_state[constraint] >= task_constraints[constraint][0] and token_state[constraint] <= task_constraints[constraint][1]):
                handleDeviation(kargs=kargs, variable=constraint, value=token_state[constraint], expected_range=f"{task_constraints[constraint][0]} - {task_constraints[constraint][1]}", correct_value = int((task_constraints[constraint][1] + task_constraints[constraint][0]) / 2), stage=position)
    
def handleDeviation(kargs, variable, value, expected_range, correct_value, stage):
    kargs['payload']['token_state'][variable] = correct_value
    kargs['task'].update({f"error_{stage}": {variable: value}}) # Save wrong value in error
    kargs['task'].update({f'{stage}_state': copy(kargs['payload']['token_state'])}) # Save correct value in payload
    
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
        checkConstraints("LiquidProteinsFeeding", "enter", kargs)
        while kargs['payload']['token_state']['weight'] < 25:
            kargs['payload']['token_state']['weight'] += 1
            kargs['payload']['token_state']['cost'] += 2
            kargs['payload']['token_state']['date'] +=1
        checkConstraints("LiquidProteinsFeeding", "exit", kargs)
        
    def on_VarioseVaccineNovember(self, **kargs):
        kargs['payload']['token_state']['weight'] -= 5
        kargs['payload']['token_state']['cost'] += 100
        kargs['payload']['token_state']['date'] += 100
        
def test_process():
    instance = BpmnProcess()
    try:
        instance.start_process(open("simple_bee.xml","r").read(),Handler())
        state, errors = instance.payload['token_state'], instance.payload['errors']
        if len(errors) == 0:
            print("\nProcess Executed. Final State:\n")
            pprint(instance.payload['token_state'])
        else:
            print("\nProcess encountered errors:\n")
            pprint(errors)
            pprint(instance.payload)
        displayInterface(instance.payload)
    except Exception as e:
        print(e)

    
if __name__ == '__main__':
    test_process()
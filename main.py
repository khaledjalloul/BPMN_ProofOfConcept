import time
from pybpmn.bpmn_process import BpmnProcess
from pprint import pprint
from copy import copy
from interface import displayInterface

def handleDeviation(kargs, variable, value, expected_value, stage='enter'):
    kargs['payload']['token_state'][variable] = expected_value
    kargs['task'].update({'error': {variable: value}}) # Save wrong value in error
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
        
    def on_exit_CheckDate(self, **kargs):
        date = kargs['payload']['token_state']['date']
        if kargs['payload']['token_state']['date'] < 20230715:
            handleDeviation(kargs=kargs, variable='date', value=date, expected_value=20230715)

    def on_HoneyCollection(self, **kargs):
        kargs['payload']['token_state']['cost'] += 50  
    
    def on_RoutineCheckUntilAugust(self, **kargs):
        kargs['payload']['token_state']['colony_strength'] = 80
        kargs['payload']['token_state']['quality'] = 90
        kargs['payload']['token_state']['cost'] += 50  
        kargs['payload']['token_state']['date'] = 20230801
        
    def on_CheckWeightUntilAugust(self, **kargs):
        if not 'weight' in kargs['payload']['token_state']:
            kargs['payload']['token_state']['weight'] = 20
        
    def on_CheckProvisions(self, **kargs):
        kargs['payload']['token_state']['num_provisions'] = 20
        kargs['payload']['token_state']['cost'] += 20
        
    def on_LiquidProteinsFeeding(self, **kargs):
        while kargs['payload']['token_state']['weight'] < 25:
            kargs['payload']['token_state']['weight'] += 1
            kargs['payload']['token_state']['cost'] += 2
            kargs['payload']['token_state']['date'] +=1
        
    def on_enter_VarioseVaccineNovember(self, **kargs):
        weight = kargs['payload']['token_state']['weight']
        if (weight < 35):
            handleDeviation(kargs=kargs, variable='weight', value=weight, expected_value=35)
        
    def on_VarioseVaccineNovember(self, **kargs):

        kargs['payload']['token_state']['weight'] -= 5
        kargs['payload']['token_state']['cost'] += 100
        kargs['payload']['token_state']['date'] += 100
        kargs['payload']['token_state']['quality'] += 10
        
def test_process():
    instance = BpmnProcess()
    try:
        instance.start_process(open("bee.xml","r").read(),Handler())
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
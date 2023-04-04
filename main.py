import time
from pybpmn.bpmn_process import BpmnProcess
from pprint import pprint
from copy import copy
from interface import displayInterface

class Handler():
    def __init__(self, initial_params = {}):
        self.initial_params = initial_params
        
    def on_enter_task(self, **kargs):
        if 'vars' in kargs['payload']:
            kargs['task'].update({'enter_state': copy(kargs['payload']['vars'])})
        else:
            kargs['task'].update({'enter_state': {}})
        
    def on_exit_task(self, **kargs):
        kargs['task'].update({'exit_state': copy(kargs['payload']['vars'])})
        
    def on_CheckDate(self, **kargs):
        kargs['payload']['vars'] = {}
        for param in self.initial_params:
            kargs['payload']['vars'][param] = self.initial_params[param]
        kargs['payload']['vars']['date'] = 20230716
        kargs['payload']['vars']['temperature'] = 26
        kargs['payload']['vars']['weather'] = 'Sunny' 
        kargs['payload']['vars']['cost'] = 100  
        
    def on_exit_CheckDate(self, **kargs):  
        if kargs['payload']['vars']['date'] < 20230715:
            raise Exception('Date is less than July 15')
        
    def on_HoneyCollection(self, **kargs):
        kargs['payload']['vars']['cost'] += 50  
    
    def on_RoutineCheckUntilAugust(self, **kargs):
        kargs['payload']['vars']['colony_strength'] = 80
        kargs['payload']['vars']['quality'] = 90
        kargs['payload']['vars']['cost'] += 50  
        kargs['payload']['vars']['date'] = 20230801
        
    def on_CheckWeightUntilAugust(self, **kargs):
        if not 'weight' in kargs['payload']['vars']:
            kargs['payload']['vars']['weight'] = 20
        
    def on_CheckProvisions(self, **kargs):
        kargs['payload']['vars']['num_provisions'] = 20
        kargs['payload']['vars']['cost'] += 20
        
    def on_LiquidProteinsFeeding(self, **kargs):
        while kargs['payload']['vars']['weight'] < 35:
            kargs['payload']['vars']['weight'] += 1
            kargs['payload']['vars']['cost'] += 2
            kargs['payload']['vars']['date'] +=1
        
    def on_VarioseVaccineNovember(self, **kargs):
        weight = kargs['payload']['vars']['weight']
        if (weight < 35):
            raise Exception('Weight is less than 35', 'weight', 35)
        kargs['payload']['vars']['weight'] -= 5
        kargs['payload']['vars']['cost'] += 100
        kargs['payload']['vars']['date'] += 100
        kargs['payload']['vars']['quality'] += 10
        
def test_process():
    instance = BpmnProcess()
    try:
        instance.start_process(open("bee.xml","r").read(),Handler())
        print("\nProcess Executed. Final State:\n")
        pprint(instance.payload['vars'])
        displayInterface(instance.payload)
    except Exception as e:
        print("\nProcess Failed. " + str(e))
        print('Retrying...')
        time.sleep(1)
        try:
            instance.start_process(open("bee.xml","r").read(),Handler({'weight': 35}))
            print("\nProcess Executed. Final State:\n")
            pprint(instance.payload['vars'])
            displayInterface(instance.payload)
        except Exception as e2:
            print("Error. " + str(e2))

    
if __name__ == '__main__':
    test_process()
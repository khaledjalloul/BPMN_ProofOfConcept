import time
from copy import copy
from pybpmn.bpmn_process import BpmnProcess

from interface import display_interface
from search import check_constraints
from data_loader import load_constraints, load_alternatives

deviation_found = False
constraints = load_constraints()
loading_start_time = time.time()
alternatives, loading_end_time = load_alternatives(in_batches=False)


class Handler():
    """
    Class that interfaces with the BPMN model to read its tasks and handle the common token state.
    """

    def on_enter_task(self, **kargs):
        """
        Triggers on the entry of any task. Initializes or updates the token state with the current values on entry
        """
        if 'token_state' in kargs['payload']:
            kargs['task'].update(
                {'enter_state': copy(kargs['payload']['token_state'])})
        else:
            kargs['task'].update({'enter_state': {}})

    def on_exit_task(self, **kargs):
        """
        Triggers on the exit of any task. Updates the token state with the current values on exit
        """
        kargs['task'].update(
            {'exit_state': copy(kargs['payload']['token_state'])})

    def on_CheckDate(self, **kargs):
        kargs['payload']['token_state'] = {}
        kargs['payload']['deviations'] = {}
        kargs['payload']['token_state']['date'] = 20230610
        kargs['payload']['token_state']['weather'] = 'rainy'
        kargs['payload']['token_state']['weight'] = 10
        kargs['payload']['token_state']['num_provisions'] = 20
        kargs['payload']['token_state']['cost'] = 52

    def on_CheckProvisions(self, **kargs):
        """
        Triggers during the execution of the specific task called "CheckProvisions".
        For this tasks, check if the entry and exit constraints of the task are respected.
        """
        check_constraints("CheckProvisions", "input", kargs, deviation_found,
                          constraints, alternatives)
        kargs['payload']['token_state']['num_provisions'] = 20
        kargs['payload']['token_state']['weight'] = 10
        kargs['payload']['token_state']['cost'] += 40

    def on_LiquidProteinsFeeding(self, **kargs):
        while kargs['payload']['token_state']['weight'] < 25:
            kargs['payload']['token_state']['weight'] += 1
            kargs['payload']['token_state']['cost'] += 2
            kargs['payload']['token_state']['date'] += 1

    def on_VarioseVaccineNovember(self, **kargs):
        kargs['payload']['token_state']['weight'] -= 5
        kargs['payload']['token_state']['cost'] += 100
        kargs['payload']['token_state']['date'] += 100


if __name__ == '__main__':
    """
    Load the BPMN model, run it, and display a report with the results
    """
    instance = BpmnProcess()
    instance.start_process(
        open("models/simple_bee.xml", "r").read(), Handler())
    display_interface(instance.payload, constraints, alternatives,
                      loading_end_time - loading_start_time)

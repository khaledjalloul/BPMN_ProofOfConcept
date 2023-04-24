import tkinter as tk
import json
with open('data/constraints.json') as f:
    constraints = json.load(f)
    
deviations = {'LiquidProteinsFeeding': {'alternatives': [{'nextProcess': 'RoutineCheck',
                                             'nextProcessIndex': 5,
                                             'solution': 'Process648'},
                                            {'nextProcess': 'VarioseVaccineNovember',
                                             'nextProcessIndex': 4,
                                             'solution': 'Process902'},
                                            {'nextProcess': 'RoutineCheck',
                                             'nextProcessIndex': 5,
                                             'solution': 'Process902'}],
                           'stats': {'firstSet': {'count': 37, 'time': 0.0},
                                     'secondSet': {'count': 3, 'time': 0.0}}}}

def getMaxIndex(constraints):
    max = 0
    for task in constraints:
        if constraints[task]["index"] > max:
            max = constraints[task]["index"]
    return max

def displayInterface():
    root = tk.Tk()
    
    root.config(padx=20, pady=10)

    for index in range(getMaxIndex(constraints)):
        task_titles = [k for k, v in constraints.items() if v["index"] == index + 1]
        task_frame = tk.Frame(root)
        task_frame.grid(column=index * 2, row=0)
        task_frame.config(padx=20, pady=10)
        for index, task_title in enumerate(task_titles):
            task_label = tk.Label(task_frame, text=task_title)
            task_label.grid(column=0, row=index)
            task_label.config(pady=10)
    
    if len(deviations.items()) != 0:
        for index, deviation in enumerate(deviations):
            print(index)
            deviation_frame = tk.Frame(root)
            deviation_frame.grid(row=index + 1, columnspan=getMaxIndex(constraints))
            deviation_frame.config(pady = 10)
            encounter_label = tk.Label(deviation_frame, text=f"Encountered a deviation at task {deviation}:")
            encounter_label.grid(row=0, sticky='w')
            first_set_stats = deviations[deviation]['stats']['firstSet']
            stats1_label = tk.Label(deviation_frame, text=
                f"- Discovered {first_set_stats['count']} alternatives as a first set of solutions in {first_set_stats['time']} seconds.")
            stats1_label.grid(row=1, sticky='w')
            second_set_stats = deviations[deviation]['stats']['secondSet']
            stats2_label = tk.Label(deviation_frame, text=
                f"- Discovered {second_set_stats['count']} alternatives as a second set of solutions in {second_set_stats['time']} seconds.")
            stats2_label.grid(row=2, sticky='w')
            
            alternatives_label = tk.Label(deviation_frame, text="Alternatives:")
            alternatives_label.grid(row=3, sticky='w')
            alternatives_label.config(pady=10)
            
            alternatives = deviations[deviation]['alternatives']
            for alternative in alternatives:
                pass
            # alternatives_title = tk.Label(deviation_frame, text="Alternatives:")
            # alternatives_title.grid(row=3, sticky='w')
            # alternatives_title.config(pady=10)
            

        



    root.mainloop()
    
    
if __name__ == '__main__':
    displayInterface()
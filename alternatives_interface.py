import tkinter as tk
import json
with open('data/constraints.json') as f:
    constraints = json.load(f)

def getMaxIndex(constraints):
    max = 0
    for task in constraints:
        if constraints[task]["index"] > max:
            max = constraints[task]["index"]
    return max

def displayAlternativesInterface(deviations, len_alternatives):
    root = tk.Tk()
    root.config(padx=20, pady=10)
    root.geometry("900x600")

    canvas = tk.Canvas(root)
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    scrollbar = tk.Scrollbar(root, command=canvas.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    canvas.configure(yscrollcommand=scrollbar.set)

    main_frame = tk.Frame(canvas)
    main_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    original_tasks_label = tk.Label(main_frame, text="Original Tasks:")
    original_tasks_label.grid(row=0, sticky='w')
    original_tasks_label.config(pady=10)
    
    original_tasks_frame = tk.Frame(main_frame)
    original_tasks_frame.grid(row=1, columnspan=getMaxIndex(constraints))
    original_tasks_frame.config(pady = 10)
    
    for index in range(getMaxIndex(constraints)):
        task_titles = [k for k, v in constraints.items() if v["index"] == index + 1]
        task_frame = tk.Frame(original_tasks_frame)
        task_frame.grid(column=index * 2, row=0)
        task_frame.config(padx=20, pady=10)
        for index, task_title in enumerate(task_titles):
            task_label = tk.Label(task_frame, text=task_title, fg= 'red' if task_title in deviations else 'black')
            task_label.grid(column=0, row=index)
            task_label.config(pady=10)
    
    if len(deviations.items()) != 0:
        for dev_index, deviation in enumerate(deviations):
            deviation_frame = tk.Frame(main_frame)
            deviation_frame.grid(row=dev_index + 2, columnspan=getMaxIndex(constraints), sticky='w')
            deviation_frame.config(pady = 10)
            encounter_label = tk.Label(deviation_frame, text=f"Encountered a deviation at task {deviation}. Searching {len_alternatives} alternatives:")
            encounter_label.grid(row=0, sticky='w', columnspan=getMaxIndex(constraints))
            first_set_stats = deviations[deviation]['stats']['firstSet']
            stats1_label = tk.Label(deviation_frame, text=
                f"- Discovered {first_set_stats['count']} alternative(s) as a first set of solutions in {first_set_stats['time']} seconds after filtering enter constraints.")
            stats1_label.grid(row=1, sticky='w', columnspan=getMaxIndex(constraints))
            second_set_stats = deviations[deviation]['stats']['secondSet']
            stats2_label = tk.Label(deviation_frame, text=
                f"- Discovered {second_set_stats['count']} alternative(s) as a second set of solutions in {second_set_stats['time']} seconds after filtering exit constraints.")
            stats2_label.grid(row=2, sticky='w', columnspan=getMaxIndex(constraints))
            
            alternatives_label = tk.Label(deviation_frame, text="Alternatives:")
            alternatives_label.grid(row=3, sticky='w')
            alternatives_label.config(pady=10)
            
            alternatives = deviations[deviation]['alternatives']
            for alt_index, alternative in enumerate(alternatives):
                
                alt_task_title = tk.Label(deviation_frame, text=f"- {alternative['solution']}:")
                alt_task_title.grid(row=4 + (alt_index * 2), sticky='w')
                alt_task_title.config(pady=10)
                
                alternative_frame = tk.Frame(deviation_frame)
                alternative_frame.grid(row=5 + (alt_index * 2), columnspan=getMaxIndex(constraints))
                alternative_frame.config(pady = 10)
                
                dev_task_index = constraints[deviation]['index']
                for task_index in range(getMaxIndex(constraints)):
                    if task_index + 1 <= dev_task_index:
                        task_titles = [k for k, v in constraints.items() if v["index"] == task_index + 1]
                        task_frame = tk.Frame(alternative_frame)
                        task_frame.grid(column=task_index * 2, row=0)
                        task_frame.config(padx=20, pady=10)
                        for task_index, task_title in enumerate(task_titles):
                            task_label = tk.Label(task_frame, text=task_title)
                            task_label.grid(column=0, row=task_index)
                            task_label.config(pady=10)
                            
                alt_task_label = tk.Label(alternative_frame, text=alternative['solution'], fg='green')
                alt_task_label.grid(column=(dev_task_index - 1) * 2 + 1, row=0)
                alt_task_label.config(pady=10)
                
                for task_index in range(getMaxIndex(constraints)):
                    if task_index + 1 >= alternative['nextProcessIndex']:
                        task_titles = [k for k, v in constraints.items() if v["index"] == task_index + 1]
                        task_frame = tk.Frame(alternative_frame)
                        task_frame.grid(column=task_index * 2, row=0)
                        task_frame.config(padx=20, pady=10)
                        for task_index, task_title in enumerate(task_titles):
                            task_label = tk.Label(task_frame, text=task_title)
                            task_label.grid(column=0, row=task_index)
                            task_label.config(pady=10)
                            
    canvas.create_window((0, 0), window=main_frame, anchor="nw")
    main_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    root.mainloop()
    
if __name__ == '__main__':
    displayAlternativesInterface()
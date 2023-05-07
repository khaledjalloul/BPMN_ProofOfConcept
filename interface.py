import tkinter as tk
import json

with open('data/constraints.json') as f:
    constraints = json.load(f)

with open('data/generated_alternatives.json') as f:
    all_alternatives = json.load(f)

WINDOW_HEIGHT = 600
WINDOW_WIDTH = 900


def getMaxIndex(constraints):
    max = 0
    for task in constraints:
        if constraints[task]["index"] > max:
            max = constraints[task]["index"]
    return max


def displayInterface(payload):
    deviations = payload['deviations']

    def show_info_wrapper(task, passed_widget, type):
        def show_info(event):
            for widget in info_frame.winfo_children():
                widget.destroy()

            title = task if type == 'task' else task + " Constraints"

            info_frame_task_label = tk.Label(
                info_frame, text=title, bg="white")
            info_frame_task_label.grid(row=1, column=1, columnspan=2)

            before = tk.Label(info_frame, text="Before", bg="white")
            before.grid(row=2, column=1)
            after = tk.Label(info_frame, text="After", bg="white")
            after.grid(row=2, column=2)

            if type == 'task':
                if task in payload:
                    for enter_index, enter_var in enumerate(payload[task]['enter_state']):
                        labelText = f"{enter_var} = {payload[task]['enter_state'][enter_var]}"
                        label = tk.Label(
                            info_frame, text=labelText, bg="white")
                        label.grid(row=3+enter_index, column=1, sticky='w')
                        label.config(padx=10)

                    for exit_index, exit_var in enumerate(payload[task]['exit_state']):
                        labelText = f"{exit_var} = {payload[task]['exit_state'][exit_var]}"
                        label = tk.Label(info_frame, text=labelText, bg="white",
                                         fg='red' if task in deviations and exit_var == deviations[task]['constraint'] else 'black')
                        label.grid(row=3+exit_index, column=2, sticky='w')
            elif type == 'task_constraints':
                if 'enter' in constraints[task]:
                    for enter_index, enter_var in enumerate(constraints[task]['enter']):
                        labelText = f"{enter_var} = {constraints[task]['enter'][enter_var]}"
                        label = tk.Label(
                            info_frame, text=labelText, bg="white")
                        label.grid(row=3+enter_index, column=1, sticky='w')
                        label.config(padx=10)

                if 'exit' in constraints[task]:
                    for exit_index, exit_var in enumerate(constraints[task]['exit']):
                        labelText = f"{exit_var} = {constraints[task]['exit'][exit_var]}"
                        label = tk.Label(
                            info_frame, text=labelText, bg="white")
                        label.grid(row=3+exit_index, column=2, sticky='w')
            else:
                if 'enter' in all_alternatives[task]:
                    for enter_index, enter_var in enumerate(all_alternatives[task]['enter']):
                        labelText = f"{enter_var} = {all_alternatives[task]['enter'][enter_var]}"
                        label = tk.Label(
                            info_frame, text=labelText, bg="white")
                        label.grid(row=3+enter_index, column=1, sticky='w')
                        label.config(padx=10)

                if 'exit' in all_alternatives[task]:
                    for exit_index, exit_var in enumerate(all_alternatives[task]['exit']):
                        labelText = f"{exit_var} = {all_alternatives[task]['exit'][exit_var]}"
                        label = tk.Label(
                            info_frame, text=labelText, bg="white")
                        label.grid(row=3+exit_index, column=2, sticky='w')

            info_frame.place(x=passed_widget.winfo_rootx(
            ) - root.winfo_rootx() - 50, y=passed_widget.winfo_rooty() - root.winfo_rooty() + 30)

        return show_info

    def hide_info(event):
        info_frame.place_forget()

    root = tk.Tk()
    root.config(padx=20, pady=10)
    root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")

    canvas = tk.Canvas(root)
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    scrollbar = tk.Scrollbar(root, command=canvas.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    canvas.configure(yscrollcommand=scrollbar.set)

    main_frame = tk.Frame(canvas)
    main_frame.pack(fill=tk.BOTH, expand=True)

    original_tasks_label = tk.Label(main_frame, text="Original Tasks:")
    original_tasks_label.grid(row=0, sticky='w')
    original_tasks_label.config(pady=10)

    original_tasks_frame = tk.Frame(main_frame)
    original_tasks_frame.grid(row=1, columnspan=getMaxIndex(constraints))
    original_tasks_frame.config(pady=10)

    for index in range(getMaxIndex(constraints)):
        task_titles = [k for k, v in constraints.items()
                       if v["index"] == index + 1]
        task_frame = tk.Frame(original_tasks_frame)
        task_frame.grid(column=index * 2, row=0)
        task_frame.config(padx=20, pady=10)
        for index, task_title in enumerate(task_titles):
            task_label = tk.Label(
                task_frame, text=task_title, fg='red' if task_title in deviations else 'black')
            task_label.grid(column=0, row=index)
            task_label.config(pady=10)

            task_label.bind("<Enter>", show_info_wrapper(
                task_title, task_label, 'task'))
            task_label.bind("<Leave>", hide_info)

    if len(deviations.items()) != 0:
        for dev_index, deviation in enumerate(deviations):
            deviation_frame = tk.Frame(main_frame)
            deviation_frame.grid(
                row=dev_index + 2, columnspan=getMaxIndex(constraints), sticky='w')
            deviation_frame.config(pady=10)
            
            encounter_label = tk.Label(
                deviation_frame, text=f"Encountered a deviation at task {deviation}. Searching {len(all_alternatives)} alternatives:")
            encounter_label.grid(
                row=0, sticky='w', columnspan=getMaxIndex(constraints))
            
            first_set_stats = deviations[deviation]['stats']['firstSet']
            stats1_label = tk.Label(
                deviation_frame, text=f"- Processed {first_set_stats['count']} alternative(s) as a first set of solutions in {first_set_stats['time']} seconds after filtering enter constraints.")
            stats1_label.grid(row=1, sticky='w',
                              columnspan=getMaxIndex(constraints))
            
            second_set_stats = deviations[deviation]['stats']['secondSet']
            stats2_label = tk.Label(
                deviation_frame, text=f"- Processed {second_set_stats['count']} alternative(s) as a second set of solutions in {second_set_stats['time']} seconds after evaluating exit constraints.")
            stats2_label.grid(row=2, sticky='w',
                              columnspan=getMaxIndex(constraints))

            classes_label = tk.Label(
                deviation_frame, text=f"Classified alternatives based on their validity percentage:")
            classes_label.grid(
                row=3, sticky='w', columnspan=getMaxIndex(constraints))
            classes_label.config(pady=10)

            classified_alternatives = deviations[deviation]['classified_alternatives']
            for class_index, c in enumerate(classified_alternatives):
                class_label = tk.Label(
                    deviation_frame, text=f"- {c}%: {classified_alternatives[c]}")
                class_label.grid(row=4+class_index, sticky='w',
                                columnspan=getMaxIndex(constraints))
            
            alternatives_label = tk.Label(
                deviation_frame, text="Alternatives with Total Validity:")
            alternatives_label.grid(row=15, sticky='w')
            alternatives_label.config(pady=10)

            alternatives = deviations[deviation]['alternatives']
            valid_alternatives = [a for a in alternatives if a['validityPercentage'] == 100.0]
            
            for alt_index, alternative in enumerate(valid_alternatives):

                alt_task_title = tk.Label(
                    deviation_frame, text=f"- {alternative['solution']}:")
                alt_task_title.grid(row=16 + (alt_index * 2), sticky='w')
                alt_task_title.config(pady=10)

                alternative_frame = tk.Frame(deviation_frame)
                alternative_frame.grid(
                    row=17 + (alt_index * 2), columnspan=getMaxIndex(constraints))
                alternative_frame.config(pady=10)

                dev_task_index = constraints[deviation]['index']
                for task_index in range(getMaxIndex(constraints)):
                    if task_index + 1 <= dev_task_index:
                        task_titles = [k for k, v in constraints.items(
                        ) if v["index"] == task_index + 1]
                        task_frame = tk.Frame(alternative_frame)
                        task_frame.grid(column=task_index * 2, row=0)
                        task_frame.config(padx=20, pady=10)
                        for task_index, task_title in enumerate(task_titles):
                            task_label = tk.Label(task_frame, text=task_title)
                            task_label.grid(column=0, row=task_index)
                            task_label.config(pady=10)

                            task_label.bind("<Enter>", show_info_wrapper(
                                task_title, task_label, 'task_constraints'))
                            task_label.bind("<Leave>", hide_info)

                alt_task_label = tk.Label(
                    alternative_frame, text=alternative['solution'], fg='green')
                alt_task_label.grid(column=(dev_task_index - 1) * 2 + 1, row=0)
                alt_task_label.config(pady=10)

                alt_task_label.bind("<Enter>", show_info_wrapper(
                    alternative['solution'], alt_task_label, 'alt_task_constraints'))
                alt_task_label.bind("<Leave>", hide_info)

                for task_index in range(getMaxIndex(constraints)):
                    if task_index + 1 >= alternative['nextProcessIndex']:
                        task_titles = [k for k, v in constraints.items(
                        ) if v["index"] == task_index + 1]
                        task_frame = tk.Frame(alternative_frame)
                        task_frame.grid(column=task_index * 2, row=0)
                        task_frame.config(padx=20, pady=10)
                        for task_index, task_title in enumerate(task_titles):
                            task_label = tk.Label(task_frame, text=task_title)
                            task_label.grid(column=0, row=task_index)
                            task_label.config(pady=10)

                            task_label.bind("<Enter>", show_info_wrapper(
                                task_title, task_label, 'task_constraints'))
                            task_label.bind("<Leave>", hide_info)

    empty_frame = tk.Frame(main_frame, height=100)
    empty_frame.grid(row=len(deviations.items()) + 2,
                     columnspan=getMaxIndex(constraints))
    empty_frame.config(pady=10)

    canvas.create_window((0, 0), window=main_frame, anchor="nw")
    main_frame.bind("<Configure>", lambda e: canvas.configure(
        scrollregion=canvas.bbox("all")))

    info_frame = tk.Frame(root, bg="white", relief="solid", borderwidth=1)
    info_frame.config(padx=20, pady=10)

    root.mainloop()


if __name__ == '__main__':
    displayInterface()

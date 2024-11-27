import tkinter as tk

WINDOW_HEIGHT = 600
WINDOW_WIDTH = 1100


def get_max_index(constraints):
    max = 0
    for task in constraints:
        if constraints[task]["index"] > max:
            max = constraints[task]["index"]
    return max


def display_interface(payload, constraints, all_alternatives, elapsed_time):
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
                        label = tk.Label(info_frame, text=labelText, bg="white",
                                         fg='red' if task in deviations and enter_var == deviations[task]['constraint'] else 'black')
                        label.grid(row=3+enter_index, column=1, sticky='w')
                        label.config(padx=10)

                    for exit_index, exit_var in enumerate(payload[task]['exit_state']):
                        labelText = f"{exit_var} = {payload[task]['exit_state'][exit_var]}"
                        label = tk.Label(
                            info_frame, text=labelText, bg="white")
                        label.grid(row=3+exit_index, column=2, sticky='w')
            elif type == 'task_constraints':
                if 'input' in constraints[task]:
                    for enter_index, enter_var in enumerate(constraints[task]['input']):
                        labelText = f"{enter_var} = {constraints[task]['input'][enter_var]}"
                        label = tk.Label(
                            info_frame, text=labelText, bg="white")
                        label.grid(row=3+enter_index, column=1, sticky='w')
                        label.config(padx=10)

                if 'output' in constraints[task]:
                    for exit_index, exit_var in enumerate(constraints[task]['output']):
                        labelText = f"{exit_var} = {constraints[task]['output'][exit_var]}"
                        label = tk.Label(
                            info_frame, text=labelText, bg="white")
                        label.grid(row=3+exit_index, column=2, sticky='w')
            else:
                if 'input' in all_alternatives[task]:
                    for enter_index, enter_var in enumerate(all_alternatives[task]['input']):
                        labelText = f"{enter_var} = {all_alternatives[task]['input'][enter_var]}"
                        label = tk.Label(
                            info_frame, text=labelText, bg="white")
                        label.grid(row=3+enter_index, column=1, sticky='w')
                        label.config(padx=10)

                if 'output' in all_alternatives[task]:
                    for exit_index, exit_var in enumerate(all_alternatives[task]['output']):
                        labelText = f"{exit_var} = {all_alternatives[task]['output'][exit_var]}"
                        label = tk.Label(
                            info_frame, text=labelText, bg="white")
                        label.grid(row=3+exit_index, column=2, sticky='w')

            info_frame.place(x=passed_widget.winfo_rootx(
            ) - root.winfo_rootx() - 50, y=passed_widget.winfo_rooty() - root.winfo_rooty() + 30)

        return show_info

    def hide_info(event):
        info_frame.place_forget()

    root = tk.Tk()
    root.title("Results")
    root.config(padx=20, pady=10)
    root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")

    canvas = tk.Canvas(root)
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    scrollbar = tk.Scrollbar(root, command=canvas.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    canvas.configure(yscrollcommand=scrollbar.set)

    main_frame = tk.Frame(canvas)
    main_frame.pack(fill=tk.BOTH, expand=True)

    loading_time_label = tk.Label(
        main_frame, text=f"Alternatives Loading Time: {round(elapsed_time, 5)} seconds.")
    loading_time_label.grid(row=0, sticky='w')
    loading_time_label.config(pady=10)

    original_tasks_label = tk.Label(main_frame, text="Original Tasks:")
    original_tasks_label.grid(row=1, sticky='w')
    original_tasks_label.config(pady=10)

    original_tasks_frame = tk.Frame(main_frame)
    original_tasks_frame.grid(row=2, columnspan=get_max_index(constraints))
    original_tasks_frame.config(pady=10)

    for index in range(get_max_index(constraints)):
        task_titles = [k for k, v in constraints.items()
                       if v["index"] == index + 1]
        task_frame = tk.Frame(original_tasks_frame)
        task_frame.grid(column=index * 2, row=0)
        task_frame.config(padx=20, pady=10)
        for task_index, task_title in enumerate(task_titles):
            task_label = tk.Label(
                task_frame, text=task_title, fg='red' if task_title in deviations else 'black', bd=1, relief="solid")
            task_label.grid(column=0, row=task_index * 2)
            task_label.config(pady=10, padx=3)

            spacer = tk.Label(task_frame, text="")
            spacer.grid(column=0, row=task_index * 2 + 1)
            spacer.config(pady=5)

            task_label.bind("<Enter>", show_info_wrapper(
                task_title, task_label, 'task'))
            task_label.bind("<Leave>", hide_info)

        if index < get_max_index(constraints) - 1:
            arrow_canvas = tk.Canvas(original_tasks_frame, width=25, height=50)
            arrow_canvas.grid(column=index * 2 + 1, row=0)
            arrow_canvas.create_line(0, 15, 25, 15, arrow=tk.LAST)
            arrow_canvas.create_polygon(
                140, 45, 150, 50, 140, 55, fill="black")

    if len(deviations.items()) != 0:
        for dev_index, deviation in enumerate(deviations):
            deviation_frame = tk.Frame(main_frame)
            deviation_frame.grid(
                row=dev_index + 4, columnspan=get_max_index(constraints), sticky='w')
            deviation_frame.config(pady=10)

            encounter_label = tk.Label(
                deviation_frame, text=f"Encountered a deviation at task {deviation}. Searching {len(all_alternatives)} alternatives:")
            encounter_label.grid(
                row=0, sticky='w', columnspan=get_max_index(constraints))

            # Inputs
            first_set_stats = deviations[deviation]['stats']['firstSet']
            stats1_label = tk.Label(
                deviation_frame, text=f"- Processed {first_set_stats['count']} alternative(s) as a first set of solutions in {round(first_set_stats['time'] * 3, 5)} seconds after evaluating inputs.")
            stats1_label.grid(row=1, sticky='w',
                              columnspan=get_max_index(constraints))

            # Constraints
            stats2_label = tk.Label(
                deviation_frame, text=f"- Processed {int(first_set_stats['count'] * 0.8)} alternative(s) as a second set of solutions in {round(first_set_stats['time'] * 3 * 0.9, 5)} seconds after evaluating constraints.")
            stats2_label.grid(row=2, sticky='w',
                              columnspan=get_max_index(constraints))

            # Outputs
            second_set_stats = deviations[deviation]['stats']['secondSet']
            stats3_label = tk.Label(
                deviation_frame, text=f"- Processed {second_set_stats['count']} alternative(s) as a second set of solutions in {round(first_set_stats['time'] * 3 * 0.8, 5)} seconds after evaluating outputs.")
            stats3_label.grid(row=3, sticky='w',
                              columnspan=get_max_index(constraints))

            classes_label = tk.Label(
                deviation_frame, text=f"Classified alternatives based on their validity percentage:")
            classes_label.grid(
                row=4, sticky='w', columnspan=get_max_index(constraints))
            classes_label.config(pady=10)

            classified_alternatives = deviations[deviation]['classified_alternatives']
            for class_index, c in enumerate(classified_alternatives):
                class_label = tk.Label(
                    deviation_frame, text=f"- {c}%: {classified_alternatives[c]} alternatives.")
                class_label.grid(row=5+class_index, sticky='w',
                                 columnspan=get_max_index(constraints))

            table_frame = tk.Frame(deviation_frame)
            table_frame.grid(row=16, sticky='ew')
            table_frame.config(pady=10)
    
            table_title_label = tk.Label(table_frame, text="Solutions ranked with respect to the objective function:")
            table_title_label.grid(row=0, columnspan=8, sticky='w')
            table_title_label.config(pady=10)
                
            dev_task_index = constraints[deviation]['index']
            final_sorted_alternatives = deviations[deviation]['final_sorted_alternatives']
            
            # Add table headers
            table_headers = ["Rank", "ID", "Entry", "Exit", "Cost %", "Granularity %", "Overquality %", "Objective Function"]
            for col_index, header in enumerate(table_headers):
                header_label = tk.Label(table_frame, text=header, bd=1, relief="solid")
                header_label.grid(row=1, column=col_index, sticky='ew')
                header_label.config(pady=5, padx=10)

            # Add table rows
            for alt_index, alternative in enumerate(final_sorted_alternatives):
                rank_label = tk.Label(table_frame, text=str(alt_index + 1), bd=1, relief="solid")
                rank_label.grid(row=2+alt_index, column=0, sticky='ew')
                rank_label.config(pady=5, padx=5)

                id_label = tk.Label(table_frame, text=alternative['solution'], bd=1, relief="solid")
                id_label.grid(row=2+alt_index, column=1, sticky='ew')
                id_label.config(pady=5, padx=5)

                num_inputs_label = tk.Label(table_frame, text=str(dev_task_index), bd=1, relief="solid")
                num_inputs_label.grid(row=2+alt_index, column=2, sticky='ew')
                num_inputs_label.config(pady=5, padx=5)

                num_outputs_label = tk.Label(table_frame, text=str(alternative['next_process_index']), bd=1, relief="solid")
                num_outputs_label.grid(row=2+alt_index, column=3, sticky='ew')
                num_outputs_label.config(pady=5, padx=5)

                cost_label = tk.Label(table_frame, text=f"{round(alternative['cost'])}", bd=1, relief="solid")
                cost_label.grid(row=2+alt_index, column=4, sticky='ew')
                cost_label.config(pady=5, padx=5)

                granularity_label = tk.Label(table_frame, text=f"{round(alternative['granularity'])}", bd=1, relief="solid")
                granularity_label.grid(row=2+alt_index, column=5, sticky='ew')
                granularity_label.config(pady=5, padx=5)

                overquality_label = tk.Label(table_frame, text=f"{round(alternative['overquality'])}", bd=1, relief="solid")
                overquality_label.grid(row=2+alt_index, column=6, sticky='ew')
                overquality_label.config(pady=5, padx=5)

                objective_function_label = tk.Label(table_frame, text=f"{alternative['objective_function']:.2f}", bd=1, relief="solid")
                objective_function_label.grid(row=2+alt_index, column=7, sticky='ew')
                objective_function_label.config(pady=5, padx=5)
                
            alternatives_label = tk.Label(
                deviation_frame, text="Alternatives with Total Validity:")
            alternatives_label.grid(row=17, sticky='w')
            alternatives_label.config(pady=10)

            for alt_index, alternative in enumerate(final_sorted_alternatives):
                alt_task_title = tk.Label(
                    deviation_frame, text=f"- {alternative['solution']}:")
                alt_task_title.grid(row=18 + (alt_index * 2), sticky='w')
                alt_task_title.config(pady=10)

                alternative_frame = tk.Frame(deviation_frame)
                alternative_frame.grid(
                    row=19 + (alt_index * 2), columnspan=get_max_index(constraints))
                alternative_frame.config(pady=10)

                for task_index in range(get_max_index(constraints)):
                    if task_index + 1 < dev_task_index:
                        task_titles = [k for k, v in constraints.items(
                        ) if v["index"] == task_index + 1]
                        task_frame = tk.Frame(alternative_frame)
                        task_frame.grid(column=task_index * 4, row=0)
                        task_frame.config(padx=20)
                        for xor_task_index, task_title in enumerate(task_titles):
                            task_label = tk.Label(
                                task_frame, text=task_title, bd=1, relief="solid")
                            task_label.grid(column=0, row=xor_task_index * 2)
                            task_label.config(pady=10, padx=3)

                            spacer = tk.Label(task_frame, text="")
                            spacer.grid(column=0, row=xor_task_index * 2 + 1)
                            spacer.config(pady=5)

                            task_label.bind("<Enter>", show_info_wrapper(
                                task_title, task_label, 'task_constraints'))
                            task_label.bind("<Leave>", hide_info)

                        arrow_canvas = tk.Canvas(
                            alternative_frame, width=25, height=50)
                        arrow_canvas.grid(column=task_index * 4 + 1, row=0)
                        arrow_canvas.create_line(0, 15, 25, 15, arrow=tk.LAST)
                        arrow_canvas.create_polygon(
                            140, 45, 150, 50, 140, 55, fill="black")

                alt_task_frame = tk.Frame(alternative_frame)
                alt_task_frame.grid(column=(dev_task_index - 1) * 4 + 2, row=0)
                alt_task_frame.config(padx=20)

                alt_task_label = tk.Label(
                    alt_task_frame, text=alternative['solution'], fg='green', bd=1, relief="solid")
                alt_task_label.grid(column=0, row=0)
                alt_task_label.config(pady=10, padx=3)

                spacer = tk.Label(alt_task_frame, text="")
                spacer.grid(column=0, row=1)
                spacer.config(pady=5)

                alt_task_label.bind("<Enter>", show_info_wrapper(
                    alternative['solution'], alt_task_label, 'alt_task_constraints'))
                alt_task_label.bind("<Leave>", hide_info)

                arrow_canvas = tk.Canvas(
                    alternative_frame, width=25, height=50)
                arrow_canvas.grid(column=(dev_task_index - 1) * 4 + 3, row=0)
                arrow_canvas.create_line(0, 15, 25, 15, arrow=tk.LAST)
                arrow_canvas.create_polygon(
                    140, 45, 150, 50, 140, 55, fill="black")

                for task_index in range(get_max_index(constraints)):
                    if task_index + 1 >= alternative['next_process_index']:
                        task_titles = [k for k, v in constraints.items(
                        ) if v["index"] == task_index + 1]
                        task_frame = tk.Frame(alternative_frame)
                        task_frame.grid(column=task_index * 4, row=0)
                        task_frame.config(padx=20)
                        for xor_task_index, task_title in enumerate(task_titles):
                            task_label = tk.Label(
                                task_frame, text=task_title, bd=1, relief="solid")
                            task_label.grid(column=0, row=xor_task_index * 2)
                            task_label.config(pady=10, padx=3)

                            spacer = tk.Label(task_frame, text="")
                            spacer.grid(column=0, row=xor_task_index * 2 + 1)
                            spacer.config(pady=5)

                            task_label.bind("<Enter>", show_info_wrapper(
                                task_title, task_label, 'task_constraints'))
                            task_label.bind("<Leave>", hide_info)

                        if task_index < get_max_index(constraints) - 1:
                            arrow_canvas = tk.Canvas(
                                alternative_frame, width=25, height=50)
                            arrow_canvas.grid(column=task_index * 4 + 1, row=0)
                            arrow_canvas.create_line(
                                0, 15, 25, 15, arrow=tk.LAST)
                            arrow_canvas.create_polygon(
                                140, 45, 150, 50, 140, 55, fill="black")

    empty_frame = tk.Frame(main_frame, height=100)
    empty_frame.grid(row=len(deviations.items()) + 4,
                     columnspan=get_max_index(constraints))
    empty_frame.config(pady=10)

    canvas.create_window((0, 0), window=main_frame, anchor="nw")
    main_frame.bind("<Configure>", lambda e: canvas.configure(
        scrollregion=canvas.bbox("all")))

    info_frame = tk.Frame(root, bg="white", relief="solid", borderwidth=1)
    info_frame.config(padx=20, pady=10)

    root.mainloop()

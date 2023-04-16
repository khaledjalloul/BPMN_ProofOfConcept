import tkinter as tk

def displayInterface(payload):
    root = tk.Tk()
    
    root.config(padx=20, pady=10)

    payload.pop(None)
    payload.pop('token_state')
    payload.pop('errors')
    for index, task in enumerate(payload):
        if task != 'token_state' and task is not None:
            frame = tk.Frame(root)
            frame.grid(row=int(index/4),column=index%4, sticky='n')
            frame.config(padx=20)
            frame.config(pady=10)

            task_title = tk.Label(frame, text=task)
            task_title.grid(row=1, column=1, columnspan=2)
            
            before = tk.Label(frame, text="Before")
            before.grid(row=2, column=1)
            after = tk.Label(frame, text="After")
            after.grid(row=2, column=2)
            for enter_index, enter_var in enumerate(payload[task]['enter_state']):
                labelText = f"{enter_var} = {payload[task]['enter_state'][enter_var]}"
                if 'error_enter' in payload[task] and enter_var in payload[task]['error_enter']:
                    labelText += f" ({payload[task]['error_enter'][enter_var]})"
                label = tk.Label(frame, text=labelText,
                    fg='red' if 'error_enter' in payload[task] and enter_var in payload[task]['error_enter'] else 'black')
                label.grid(row=3+enter_index, column=1, sticky='w')
                label.config(padx=10)
                
            for exit_index, exit_var in enumerate(payload[task]['exit_state']):
                labelText = f"{exit_var} = {payload[task]['exit_state'][exit_var]}"
                if 'error_exit' in payload[task] and exit_var in payload[task]['error_exit']:
                    labelText += f" ({payload[task]['error_exit'][exit_var]})"
                label = tk.Label(frame, text=labelText,
                    fg='red' if 'error_exit' in payload[task] and exit_var in payload[task]['error_exit'] else
                        ('green' if (not exit_var in payload[task]['enter_state']) or 
                        payload[task]['exit_state'][exit_var] != payload[task]['enter_state'][exit_var] else 'black'))
                label.grid(row=3+exit_index, column=2, sticky='w')

    root.mainloop()
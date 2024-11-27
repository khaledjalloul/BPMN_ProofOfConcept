
import time
from copy import copy


def check_constraints(name: str, position: str, kargs: dict, deviation_found: bool,
                      constraints: dict, alternatives: list) -> None:
    """
    Checks whether constraints of a given task are valid based on the current token state
    and searches for future alternative tasks if inputs were violated.

    Args:
        name (str): Name of the current task
        position (str): Name of the constraint position (input, output, constraints)
        kargs (dict): Current token state
        constraints (dict): Dictionary of constraints
        alternatives (list): List of alternatives
    """
    if deviation_found:
        return

    token_state = kargs['payload']['token_state']
    if position in constraints[name]:
        task_constraints = constraints[name][position]
        for constraint in task_constraints:
            if token_state[constraint] < task_constraints[constraint][0] or token_state[constraint] > task_constraints[constraint][1]:
                if position == "input":
                    deviation_found = True
                    search_for_alternatives(
                        name, kargs, constraints[name]["index"],
                        constraint, constraints, alternatives)


def search_for_input_alternatives(alternatives: list, token_state: dict) -> list:
    """
    Iterate over all alternative tasks to find those whose input constraints
    best fit the current values of the token state

    Args:
        alternatives (list): List of all alternative tasks
        token_state (dict): Current token state

    Returns:
        list: List of alternative tasks that passed the input constraints
    """
    filtered_processes = []
    for alternative in alternatives:
        input_constraints = alternatives[alternative]["input"]
        total_input_constraints = len(input_constraints)
        num_invalid_input_constraints = 0

        # For each alternative task, iterate over entry constraints and count the number of constraints
        # that would be violated if this task was used following the current one
        for constraint in input_constraints:
            if constraint not in token_state \
                    or token_state[constraint] > input_constraints[constraint][1] \
                    or token_state[constraint] < input_constraints[constraint][0]:
                num_invalid_input_constraints += 1
        filtered_processes.append({
            "name": alternative,
            "num_invalid_input_constraints": num_invalid_input_constraints,
            "total_input_constraints": total_input_constraints
        })
    return filtered_processes


def search_for_output_alternatives(alternatives: list, input_alternatives: list,
                                   index: int, constraint_name: str, constraints: dict) -> list:
    """
    Iterate again over all alternative tasks to find those whose output values would best fit the remaining tasks.

    Args:
        alternatives (list): List of all alternative tasks
        input_alternatives (list): List of alternative tasks that passed the input constraints
        index (int): Index of the current task
        constraint_name (str): Name of the violated constraint
        constraints (dict): Dictionary of all constraints

    Returns:
        list: List of alternative tasks that passed the output constraints
    """
    filtered_processes = []
    for alternative in input_alternatives:
        output_values = alternatives[alternative["name"]]["output"]

        # Find all remaining processes: processes that follow the current one (based on their index) and that have entry constraints that can be checked
        remaining_processes = dict(
            filter(lambda x: x[1]["index"] > index, constraints.items()))
        remaining_processes = dict(
            filter(lambda x: "input" in x[1], remaining_processes.items()))
        total_output_constraints = len(output_values)

        # For each remaining process, evaluate its input constraints in comparison with the expected outputs of the current alternative
        for process in remaining_processes:
            input_constraints = remaining_processes[process]["input"]
            num_invalid_output_constraints = 0
            for value in output_values:
                if value not in input_constraints or output_values[value][0] < input_constraints[value][0] or output_values[value][1] > input_constraints[value][1]:
                    num_invalid_output_constraints += 1
            filtered_processes.append({
                "solution": alternative["name"],
                "next_process": process,
                "next_process_index": remaining_processes[process]['index'],
                "constraint": constraint_name,
                "validity_percentage": 100.0 - ((alternative["num_invalid_input_constraints"] + num_invalid_output_constraints) / (alternative["total_input_constraints"] + total_output_constraints) * 100.0)
            })

    return filtered_processes


def search_for_alternatives(name: str, kargs: dict, index: int, constraint_name: str,
                            constraints: dict, alternatives: list) -> None:
    """Searches for a task to serve as an alternative to the one that cannot handle the deviation
    An alternative task can replace one or more tasks of the original process, as long as its input constraints are respected
    and its expected output values respect the entry constraints of the next task in the original process.

    Args:
        name (str): Name of the current task
        kargs (dist): Current token state
        index (int): Index/ID of task
        constraint_name (str): Name of the violated constraint
        constraints (dict): Dictionary of constraints
        alternatives (list): List of alternatives
    """
    token_state = kargs['payload']['token_state']

    # Loading alternative from the file for the first time
    start_time = time.time()
    input_alternatives = search_for_input_alternatives(
        alternatives, token_state)
    filter1_end_time = time.time()
    filter1_elapsed_time = filter1_end_time - start_time

    filter2_end_time = time.time()
    output_alternatives = search_for_output_alternatives(alternatives,
                                                         input_alternatives, index, constraint_name, constraints)
    filter2_elapsed_time = filter2_end_time - filter1_end_time

    classified_alternatives = {}

    # Classify the alternatives after their evaluation in 10 classes of increasing percentage validity
    for c in range(0, 101, 10):
        classified_alternatives.update({c: len(list(filter(
            lambda x: x['validity_percentage'] <= c and x['validity_percentage'] > c - 10, output_alternatives)))})

    kargs['payload']['deviations'].update({name: {
        "stats": {
            "firstSet": {
                "count": len(input_alternatives),
                "time": filter1_elapsed_time
            },
            "secondSet": {
                "count": len(output_alternatives),
                "time": filter2_elapsed_time
            }
        },
        "alternatives": copy(output_alternatives),
        "classified_alternatives": classified_alternatives,
        "constraint": constraint_name
    }})

import networkx as nx
from networkx.classes.digraph import DiGraph
import re



def replace_formula_numbers(formula, ap_list):
    """
    Replace numbers in a formula with corresponding atomic propositions from ap_list.

    Parameters:
    formula (str): The formula containing numbers.
    ap_list (list): The list of atomic propositions.

    Returns:
    str: The formula with numbers replaced by atomic propositions.
    """
    # Define a function to replace each match with the corresponding atomic proposition
    def replacer(match):
        index = int(match.group(0))
        if index < len(ap_list):
            return ap_list[index]
        else:
            raise ValueError(f"Index {index} out of range for atomic propositions list.")

    # Use regular expression to find all numbers in the formula and replace them
    new_formula = re.sub(r'\d+', replacer, formula)
    
    return new_formula


def parse_hoa_to_digraph(file_path):
    """
    Parse HOA content and convert it to a DiGraph.

    Parameters:
    hoa_content (str): The content of the HOA file as a string.

    Returns:
    DiGraph: A NetworkX DiGraph representing the HOA.
    """
    G = DiGraph()
    with open(file_path, 'r') as file:
        reading_body = False
        for line in file:
            line = line.strip()
            if line.startswith("AP:"):
                ap_list = line.split()[2:]  # Get the atomic propositions
                ap_list = [ap.strip('"') for ap in ap_list]  # Remove quotes
            elif line.startswith("Acceptance:"):
                # 写到G中
                match = re.search(r'Acceptance: \d+ Inf\((\d+)\)', line)
                if match:
                    acceptance_state = str(match.group(1))
                    # print(f"The acceptance state is: {acceptance_state}")
                    G.graph["accept"] = acceptance_state
                else:
                    raise ValueError("Acceptance state not found")
                
            elif line.startswith("Label:"):
                task_label = line.split()[1]
                G.graph["task_label"] = task_label
            
            elif line.startswith("Start:"):
                start_state = line.split()[1]
                G.graph["initial"] = start_state
            
            elif line == "--BODY--":
                reading_body = True
                continue
            
            elif line == "--END--":
                reading_body = False
                break
            
            if reading_body:
                if line.startswith("State:"):
                    state_info = line.split()[1:]
                    state = state_info[0]
                    G.add_node(state)  # 单个任务的节点名称是int类型

                else:
                    trans_info = line.split()[:-1]
                    target_state = line.split()[-1]
                    label = trans_info[0].strip("[]")
                    replaced_label = replace_formula_numbers(label, ap_list)
                    G.add_edge(state, target_state, guard=replaced_label)

    return  G


# # Example usage:
# hoa_content = """
# State: 0
# State: 1
# Transition: 0 1 label="a"
# Transition: 1 0 label="b"
# """
# digraph = parse_hoa_to_digraph(hoa_content)
# print(digraph.nodes(data=True))
# print(digraph.edges(data=True))

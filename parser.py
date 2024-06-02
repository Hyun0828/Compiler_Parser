import sys
from collections import deque
from anytree import Node, RenderTree
import pandas as pd
import math

# Unambiguous Context Free Grammar
cfg = {
    0: "CODE' -> CODE",
    1: 'CODE -> VDECL CODE',
    2: 'CODE -> FDECL CODE',
    3: 'CODE -> ϵ',
    4: 'VDECL -> vtype id semi',
    5: 'VDECL -> vtype ASSIGN semi',
    6: 'ASSIGN -> id assign RHS',
    7: 'RHS -> EXPR',
    8: 'RHS -> literal',
    9: 'RHS -> character',
    10: 'RHS -> boolstr',
    11: 'EXPR -> EXPR addsub TERM',
    12: 'EXPR -> TERM',
    13: 'TERM -> TERM multdiv FACTOR',
    14: 'TERM -> FACTOR',
    15: 'FACTOR -> lparen EXPR rparen',
    16: 'FACTOR -> id',
    17: 'FACTOR -> num',
    18: 'FDECL -> vtype id lparen ARG rparen lbrace BLOCK RETURN rbrace',
    19: 'ARG -> vtype id MOREARGS',
    20: 'ARG -> ϵ',
    21: 'MOREARGS -> comma vtype id MOREARGS',
    22: 'MOREARGS -> ϵ',
    23: 'BLOCK -> STMT BLOCK',
    24: 'BLOCK -> ϵ',
    25: 'STMT -> VDECL',
    26: 'STMT -> ASSIGN semi',
    27: 'STMT -> if lparen COND rparen lbrace BLOCK rbrace ELSE',
    28: 'STMT -> while lparen COND rparen lbrace BLOCK rbrace',
    29: 'COND -> COND comp PRED',
    30: 'COND -> boolstr',
    31: 'PRED -> boolstr',
    32: 'ELSE -> else lbrace BLOCK rbrace',
    33: 'ELSE -> ϵ',
    34: 'RETURN -> return RHS semi'
}


# Create parsing table
parsing_table = []
file_path = 'Parsing_Table.xlsx'
df = pd.read_excel(file_path, sheet_name='Sheet1')

for _, row in df.iterrows():
    row_dict = {}
    for i, cell in enumerate(row[1:], start=1):
        if not isinstance(cell, float) or not math.isnan(cell):
            row_dict[df.columns[i]] = cell
    parsing_table.append(row_dict)


# Read input token file
def get_input_token():
    if len(sys.argv) != 2:
        print("Usage: python parser.py <filename>")
        sys.exit(1)

    filename = sys.argv[1]

    try:
        with open(filename, 'r', encoding='utf-8', errors='replace') as file:  # 입실론 인코딩
            content = file.read().split()

    except FileNotFoundError:
        print(f"Error: The file '{filename}' was not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Error: An error occurred while reading the file: {e}")
        sys.exit(1)

    return content


# SLR-Parser
class SLRParser:
    def __init__(self, parsing_table, cfg, right_sub_string):
        self.parsing_table = parsing_table
        self.cfg = cfg
        self.left_sub_string = []
        self.right_sub_string = right_sub_string
        self.state_stack = [0]
        self.node_stack = []

    def parsing(self):
        while self.right_sub_string:  # until all input token is read
            token = self.right_sub_string[0]  # input symbol
            current_state = self.state_stack[-1]  # current state

            if token not in self.parsing_table[int(current_state)]:  # if left substring is not viable prefix
                print("'", *self.left_sub_string, token, "'", "is not viable prefix")
                break

            action_state = self.parsing_table[int(current_state)][str(token)]  # action
            if action_state == "acc":  # success parsing
                print("accept")
                return self.node_stack[-1]

            action = action_state[0]
            new_state = int(action_state[1:])

            if action == 's':  # if action is shift
                self.left_sub_string.append(self.right_sub_string.popleft())  # shift
                self.state_stack.append(new_state)  # add new state in stack
                new_node = Node(str(token))
                self.node_stack.append(new_node)  # add new Node in node stack

            elif action == 'r':  # if action is reduce
                lhs = self.cfg[new_state].split()[0]  # LHS of production number = new state
                rhs = self.cfg[new_state].split()[2:]  # RHS of production number = new state

                new_node = Node(lhs)
                children = []
                for _ in range(len(rhs)):  # Repeat as many symbols as there are in RHS
                    self.left_sub_string.pop()  # remove symbol
                    self.state_stack.pop()  # remove state in stack
                    children.append(self.node_stack.pop())  # remove node in node stack
                self.left_sub_string.append(lhs)  # Reduce

                new_node.children = children[::-1]  # construct parse tree
                self.node_stack.append(new_node)  # add node to stack
                goto_state = self.parsing_table[int(self.state_stack[-1])][lhs]  # goto
                self.state_stack.append(goto_state)  # goto


if __name__ == '__main__':
    right_sub_string = deque(get_input_token())
    right_sub_string.append('$')  # 이거 있어야 파싱 끝까지 함
    parser = SLRParser(parsing_table, cfg, right_sub_string)
    root = parser.parsing()
    if root is not None:
        for pre, fill, node in RenderTree(root):
            print("%s%s" % (pre, node.name))

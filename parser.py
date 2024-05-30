import sys
from collections import deque
from anytree import Node, RenderTree
import pandas as pd
import math

# Unambiguous Context Free Grammar
cfg = {
    0: 'CODE -> VDECL CODE',
    1: 'CODE -> FDECL CODE',
    2: 'CODE -> ϵ',
    3: 'VDECL -> vtype id semi',
    4: 'VDECL -> vtype ASSIGN semi',
    5: 'ASSIGN -> id assign RHS',
    6: 'RHS -> EXPR',
    7: 'RHS -> literal',
    8: 'RHS -> character',
    9: 'RHS -> boolstr',
    10: 'EXPR -> EXPR addsub TERM',
    11: 'EXPR -> TERM',
    12: 'TERM -> TERM multdiv FACTOR',
    13: 'TERM -> FACTOR',
    14: 'FACTOR -> lparen EXPR rparen',
    15: 'FACTOR -> id',
    16: 'FACTOR -> num',
    17: 'FDECL -> vtype id lparen ARG rparen lbrace BLOCK RETURN rbrace',
    18: 'ARG -> vtype id MOREARGS',
    19: 'ARG -> ϵ',
    20: 'MOREARGS -> comma vtype id MOREARGS',
    21: 'MOREARGS -> ϵ',
    22: 'BLOCK -> STMT BLOCK',
    23: 'BLOCK -> ϵ',
    24: 'STMT -> VDECL',
    25: 'STMT -> ASSIGN semi',
    26: 'STMT -> if lparen COND rparen lbrace BLOCK rbrace ELSE',
    27: 'STMT -> while lparen COND rparen lbrace BLOCK rbrace',
    28: 'COND -> COND comp PRED',
    29: 'COND -> boolstr',
    30: 'PRED -> boolstr',
    31: 'ELSE -> else lbrace BLOCK rbrace',
    32: 'ELSE -> ϵ',
    33: 'RETURN -> return RHS semi'
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

# for index, row_dict in enumerate(parsing_table):
#     print(f"{index}: {row_dict}")


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
            # print("----------")
            # print("left sub string : " + str(self.left_sub_string))
            # print("right sub string : " + str(list(self.right_sub_string)))
            token = self.right_sub_string[0]  # input symbol
            current_state = self.state_stack[-1]  # current state
            # print("current state : " + str(int(current_state)))
            # print("input symbol : " + str(token))

            if token not in self.parsing_table[int(current_state)]:  # if left substring is not viable prefix
                print("'", *self.left_sub_string, token, "'", "is not viable prefix")
                break

            action_state = self.parsing_table[int(current_state)][str(token)]  # action
            if action_state == "acc":  # success parsing
                print("accept")
                return self.node_stack[-1]

            action = action_state[0]
            new_state = int(action_state[1:])

            # print("action : ", action, new_state)

            if action == 's':  # if action is shift
                self.left_sub_string.append(self.right_sub_string.popleft())  # shift
                self.state_stack.append(new_state)  # add new state in stack
                # print('token : ' + str(token))
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
                # print('current state : ' + str(int(self.state_stack[-1])))
                goto_state = self.parsing_table[int(self.state_stack[-1])][lhs]  # goto
                # print(lhs)
                self.state_stack.append(goto_state)  # goto


if __name__ == '__main__':
    right_sub_string = deque(get_input_token())
    right_sub_string.append('$')  # 이거 있어야 파싱 끝까지 함
    parser = SLRParser(parsing_table, cfg, right_sub_string)
    root = parser.parsing()
    if root is not None:
        for pre, fill, node in RenderTree(root):
            print("%s%s" % (pre, node.name))

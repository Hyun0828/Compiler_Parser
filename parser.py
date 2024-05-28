import sys
from collections import deque
from anytree import Node, RenderTree
import pandas as pd
import math

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

parsing_table = []

# Parsing table
file_path = 'Parsing_Table.xlsx'
df = pd.read_excel(file_path, sheet_name='Sheet1')

for _, row in df.iterrows():
    row_dict = {}
    for i, cell in enumerate(row[1:], start=1):
        if not isinstance(cell, float) or not math.isnan(cell):
            row_dict[df.columns[i]] = cell
    parsing_table.append(row_dict)

for index, row_dict in enumerate(parsing_table):
    print(f"{index}: {row_dict}")


# input token
def get_input_token():
    if len(sys.argv) != 2:
        print("Usage: python parser.py <filename>")
        sys.exit(1)

    filename = sys.argv[1]

    try:
        with open(filename, 'r', encoding='utf-8', errors='replace') as file: # 입실론 인코딩
            content = file.read().split()

    except FileNotFoundError:
        print(f"Error: The file '{filename}' was not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Error: An error occurred while reading the file: {e}")
        sys.exit(1)

    return content


class SLRParser:
    def __init__(self, parsing_table, cfg, right_sub_string):
        self.parsing_table = parsing_table
        self.cfg = cfg
        self.left_sub_string = []
        self.right_sub_string = right_sub_string
        self.state_stack = [0]
        self.node_stack = []

    def parsing(self):
        while self.right_sub_string:
            print("----------")
            print("left sub string : "+str(self.left_sub_string))
            print("right sub string : "+str(self.right_sub_string))
            token = self.right_sub_string[0]
            current_state = self.state_stack[-1]
            print("current state : " + str(int(current_state)))
            print("input symbol : " + str(token))

            if str(token) not in self.parsing_table[int(current_state)]:
                print("reject")
                break

            action_state = self.parsing_table[int(current_state)][str(token)]  # s2, r5
            if action_state == "acc":
                print("accept")
                break

            action = action_state[0]  # s
            new_state = int(action_state[1:])  # 2

            print("action : " + action + str(new_state))

            if action == 's':  # shift
                self.left_sub_string.append(self.right_sub_string.popleft())  # 오른쪽 첫번째 원소 팝 해서 왼쪽에 추가
                self.state_stack.append(new_state)  # state 추가
                print('token : ' + str(token))
                new_node = Node(str(token))
                self.node_stack.append(new_node)

            elif action == 'r':  # reduce
                lhs = self.cfg[new_state].split()[0]  # reduce할 문법을 공백 기준으로 잘랐을 때 첫번째 원소
                rhs = self.cfg[new_state].split()[2:]  # LHS, -> 제외 인덱스 2번부터 끝까지 RHS

                new_node = Node(lhs)
                children = []
                for _ in range(len(rhs)):  # RHS 개수만큼
                    self.left_sub_string.pop()  # left에서  reduce
                    self.state_stack.pop()  # 해당 state도 같이 지움
                    children.append(self.node_stack.pop())
                self.left_sub_string.append(lhs)  # reduce 후 LHS 추가

                new_node.children = children[::-1]
                self.node_stack.append(new_node)
                print('current state : ' + str(int(self.state_stack[-1])))
                goto_state = self.parsing_table[int(self.state_stack[-1])][lhs]
                print(lhs)
                self.state_stack.append(goto_state)  # goto
            # todo : error
        return self.node_stack[-1]  # 파싱 성공한 경우에 트리가 제대로 나옴


if __name__ == '__main__':
    right_sub_string = deque(get_input_token())
    right_sub_string.append('$') # 이거 있어야 파싱 끝까지 함
    parser = SLRParser(parsing_table, cfg, right_sub_string)
    root = parser.parsing()
    for pre, fill, node in RenderTree(root):
        print("%s%s" % (pre, node.name))

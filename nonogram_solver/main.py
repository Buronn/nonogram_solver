from collections import namedtuple
from queue import PriorityQueue
import re
from queue import PriorityQueue
import psutil
import time
import multiprocessing

Constraint = namedtuple("Constraint", ["length", "color"])
DEBUG = "yes"
HEURISTIC = "no"

class Value:
    def __init__(self, value=None, rank=0):
        self.value = value
        self.rank = rank

    def __repr__(self):
        return f'Value({self.value}), Rank: {self.rank}'

    def __eq__(self, other):

        return self.value == other.value

    def __lt__(self, other):
        return self.rank < other.rank

    def get(self):
        return self.value


class Variable:
    def __init__(self, id, size, row, col):
        self.id = id
        self.size = size
        self.row = row
        self.col = col
        self.assigned_value = None
        self.constraints = []
        self.domain = PriorityQueue()
        self.removed_values = []
        self.track = {}

    def push_to_removed(self, val, step):
        count = self.track.get(step, 0)
        self.track[step] = count + 1
        self.removed_values.append(val)

    def pop_from_removed(self, step):
        if step in self.track:
            for _ in range(self.track[step]):
                self.domain.put(self.removed_values.pop())
            del self.track[step]

    def set_constraint(self, constr):
        self.constraints.append(constr)

    def get_constraints(self):
        return self.constraints

    def set_domain(self):
        self.find_values(0, 0, None, [None] * self.size)

    def get_domain(self):
        return self.domain

    def print_domain(self):
        for value in self.domain.queue:
            print(value.value)

    def set_value(self, val):
        self.assigned_value = val

    def get_value(self):
        return self.assigned_value

    def find_values(self, index, constr_id, prev, val):
        if index < self.size:
            if constr_id < len(self.constraints):
                constr = self.constraints[constr_id]
                if constr.length + index <= self.size and (prev is None or (prev is not None and prev != constr.color)):
                    for i in range(constr.length):
                        val[index + i] = constr.color
                    self.find_values(index + constr.length,
                                     constr_id + 1, constr.color, val)
            val[index] = None
            self.find_values(index + 1, constr_id, None, val)
        else:
            if constr_id >= len(self.constraints):
                self.domain.put(Value(value=val.copy(), rank=0))

    def is_row(self):
        return self.row

    def is_col(self):
        return self.col

    def get_id(self):
        return self.id

    def __lt__(self, other):
        if HEURISTIC == "yes":
            return self.domain.qsize() < other.domain.qsize()
        else:
            return self.id < other.id
    
    def __str__(self):
        return f"Variable ID: {self.id}, Is row: {self.row}, Is col: {self.col}"


class CSPSolver:
    def __init__(self):
        self.variables = PriorityQueue()
        self.solutions = []
        self.nodes_explored = 0

    def solve_task(self):
        self.load_task()
        self.backtracking_search()
        self.print_solutions()

        print(f"Nodes explored: {self.nodes_explored}")


    def load_task(self):
        line_number = 0
        word = ""
        with open("input.txt", "r") as file:
            for line in file:
                word += line
        for line in word.split():
            line = line.strip().split(",")
            if line_number == 0:
                self.num_rows = int(line[0])
                self.num_cols = int(line[1])
                self.rows = [None] * self.num_rows
                self.cols = [None] * self.num_cols
            elif line_number > 0 and line_number <= self.num_rows:
                id = line_number - 1
                self.rows[id] = Variable(id, self.num_cols, True, False)
                for i in range(0, len(line), 2):
                    color = line[i][0]
                    length = int(line[i + 1])
                    self.rows[id].set_constraint(Constraint(length, color))
                self.rows[id].set_domain()
            elif line_number > self.num_rows and line_number <= self.num_rows + self.num_cols:
                id = line_number - self.num_rows - 1
                self.cols[id] = Variable(id, self.num_rows, False, True)
                for i in range(0, len(line), 2):
                    color = line[i][0]
                    length = int(line[i + 1])
                    self.cols[id].set_constraint(Constraint(length, color))
                self.cols[id].set_domain()

            line_number += 1
            if line_number > self.num_rows + self.num_cols:
                break

    def backtracking_search(self):
        self.recursive_backtracking(0)

    def recursive_backtracking(self, step):
        self.sort_variables()
        if self.variables.empty():
            self.add_solution()
            return

        var = self.variables.get()
        for val in var.get_domain().queue:
            self.nodes_explored += 1
            self.assign_value(var, val)
            if DEBUG == "yes":
                print(f"Step: {step}, Variable: {var}, Value: {val}")
            if self.forward_checking(var, step):
                self.recursive_backtracking(step + 1)
            self.step_back(step)
            self.assign_value(var, None)


    def sort_variables(self):
        while not self.variables.empty():
            self.variables.get()

        for row in self.rows:
            if row.get_value() is None:
                self.variables.put(row)

        for col in self.cols:
            if col.get_value() is None:
                self.variables.put(col)

    def assign_value(self, var, val):
        if var.is_row():
            self.rows[var.get_id()].set_value(val)
        if var.is_col():
            self.cols[var.get_id()].set_value(val)

    def forward_checking(self, var, step):
        if var.is_row():
            val_1 = self.rows[var.get_id()].get_value()
            for col in self.cols:
                if col.get_value() is None:
                    domain = list(col.get_domain().queue)
                    for val_2 in domain:
                        if val_1.get()[col.get_id()] != val_2.get()[var.get_id()]:
                            col.push_to_removed(val_2, step)
                            col.get_domain().queue.remove(val_2)
                    if not col.get_domain().queue:
                        return False
        if var.is_col():
            val_1 = self.cols[var.get_id()].get_value()
            for row in self.rows:
                if row.get_value() is None:
                    domain = list(row.get_domain().queue)
                    for val_2 in domain:
                        if val_1.get()[row.get_id()] != val_2.get()[var.get_id()]:
                            row.push_to_removed(val_2, step)
                            row.get_domain().queue.remove(val_2)
                    if not row.get_domain().queue:
                        return False
        return True

    def step_back(self, step):
        for col in self.cols:
            col.pop_from_removed(step)
        for row in self.rows:
            row.pop_from_removed(step)

    def add_solution(self):
        solution = ""
        for row in self.rows:
            solution += str(row.get_value().get()) + "\n"

        self.solutions.append(solution)

    def print_solutions(self):
        if DEBUG == "no":
            return
        if not self.solutions:
            print("null")
        else:
            for solution in self.solutions:
                solution = re.sub(r"None", "□", solution)
                solution = re.sub(r"[,\[\]']", "", solution)
                print(solution)

    class variable_comparator:
        def __lt__(self, other):
            if self.get_domain().queue.size() > other.get_domain().queue.size():
                return 1
            if self.get_domain().queue.size() < other.get_domain().queue.size():
                return -1
            return 0


def run_solver():
    solver = CSPSolver()
    start_time = time.time()
    solver.solve_task()
    end_time = time.time()
    print(f"Time elapsed: {end_time - start_time}")

if __name__ == "__main__":
    HEURISTIC = input("Use Heuristic? (yes/no): ")
    DEBUG = input("Print results? (yes/no): ")
    if DEBUG != "yes" and DEBUG != "no" or HEURISTIC != "yes" and HEURISTIC != "no":
        print("Wrong input")
        exit(1)
    
    # Crea un nuevo proceso para ejecutar el CSPSolver
    process = multiprocessing.Process(target=run_solver)
    process.start()
    pid = process.pid

    psutil_process = psutil.Process(pid)

    cpu_percent_list = []
    max_cpu_percent = 0
    while process.is_alive():
        current_cpu_percent = psutil_process.cpu_percent(interval=1)
        cpu_percent_list.append(current_cpu_percent)
        max_cpu_percent = max(max_cpu_percent, current_cpu_percent)
    process.join()

    avg_cpu_percent = sum(cpu_percent_list) / len(cpu_percent_list)
    print(f"Average CPU usage: {format(avg_cpu_percent, '.4f')}%")
    print(f"Maximum CPU usage: {format(max_cpu_percent, '.4f')}%")
# -*- coding: utf-8 -*-
import math, time
import sys
import matplotlib.pyplot as plt, numpy as np, pandas as pd


class Variable():
    def __init__(self,i,j):
        self.i = i
        self.j = j
    
    def __str__(self):
        return f"({self.i}, {self.j})"
    
class Sodoku():
    def __init__(self, structure_file, sodoku_string =None):
        if sodoku_string == None: 
            with open(structure_file) as f:
                self.content = f.readline().replace("\n", "")
        else:
            self.content = sodoku_string
            
        self.height = int(math.sqrt(len(self.content)))
        self.width = int(math.sqrt(len(self.content)))
        if pow(self.height, 2) != len(self.content):
            print("Incorrect Sodoku grid. must be a perfect square")
            raise ValueError("Incorrect Sodoku grid. must be a perfect square")
           
        self.variables = []
        for i in range(self.height):
            for j in range(self.width):
                self.variables.append(Variable(i=i,j=j))
            
                
            
        self.neighbours = {}
        for variable in self.variables:
            self.neighbours[variable] = []
            for possible_neighbour in self.variables:
                if possible_neighbour.i == variable.i and possible_neighbour.j == variable.j:
                    continue
                if possible_neighbour not in self.neighbours[variable]:
                    
                    if possible_neighbour.i == variable.i:
                        self.neighbours[variable].append(possible_neighbour)
                    if possible_neighbour.j == variable.j:
                        self.neighbours[variable].append(possible_neighbour)
            for x in range(0 - variable.i % 3, 3 - variable.i % 3):
                for y in range(0 - variable.j % 3, 3 - variable.j % 3):
                    for possible_neighbour in self.variables:
                        if possible_neighbour.i == variable.i and possible_neighbour.j == variable.j:
                            continue
                        if possible_neighbour not in self.neighbours[variable]:
                            if possible_neighbour.i == variable.i+x and possible_neighbour.j == variable.j+y:
                                self.neighbours[variable].append(possible_neighbour)
    


class Sodoku_Solver():
    def __init__(self,game):
        self.sodoku = game
        self.domains = {}
        self.init_assignment = {}
        for var in self.sodoku.variables:
            self.init_assignment[var] = (self.sodoku.content[var.i * 9 + var.j])
            if int(self.sodoku.content[self.sodoku.height*var.i + var.j]) != 0:
                self.domains[var] = [int(self.sodoku.content[self.sodoku.height*var.i + var.j])]
            else:
                self.domains[var] = [1,2,3,4,5,6,7,8,9]
        self.time_revise = 0
        self.time_ac3 = 0
        self.time_select_value = 0
        self.time_select_var = 0
        self.time_consistent = 0
        self.time_complete = 0
        self.time_backtrack = 0
        
        
        self.display(self.init_assignment)
        
            
    def display(self, data):
        data_map={}
        data = dict(sorted(data.items(), key=lambda item: (item[0].i, item[0].j)))
        for var in data:
            x,y = var.i,var.j
            if not y in  data_map:
                data_map[y] = [int(data[var])]
            else:
                data_map[y].append(int(data[var]))
        data_map = pd.DataFrame(data_map)
        
        plt.matshow(data_map)
        
        for (x, y), value in np.ndenumerate(data_map):
            plt.text(y, x, f"{value}")
    
    
            
    def Solve(self):
        """initialises the known values in the sodoku then solves the Sodoku
        Return the final assignment or None if not possible
        """
               
        self.ac3()
        return self.backtrack(dict())
    
         
    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        self.time_revise -= time.time()
        revised = False       
        if y in self.sodoku.neighbours[x]:
            if len(self.domains[y]) == 1:
                if self.domains[y][0] in self.domains[x]:
                    self.domains[x].remove(self.domains[y][0])
                    
                    revised = True  
        self.time_revise += time.time()
        return revised
        
    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        self.time_ac3 -= time.time()

        queue = set()
        if arcs == None:
            for var in self.domains:
                for neighbour in self.sodoku.neighbours[var]:
                    queue.add((var,neighbour))
        else:
            queue = arcs
            
        while len(queue) != 0:
            arc = queue.pop()
            """if arc[0] not in self.domains
                return False"""
            if self.revise(arc[0],arc[1]):
                if len(self.domains[arc[0]]) == 0:
                    self.time_ac3 += time.time()
                    return False
                
                for neighbour in self.sodoku.neighbours[arc[0]]:
                    queue.add((neighbour,arc[0]))
        self.time_ac3 += time.time()
        return True
        
        
        
        
    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., every sodoku variable (cell) is assigned a value);
        return False otherwise.
        """
        
        self.time_complete -= time.time()
        if len(self.domains) == len(assignment):
            if self.consistent(assignment):
                self.time_complete += time.time()
                return True
        self.time_complete += time.time()
        return False
        

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., all values assigned to cells
        without any repeats among neighbours); return False otherwise.
        """
        self.time_consistent -= time.time()
        
        for var in assignment:
            for neighbour in self.sodoku.neighbours[var]:
                if neighbour in assignment:
                    if int(assignment[var]) == int(assignment[neighbour]):
                        self.time_consistent += time.time()
                        return False 
        self.time_consistent += time.time()
        
        return True
        
        
        
    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        self.time_select_value -= time.time()

        ordered_values = []
        counts = []
        for value in self.domains[var]:
            ordered_values.append(value)
            local_count = 0
            neighbours = self.sodoku.neighbours[var]
            for neighbour in neighbours:
                               
                if value in self.domains[neighbour]:
                    local_count -=1
            counts.append(local_count)
          
        ordered_values = [value for count,value in sorted(zip(counts,ordered_values))]
        self.time_select_value += time.time()
        return ordered_values
        
        
        
    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        self.time_select_var -= time.time()
        min_count = 1000
        for var in self.domains:
            if var not in assignment:
                if len(self.domains[var]) < min_count:
                    min_count = len(self.domains[var])
                    variable = var
                elif len(self.domains[var]) == min_count:
                    if len(self.sodoku.neighbours[var]) > len(self.sodoku.neighbours[variable]):
                        variable = var
                   
        self.time_select_var += time.time()       
        return variable
        
        
    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        self.time_backtrack -= time.time()
        if self.assignment_complete(assignment):
            self.time_backtrack += time.time()
            return assignment
        
        var = self.select_unassigned_variable(assignment)
        for value in self.order_domain_values(var, assignment):          
            assignment[var] = value
            
            if self.consistent(assignment):
                arcs = set()
                for neighbour in self.sodoku.neighbours[var]:
                    arcs.add((neighbour,var))
                
                if self.ac3(arcs):
                    self.time_backtrack += time.time()
                    result = self.backtrack(assignment)
                    self.time_backtrack -= time.time()
                    if result:
                        self.time_backtrack += time.time()
                        return result

            del assignment[var]

        self.time_backtrack += time.time()    
        return False
            
def main():
    start_time = time.time()
    easy = "53..7....6..195....98....6.8...6...34..8.3..17...2...6.6....28....419..5....8..79".replace(".",'0')
    hard = "8..........36......7..9.2...5...7.......457.....1...3...1....68..85...1..9....4..".replace(".","0")
    inkala = "800000000003600000070090200050007000000045700000100030001000068008500010090000400"
    
    if len(sys.argv) != 2:
        sys.exit("Usage: python Generate.py structure.txt")
        
    structure = sys.argv[1]   
    game = Sodoku(structure)
    time_1 = time.time()
    creator = Sodoku_Solver(game)
    time_2 = time.time()
    assignment = creator.Solve()
    time_3 = time.time()
    print(f"time to load game: {time_1-start_time}")
    print(f"time to create creator:  {time_2-time_1}")
    print(f"time to solve:   {time_3-time_2}")
    print(f"total time to make+solve:   {time_3-start_time}")
    print("time in Revise:  ",creator.time_revise)
    print("time in ac3:  ", creator.time_ac3)
    print("time in select Value:  ", creator.time_select_value)
    print("time in select VAR:  ", creator.time_select_var)
    print("time in backtrack:  ", creator.time_backtrack)
    print("time to consistent:  ",  creator.time_consistent)
    print("time to check complete:  ",  creator.time_complete)
    
    if assignment is None:
        print("No solution.")
    else:
        creator.display(assignment)
    
               
if __name__ == "__main__":
    main()            
"""start_time = time.time()
easy = "53..7....6..195....98....6.8...6...34..8.3..17...2...6.6....28....419..5....8..79".replace(".",'0')
hard = "8..........36......7..9.2...5...7.......457.....1...3...1....68..85...1..9....4..".replace(".","0")
inkala = "800000000003600000070090200050007000000045700000100030001000068008500010090000400"
game = Sodoku("Sodokus/hard_sodoku.txt")
time_1 = time.time()

creator = Sodoku_Solver(game)

time_2 = time.time()
assignment = creator.Solve()
time_3 = time.time()
print(f"time to load game: {time_1-start_time}")
print(f"time to create creator:  {time_2-time_1}")
print(f"time to solve:   {time_3-time_2}")
print(f"total time to make+solve:   {time_3-start_time}")
print("time in Revise:  ",creator.time_revise)
print("time in ac3:  ", creator.time_ac3)
print("time in select Value:  ", creator.time_select_value)
print("time in select VAR:  ", creator.time_select_var)
print("time in backtrack:  ", creator.time_backtrack)
print("time to consistent:  ",  creator.time_consistent)
print("time to check complete:  ",  creator.time_complete)

if assignment:
    creator.display(assignment)
    time_4 = time.time()
    print("time to display:  ", time_4-time_3)
    
else:
    print("NO Solution")
            
hi = "53..7....6..195....98....6.8...6...34..8.3..17...2...6.6....28....419..5....8..79".replace(".",'0')          
"""
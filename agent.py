from collections import deque
from knowledgebase import KnowledgeBase

class Agent:
    def __init__(self):
        self.kb = KnowledgeBase()
        self.position = (0, 0)
        self.start_position = (0, 0)
        self.score = 0
        self.hp = 100
        self.direction = 'RIGHT'
        self.visited = set()
        self.grid_size = 10
        self.graphic = 0
        self.queue = deque()
        self.queue.append(self.position)
        self.visited.add(self.position)
        self.path = [(0, 0)]
        self.action_log = []

    def move_forward(self):
        new_position = self.get_new_position(self.direction)
        if self.is_valid_position(new_position) and not self.is_pit(new_position):
            self.position = new_position
            self.visited.add(self.position)
            self.queue.append(self.position)
            self.path.append(self.position)
            self.check_cell()
            print(f"Moved {self.direction} to {self.position}")
            self.log_action(f"{self.position}: moveforward ")
            self.apply_percept(self.graphic[new_position[0]][new_position[1]])
        else:
            print(f"Cannot move {self.direction} to {new_position}. It's either invalid or contains a pit.")

    def get_new_position(self, direction):
        """Return new position based on current direction."""
        x, y = self.position
        if direction == 'UP':
            return (x - 1, y)
        elif direction == 'DOWN':
            return (x + 1, y)
        elif direction == 'LEFT':
            return (x, y - 1)
        elif direction == 'RIGHT':
            return (x, y + 1)
        else:
            raise ValueError("Invalid direction")
        


    def check_cell(self):
        x, y = self.position
        cell_content = self.graphic[x][y]
        if 'P_G' in cell_content:
            self.hp -= 25
            self.log_action(f"{self.position}: -25 hp, HP: {self.hp}")
        if 'H_P' in cell_content:
            self.collect_healing_potion()
        if 'G' in cell_content:
            self.collect_gold()
        if 'W' in cell_content:
            self.score -= 10000
        if 'P' in cell_content:
            self.score -= 10000
        

    def collect_healing_potion(self):
        self.hp = min(self.hp + 25, 100) 
        self.score -= 10
        print(f"{self.position}: collected healing potion, HP: {self.hp}")
        self.log_action(f"{self.position}: collected healing potion")
        self.remove_glow_around(self.position)
        self.graphic[self.position[0]][self.position[1]].remove('H_P')# Update the display to reflect the change

    def collect_gold(self):
        self.score += 5000  # Example score increment
        print(f"{self.position}: collected gold, Score: {self.score}")
        self.log_action(f"{self.position}: collected gold")
        self.graphic[self.position[0]][self.position[1]].remove('G')

    def shoot(self):
        """Decide whether to shoot based on the KnowledgeBase and update the grid if a Wumpus is detected."""
        front_position = self.get_new_position(self.direction)
        if 'W' in self.graphic[front_position[0]][front_position[1]]:
            self.graphic[front_position[0]][front_position[1]].remove('W')
            self.log_action(f"{self.position}: shot Wumpus")
        self.update_stench_info()
        self.remove_stench_around(front_position)
        print(f"Shooting Wumpus at {front_position}")
        self.score -= 100        
        print(f"Shot fired, Score: {self.score}")   

    def turn_right(self):
        directions = ['UP', 'RIGHT', 'DOWN', 'LEFT']
        self.direction = directions[(directions.index(self.direction) + 1) % 4]
        self.score -= 10
        print(f"{self.position}: turn right")
        self.action_log.append(f"{self.position}: turn right")

    def turn_left(self):
        directions = ['UP', 'LEFT', 'DOWN', 'RIGHT']
        self.direction = directions[(directions.index(self.direction) + 1) % 4]
        self.score -= 10
        print(f"{self.position}: turn left")
        self.action_log.append(f"{self.position}: turn left")

    def is_valid_position(self, position):
        x, y = position
        return 0 <= x < self.grid_size and 0 <= y < self.grid_size

    def decide_action(self):

        # 1. Check if Wumpus is definitely in front
        front_position = self.get_new_position(self.direction)
        if self.kb.query(f"Wumpus at {front_position}"):
            self.shoot()
            self.move_forward()
            return

        # 2. Check if the agent has reached a goal or needs to return
        if 'G' in self.graphic[self.position[0]][self.position[1]]:
            self.collect_gold()
            return 

        # 3. Check if there is a pit nearby
        if self.kb.query(f"Pit at {self.position}"):
            self.avoid_pit()
            return

        # Move forward if possible
        next_position = self.get_new_position(self.direction)
        if self.is_valid_position(next_position) and next_position not in self.visited and not self.is_pit(next_position):
            self.move_forward()
            return

        # Try turning right
        self.turn_right()
        next_position = self.get_new_position(self.direction)
        if self.is_valid_position(next_position) and next_position not in self.visited and not self.is_pit(next_position):
            self.move_forward()
            return

        # Try turning left twice (180 degrees)
        self.turn_left()
        self.turn_left()
        next_position = self.get_new_position(self.direction)
        if self.is_valid_position(next_position) and next_position not in self.visited and not self.is_pit(next_position):
            self.move_forward()
            return

        # If all options fail, handle dead-end
        print("No valid move. Backtracking or other strategy required.")
        self.handle_dead_end()

    def avoid_pit(self):
        directions = ['UP', 'RIGHT', 'DOWN', 'LEFT']
        original_direction = self.direction

        for direction in directions:
            if direction != original_direction:
                next_position = self.get_new_position(direction)
                if self.is_valid_position(next_position) and next_position not in self.visited and not self.is_pit(next_position):
                    # Move in this direction if it is not a pit and not visited
                    self.direction = direction
                    self.move_forward()
                    return

        # If no valid move was found, handle dead-end or backtrack
        print("No valid moves available to avoid pit. Handling dead-end.")
        self.handle_dead_end()

    def is_pit(self, position):
        x, y = position
        return 'P' in self.graphic[x][y]
            

    def handle_dead_end(self):

        if self.path:
            prev_position = self.path.pop()
            self.position = prev_position
            print(f"Backtracking to {self.position}")      
        if self.position == self.start_position:
            print("Returned to start position. Game over.")
            self.update_log_file()
            return
    def apply_percept(self, percepts):
        
        for percept in percepts:
            print(percept)
            if percept == 'S':
                self.kb.add_fact(f"Stench at {self.position}")
                self.add_stench_rules()
            elif percept == 'B':
                self.kb.add_fact(f"Breeze at {self.position}")
                self.add_breeze_rules()
            elif percept == 'W_H':
                self.kb.add_fact(f"Whiff at {self.position}")
                self.add_whiff_rules()
            elif percept == 'G':
                self.kb.add_fact(f"Glow at {self.position}")
                self.add_glow_rules()

    def add_breeze_rules(self):
        x, y = self.position
        directions = {
            'UP': [(x-1, y), (x, y-1), (x, y+1)],
            'DOWN': [(x+1, y), (x, y-1), (x, y+1)],
            'LEFT': [(x, y-1), (x-1, y), (x+1, y)],
            'RIGHT': [(x, y+1), (x-1, y), (x+1, y)]
        }
        for px, py in directions[self.direction]:
            if self.is_valid_position((px, py)):
                self.kb.add_implication(f"Breeze at {self.position}", f"Pit at {(px, py)}")

    def add_stench_rules(self):
        x, y = self.position
        directions = {
            'UP': [(x-1, y), (x, y-1), (x, y+1)],
            'DOWN': [(x+1, y), (x, y-1), (x, y+1)],
            'LEFT': [(x, y-1), (x-1, y), (x+1, y)],
            'RIGHT': [(x, y+1), (x-1, y), (x+1, y)]
        }
        for px, py in directions[self.direction]:
            if self.is_valid_position((px, py)):
                self.kb.add_implication(f"Stench at {self.position}", f"Wumpus at {(px, py)}")

    def add_whiff_rules(self):
        x, y = self.position
        directions = {
            'UP': [(x-1, y), (x, y-1), (x, y+1)],
            'DOWN': [(x+1, y), (x, y-1), (x, y+1)],
            'LEFT': [(x, y-1), (x-1, y), (x+1, y)],
            'RIGHT': [(x, y+1), (x-1, y), (x+1, y)]
        }
        for px, py in directions[self.direction]:
            if self.is_valid_position((px, py)):
                self.kb.add_implication(f"Whiff at {self.position}", f"Gas at {(px, py)}")

    def add_glow_rules(self):
        x, y = self.position
        directions = {
            'UP': [(x-1, y), (x, y-1), (x, y+1)],
            'DOWN': [(x+1, y), (x, y-1), (x, y+1)],
            'LEFT': [(x, y-1), (x-1, y), (x+1, y)],
            'RIGHT': [(x, y+1), (x-1, y), (x+1, y)]
        }
        for px, py in directions[self.direction]:
            if self.is_valid_position((px, py)):
                self.kb.add_implication(f"Glow at {self.position}", f"Potion at {(px, py)}")

    def update_stench_info(self):
        x, y = self.position
        adjacent_positions = [
            (x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)
        ]
        if not self.kb.query(f"Stench at {self.position}"):
            # No stench detected, so there should be no Wumpus in adjacent cells
            for pos in adjacent_positions:
                if self.is_valid_position(pos):
                    self.kb.remove_fact(f"Wumpus at {pos}")

    def update_gas_info(self):
        x, y = self.position
        directions = {
            'UP': [(x-1, y), (x, y-1), (x, y+1)],
            'DOWN': [(x+1, y), (x, y-1), (x, y+1)],
            'LEFT': [(x, y-1), (x-1, y), (x+1, y)],
            'RIGHT': [(x, y+1), (x-1, y), (x+1, y)]
        }
        for px, py in directions[self.direction]:
            if not self.kb.query(f"Whiff at {self.position}"):
                self.kb.remove_fact(f"Gas at {(px, py)}")

    def update_pit_info(self):
        x, y = self.position
        directions = {
            'UP': [(x-1, y), (x, y-1), (x, y+1)],
            'DOWN': [(x+1, y), (x, y-1), (x, y+1)],
            'LEFT': [(x, y-1), (x-1, y), (x+1, y)],
            'RIGHT': [(x, y+1), (x-1, y), (x+1, y)]
        }
        for px, py in directions[self.direction]:
            if not self.kb.query(f"Breeze at {self.position}"):
                self.kb.remove_fact(f"Pit at {(px, py)}")

    def update_potion_info(self):
        x, y = self.position
        directions = {
            'UP': [(x-1, y), (x, y-1), (x, y+1)],
            'DOWN': [(x+1, y), (x, y-1), (x, y+1)],
            'LEFT': [(x, y-1), (x-1, y), (x+1, y)],
            'RIGHT': [(x, y+1), (x-1, y), (x+1, y)]
        }
        for pos in directions[self.direction]:
            if not self.kb.query(f"Glow at {pos}"):
                self.kb.remove_fact(f"Potion at {pos}")
    def update_knowledge_base(self):
        self.update_stench_info()
        self.update_gas_info()
        self.update_pit_info()
        self.update_potion_info()
    def remove_stench_around(self, position):
        x, y = position
        adjacent_positions = [
            (x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)
        ]
        for pos in adjacent_positions:
            if self.is_valid_position(pos):
                if 'S' in self.graphic[pos[0]][pos[1]]:
                    self.graphic[pos[0]][pos[1]].remove('S')

    def remove_glow_around(self, position):
        x, y = position
        adjacent_positions = [
            (x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)
        ]
        for pos in adjacent_positions:
            if self.is_valid_position(pos):
                if 'G_L' in self.graphic[pos[0]][pos[1]]:
                    self.graphic[pos[0]][pos[1]].remove('G_L')

    def log_action(self, message):
        self.action_log.append(message)
        self.update_log_file()

    def update_log_file(self):
        with open("output.txt", "w") as file:
            for log in self.action_log:
                file.write(f"{log}\n")
            file.write(f"Score: {self.score}\n")
            file.write(f"Hp: {self.hp}\n")
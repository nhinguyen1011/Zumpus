import pygame
import sys
from agent import Agent
class Graphic:
    def __init__(self, file_path):
        self.N, self.grid = self.read_input(file_path)
        self.cell_size = 60
        self.grid_size = self.N * self.cell_size
        self.sidebar_width = 200 
        self.window_width = self.grid_size + self.sidebar_width
        self.window_height = self.grid_size
        self.screen = None
        self.elements = {}
        self.agent = Agent()
        self.agent_position = self.agent.position
        self.start_position = self.agent.position 
        self.action_log = []

        # Initialize Pygame
        pygame.init()
        self.screen = pygame.display.set_mode((self.window_width, self.window_height))
        pygame.display.set_caption('Wumpus World')
        self.font = pygame.freetype.SysFont('Arial', 20, bold=True)
        # Load assets
        self.load_assets()

        # Update percepts
        self.update_percepts()

        # Load actions from the output file
        self.load_actions('output.txt')

    def read_input(self, file_path):
        with open(file_path, 'r') as f:
            lines = f.readlines()

        N = int(lines[0].strip())  # First line is the grid size
        grid = [[cell.split(',') if cell != '-' else [] for cell in line.strip().split('.')] for line in lines[1:]]
        return N, grid
    def load_actions(self, file_path):
        with open(file_path, 'r') as f:
            lines = f.readlines()

        self.action_log = [line.strip() for line in lines if line.strip()]
    def draw_agent(self):
        direction_asset = self.elements.get(self.agent.direction, self.elements['RIGHT'])
        agent_x, agent_y = self.agent.position
        self.screen.blit(direction_asset, (agent_y * self.cell_size, agent_x * self.cell_size))
        self.agent.decide_action()
    def draw_agent_pause(self):
        direction_asset = self.elements.get(self.agent.direction, self.elements['RIGHT'])
        agent_x, agent_y = self.agent.position
        self.screen.blit(direction_asset, (agent_y * self.cell_size, agent_x * self.cell_size))

    def update_agent(self):
        self.agent_position = self.agent.position

    def load_assets(self):
        self.elements['W'] = pygame.image.load('./asset/wumpus.png')
        self.elements['G'] = pygame.image.load('./asset/gold.png')
        self.elements['P'] = pygame.image.load('./asset/pit.png')
        self.elements['P_G'] = pygame.image.load('./asset/gas.png')
        self.elements['H_P'] = pygame.image.load('./asset/potion.png')

        self.elements['UP'] = pygame.image.load('./asset/agent_up.png')
        self.elements['DOWN'] = pygame.image.load('./asset/agent_down.png')
        self.elements['LEFT'] = pygame.image.load('./asset/agent_left.png')
        self.elements['RIGHT'] = pygame.image.load('./asset/agent_right.png')

        self.elements['S'] = pygame.Surface((self.cell_size // 0.5, self.cell_size // 0.5), pygame.SRCALPHA)
        self.elements['B'] = pygame.Surface((self.cell_size // 0.5, self.cell_size // 0.5), pygame.SRCALPHA)
        self.elements['W_H'] = pygame.Surface((self.cell_size // 0.5, self.cell_size // 0.5), pygame.SRCALPHA)
        self.elements['G_L'] = pygame.Surface((self.cell_size // 0.5, self.cell_size // 0.5), pygame.SRCALPHA)

        self.font.size = 20 
        self.font.render_to(self.elements['S'], (5, 5), 'S', (0, 0, 0))  # Top-left corner
        self.font.render_to(self.elements['B'], (self.cell_size*1.5 - 5, 0), 'B', (0, 0, 0))  # Top-right corner
        self.font.render_to(self.elements['W_H'], (5, self.cell_size*1.5 - 5), 'W_H', (0, 0, 0))  # Bottom-left corner
        self.font.render_to(self.elements['G_L'], (self.cell_size*1.5 - 5, self.cell_size*1.5 - 5), 'G_L', (0, 0, 0))  # Bottom-right corner
        
        for key in self.elements:
            self.elements[key] = pygame.transform.scale(self.elements[key], (self.cell_size, self.cell_size))

    def update_percepts(self):
        for x in range(self.N):
            for y in range(self.N):
                cell_content = self.grid[x][y]
                if 'W' in cell_content:
                    self.apply_stench(x, y)
                if 'P' in cell_content:
                    self.apply_breeze(x, y)
                if 'P_G' in cell_content:
                    self.apply_whiff(x, y)
                if 'H_P' in cell_content:
                    self.apply_glow(x, y)

    def apply_stench(self, x, y):
        self.apply_percept(x, y, 'S')

    def apply_breeze(self, x, y):
        self.apply_percept(x, y, 'B')

    def apply_whiff(self, x, y):
        self.apply_percept(x, y, 'W_H')

    def apply_glow(self, x, y):
        self.apply_percept(x, y, 'G_L')

    def apply_percept(self, x, y, percept):
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.N and 0 <= ny < self.N:
                if percept not in self.grid[nx][ny]:
                    self.grid[nx][ny].append(percept)

    def draw_grid(self):
        for x in range(self.N):
            for y in range(self.N):
                rect = pygame.Rect(y * self.cell_size, x * self.cell_size, self.cell_size, self.cell_size)
                pygame.draw.rect(self.screen, (0, 0, 0), rect, 1)
                cell_content = self.grid[x][y]
                for element in cell_content:
                    if element in self.elements:
                        self.screen.blit(self.elements[element], (y * self.cell_size, x * self.cell_size))
        self.draw_agent()
    def draw_grid_pause(self):
        for x in range(self.N):
            for y in range(self.N):
                rect = pygame.Rect(y * self.cell_size, x * self.cell_size, self.cell_size, self.cell_size)
                pygame.draw.rect(self.screen, (0, 0, 0), rect, 1)
                cell_content = self.grid[x][y]
                for element in cell_content:
                    if element in self.elements:
                        self.screen.blit(self.elements[element], (y * self.cell_size, x * self.cell_size))
        self.draw_agent_pause()
    def display_actions(self):
        log_width = 200
        log_height = self.window_height
        x_offset = self.grid_size
        y_offset = 10
        self.screen.fill((255, 255, 255), rect=pygame.Rect(x_offset, 0, log_width, log_height))
        action_log = self.agent.action_log
        log_length = len(action_log)
        
        visible_lines = log_height // 25 
        scroll_start = max(0, log_length - visible_lines) 
        scroll_end = log_length 

        for i in range(scroll_start, scroll_end):
            action = action_log[i]
            self.font.render_to(self.screen, (x_offset + 10, y_offset), action, (0, 0, 0))
            y_offset += 25

        # Draw a scrollbar if necessary
        if log_length > visible_lines:
            scrollbar_height = (log_height / log_length) * log_height
            scrollbar_y = (scroll_start / log_length) * log_height
            scrollbar_rect = pygame.Rect(x_offset + log_width - 10, scrollbar_y, 10, scrollbar_height)
            pygame.draw.rect(self.screen, (0, 0, 0), scrollbar_rect)
    def display_score(self):
        # Draw the score in the sidebar
        score_text = f"Score: {self.agent.score}"
        hp_text = f"HP: {self.agent.hp}"
        self.font.size = 30
        score_position = (self.grid_size + 10, 20)
        hp_text_position = (self.grid_size + 10, 50)
        
        self.screen.fill((255, 255, 255), rect=pygame.Rect(self.grid_size, 0, self.sidebar_width, self.window_height))  # Clear the sidebar area
        self.font.render_to(self.screen, score_position, score_text, (0, 0, 0))
        self.font.render_to(self.screen, hp_text_position, hp_text, (0, 0, 0))
    def run_game(self):
        running = True
        flag = True
        clock = pygame.time.Clock()
        self.agent.graphic = self.grid
        self.agent.apply_percept(self.agent.graphic[0][0])
        print(self.agent.graphic[0][0])

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            self.update_agent()
            self.screen.fill((255, 255, 255))
            
            if(flag):
                self.draw_grid()
                self.display_actions()
            else:
                self.draw_grid_pause()
                self.display_actions()
                self.display_score()
            if self.agent.position == self.start_position:
                flag = False
            pygame.display.flip()
            clock.tick(50)



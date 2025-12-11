import pygame
from board import Board
from player import Player
import os

class QuoridorGUI:
    def __init__(self, board, players):
        pygame.init()
        self.board = board
        self.players = players
        self.screen = pygame.display.set_mode((1150, 800))
        pygame.display.set_caption("Quoridor")
        self.cell_size = 60
        self.running = True
        self.current_player_idx = 0
        ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets")
        self.pawn_p1_img = pygame.image.load(os.path.join(ASSETS_DIR, "monster2.png"))
        self.pawn_p2_img = pygame.image.load(os.path.join(ASSETS_DIR, "monster3.png"))

        pawn_size = int(self.cell_size * 0.8)
        self.pawn_p1_img = pygame.transform.scale(self.pawn_p1_img, (pawn_size, pawn_size))
        self.pawn_p2_img = pygame.transform.scale(self.pawn_p2_img, (pawn_size, pawn_size))
        self.pawn_size = pawn_size

        self.player1_icon = pygame.image.load(os.path.join(ASSETS_DIR, "BlueHuman.png")).convert_alpha()
        self.player2_icon = pygame.image.load(os.path.join(ASSETS_DIR, "RedHuman.png")).convert_alpha()

        self.player1_icon = pygame.transform.scale(self.player1_icon, (80, 80))
        self.player2_icon = pygame.transform.scale(self.player2_icon, (80, 80))

        self.font = pygame.font.SysFont("arial", 28, bold=True)
        self.text_color = (255, 255, 255)

        self.ui_font = pygame.font.SysFont("arial", 30, bold=True)

        self.button_reset = Button(
            x=60, y=720, w=180, h=50,
            text="Reset Game",
            font=self.ui_font,
            bg_color=(30, 140, 230),
            text_color=(255, 255, 255)
        )

        self.button_quit = Button(
            x=900, y=720, w=180, h=50,
            text="Quit",
            font=self.ui_font,
            bg_color=(200, 50, 50),
            text_color=(255, 255, 255)
        )

    def draw_players_icons(self):
        x1 = 80
        y1 = 20
        x2 = self.screen.get_width() - 160
        y2 = 20
        self.screen.blit(self.player1_icon, (x1, y1))
        self.screen.blit(self.player2_icon, (x2, y2))
        label1 = self.font.render("Player 1", True, self.text_color)
        label2 = self.font.render("Player 2", True, self.text_color)

        text_x1 = x1 + (self.player1_icon.get_width() - label1.get_width()) // 2
        text_y1 = y1 + self.player1_icon.get_height() + 5

        text_x2 = x2 + (self.player2_icon.get_width() - label2.get_width()) // 2
        text_y2 = y2 + self.player2_icon.get_height() + 5

        self.screen.blit(label1, (text_x1, text_y1))
        self.screen.blit(label2, (text_x2, text_y2))

        self.button_reset.draw(self.screen)
        self.button_quit.draw(self.screen)
        
    def draw_pawn(self, image, x, y):
        px = (x + 5) * self.cell_size + (self.cell_size - self.pawn_size) // 2
        py = (y + 2) * self.cell_size + (self.cell_size - self.pawn_size) // 2
        self.screen.blit(image, (px, py))

    def write_turn(self):
        label1 = self.font.render("Turn", True, self.text_color)
        self.screen.blit(label1, ((self.screen.get_width()/2)-30, 30))

    def write_walls_left(self):
        label1 = self.font.render("Walls left:", True, self.text_color)
        label2 = self.font.render("Walls left:", True, self.text_color)
        self.screen.blit(label1, (60, 200))
        self.screen.blit(label2, (self.screen.get_width()-190, 200))
        
    def draw_board(self):
        self.screen.fill((80, 50, 150))
        # Draw grid
        for x in range(5,self.board.size+5):
            for y in range(2,self.board.size+2):
                rect = pygame.Rect(x*self.cell_size, y*self.cell_size, self.cell_size, self.cell_size)
                pygame.draw.rect(self.screen, (0,0,0), rect, 3)

        p1_x, p1_y = self.board.pawns["Player1"]
        p2_x, p2_y = self.board.pawns["Player2"]

        self.draw_pawn(self.pawn_p1_img, p1_x, p1_y)
        self.draw_pawn(self.pawn_p2_img, p2_x, p2_y)
        self.draw_players_icons()
        self.write_turn()
        self.write_walls_left()
        
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

    def game_loop(self):
        while self.running:
            self.handle_events()
            self.draw_board()
            pygame.display.flip()

if __name__ == "__main__":
    board = Board()
    players = [Player("Player1"), Player("Player2", is_ai=True)]
    gui = QuoridorGUI(board, players)
    gui.game_loop()



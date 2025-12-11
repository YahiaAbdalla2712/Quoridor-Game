import pygame
from sympy import false

from board import Board
from player import Player
from button import Button
import os

class QuoridorGUI:
    is_ai = False
    def __init__(self, board, players):
        pygame.init()
        self.state = "menu"
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

        self.button_return = Button(
            x=self.screen.get_width()-230, y=720, w=180, h=50,
            text="Return",
            font=self.ui_font,
            bg_color=(200, 50, 50),
            text_color=(255, 255, 255)
        )

        self.wall_icon = pygame.image.load(os.path.join(ASSETS_DIR, "wall.png")).convert_alpha()
        self.wall_icon = pygame.transform.scale(self.wall_icon, (120, 40))
        self.wall_icon_v = pygame.transform.rotate(self.wall_icon, 90)

        self.button_horizontal_1 = Button(
            x=60, y=300, w=180, h=50,
            text= "Add Wall ",
            font=self.ui_font,
            bg_color=(30, 140, 230),
            text_color=(255, 255, 255),
            icon=self.wall_icon,
            icon_size=45
        )

        self.button_vertical_1 = Button(
            x=60, y=400, w=180, h=50,
            text="Add Wall ",
            font=self.ui_font,
            bg_color=(30, 140, 230),
            text_color=(255, 255, 255),
            icon=self.wall_icon_v,
            icon_size=45
        )

        self.button_horizontal_2 = Button(
            x=self.screen.get_width()-230, y=300, w=180, h=50,
            text="Add Wall ",
            font=self.ui_font,
            bg_color=(200, 50, 50),
            text_color=(255, 255, 255),
            icon=self.wall_icon,
            icon_size=45
        )

        self.button_vertical_2 = Button(
            x=self.screen.get_width()-230, y=400, w=180, h=50,
            text="Add Wall ",
            font=self.ui_font,
            bg_color=(200, 50, 50),
            text_color=(255, 255, 255),
            icon=self.wall_icon_v,
            icon_size=45
        )

        self.button_vshuman = Button(
            x=230, y=300, w=250, h=150,
            text="VS Player",
            font=self.ui_font,
            bg_color=(200, 50, 50),
            text_color=(255, 255, 255),
        )

        self.button_vsAI = Button(
            x=self.screen.get_width() - 480, y=300, w=250, h=150,
            text="VS AI",
            font=self.ui_font,
            bg_color=(200, 50, 50),
            text_color=(255, 255, 255),
        )

    def draw_menu(self):
        self.screen.fill((30, 10, 70))
        title_font = pygame.font.Font(None, 70)
        title = title_font.render("Quoridor", True, (255, 255, 255))
        self.screen.blit(title, (450, 120))

        self.button_vshuman.draw(self.screen)
        self.button_vsAI.draw(self.screen)

    def draw_players_icons(self):
        x1 = 80
        y1 = 20
        x2 = self.screen.get_width() - 160
        y2 = 20
        self.screen.blit(self.player1_icon, (x1, y1))
        self.screen.blit(self.player2_icon, (x2, y2))
        label1 = self.font.render("Player 1", True, self.text_color)
        label2 = ""
        if self.state == "game":
            label2 = self.font.render("Player 2", True, self.text_color)
        elif self.state == "gameai":
            label2 = self.font.render("AI", True, self.text_color)

        text_x1 = x1 + (self.player1_icon.get_width() - label1.get_width()) // 2
        text_y1 = y1 + self.player1_icon.get_height() + 5

        text_x2 = x2 + (self.player2_icon.get_width() - label2.get_width()) // 2
        text_y2 = y2 + self.player2_icon.get_height() + 5

        self.screen.blit(label1, (text_x1, text_y1))
        self.screen.blit(label2, (text_x2, text_y2))



    def add_buttons(self):
        self.button_reset.draw(self.screen)
        self.button_return.draw(self.screen)
        self.button_horizontal_1.draw(self.screen)
        self.button_vertical_1.draw(self.screen)
        if self.state == "game":
            self.button_horizontal_2.draw(self.screen)
            self.button_vertical_2.draw(self.screen)

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
        self.add_buttons()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = event.pos

                if self.state == "menu":
                    if self.button_vshuman.is_clicked(pos):
                        print("Start Game")
                        self.state = "game"
                        QuoridorGUI.is_ai = False

                    if self.button_vsAI.is_clicked(pos):
                        print("VS AI")
                        self.state = "gameai"
                        QuoridorGUI.is_ai = True

                elif self.state == "game":
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        pos = event.pos
                        if self.button_return.is_clicked(pos):
                            self.state = "menu"
                    pass
                elif self.state == "gameai":
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        pos = event.pos
                        if self.button_return.is_clicked(pos):
                            self.state = "menu"
                    pass
    def game_loop(self):
        while self.running:
            self.handle_events()
            if self.state == "menu":
                self.draw_menu()
            elif self.state == "game" or self.state == "gameai":
                self.draw_board()
            pygame.display.flip()

if __name__ == "__main__":
    board = Board()
    players = [Player("Player1"), Player("Player2",QuoridorGUI.is_ai)]
    gui = QuoridorGUI(board, players)
    gui.game_loop()

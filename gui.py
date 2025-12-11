import pygame
from sympy import false
from board import Board
from player import Player
from button import Button
import random
import os

class QuoridorGUI:
    is_ai = False
    turn = random.randint(1,2)
    is_finished = False

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

        self.placing_wall = False
        self.placing_wall_type = None
        self.wall_preview_pos = (0, 0)

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
        self.board.pawns = {
            "Player1": (0, self.board.size // 2),
            "Player2": (self.board.size - 1, self.board.size // 2)
        }
        self.pawn_images = {
            "Player1": self.pawn_p1_img,
            "Player2": self.pawn_p2_img
        }

        self.label1 = self.font.render("Turn", True, self.text_color)

    def draw_menu(self):
        self.screen.fill((30, 10, 70))
        title_font = pygame.font.Font(None, 70)
        title = title_font.render("Quoridor", True, (255, 255, 255))
        self.screen.blit(title, (450, 120))

        self.button_vshuman.draw(self.screen)
        self.button_vsAI.draw(self.screen)

    def alternate_turn(self):
        if QuoridorGUI.turn == 1:
            QuoridorGUI.turn = 2
            self.label1 = self.font.render("Turn", True, (255,0,0))
        elif QuoridorGUI.turn == 2:
            QuoridorGUI.turn = 1
            self.label1 = self.font.render("Turn", True, (0, 0, 255))

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
        if self.state == "game":
            if QuoridorGUI.turn == 2:
                self.button_horizontal_1.draw(self.screen)
                self.button_vertical_1.draw(self.screen)
            if QuoridorGUI.turn == 1:
                self.button_horizontal_2.draw(self.screen)
                self.button_vertical_2.draw(self.screen)

    def draw_pawn(self, image, row, col):
        px = (col + 5) * self.cell_size + (self.cell_size - self.pawn_size) // 2
        py = (row + 2) * self.cell_size + (self.cell_size - self.pawn_size) // 2
        self.screen.blit(image, (px, py))

    def write_turn(self):
        if (QuoridorGUI.turn == 1):
            self.label1 = self.font.render("Turn", True, (255, 0, 0))
        elif(QuoridorGUI.turn == 2):
            self.label1 = self.font.render("Turn", True, (0, 0, 255))
        self.screen.blit(self.label1, ((self.screen.get_width()/2)-30, 30))

    def write_walls_left(self):
        label1 = self.font.render("Walls left:", True, self.text_color)
        label2 = self.font.render("Walls left:", True, self.text_color)
        self.screen.blit(label1, (60, 200))
        self.screen.blit(label2, (self.screen.get_width()-190, 200))

    def draw_board(self):
        self.screen.fill((80, 50, 150))

        for x in range(5, self.board.size + 5):
            for y in range(2, self.board.size + 2):
                rect = pygame.Rect(x * self.cell_size, y * self.cell_size, self.cell_size, self.cell_size)
                pygame.draw.rect(self.screen, (0, 0, 0), rect, 3)

        for player_name, (x, y) in self.board.pawns.items():
            self.draw_pawn(self.pawn_images[player_name], x, y)

        for r, c in self.board.horizontal_walls:
            x = (c + 5) * self.cell_size
            y = (r + 2) * self.cell_size + self.cell_size - 6
            self.screen.blit(self.wall_icon, (x, y-15))

        for r, c in self.board.vertical_walls:
            x = (c + 5) * self.cell_size + self.cell_size - 6
            y = (r + 2) * self.cell_size
            self.screen.blit(self.wall_icon_v, (x-15, y))

        if self.placing_wall and self.wall_preview_pos:
            mouse_x, mouse_y = self.wall_preview_pos
            board_offset_x = 5 * self.cell_size
            board_offset_y = 2 * self.cell_size
            col = (mouse_x - board_offset_x ) // self.cell_size
            row = (mouse_y - board_offset_y) // self.cell_size

            if 0 <= col < self.board.size - 1 and 0 <= row < self.board.size - 1:
                icon = self.wall_icon if self.placing_wall_type == "H" else self.wall_icon_v
                x = (col + 5) * self.cell_size
                y = (row + 2) * self.cell_size
                if self.placing_wall_type == "H":
                    y += self.cell_size - 21
                else:
                    x += self.cell_size - 21
                self.screen.blit(icon, (x, y))

        self.draw_players_icons()
        self.write_turn()
        self.write_walls_left()
        self.add_buttons()

    def get_wall_position_from_click(self, pos):
        mouse_x, mouse_y = pos

        board_offset_x = 5 * self.cell_size
        board_offset_y = 2 * self.cell_size

        col = (mouse_x - board_offset_x) // self.cell_size
        row = (mouse_y - board_offset_y) // self.cell_size

        if 0 <= col < self.board.size - 1 and 0 <= row < self.board.size - 1:
            return (row, col)
        return None

    def get_move_from_click(self, pos):
        mouse_x, mouse_y = pos

        board_offset_x = 5 * self.cell_size
        board_offset_y = 2 * self.cell_size

        col = (mouse_x - board_offset_x) // self.cell_size
        row = (mouse_y - board_offset_y) // self.cell_size

        if 0 <= col < self.board.size and 0 <= row < self.board.size:
            return (row, col)
        else:
            return None  

    def apply_move(self, player, move):
        if isinstance(move, tuple):
            row, col = move
            self.board.pawns[player.name] = (row, col)

        if isinstance(move, dict):
            orientation = move["type"]
            row, col = move["pos"]

            if self.board.place_wall(row, col, orientation):
                print(f"Placed wall {orientation} at ({row},{col})")
            else:
                print("Invalid wall placement!")

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return

            if event.type == pygame.MOUSEMOTION:
                if self.placing_wall:
                    self.wall_preview_pos = event.pos
                continue

            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = event.pos

                if self.state == "menu":
                    if self.button_vshuman.is_clicked(pos):
                        self.state = "game"
                        QuoridorGUI.is_ai = False
                        self.players = [Player("Player1"), Player("Player2", is_ai=False)]
                    elif self.button_vsAI.is_clicked(pos):
                        self.state = "gameai"
                        QuoridorGUI.is_ai = True
                        self.players = [Player("Player1"), Player("Player2", is_ai=True)]
                    continue

                if self.state in ("game", "gameai"):
                    if self.button_return.is_clicked(pos):
                        self.state = "menu"
                        self.placing_wall = False
                        self.placing_wall_type = None
                        continue

                    current_player = self.players[QuoridorGUI.turn - 1]

                    if self.placing_wall:
                        wall_pos = self.get_wall_position_from_click(pos)
                        if wall_pos:
                            move = {"type": self.placing_wall_type, "pos": wall_pos}

                            success = self.board.place_wall(wall_pos[0], wall_pos[1], self.placing_wall_type)
                            if success:
                                self.apply_move(current_player, move)
                                self.alternate_turn()
                            else:
                                print("Invalid wall placement!")

                        self.placing_wall = False
                        self.placing_wall_type = None
                        continue

                    if (self.button_horizontal_1.is_clicked(pos) or self.button_horizontal_2.is_clicked(pos)):
                        self.placing_wall = True
                        self.placing_wall_type = "H"
                        self.wall_preview_pos = pos
                        continue

                    if (self.button_vertical_1.is_clicked(pos) or self.button_vertical_2.is_clicked(pos)):
                        self.placing_wall = True
                        self.placing_wall_type = "V"
                        self.wall_preview_pos = pos
                        continue

                    move = self.get_move_from_click(pos)
                    if move and self.board.is_valid_move(current_player, move):
                        self.apply_move(current_player, move)
                        self.alternate_turn()
                    continue

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

    gui = QuoridorGUI(board, players=[])

    while gui.state == "menu":
        gui.handle_events()
        gui.draw_menu()
        pygame.display.flip()

    players = [
        Player("Player1"),
        Player("Player2", is_ai=QuoridorGUI.is_ai)
    ]

    gui.players = players

    gui.game_loop()

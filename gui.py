import pygame
from board import Board
from player import Player
from button import Button
import random
import os
import copy
from collections import deque


class QuoridorGUI:
    is_ai = False
    turn = random.randint(1, 2)
    is_finished = False
    SEARCH_DEPTH = 5

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
        self.pawn_p1_img = pygame.image.load(os.path.join(ASSETS_DIR, "monster3.png"))
        self.pawn_p2_img = pygame.image.load(os.path.join(ASSETS_DIR, "monster2.png"))

        pawn_size = int(self.cell_size * 0.8)
        self.pawn_p1_img = pygame.transform.scale(self.pawn_p1_img, (pawn_size, pawn_size))
        self.pawn_p2_img = pygame.transform.scale(self.pawn_p2_img, (pawn_size, pawn_size))
        self.pawn_size = pawn_size

        blue_icon = pygame.image.load(os.path.join(ASSETS_DIR, "BlueHuman.png")).convert_alpha()
        red_icon = pygame.image.load(os.path.join(ASSETS_DIR, "RedHuman.png")).convert_alpha()

        self.player1_icon = pygame.transform.scale(blue_icon, (80, 80))
        self.player2_icon = pygame.transform.scale(red_icon, (80, 80))

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
            x=self.screen.get_width() - 230, y=720, w=180, h=50,
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
            text="Add Wall ",
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
            x=self.screen.get_width() - 230, y=300, w=180, h=50,
            text="Add Wall ",
            font=self.ui_font,
            bg_color=(200, 50, 50),
            text_color=(255, 255, 255),
            icon=self.wall_icon,
            icon_size=45
        )

        self.button_vertical_2 = Button(
            x=self.screen.get_width() - 230, y=400, w=180, h=50,
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
            "Player1": (self.board.size - 1, self.board.size // 2),
            "Player2": (0, self.board.size // 2)
        }

        self.pawn_images = {
            "Player1": self.pawn_p1_img,
            "Player2": self.pawn_p2_img
        }

        self.label1 = self.font.render("Turn", True, self.text_color)

        self.temp_message = ""
        self.temp_message_time = 2000

        self.winner = None
        self.ai_thinking = False

    def _clone_state(self, board_state, players_state):
        clone = Board(size=board_state.size)
        clone.pawns = dict(board_state.pawns)
        clone.horizontal_walls = set(board_state.horizontal_walls)
        clone.vertical_walls = set(board_state.vertical_walls)
        clone.blocked_edges = set(board_state.blocked_edges)
        clone_players = copy.deepcopy(players_state)
        return clone, clone_players

    def apply_move(self, player, move):
        if isinstance(move, tuple):
            row, col = move

            for pname, ppos in self.board.pawns.items():
                if ppos == (row, col):
                    return False

            self.board.pawns[player.name] = (row, col)
            return True

        elif isinstance(move, dict):
            if player.walls_remaining <= 0:
                return False

            r, c = move["pos"]
            o = move["type"]

            test_board, test_players = self._clone_state(self.board, self.players)
            wall_placed = test_board.place_wall(r, c, o)

            if not wall_placed:
                return False

            p1_path = self._shortest_path_length(test_board, test_players[0])
            p2_path = self._shortest_path_length(test_board, test_players[1])

            if p1_path >= 999 or p2_path >= 999:
                print(
                    f"Wall placement at ({r},{c}) {o} rejected: would trap a player (P1 dist: {p1_path}, P2 dist: {p2_path})")
                return False

            success = self.board.place_wall(r, c, o)
            if success:
                player.walls_remaining -= 1
                return True
            else:
                return False

        return False

    def ai_make_move(self, ai_player):
        if self.ai_thinking or self.is_finished:
            return

        self.ai_thinking = True
        self.show_temp_message("AI is thinking...")
        pygame.display.flip()

        try:
            ai_idx = None
            for idx, p in enumerate(self.players):
                if p is ai_player:
                    ai_idx = idx
                    break

            if ai_idx is None:
                self.ai_thinking = False
                return

            ai_pos = self.board.pawns[ai_player.name]
            target_row = self.board.size - 1 if ai_player.name == "Player2" else 0

            pawn_moves = self.board.get_valid_pawn_moves(ai_player)

            for move in pawn_moves:
                if move[0] == target_row:
                    occupied = any(pos == move for pos in self.board.pawns.values())
                    if not occupied:
                        applied = self.apply_move(ai_player, move)
                        if applied:
                            self.show_temp_message("AI wins!")
                            winner = self.check_for_win()
                            if not winner:
                                self.alternate_turn()
                            self.ai_thinking = False
                            return

            ai_path_length = self._shortest_path_length(self.board, ai_player)

            if ai_path_length >= 999:
                print("AI is blocked! Attempting emergency move...")

                best_emergency_move = None
                best_emergency_dist = 999

                for move in pawn_moves:
                    occupied = any(pos == move for pos in self.board.pawns.values())
                    if not occupied:
                        test_board, test_players = self._clone_state(self.board, self.players)
                        test_board.pawns[ai_player.name] = move
                        test_dist = self._shortest_path_length(test_board, test_players[ai_idx])
                        if test_dist < best_emergency_dist:
                            best_emergency_dist = test_dist
                            best_emergency_move = move

                if best_emergency_move and best_emergency_dist < 999:
                    applied = self.apply_move(ai_player, best_emergency_move)
                    if applied:
                        self.show_temp_message("AI found escape route!")
                        print(f"AI escaped to {best_emergency_move}, new path length: {best_emergency_dist}")
                    else:
                        self.show_temp_message("AI blocked - skipping turn")
                else:
                    self.show_temp_message("AI completely blocked - skipping turn")
                    print("AI has no valid path available")

                self.alternate_turn()
                self.ai_thinking = False
                return

            clone_board, clone_players = self._clone_state(self.board, self.players)
            best_move, best_value = self.minimax(
                board_state=clone_board,
                players_state=clone_players,
                depth=self.SEARCH_DEPTH,
                alpha=float('-inf'),
                beta=float('inf'),
                maximizing=True,
                player_idx=ai_idx
            )

            if best_move is None:
                print("Minimax returned no move, using greedy fallback")
                if pawn_moves:
                    best_fallback = None
                    best_fallback_dist = float('inf')

                    for move in pawn_moves:
                        occupied = any(pos == move for pos in self.board.pawns.values())
                        if not occupied:
                            dist_to_goal = abs(move[0] - target_row)
                            if dist_to_goal < best_fallback_dist:
                                best_fallback_dist = dist_to_goal
                                best_fallback = move

                    if best_fallback:
                        applied = self.apply_move(ai_player, best_fallback)
                        if applied:
                            self.show_temp_message("AI moved (greedy)")
                            print(f"AI greedy move to {best_fallback}")
                        else:
                            self.show_temp_message("AI couldn't apply greedy move")
                    else:
                        self.show_temp_message("AI has no valid moves")
                else:
                    self.show_temp_message("AI has no valid moves")
                    self.alternate_turn()
                    self.ai_thinking = False
                    return
            else:
                move_type, data = best_move
                if move_type == "move":
                    occupied = any(pos == data for pos in self.board.pawns.values())
                    if occupied:
                        print(f"Minimax chose occupied square {data}, trying alternatives")
                        for mv in pawn_moves:
                            occupied_alt = any(pos == mv for pos in self.board.pawns.values())
                            if not occupied_alt:
                                applied = self.apply_move(ai_player, mv)
                                if applied:
                                    self.show_temp_message("AI moved (alternative)")
                                    break
                    else:
                        applied = self.apply_move(ai_player, data)
                        if applied:
                            self.show_temp_message("AI moved pawn")
                            print(f"AI moved pawn to {data}, evaluation: {best_value}")
                        else:
                            print(f"Failed to apply move to {data}")
                            for mv in pawn_moves:
                                occupied_alt = any(pos == mv for pos in self.board.pawns.values())
                                if not occupied_alt and self.apply_move(ai_player, mv):
                                    self.show_temp_message("AI moved (recovery)")
                                    break
                else:
                    r, c, o = data
                    applied = self.apply_move(ai_player, {"type": o, "pos": (r, c)})
                    if applied:
                        self.show_temp_message("AI placed a wall")
                        print(
                            f"AI placed wall at ({r},{c}) {o}, walls left: {ai_player.walls_remaining}, eval: {best_value}")
                    else:
                        print(f"AI wall placement failed at ({r},{c}) {o}, falling back to pawn move")
                        for mv in pawn_moves:
                            occupied_alt = any(pos == mv for pos in self.board.pawns.values())
                            if not occupied_alt and self.apply_move(ai_player, mv):
                                self.show_temp_message("AI moved (after wall fail)")
                                break

            winner = self.check_for_win()
            if not winner:
                self.alternate_turn()

        except Exception as e:
            print(f"AI Error: {e}")
            import traceback
            traceback.print_exc()
            self.show_temp_message("AI error - skipping turn")
            self.alternate_turn()

        finally:
            self.ai_thinking = False

    def minimax(self, board_state, players_state, depth, alpha, beta, maximizing, player_idx):
        p1_r, _ = board_state.pawns["Player1"]
        p2_r, _ = board_state.pawns["Player2"]

        if p1_r == 0:
            return None, 100000 if player_idx == 0 else -100000
        elif p2_r == board_state.size - 1:
            return None, 100000 if player_idx == 1 else -100000

        if depth == 0:
            return None, self._evaluate_board(board_state, players_state)

        all_moves = self._generate_all_moves(board_state, players_state, player_idx)
        if not all_moves:
            return None, -50000 if maximizing else 50000

        best_move = None
        best_value = float('-inf') if maximizing else float('inf')
        next_idx = 1 - player_idx

        for move_type, move in all_moves:
            branch_board, branch_players = self._clone_state(board_state, players_state)
            self._apply_simulated_move(branch_board, branch_players, player_idx, (move_type, move))

            current_player = branch_players[player_idx]
            path_len = self._shortest_path_length(branch_board, current_player)

            if path_len >= 999:
                continue

            _, val = self.minimax(
                board_state=branch_board,
                players_state=branch_players,
                depth=depth - 1,
                alpha=alpha,
                beta=beta,
                maximizing=not maximizing,
                player_idx=next_idx
            )

            if maximizing:
                if val > best_value:
                    best_value = val
                    best_move = (move_type, move)
                alpha = max(alpha, val)
            else:
                if val < best_value:
                    best_value = val
                    best_move = (move_type, move)
                beta = min(beta, val)

            if beta <= alpha:
                break

        return best_move, best_value

    def _get_wall_candidates(self, board_state, player):
        out = []
        size = board_state.size
        pr1, pc1 = board_state.pawns["Player1"]
        pr2, pc2 = board_state.pawns["Player2"]

        important = {(pr1 + dr, pc1 + dc) for dr in range(-2, 3) for dc in range(-2, 3)}
        important |= {(pr2 + dr, pc2 + dc) for dr in range(-2, 3) for dc in range(-2, 3)}

        for r, c in important:
            if 0 <= r < size - 1 and 0 <= c < size - 1:
                out.append((r, c, "H"))
                out.append((r, c, "V"))

        return out

    def _generate_all_moves(self, board_state, players_state, player_idx):
        moves = []
        player = players_state[player_idx]

        pawn_moves = board_state.get_valid_pawn_moves(player)

        target_row = 0 if player.name == "Player1" else board_state.size - 1
        current_pos = board_state.pawns[player.name]

        valid_pawn_moves_with_scores = []
        for mv in pawn_moves:
            occupied = any(pos == mv for pos in board_state.pawns.values())
            if not occupied:
                test_board, test_players = self._clone_state(board_state, players_state)
                test_board.pawns[player.name] = mv

                path_length = self._shortest_path_length(test_board, test_players[player_idx])

                valid_pawn_moves_with_scores.append((path_length, mv))

        valid_pawn_moves_with_scores.sort(key=lambda x: x[0])

        for _, mv in valid_pawn_moves_with_scores:
            moves.append(("move", mv))

        if player.walls_remaining > 0:
            opponent_idx = 1 - player_idx
            opponent = players_state[opponent_idx]

            d1 = self._shortest_path_length(board_state, players_state[0])
            d2 = self._shortest_path_length(board_state, players_state[1])

            my_dist = d2 if player_idx == 1 else d1
            opp_dist = d1 if player_idx == 1 else d2

            candidates = self._get_wall_candidates(board_state, player)
            if player_idx == 1:
                if my_dist <= 2:
                    return moves
                if my_dist == 3 and my_dist < opp_dist:
                    if opp_dist <= 3:
                        for (r, c, o) in candidates[:3]:
                            if board_state.is_valid_wall(r, c, o):
                                test_board, test_players = self._clone_state(board_state, players_state)
                                if test_board.place_wall(r, c, o):
                                    new_opp_dist = self._shortest_path_length(test_board, test_players[opponent_idx])
                                    new_my_dist = self._shortest_path_length(test_board, test_players[player_idx])
                                    if new_opp_dist < 999 and new_my_dist < 999 and new_opp_dist > opp_dist + 1:
                                        moves.append(("wall", (r, c, o)))
                    return moves
                if opp_dist <= 4:
                    blocking_walls = []
                    for (r, c, o) in candidates[:50]:
                        if board_state.is_valid_wall(r, c, o):
                            test_board, test_players = self._clone_state(board_state, players_state)
                            if test_board.place_wall(r, c, o):
                                new_opp_dist = self._shortest_path_length(test_board, test_players[opponent_idx])
                                new_my_dist = self._shortest_path_length(test_board, test_players[player_idx])

                                if new_opp_dist < 999 and new_my_dist < 999 and new_opp_dist > opp_dist:
                                    blocking_power = new_opp_dist - opp_dist
                                    cost_to_us = new_my_dist - my_dist
                                    effectiveness = blocking_power - (cost_to_us * 0.5)
                                    blocking_walls.append((effectiveness, ("wall", (r, c, o))))

                    blocking_walls.sort(reverse=True, key=lambda x: x[0])
                    for _, wall_move in blocking_walls[:20]:
                        moves.append(wall_move)
                elif my_dist >= opp_dist:
                    strategic_walls = []
                    for (r, c, o) in candidates[:40]:
                        if board_state.is_valid_wall(r, c, o):
                            test_board, test_players = self._clone_state(board_state, players_state)
                            if test_board.place_wall(r, c, o):
                                new_my_dist = self._shortest_path_length(test_board, test_players[player_idx])
                                new_opp_dist = self._shortest_path_length(test_board, test_players[opponent_idx])

                                if new_opp_dist < 999 and new_my_dist < 999:
                                    opp_increase = new_opp_dist - opp_dist
                                    my_increase = new_my_dist - my_dist
                                    net_advantage = opp_increase - my_increase

                                    if net_advantage > 0:
                                        strategic_walls.append((net_advantage, ("wall", (r, c, o))))

                    strategic_walls.sort(reverse=True, key=lambda x: x[0])
                    for _, wall_move in strategic_walls[:15]:
                        moves.append(wall_move)

                else:
                    conservative_walls = []
                    for (r, c, o) in candidates[:20]:
                        if board_state.is_valid_wall(r, c, o):
                            test_board, test_players = self._clone_state(board_state, players_state)
                            if test_board.place_wall(r, c, o):
                                new_my_dist = self._shortest_path_length(test_board, test_players[player_idx])
                                new_opp_dist = self._shortest_path_length(test_board, test_players[opponent_idx])

                                if new_my_dist < 999 and new_opp_dist < 999:
                                    if new_opp_dist > opp_dist and new_my_dist <= my_dist + 1:
                                        benefit = (new_opp_dist - opp_dist) - (new_my_dist - my_dist)
                                        conservative_walls.append((benefit, ("wall", (r, c, o))))

                    conservative_walls.sort(reverse=True, key=lambda x: x[0])
                    for _, wall_move in conservative_walls[:10]:
                        moves.append(wall_move)

            else:
                for (r, c, o) in candidates[:25]:
                    if board_state.is_valid_wall(r, c, o):
                        test_board, test_players = self._clone_state(board_state, players_state)
                        if test_board.place_wall(r, c, o):
                            new_p1_dist = self._shortest_path_length(test_board, test_players[0])
                            new_p2_dist = self._shortest_path_length(test_board, test_players[1])
                            if new_p1_dist < 999 and new_p2_dist < 999:
                                moves.append(("wall", (r, c, o)))

        return moves

    def _apply_simulated_move(self, board_state, players_state, player_idx, move_tuple):
        move_type, data = move_tuple
        player = players_state[player_idx]

        if move_type == "move":
            r, c = data
            occupied = any(pos == (r, c) for pos in board_state.pawns.values())
            if not occupied:
                board_state.pawns[player.name] = (r, c)
        elif move_type == "wall":
            r, c, o = data
            success = board_state.place_wall(r, c, o)
            if success and player.walls_remaining > 0:
                player.walls_remaining -= 1

    def _evaluate_board(self, board_state, players_state):
        p1 = players_state[0]
        p2 = players_state[1]

        d1 = self._shortest_path_length(board_state, p1)
        d2 = self._shortest_path_length(board_state, p2)

        if d2 >= 999:
            return -200000
        if d1 >= 999:
            return 200000

        if d2 == 1:
            return 50000
        elif d2 == 2:
            return 25000
        elif d2 == 3:
            return 15000
        elif d2 == 4:
            return 8000
        elif d2 == 5:
            return 4000

        if d1 == 1:
            return -50000
        elif d1 == 2:
            return -25000
        elif d1 == 3:
            return -15000
        elif d1 == 4:
            return -8000

        distance_advantage = (d1 - d2)

        score = distance_advantage * 2000

        score -= d2 * 500

        score += d1 * 300

        if d2 < d1:
            lead = d1 - d2
            score += lead * 800
        elif d2 > d1:
            deficit = d2 - d1
            score -= deficit * 600
        score += (9 - d2) * 150

        walls_used_by_ai = 10 - p2.walls_remaining
        walls_used_by_human = 10 - p1.walls_remaining

        if d2 < d1 - 2:
            score -= walls_used_by_ai * 25
        elif d2 < d1:
            score -= walls_used_by_ai * 15
        else:
            score -= walls_used_by_ai * 5
        score += walls_used_by_human * 20

        return score

    def _shortest_path_length(self, board_state, player):
        start = board_state.pawns[player.name]
        target_row = 0 if player.name == "Player1" else board_state.size - 1

        q = deque([(start, 0)])
        visited = {start}

        while q:
            (r, c), dist = q.popleft()
            if r == target_row:
                return dist

            for nr, nc in board_state.get_neighbors(r, c):
                if (nr, nc) not in visited:
                    visited.add((nr, nc))
                    q.append(((nr, nc), dist + 1))

        return 999

    def show_temp_message(self, msg, duration=1500):
        self.temp_message = msg
        self.temp_message_time = pygame.time.get_ticks() + duration

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
        else:
            QuoridorGUI.turn = 1

    def draw_players_icons(self):
        x1 = 80
        y1 = 20
        x2 = self.screen.get_width() - 160
        y2 = 20
        self.screen.blit(self.player1_icon, (x1, y1))
        self.screen.blit(self.player2_icon, (x2, y2))
        label1 = self.font.render("Player 1", True, self.text_color)
        label2 = self.font.render("AI" if self.state == "gameai" else "Player 2", True, self.text_color)

        text_x1 = x1 + (self.player1_icon.get_width() - label1.get_width()) // 2
        text_y1 = y1 + self.player1_icon.get_height() + 5
        text_x2 = x2 + (self.player2_icon.get_width() - label2.get_width()) // 2
        text_y2 = y2 + self.player2_icon.get_height() + 5

        self.screen.blit(label1, (text_x1, text_y1))
        self.screen.blit(label2, (text_x2, text_y2))

    def add_buttons(self):
        self.button_reset.draw(self.screen)
        self.button_return.draw(self.screen)

        current_player = self.players[QuoridorGUI.turn - 1]

        if not current_player.is_ai:
            if QuoridorGUI.turn == 1:
                self.button_horizontal_1.draw(self.screen)
                self.button_vertical_1.draw(self.screen)
            else:
                self.button_horizontal_2.draw(self.screen)
                self.button_vertical_2.draw(self.screen)

    def draw_pawn(self, image, row, col):
        px = (col + 5) * self.cell_size + (self.cell_size - self.pawn_size) // 2
        py = (row + 2) * self.cell_size + (self.cell_size - self.pawn_size) // 2
        self.screen.blit(image, (px, py))

    def write_turn(self):
        if QuoridorGUI.turn == 1:
            self.label1 = self.font.render("Turn", True, (0, 0, 255))
        elif QuoridorGUI.turn == 2:
            self.label1 = self.font.render("Turn", True, (255, 0, 0))
        self.screen.blit(self.label1, ((self.screen.get_width() / 2) - 30, 30))

    def write_walls_left(self):
        label1 = self.font.render(f"Walls left: {self.players[0].walls_remaining}", True, self.text_color)
        label2 = self.font.render(f"Walls left: {self.players[1].walls_remaining}", True, self.text_color)
        self.screen.blit(label1, (60, 200))
        self.screen.blit(label2, (self.screen.get_width() - 190, 200))

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
            self.screen.blit(self.wall_icon, (x, y - 15))

        for r, c in self.board.vertical_walls:
            x = (c + 5) * self.cell_size + self.cell_size - 6
            y = (r + 2) * self.cell_size
            self.screen.blit(self.wall_icon_v, (x - 15, y))

        if self.placing_wall and self.wall_preview_pos:
            mouse_x, mouse_y = self.wall_preview_pos
            board_offset_x = 5 * self.cell_size
            board_offset_y = 2 * self.cell_size
            col = (mouse_x - board_offset_x) // self.cell_size
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

        if self.temp_message and pygame.time.get_ticks() < self.temp_message_time:
            text = self.font.render(self.temp_message, True, (255, 0, 0))
            self.screen.blit(text, (self.screen.get_width() / 2 - 100, 720))

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

    def check_for_win(self):
        p1_r, p1_c = self.board.pawns["Player1"]
        p2_r, p2_c = self.board.pawns["Player2"]

        if p1_r == 0:
            self.is_finished = True
            self.winner = self.players[0]
            self.show_temp_message(f"{self.winner.name} Wins!")
            return self.winner

        if p2_r == self.board.size - 1:
            self.is_finished = True
            self.winner = self.players[1]
            self.show_temp_message(f"{self.winner.name} Wins!")
            return self.winner

        return None

    def get_move_from_click(self, pos):
        mouse_x, mouse_y = pos
        board_offset_x = 5 * self.cell_size
        board_offset_y = 2 * self.cell_size
        col = (mouse_x - board_offset_x) // self.cell_size
        row = (mouse_y - board_offset_y) // self.cell_size

        if 0 <= col < self.board.size and 0 <= row < self.board.size:
            return (row, col)
        return None

    def draw_winner(self):
        overlay = pygame.Surface((self.screen.get_width(), self.screen.get_height()))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        font = pygame.font.SysFont(None, 64)
        winner_text = self.winner.name if self.winner else "Player"
        text = font.render(f"{winner_text} Wins!", True, (255, 255, 255))
        rect = text.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 2 - 30))
        self.screen.blit(text, rect)

        small = pygame.font.SysFont(None, 28)
        info = small.render("Click Reset to play again", True, (200, 200, 200))
        info_rect = info.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 2 + 30))
        self.screen.blit(info, info_rect)

        self.button_reset.draw(self.screen)

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

                if self.button_reset.is_clicked(pos):
                    self.is_finished = False
                    self.winner = None
                    self.temp_message = ""
                    self.placing_wall = False
                    self.placing_wall_type = None
                    self.wall_preview_pos = None
                    self.ai_thinking = False

                    self.board.reset_board()
                    self.board.pawns["Player1"] = (self.board.size - 1, self.board.size // 2)
                    self.board.pawns["Player2"] = (0, self.board.size // 2)

                    if len(self.players) >= 2:
                        self.players[0].walls_remaining = 10
                        self.players[1].walls_remaining = 10

                    QuoridorGUI.turn = random.randint(1, 2)
                    return

                if self.is_finished:
                    return

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
                        self.ai_thinking = False
                        continue

                    current_player = self.players[QuoridorGUI.turn - 1]

                    if current_player.is_ai:
                        continue

                    if self.placing_wall:
                        wall_pos = self.get_wall_position_from_click(pos)
                        if wall_pos:
                            move = {"type": self.placing_wall_type, "pos": wall_pos}
                            success = self.apply_move(current_player, move)
                            if success:
                                winner = self.check_for_win()
                                if not winner:
                                    self.alternate_turn()
                            else:
                                self.show_temp_message("Invalid wall placement!")
                        self.placing_wall = False
                        self.placing_wall_type = None
                        continue

                    if (self.button_horizontal_1.is_clicked(pos) or self.button_horizontal_2.is_clicked(pos)):
                        if current_player.walls_remaining <= 0:
                            self.show_temp_message("No walls remaining!")
                            continue
                        self.placing_wall = True
                        self.placing_wall_type = "H"
                        self.wall_preview_pos = pos
                        continue

                    if (self.button_vertical_1.is_clicked(pos) or self.button_vertical_2.is_clicked(pos)):
                        if current_player.walls_remaining <= 0:
                            self.show_temp_message("No walls remaining!")
                            continue
                        self.placing_wall = True
                        self.placing_wall_type = "V"
                        self.wall_preview_pos = pos
                        continue

                    move = self.get_move_from_click(pos)
                    if move and self.board.is_valid_move(current_player, move):

                        dest_occupied = any(pos == move for pos in self.board.pawns.values())
                        if dest_occupied:
                            self.show_temp_message("Square occupied!")
                            continue
                        applied = self.apply_move(current_player, move)
                        if applied:
                            winner = self.check_for_win()
                            if winner:
                                self.placing_wall = False
                                self.placing_wall_type = None
                                return
                            self.alternate_turn()
                        else:
                            self.show_temp_message("Invalid move!")

    def game_loop(self):
        clock = pygame.time.Clock()
        ai_move_delay = 0

        while self.running:
            self.handle_events()

            if self.is_finished:
                self.draw_board()
                self.draw_winner()
                pygame.display.flip()
                clock.tick(60)
                continue

            if self.state == "gameai" and not self.is_finished and not self.ai_thinking:
                current_player = self.players[QuoridorGUI.turn - 1]
                if current_player.is_ai:
                    current_time = pygame.time.get_ticks()
                    if ai_move_delay == 0:
                        ai_move_delay = current_time + 500
                    elif current_time >= ai_move_delay:
                        self.ai_make_move(current_player)
                        ai_move_delay = 0
            else:
                ai_move_delay = 0

            if self.state == "menu":
                self.draw_menu()
            elif self.state == "game" or self.state == "gameai":
                self.draw_board()

            pygame.display.flip()
            clock.tick(60)


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

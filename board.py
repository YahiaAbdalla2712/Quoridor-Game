class Board:
    def __init__(self, size=9):
        self.size = size
        self.pawns = {}
        self.horizontal_walls = set()
        self.vertical_walls = set()
        self.blocked_edges = set()
        self.reset_board()

    def reset_board(self):
        self.pawns["Player1"] = (0, self.size // 2)
        self.pawns["Player2"] = (self.size - 1, self.size // 2)
        self.horizontal_walls.clear()
        self.vertical_walls.clear()
        self.blocked_edges.clear()

        for r in range(self.size):
            self._block_edge((r, -1), (r, 0))
            self._block_edge((r, self.size - 1), (r, self.size))
        for c in range(self.size):
            self._block_edge((-1, c), (0, c))
            self._block_edge((self.size - 1, c), (self.size, c))

    def _edge(self, a, b):
        return frozenset((a, b))

    def _block_edge(self, a, b):
        self.blocked_edges.add(self._edge(a, b))

    def _unblock_edge(self, a, b):
        self.blocked_edges.discard(self._edge(a, b))

    def is_edge_blocked(self, a, b):
        r1, c1 = a
        r2, c2 = b

        if not (0 <= r1 < self.size and 0 <= c1 < self.size):
            return True
        if not (0 <= r2 < self.size and 0 <= c2 < self.size):
            return True
        return self._edge(a, b) in self.blocked_edges

    def get_neighbors(self, r, c):
        neighbors = []
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < self.size and 0 <= nc < self.size and not self.is_edge_blocked((r, c), (nr, nc)):
                neighbors.append((nr, nc))
        return neighbors

    def region_has_goal_exit(self, start, goal_row):
        from collections import deque
        q = deque([start])
        visited = {start}
        while q:
            r, c = q.popleft()
            if r == goal_row:
                return True
            for nr, nc in self.get_neighbors(r, c):
                if (nr, nc) not in visited:
                    visited.add((nr, nc))
                    q.append((nr, nc))
        return False

    def _edges_for_wall(self, row, col, orientation):
        if orientation == "H":
            return [
                ((row, col), (row + 1, col)),
                ((row, col + 1), (row + 1, col + 1))
            ]
        else:
            return [
                ((row, col), (row, col + 1)),
                ((row + 1, col), (row + 1, col + 1))
            ]

    def is_valid_wall(self, row, col, orientation):

        if row < 0 or col < 0 or row >= self.size - 1 or col >= self.size - 1:
            return False

        if orientation == "H" and (row, col) in self.horizontal_walls:
            return False

        if orientation == "V" and (row, col) in self.vertical_walls:
            return False

        edges = self._edges_for_wall(row, col, orientation)
        for a, b in edges:
            if self._edge(a, b) in self.blocked_edges:
                return False

        if orientation == "H" and (row, col) in self.vertical_walls:
            return False
        if orientation == "V" and (row, col) in self.horizontal_walls:
            return False

        return True

    def place_wall(self, row, col, orientation):
        if not self.is_valid_wall(row, col, orientation):
            return False

        edges = self._edges_for_wall(row, col, orientation)

        if orientation == "H":
            self.horizontal_walls.add((row, col))
        else:
            self.vertical_walls.add((row, col))

        for a, b in edges:
            self._block_edge(a, b)

        p1 = self.pawns["Player1"]
        p2 = self.pawns["Player2"]
        ok1 = self.region_has_goal_exit(p1, self.size - 1)
        ok2 = self.region_has_goal_exit(p2, 0)

        if not (ok1 and ok2):
            for a, b in edges:
                self._unblock_edge(a, b)
            if orientation == "H":
                self.horizontal_walls.remove((row, col))
            else:
                self.vertical_walls.remove((row, col))
            return False

        return True

    def is_valid_move(self, player, move):
        row, col = move
        if not (0 <= row < self.size and 0 <= col < self.size):
            return False

        curr_r, curr_c = self.pawns[player.name]
        if (row, col) == (curr_r, curr_c):
            return False

        dr = row - curr_r
        dc = col - curr_c


        if abs(dr) + abs(dc) == 1:
            return not self.is_edge_blocked((curr_r, curr_c), (row, col))

        opponent = "Player2" if player.name == "Player1" else "Player1"
        opp_r, opp_c = self.pawns[opponent]

        allowed = []

        for ddr, ddc in [(-1,0),(1,0),(0,-1),(0,1)]:
            nr, nc = curr_r + ddr, curr_c + ddc
            if not (0 <= nr < self.size and 0 <= nc < self.size):
                continue
            if self.is_edge_blocked((curr_r, curr_c), (nr, nc)):
                continue

            if (nr, nc) == (opp_r, opp_c):
                jr, jc = opp_r + ddr, opp_c + ddc
                if 0 <= jr < self.size and 0 <= jc < self.size and not self.is_edge_blocked((opp_r, opp_c), (jr, jc)):
                    allowed.append((jr, jc))
                else:
                    for diag in [(-ddc, -ddr), (ddc, ddr)]:
                        rr = opp_r + diag[0]
                        cc = opp_c + diag[1]
                        if 0 <= rr < self.size and 0 <= cc < self.size and not self.is_edge_blocked((opp_r, opp_c), (rr, cc)):
                            allowed.append((rr, cc))
            else:
                allowed.append((nr, nc))

        if (row, col) not in allowed:
            return False

        orig = self.pawns[player.name]
        self.pawns[player.name] = (row, col)

        ok1 = self.region_has_goal_exit(self.pawns["Player1"], self.size - 1)
        ok2 = self.region_has_goal_exit(self.pawns["Player2"], 0)

        self.pawns[player.name] = orig

        return ok1 and ok2

    def move_pawn(self, player, move):
        if self.is_valid_move(player, move):
            self.pawns[player.name] = move
            return True
        return False



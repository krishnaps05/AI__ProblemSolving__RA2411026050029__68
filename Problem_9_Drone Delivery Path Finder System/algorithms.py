"""
algorithms.py
=============
Drone Delivery Path Finder System
----------------------------------
Contains the core pathfinding algorithms:
  - BFS (Breadth-First Search)  → guarantees shortest path
  - DFS (Depth-First Search)    → finds first valid path (may not be shortest)

Both algorithms return:
  - path          : list of (row, col) tuples from start → goal, or []
  - visited_order : list of cells in the order they were explored
  - elapsed_time  : wall-clock seconds taken by the search
"""

import time
from collections import deque


# ─────────────────────────────────────────────────────────────────────────────
#  Shared helpers
# ─────────────────────────────────────────────────────────────────────────────

def _get_neighbors(row: int, col: int, rows: int, cols: int,
                   allow_diagonal: bool = False) -> list[tuple[int, int]]:
    """
    Return valid grid neighbours for a cell.

    Parameters
    ----------
    row, col        : Current cell coordinates.
    rows, cols      : Grid dimensions.
    allow_diagonal  : If True, include 8-directional movement; else 4-directional.
    """
    cardinal = [(row - 1, col), (row + 1, col),
                (row, col - 1), (row, col + 1)]

    diagonal = [(row - 1, col - 1), (row - 1, col + 1),
                (row + 1, col - 1), (row + 1, col + 1)]

    candidates = cardinal + (diagonal if allow_diagonal else [])

    return [(r, c) for r, c in candidates if 0 <= r < rows and 0 <= c < cols]


def _reconstruct_path(parent: dict, start: tuple, goal: tuple) -> list[tuple[int, int]]:
    """
    Walk the parent map backwards from goal → start to reconstruct the path.

    Returns the path in start → goal order, or [] if goal is not reachable.
    """
    if goal not in parent:
        return []

    path = []
    current = goal
    while current is not None:
        path.append(current)
        current = parent.get(current)
    path.reverse()
    return path


# ─────────────────────────────────────────────────────────────────────────────
#  BFS — Breadth-First Search
# ─────────────────────────────────────────────────────────────────────────────

def bfs(grid: list[list[int]],
        start: tuple[int, int],
        goal: tuple[int, int],
        allow_diagonal: bool = False) -> dict:
    """
    Breadth-First Search on a 2-D grid.

    Parameters
    ----------
    grid            : 2-D list where 0 = free, 1 = obstacle.
    start           : (row, col) of the warehouse / source.
    goal            : (row, col) of the customer / destination.
    allow_diagonal  : Allow diagonal moves when True.

    Returns
    -------
    dict with keys:
        path            – list[(row, col)] shortest path, or []
        visited_order   – list[(row, col)] exploration order
        nodes_explored  – int
        path_length     – int (0 when no path)
        elapsed_time    – float seconds
        found           – bool
    """
    rows, cols = len(grid), len(grid[0])
    t_start = time.perf_counter()

    # Guard: start or goal is an obstacle
    if grid[start[0]][start[1]] == 1 or grid[goal[0]][goal[1]] == 1:
        return _empty_result(time.perf_counter() - t_start)

    # parent[cell] = cell we came from; None marks the start
    parent: dict[tuple, tuple | None] = {start: None}
    queue = deque([start])
    visited_order: list[tuple[int, int]] = []

    while queue:
        current = queue.popleft()
        visited_order.append(current)

        # ── Goal reached ──────────────────────────────────────────────────
        if current == goal:
            path = _reconstruct_path(parent, start, goal)
            elapsed = time.perf_counter() - t_start
            return {
                "path": path,
                "visited_order": visited_order,
                "nodes_explored": len(visited_order),
                "path_length": len(path) - 1,   # edges, not nodes
                "elapsed_time": elapsed,
                "found": True,
            }

        # ── Expand neighbours ─────────────────────────────────────────────
        for neighbour in _get_neighbors(*current, rows, cols, allow_diagonal):
            r, c = neighbour
            if neighbour not in parent and grid[r][c] == 0:
                parent[neighbour] = current
                queue.append(neighbour)

    # No path found
    elapsed = time.perf_counter() - t_start
    return {
        "path": [],
        "visited_order": visited_order,
        "nodes_explored": len(visited_order),
        "path_length": 0,
        "elapsed_time": elapsed,
        "found": False,
    }


# ─────────────────────────────────────────────────────────────────────────────
#  DFS — Depth-First Search
# ─────────────────────────────────────────────────────────────────────────────

def dfs(grid: list[list[int]],
        start: tuple[int, int],
        goal: tuple[int, int],
        allow_diagonal: bool = False) -> dict:
    """
    Depth-First Search on a 2-D grid (iterative using an explicit stack).

    The algorithm explores as deep as possible before backtracking.
    It is NOT guaranteed to find the shortest path.

    Parameters
    ----------
    grid            : 2-D list where 0 = free, 1 = obstacle.
    start           : (row, col) of the warehouse / source.
    goal            : (row, col) of the customer / destination.
    allow_diagonal  : Allow diagonal moves when True.

    Returns
    -------
    Same dict structure as bfs().
    """
    rows, cols = len(grid), len(grid[0])
    t_start = time.perf_counter()

    # Guard: start or goal is an obstacle
    if grid[start[0]][start[1]] == 1 or grid[goal[0]][goal[1]] == 1:
        return _empty_result(time.perf_counter() - t_start)

    # parent[cell] = predecessor (None for start)
    parent: dict[tuple, tuple | None] = {start: None}
    stack = [start]
    visited: set[tuple] = set()
    visited_order: list[tuple[int, int]] = []

    while stack:
        current = stack.pop()

        # Skip already-processed cells (stack can have duplicates)
        if current in visited:
            continue

        visited.add(current)
        visited_order.append(current)

        # ── Goal reached ──────────────────────────────────────────────────
        if current == goal:
            path = _reconstruct_path(parent, start, goal)
            elapsed = time.perf_counter() - t_start
            return {
                "path": path,
                "visited_order": visited_order,
                "nodes_explored": len(visited_order),
                "path_length": len(path) - 1,
                "elapsed_time": elapsed,
                "found": True,
            }

        # ── Push neighbours onto stack ────────────────────────────────────
        for neighbour in _get_neighbors(*current, rows, cols, allow_diagonal):
            r, c = neighbour
            if neighbour not in visited and grid[r][c] == 0:
                if neighbour not in parent:         # first time we see it
                    parent[neighbour] = current
                stack.append(neighbour)

    # No path found
    elapsed = time.perf_counter() - t_start
    return {
        "path": [],
        "visited_order": visited_order,
        "nodes_explored": len(visited_order),
        "path_length": 0,
        "elapsed_time": elapsed,
        "found": False,
    }


# ─────────────────────────────────────────────────────────────────────────────
#  Utility
# ─────────────────────────────────────────────────────────────────────────────

def _empty_result(elapsed: float) -> dict:
    """Return a result dict indicating no search was performed."""
    return {
        "path": [],
        "visited_order": [],
        "nodes_explored": 0,
        "path_length": 0,
        "elapsed_time": elapsed,
        "found": False,
    }

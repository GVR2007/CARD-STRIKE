from game_grid import get_neighbors

def get_paths_of_length_k(start_pos, k, grid, blocked_tiles):
    """
    Finds all valid paths of exactly length k from start_pos.
    Returns: List of paths (each path is a list of (col, row) tuples)
    """
    solutions = []
    
    def backtrack(current_path):
        if len(current_path) == k + 1: # path includes start node, so length k+1 nodes = k steps
            solutions.append(list(current_path))
            return

        last_pos = current_path[-1]
        neighbors = get_neighbors(last_pos[0], last_pos[1], grid.cols, grid.rows, diagonal=False)
        
        for n in neighbors:
            if n in blocked_tiles:
                continue
            if n in current_path: # No cycles in simple path
                continue
            
            # Constraint: Unit cannot move through enemies (blocked_tiles should handle this)
            
            current_path.append(n)
            backtrack(current_path)
            current_path.pop() # Backtrack

    backtrack([start_pos])
    return solutions

from game_grid import chebyshev_dist, bfs_reachable

def can_form_triangle(u1, u2, u3, grid):
    """
    Check if 3 units can move to form a triangle formation.
    """
    
    def get_reachable(pos, range_dist):
        return bfs_reachable(pos, range_dist, grid, diagonal=False)
        
    p1s = get_reachable(u1, 2)
    p2s = get_reachable(u2, 2) 
    p3s = get_reachable(u3, 2)
    
    for p1 in p1s:
        for p2 in p2s:
            if p1 == p2: continue
            if chebyshev_dist(*p1, *p2) > 1: continue # Must be adjacent
            
            for p3 in p3s:
                if p3 == p1 or p3 == p2: continue
                
                d12 = chebyshev_dist(*p1, *p2)
                d23 = chebyshev_dist(*p2, *p3)
                d31 = chebyshev_dist(*p3, *p1)
                
                if d12 <= 1 and d23 <= 1 and d31 <= 1:
                    return True, (p1, p2, p3)
                    
    return False, None

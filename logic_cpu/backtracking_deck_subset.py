def find_subset_sum_exact(cards, target_sum, attribute='hp'):
    """
    Finds a subset of cards where sum(card.attribute) == target_sum.
    Classic Subset Sum problem solved with backtracking.
    """
    solutions = []
    
    def backtrack(start_idx, current_sum, current_subset):
        if current_sum == target_sum:
            solutions.append(list(current_subset))
            return
        
        if current_sum > target_sum:
            return
            
        for i in range(start_idx, len(cards)):
            val = getattr(cards[i], attribute, 0)
            
            current_subset.append(cards[i])
            backtrack(i + 1, current_sum + val, current_subset)
            current_subset.pop()
            
    backtrack(0, 0, [])
    return solutions

def find_synergy_combo(cards, limit_cost, maximize_attr='damage'):
    """
    Find best combo of cards within cost limit that maximizes attribute.
    Like Knapsack but using backtracking for small N.
    """
    best_val = -1
    best_combo = []
    
    def backtrack(idx, current_cost, current_val, current_combo):
        nonlocal best_val, best_combo
        
        if current_val > best_val:
            best_val = current_val
            best_combo = list(current_combo)
        
        for i in range(idx, len(cards)):
            cost = getattr(cards[i], 'cost', 1) # simple cost assumption
            val = getattr(cards[i], maximize_attr, 0)
            
            if current_cost + cost <= limit_cost:
                current_combo.append(cards[i])
                backtrack(i + 1, current_cost + cost, current_val + val, current_combo)
                current_combo.pop()
                
    backtrack(0, 0, 0, [])
    return best_combo

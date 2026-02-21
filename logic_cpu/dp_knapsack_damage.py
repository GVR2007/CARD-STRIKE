def max_damage_knapsack(attacks, max_cost):
    """
    Selects a subset of attacks to maximize total damage such that total cost (e.g. cooldown) <= max_cost.
    Standard 0/1 Knapsack DP.
    
    attacks: List of objects with .dmg and .cost (cooldown)
    max_cost: Integer capacity
    """
    n = len(attacks)
    dp = [[0 for _ in range(max_cost + 1)] for _ in range(n + 1)]
    
    for i in range(1, n + 1):
        atk = attacks[i-1]
        cost = getattr(atk, 'max_cooldown', 1) 
        val = atk.dmg
        
        for w in range(max_cost + 1):
            if cost <= w:
                if val + dp[i-1][w-cost] > dp[i-1][w]:
                    dp[i][w] = val + dp[i-1][w-cost]
                else:
                    dp[i][w] = dp[i-1][w]
            else:
                dp[i][w] = dp[i-1][w]
                
    # Backtrack to find items
    w = max_cost
    selected = []
    for i in range(n, 0, -1):
        if dp[i][w] != dp[i-1][w]:
            atk = attacks[i-1]
            selected.append(atk)
            w -= getattr(atk, 'max_cooldown', 1)
            
    return dp[n][max_cost], selected

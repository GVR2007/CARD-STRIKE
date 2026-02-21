def allocate_resource_dp(units, total_resource, utility_fn):
    """
    Distributes 'total_resource' integer units among 'units' to maximize sum(utility_fn(unit, allocated_amount)).
    Standard Unbounded Knapsack / Allocation DP.
    
    units: List of unit objects
    total_resource: Int (e.g. 10 mana points)
    utility_fn: specific function(unit, amount) -> float value (e.g. HP gained)
    """
    n = len(units)
    # dp[i][r] using first i units with r resource
    dp = [[0.0 for _ in range(total_resource + 1)] for _ in range(n + 1)]
    allocation = [[0 for _ in range(total_resource + 1)] for _ in range(n + 1)]
    
    for i in range(1, n + 1):
        unit = units[i-1]
        for r in range(total_resource + 1):
            
            best_val = -1.0
            best_k = 0
            
            # Try giving k amount to this unit
            for k in range(r + 1):
                # Constraints check inside utility_fn or here (e.g. max capacity)
                val = utility_fn(unit, k) + dp[i-1][r-k]
                
                if val > best_val:
                    best_val = val
                    best_k = k
                    
            dp[i][r] = best_val
            allocation[i][r] = best_k
            
    # Backtrack to find allocation
    result = {}
    remaining = total_resource
    for i in range(n, 0, -1):
        amt = allocation[i][remaining]
        result[units[i-1]] = amt
        remaining -= amt
        
    return result

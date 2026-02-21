from game_grid import chebyshev_dist

def can_kill_target(attacker, attacker_pos, target, target_pos, grid, attacks_left):
    """
    Backtracking to determine if 'attacker' can kill 'target' this turn.
    """
    if target.hp <= 0:
        return True
    
    if not attacks_left:
        return False
        
    for i, attack in enumerate(attacks_left):
        if attack.current_cooldown > 0:
            continue
            
        dist = chebyshev_dist(attacker_pos[0], attacker_pos[1], target_pos[0], target_pos[1])
        if dist > attack.attack_range:
            continue
        
        # Simulate attack (simplified damage calc)
        # In real game, use logic_attack.perform_attack_logic's formula or heuristic
        # We'll use a simple approximation here for the AI check
        base_dmg = attack.dmg - dist
        if attack.element == "fire": base_dmg += 2 # Simplified trait
        
        # Element multiplier approx
        # Ideally import get_element_multiplier
        # For now assume 1.0 or safe estimate
        
        damage = max(1, base_dmg)
        
        original_hp = target.hp
        target.hp -= damage
        
        remaining = attacks_left[:i] + attacks_left[i+1:]
        
        if can_kill_target(attacker, attacker_pos, target, target_pos, grid, remaining):
            target.hp = original_hp
            return True
            
        target.hp = original_hp
        
    return False

def solve_kill(attacker, attacker_pos, target, target_pos, grid):
    usable = [a for a in attacker.attacks if a.current_cooldown == 0]
    return can_kill_target(attacker, attacker_pos, target, target_pos, grid, usable)

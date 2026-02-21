from itertools import permutations

def maximize_damage_sequence(attacker, target):
    """
    Finds the optimal sequence of attacks to maximize damage against a target.
    
    attacker: Card object
    target: Card object
    
    Returns: (max_damage, best_sequence)
    """
    attacks = [a for a in attacker.attacks if a.current_cooldown == 0]
    if not attacks:
        return 0, []
    
    best_damage = -1
    best_seq = []
    
    # Try all permutations (n! where n is usually 2 or 3, so very fast)
    for seq in permutations(attacks):
        current_damage = 0
        
        # Simulate sequence on temporary target copy?
        # Since Status effects persist, we need to track state carefully.
        # Simplified: We calculate damage based on known effects of attacks in the sequence.
        
        sim_target_effects = [e.type for e in target.active_effects]
        
        for atk in seq:
            # Calculate damage based on current sim effects
            dmg = atk.dmg
            
            # Apply Vulnerable
            from status_system import StatusType
            if StatusType.VULNERABLE in sim_target_effects:
                dmg += 2
                
            # Apply Weaken from attacker (if attacker had Weaken, but here we assume attacker state is constant)
            
            current_damage += dmg
            
            # Apply new status from attack to sim state
            if atk.status_type == "wind": # Assuming wind applies Vulnerable
                 sim_target_effects.append(StatusType.VULNERABLE)
                 # In reality we should check element or logic_attack map
            
        if current_damage > best_damage:
            best_damage = current_damage
            best_seq = seq
            
    return best_damage, best_seq

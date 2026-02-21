"""
Advanced CPU Controller with Stealing Phase
Flow: Timing -> Steal Eval -> Greedy Deck -> Combat D&C -> Execute

Advanced CPU Turn Logic

Uses:
- Divide & Conquer for target reduction
- Greedy heuristics for movement and execution

Overall Time Complexity per turn:
O(p + r + a)
where:
p = number of players
r = reachable grid tiles
a = number of attacks
"""



import random
from game_grid import cell_center, chebyshev_dist
from animations import anim_mgr
from logic_attack import perform_attack_logic, decrement_cooldowns, process_turn_start_statuses

from logic_cpu.dc_combat import select_attack_target, select_position, select_attack_placement
from logic_cpu.backtracking_kill_confirm import solve_kill
from logic_cpu.dp_survival_prob import survive_probability
from logic_cpu.backtracking_formation import can_form_triangle
from logic_cpu.dp_matchup_matrix import optimize_matchups
from logic_attack import cell_center

current_turn = 0

def advanced_cpu_turn(grid):
    global current_turn
    current_turn += 1
    
    # Decrement enemy cooldowns at start of enemy turn
    decrement_cooldowns(grid, "enemy")
    process_turn_start_statuses(grid, "enemy")
    
    if anim_mgr.blocking:
        return

    # -----------------------------------------------------------------
    # PHASE 2: COMBAT PHASE (Strict Move OR Attack)
    # -----------------------------------------------------------------
    
    enemy_positions = []
    curr_player_positions = []
    
    for c in range(grid.cols):
        for r in range(grid.rows):
            card = grid.tiles[c][r].card
            if card:
                if card.owner == "enemy":
                    enemy_positions.append((c,r))
                else:
                    curr_player_positions.append((c,r))

    # Evaluate best single action across all cards
    best_action = None
    best_score = -1
    
    # 0. MATCHUP DP: OPTIMAL HEALING ASSIGNMENT
    # Identify Healers and Patients
    healers = []
    patients = []
    
    for e_pos in enemy_positions:
        card = grid.tiles[e_pos[0]][e_pos[1]].card
        # Check if healer
        has_heal = False
        for atk in card.attacks:
            is_heal = ("heal" in atk.name.lower()) or ("Embrace" in atk.name) or atk.is_healing
            if is_heal and atk.current_cooldown == 0:
                has_heal = True
                break
        if has_heal:
            healers.append(card)
        if card.hp < card.max_hp:
            patients.append(card)
            
    healing_assignments = {} # Map healer_card -> patient_card
    
    if healers and patients:
        def heal_score(healer, patient):
            if healer == patient: return 0 # Self-heal usually covered, but okay
            dist = abs(healer.index - patient.index) # Dummy metric, should use grid dist
            # Better: use HP gained
            gained = min(patient.max_hp - patient.hp, 20) # Assume 20 heal
            # Prioritize LOW HP
            criticality = 1.0
            if patient.hp < patient.max_hp * 0.3: criticality = 3.0
            
            return gained * criticality
            
        _, assignments = optimize_matchups(healers, patients, heal_score)
        for h, p in assignments:
            healing_assignments[h] = p
            print(f"[Matchup] Assigned {h.name} to heal {p.name}")

    print(f"--- CPU TURN START (Turn {current_turn}) ---")
    print(f"CPU evaluating {len(enemy_positions)} units.")

    for e_pos in enemy_positions:
        e_card = grid.tiles[e_pos[0]][e_pos[1]].card
        if not e_card: continue
        
        # 1. BACKTRACKING: KILL CONFIRM
        # Check if we can kill any adjacent player card this turn
        for p_pos in curr_player_positions:
             p_card = grid.tiles[p_pos[0]][p_pos[1]].card
             if p_card and solve_kill(e_card, e_pos, p_card, p_pos, grid):
                 print(f"!!! KILL CONFIRMED: {e_card.name} can kill {p_card.name} !!!")
                 # Force attack logic
                 # Find the attack that does the job (simplified here, just boost score massive)
                 target_pos = p_pos
                 attack_obj = select_attack_placement(e_card, e_pos, target_pos, grid)
                 if attack_obj:
                     best_score = 9999
                     best_action = {
                        'type': 'ATTACK',
                        'card': e_card,
                        'pos': e_pos,
                        'target': target_pos,
                        'attack': attack_obj
                     }
                     break # Stop checking other targets, take the kill

        if best_score > 9000: break # Stop checking other units, take the kill

        if best_score > 9000: break # Stop checking other units, take the kill

        # 1b. HEAL ASSIGNMENT EXECUTION
        if e_card in healing_assignments:
            patient = healing_assignments[e_card]
            # Find the healing attack
            heal_atk = None
            for atk in e_card.attacks:
                if ("heal" in atk.name.lower() or "Embrace" in atk.name or atk.is_healing) and atk.current_cooldown == 0:
                    heal_atk = atk
                    break
            
            if heal_atk:
                # Find patient pos
                p_pos = None
                for c in range(grid.cols):
                    for r in range(grid.rows):
                        if grid.tiles[c][r].card == patient:
                            p_pos = (c,r)
                            break
                if p_pos:
                     # Check range
                     hd = chebyshev_dist(e_pos[0], e_pos[1], p_pos[0], p_pos[1])
                     if hd <= heal_atk.attack_range:
                         heal_score = 200 # High priority
                         # Execute Heal
                         if heal_score > best_score:
                             best_score = heal_score
                             best_action = {
                                'type': 'ATTACK', # Uses attack logic for healing
                                'card': e_card,
                                'pos': e_pos,
                                'target': p_pos,
                                'attack': heal_atk
                             }
                             print(f"[Matchup] Executing Planned Heal on {patient.name}")

        # 2. STRATEGY: FORMATION CHECK
        # If we have 3+ units, try to form a triangle
        formation_move = None
        if len(enemy_positions) >= 3:
            others = [p for p in enemy_positions if p != e_pos]
            if len(others) >= 2:
                # Check first pair (optimization: could check all)
                u2, u3 = others[:2]
                success, coords = can_form_triangle(e_pos, u2, u3, grid)
                if success:
                    target, _, _ = coords
                    if target != e_pos:
                        formation_move = target
                        print(f"[Strategy] Formation opportunity for {e_card.name} at {target}")

        # --- OPTION A: ATTACK (from current position) ---
        target_pos = None
        if getattr(e_card, "stun_duration", 0) > 0:
            attack_score = -1
        else:
            target_pos = select_attack_target(e_card, e_pos, curr_player_positions, grid, prioritize_range=True)
        
        attack_obj = None
        attack_score = -1
        
        if target_pos:
            attack_obj = select_attack_placement(e_card, e_pos, target_pos, grid)
            if attack_obj:
                attack_score = attack_obj.dmg
                if attack_obj.element == "fire": attack_score += 2
                
                # Bonus for killing blow
                t_card = grid.tiles[target_pos[0]][target_pos[1]].card
                if t_card and t_card.hp <= attack_obj.dmg:
                    attack_score += 50
        
            print(f"[{current_turn}] Eval ATTACK {e_card.name}: Score={attack_score}")
        
        if attack_score > best_score:
            best_score = attack_score
            best_action = {
                'type': 'ATTACK',
                'card': e_card,
                'pos': e_pos,
                'target': target_pos,
                'attack': attack_obj
            }
            print(f"[{current_turn}] New Best: ATTACK {e_card.name} (Score: {best_score})")

        # --- OPTION B: MOVE (no attack) ---
        if getattr(e_card, "root_duration", 0) > 0:
            move_score = -1
            new_pos = e_pos
        else:
            move_target_pos = select_attack_target(e_card, e_pos, curr_player_positions, grid)
            new_pos = select_position(e_card, e_pos, move_target_pos, grid)
            move_score = 0
            if new_pos != e_pos:
                move_score = 10  # Base score for moving
                
                # 2. DP: SURVIVAL CHECK
                # If current position is dangerous, boost move score
                # Estimate danger: average 20 dmg/turn from 1 enemy? 
                # Simplified: if HP < 30% and survival prob low, retreat
                if e_card.hp < e_card.max_hp * 0.4:
                    prob = survive_probability(e_card.hp, e_card.max_hp, 2, (10, 25))
                    if prob < 0.5:
                        move_score += 50 # Priority Retreat
                        print(f"DP Survival Warn: {e_card.name} survival prob {prob:.2f} -> RETREAT")
                
                # 3. Apply Formation Bonus
                if formation_move and new_pos == formation_move:
                    move_score += 25 # High priority but less than Kill or Emergency Retreat
                    print(f"Formation Bonus applied to {e_card.name}")
        
        print(f"[{current_turn}] Eval MOVE {e_card.name} to {new_pos}: Score={move_score}")

        if move_score > best_score:
            best_score = move_score
            best_action = {
                'type': 'MOVE',
                'card': e_card,
                'pos': e_pos, # Current pos
                'new_pos': new_pos
            }
            print(f"[{current_turn}] New Best: MOVE {e_card.name} (Score: {best_score})")

    # Execute the SINGLE best action
    if best_action:
        print(f"--- EXECUTING BEST ACTION ---")
        if best_action['type'] == 'MOVE':
            card = best_action['card']
            old_pos = best_action['pos']
            new_pos = best_action['new_pos']
            
            if old_pos == new_pos:
                print(f"[{card.name}] decided to stay at {old_pos}")
            else:
                print(f"CPU Action: MOVE {card.name} from {old_pos} to {new_pos}")
                
                # Helper for move animation callback
                def finalize_move(g=grid, old=old_pos, new=new_pos, c=card):
                    move_grid_card(g, old, new, c)
                    print(f"[DEBUG_MOVE] {c.name} moved from {old} to {new}")
                    
                anim_mgr.trigger_move_anim(
                    cell_center(*old_pos),
                    cell_center(*new_pos),
                    finalize_move
                )
                anim_mgr.add_floating_text(f"Moving {card.name}", cell_center(*new_pos)[0], cell_center(*new_pos)[1] - 40, (255, 255, 255))
            
        elif best_action['type'] == 'ATTACK':
            card = best_action['card']
            pos = best_action['pos']
            target = best_action['target']
            attack = best_action['attack']
            print(f"[{current_turn}] CPU Action: ATTACK {card.name} at {target} with {attack.name}")
            
            dist = chebyshev_dist(pos[0], pos[1], target[0], target[1])
            # Apply Cooldown
            attack.current_cooldown = attack.max_cooldown

            anim_mgr.trigger_attack_anim(
                cell_center(*pos),
                cell_center(*target),
                attack.element,
                lambda ep=pos, tp=target, atk=attack, g=grid, d=dist: perform_attack_logic(
                    ep[0], ep[1], tp[0], tp[1], atk, g, d
                )
            )
            anim_mgr.add_floating_text(f"Attacking!", cell_center(*pos)[0], cell_center(*pos)[1] - 40, (255, 50, 50))
    else:
        print("CPU found no valid actions.")

def move_grid_card(grid, old_pos, new_pos, card):
    if old_pos == new_pos:
        return
    grid.tiles[new_pos[0]][new_pos[1]].card = card
    grid.tiles[old_pos[0]][old_pos[1]].card = None

# Marvel-Strike 2.0: Advanced AI & Mechanics Implementation Plan

## Overview
This document outlines the complete plan to integrate rigorous algorithmic implementations (5 Backtracking & 5 Dynamic Programming) and enhanced gameplay mechanics (Buffs/Debuffs) into Marve-Strike.

The goal is to transform the game into a showcase of advanced CS concepts while significantly improving strategic depth.

---

## 1. Core Mechanics Upgrade: Status Effects System
**Objective:** Add depth to combat with persistant buffs and debuffs.

### New Architecture
- **`status_effect.py`**: A new module defining effect types (FLAME, REGEN, STUN, WEAKEN, STRENGTH).
- **`Card` Class Update**: Add `active_effects: List[StatusEffect]` to track current states.
- **Turn Logic**: Implement `apply_status_effects()` at turn start to handle DoT (Damage over Time) and duration decrement.

### Specific Effects
1. **Flame (Fire Debuff)**: Deals 2 damage per turn for 2 rounds. (Source: Fire Attacks)
2. **Frost/Slow (Water Debuff)**: Reduces Movement Range by 1 for 2 rounds. (Source: Water Attacks)
3. **Regen (Plant Buff)**: Heals 2 HP per turn for 3 rounds. (Source: Plant Support)
4. **Thorns (Plant Buff)**: Reflects 1 damage to attacker. (Source: Plant Defense)
5. **Vulnerable (Wind Debuff)**: Increases incoming damage by 2. (Source: Wind Attacks)

---

## 2. Backtracking Implementations (5 Modules)
*Backtracking explores all potential solutions to find the correct one or all valid ones.*

1. **`backtracking_kill_confirm.py` ("Mate-in-N Solver")**
   - **Logic:** Recursively simulates sequences of Move->Attack to see if *any* sequence results in a target kill this turn.
   - **Why:** Allows CPU to be aggressive only when a kill is guaranteed.

2. **`backtracking_pathing.py` (Complex Pathing)**
   - **Logic:** Finds *all* valid paths of exactly length `K` to a destination, avoiding dynamic obstacles. Useful for "flanking" logic where specific path shapes matter.
   - **Why:** Enables movement patterns that aren't just "shortest path".

3. **`backtracking_deck_subset.py` (Stealing Phase)**
   - **Logic:** Finds a subset of cards in the draft pool that sum to a specific attribute threshold (e.g., "Find 3 cards with total HP > 50 and Attack > 60").
   - **Why:** Ensures the CPU drafts a balanced deck meeting specific stat quotas.

4. **`backtracking_puzzle.py` (Formation Check)**
   - **Logic:** Can the current units move to form a "Triangle" or "Line" formation within 1 turn?
   - **Why:** To encourage defensive positioning (e.g., shielding weak units).

5. **`backtracking_attack_sequence.py` (Combo optimizer)**
   - **Logic:** If a unit has multiple actions/attacks, try all permutations to maximize damage (e.g., Attack 1 applies Vulnerable, Attack 2 deals damage. Order A->B is better than B->A).
   - **Why:** Maximizes damage output by exploiting status effect synergy.

---

## 3. Dynamic Programming Implementations (5 Modules)
*DP solves optimization problems by breaking them down into simpler subproblems and storing results.*

1. **`dp_knapsack_damage.py` (Damage Optimization)**
   - **Logic:** Given a limit (e.g., "Max 5 Cooldown Worth of usage" or implicit AP), select the set of attacks that maximizes total damage.
   - **Features:** Classic 0/1 Knapsack implementation.
   - **Why:** Ensures the most efficient use of turn resources.

2. **`dp_min_cost_path.py` (Grid Traversal)**
   - **Logic:** Calculate the path from A to B that minimizes "Danger Cost" (Fire tiles = 5 cost, Normal = 1 cost).
   - **Features:** Standard Grid DP / Min-Path-Sum logic.
   - **Why:** CPU will intelligently avoid fire/trap tiles unless necessary.

3. **`dp_survival_prob.py` (Defensive Calculation)**
   - **Logic:** Calculate "Survival Probability" for next turn based on current HP and enemy potential max damage.
   - **Features:** Memoized state evaluation.
   - **Why:** CPU retreats if survival probability drops below threshold.

4. **`dp_matchup_matrix.py` (Target Assignemnt)**
   - **Logic:** Create a matrix of MyUnits x EnemyUnits with "Advantage Scores". Use DP to find the best non-overlapping assignment of attackers to targets.
   - **Why:** Optimizes global team damage output.

5. **`dp_resource_allocation.py` (Mana/Energy Planning)**
   - **Logic:** If we have a shared resource (or just "Tempo"), how to distribute it across 3 turns? (Simplified for this game: "How much HP can I afford to trade?").
   - **Why:** Long-term resource management.

---

## 4. Integration Plan
1. **Phase 1**: Status Effects & Core Mechanics Update.
2. **Phase 2**: Implement the 5 Backtracking algorithms in `logic_cpu/`.
3. **Phase 3**: Implement the 5 DP algorithms in `logic_cpu/`.
4. **Phase 4**: Integrate these into `advanced_cpu.py` so they are actively used in decision making.
5. **Phase 5**: Documentation (README) & Final Polish.


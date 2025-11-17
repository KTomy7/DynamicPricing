from typing import List, Dict, Any
import pandas as pd
from collections import Counter  # For the analysis function

from app.utils.helper import load_dataset, save_to_csv
from app.core.linucb_model import LinUCB, extract_features, compute_reward


def simulate_dynamic_pricing() -> Dict[str, Any]:
    """
    Simulate dynamic pricing using LinUCB algorithm.
    This version includes a WARM-UP phase to solve the argmax tie.
    """
    df = load_dataset()
    df.dropna(subset=["Price", "Quantity", "InvoiceDate"], inplace=True)
    df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"], errors="coerce")
    df = df[(df["Quantity"] > 0) & (df["Price"] > 0)]
    product_df = df[df["StockCode"] == df["StockCode"].unique()[0]].head(500)

    actions = [-0.1, 0, 0.1]
    n_arms = len(actions)
    d = 2  # <-- CRITICAL: This must be 2 to match extract_features (month, stock)

    # Use a high alpha to force exploration
    agent = LinUCB(n_arms=n_arms, d=d, alpha=1.0)

    stock = 100

    # --- START OF STATEFUL LOGIC ---
    # 1. Get BASE values from historical data ONCE.
    current_base_price = float(product_df["Price"].mean())
    avg_prev_price = current_base_price
    base_demand_for_product = int(product_df["Quantity"].mean())

    current_month = 1
    results: List[Dict[str, Any]] = []

    # --- START OF "WARM-UP" LOGIC ---
    # We must "warm up" the model by forcing it to try each arm once
    # This avoids the initial argmax tie and gives it a baseline for all arms
    for arm_to_warm_up in range(n_arms):
        if stock <= 0: break  # Stop if stock runs out during warm-up

        # 1. Get a context
        state = extract_features(current_month, stock)
        current_month = (current_month % 12) + 1

        # 2. Force the action
        price_change = actions[arm_to_warm_up]
        new_price = float(current_base_price * (1 + price_change))

        # 3. Simulate quantity
        if price_change == 0.1:
            quantity_multiplier = 0.85
        elif price_change == -0.1:
            quantity_multiplier = 1.25
        else:
            quantity_multiplier = 1.0
        simulated_quantity = max(1, int(base_demand_for_product * quantity_multiplier))

        # 4. Compute reward
        reward = compute_reward(new_price, simulated_quantity, price_change, avg_prev_price)

        # 5. Update agent
        agent.update(arm_to_warm_up, state, reward)

        # 6. Update state (but DON'T save results yet)
        avg_prev_price = new_price
        current_base_price = new_price
        stock = max(0, stock - simulated_quantity)
    # --- END OF "WARM-UP" LOGIC ---

    # --- START OF MAIN SIMULATION LOOP ---
    # Run for the remaining steps (e.g., 50 - 3 warm-up steps)
    for t in range(50 - n_arms):
        if stock <= 0: break  # Check stock at the beginning of the loop

        # 1. Extract features from the CURRENT state
        state = extract_features(current_month, stock)

        arm = agent.select_arm(state)
        price_change = actions[arm]

        # 2. Calculate new price based on the PREVIOUS step's price
        new_price = float(current_base_price * (1 + price_change))

        # 3. Use the asymmetric demand model
        if price_change == 0.1:
            quantity_multiplier = 0.85
        elif price_change == -0.1:
            quantity_multiplier = 1.08
        else:
            quantity_multiplier = 1.0

        simulated_quantity = max(1, int(base_demand_for_product * quantity_multiplier))

        # 4. Compute reward
        reward = compute_reward(new_price, simulated_quantity, price_change, avg_prev_price)

        # 5. Update the state for the NEXT loop
        avg_prev_price = new_price
        current_base_price = new_price  # Price is stateful
        agent.update(arm, state, reward)
        stock = max(0, stock - simulated_quantity)  # Stock is stateful
        current_month = (current_month % 12) + 1  # Time is stateful

        results.append({
            "step": t + 1,  # This will now start from "1" after warm-up
            "action": price_change,
            "new_price": round(new_price, 2),
            "quantity": simulated_quantity,
            "reward": round(float(reward), 2)
        })

    # --- END OF MAIN LOOP ---

    return {
        "total_profit": round(sum([r["reward"] for r in results]), 2),
        "steps": results
    }


# --- This is your function for the 100-run analysis ---
def run_and_analyze_simulations(n_runs: int = 100) -> Dict[str, Any]:
    """
    Runs the simulation n_runs times and returns a summary.
    """
    # --- START OF FIX ---
    # The 'actions' list must be defined here to get n_arms
    actions = [-0.1, 0, 0.1]
    n_arms = len(actions)
    # --- END OF FIX ---

    all_run_data = []
    for i in range(n_runs):
        sim_results = simulate_dynamic_pricing()
        total_profit = sim_results["total_profit"]

        # We add the warm-up steps to the total step count
        # (n_arms is now defined)
        steps_taken = len(sim_results["steps"]) + n_arms

        # We'll just count the actions from the main loop for this summary
        action_counts = Counter([s["action"] for s in sim_results["steps"]])

        all_run_data.append({
            "run": i + 1,
            "total_profit": total_profit,
            "steps_taken": steps_taken,
            "action_increase_count": action_counts.get(0.1, 0),
            "action_maintain_count": action_counts.get(0.0, 0),
            "action_decrease_count": action_counts.get(-0.1, 0)
        })
    df = pd.DataFrame(all_run_data)

    save_to_csv(df, "simulation_analysis_results")

    summary = {
        "total_runs": n_runs,
        "average_profit": round(df["total_profit"].mean(), 2),
        "average_steps_taken": round(df["steps_taken"].mean(), 1),
        "average_action_increase": round(df["action_increase_count"].mean(), 1),
        "average_action_maintain": round(df["action_maintain_count"].mean(), 1),
        "average_action_decrease": round(df["action_decrease_count"].mean(), 1),
    }
    return summary

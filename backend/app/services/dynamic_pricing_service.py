from collections import Counter
from typing import Dict, Any
import pandas as pd
import traceback

from app.utils.helper import load_dataset, clean_and_prepare_data, save_to_csv
from app.core.linucb_model import LinUCB, extract_features, compute_reward

def simulate_dynamic_pricing() -> Dict[str, Any]:
    """
    Simulate dynamic pricing using LinUCB algorithm.
    :return:
    Dict[str, Any]: Simulation results including total profit and step details.
    """
    try:
        df = load_dataset()
        product_df = clean_and_prepare_data(df)

        if product_df.empty:
            return {"total_profit": 0, "steps": []}

        actions = [-0.1, 0, 0.1]
        n_arms = len(actions)
        d = 4
        agent = LinUCB(n_arms=n_arms, d=d, alpha=1.0)

        stock = 100
        avg_prev_price = float(product_df["Price"].iloc[0])
        results = []

        for t in range(50):
            row = product_df.sample(1).iloc[0]
            recent_sample = product_df["Quantity"].sample(5)
            recent_demand = float(recent_sample.mean()) if not recent_sample.empty else float(row["Quantity"])
            state = extract_features(row, recent_demand, stock)

            # DEBUG prints
            print(f"Step {t + 1}: state={state.ravel()}, stock={stock}")

            arm = agent.select_arm(state)
            price_change = actions[arm]
            new_price = float(row["Price"] * (1 + price_change))

            if price_change == 0.1:
                # A 10% price increase drops quantity by 15%
                quantity_multiplier = 0.85
            elif price_change == -0.1:
                # A 10% price cut only boosts quantity by 8%
                quantity_multiplier = 1.08
            else:
                # No change
                quantity_multiplier = 1.0

            simulated_quantity = max(1, int(row["Quantity"] * quantity_multiplier))

            reward = float(compute_reward(new_price, simulated_quantity, price_change, avg_prev_price))
            avg_prev_price = new_price
            agent.update(arm, state, reward)
            stock = max(0, stock - simulated_quantity)

            results.append({
                "step": t + 1,
                "action": price_change,
                "new_price": round(new_price, 2),
                "quantity": simulated_quantity,
                "reward": round(reward, 2)
            })

            if stock <= 0:
                break

        return {
            "total_profit": round(sum([r["reward"] for r in results]), 2),
            "steps": results
        }

    except Exception as e:
        print("❌ ERROR inside simulate_dynamic_pricing:", e)
        traceback.print_exc()
        raise e  # re-raise so FastAPI shows it


def run_and_analyze_simulations(n_runs: int = 100) -> Dict[str, Any]:
    """
    Runs the simulation n_runs times and returns a summary.
    """
    all_run_data = []

    for i in range(n_runs):
        sim_results = simulate_dynamic_pricing()

        total_profit = sim_results["total_profit"]
        steps_taken = len(sim_results["steps"])

        action_counts = Counter([s["action"] for s in sim_results["steps"]])

        all_run_data.append({
            "run": i + 1,
            "total_profit": total_profit,
            "steps_taken": steps_taken,
            "action_increase_count": action_counts.get(0.1, 0),
            "action_maintain_count": action_counts.get(0.0, 0),
            "action_decrease_count": action_counts.get(-0.1, 0)
        })

    # Convert to DataFrame for easy analysis
    df = pd.DataFrame(all_run_data)

    # Save the full results to a CSV for your own analysis
    save_to_csv(df, "dynamic_pricing_simulation_results")

    # Create the summary dictionary to send to the frontend
    summary = {
        "total_runs": n_runs,
        "average_profit": round(df["total_profit"].mean(), 2),
        "average_steps_taken": round(df["steps_taken"].mean(), 1),
        "average_action_increase": round(df["action_increase_count"].mean(), 1),
        "average_action_maintain": round(df["action_maintain_count"].mean(), 1),
        "average_action_decrease": round(df["action_decrease_count"].mean(), 1),
    }
    return summary

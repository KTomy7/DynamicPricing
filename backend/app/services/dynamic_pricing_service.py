from typing import Dict, Any
import pandas as pd
import traceback

from app.utils.helper import load_dataset
from app.core.linucb_model import LinUCB, extract_features, compute_reward

def simulate_dynamic_pricing() -> Dict[str, Any]:
    """
    Simulate dynamic pricing using LinUCB algorithm.
    :return:
    Dict[str, Any]: Simulation results including total profit and step details.
    """
    try:
        df = load_dataset()

        df.dropna(subset=["Price", "Quantity", "InvoiceDate"], inplace=True)
        df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"], errors="coerce")
        df = df[(df["Quantity"] > 0) & (df["Price"] > 0)]

        product_df = df[df["StockCode"] == df["StockCode"].unique()[0]].head(500)
        actions = [-0.1, 0, 0.1]
        n_arms = len(actions)
        d = 5
        agent = LinUCB(n_arms=n_arms, d=d, alpha=0.3)

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
            simulated_quantity = max(1, int(row["Quantity"] * (1 - price_change)))

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

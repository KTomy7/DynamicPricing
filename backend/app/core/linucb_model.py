import numpy as np
import random

class LinUCB:
    """
    LinUCB algorithm for contextual bandits.
    """
    def __init__(self, n_arms, d, alpha=0.3):
        """
        Initialize the LinUCB model.
        :param n_arms: Number of arms (price points).
        :param d: Dimension of feature vectors.
        alpha: Exploration parameter.
        """
        self.n_arms = n_arms
        self.d = d
        self.alpha = alpha

        self.A = [np.identity(d) for _ in range(n_arms)]
        self.b = [np.zeros((d, 1)) for _ in range(n_arms)]

    def select_arm(self, x):
        """
        Select an arm based on the current context x.
        :param x: The context feature vector.
        :return:
        The index of the selected arm.
        """
        x = x.reshape(-1, 1)
        p_values = []
        for a in range(self.n_arms):
            A_inv = np.linalg.inv(self.A[a])
            theta = A_inv @ self.b[a]
            p = float(theta.T @ x + self.alpha * np.sqrt(x.T @ A_inv @ x))
            p_values.append(p)
        return int(np.argmax(p_values))

    def update(self, chosen_arm, x, reward):
        """
        Update the model with the observed reward.
        :param chosen_arm: The index of the chosen arm.
        :param x: The context feature vector.
        :param reward: The observed reward.
        """
        x = x.reshape(-1, 1)
        self.A[chosen_arm] += x @ x.T
        self.b[chosen_arm] += reward * x

def extract_features(row, recent_demand, stock):
    """
    Extract features from the data row.
    :param row:
    :param recent_demand:
    :param stock:
    :return:
    A numpy array of features.
    """
    price = row["Price"]
    demand = recent_demand
    month = row["InvoiceDate"].month / 12.0
    stock_norm = stock / 100.0

    return np.array([price, demand, month, stock_norm]).reshape(-1, 1)

def compute_reward(price, quantity, price_change, avg_prev_price, alpha=0.1):
    """
    Compute the reward based on price, quantity, and price stability.
    :param price:
    :param quantity:
    :param price_change:
    :param avg_prev_price:
    :param alpha:
    :return:
    The computed reward.
    """
    profit = price * quantity
    instability_penalty = abs(price - avg_prev_price) * 20.0
    proxy_LTV = profit / 100.0

    stability_bonus = 0.0
    if price_change == 0.0:
        # Give a large, fixed bonus for choosing the "Maintain" action.
        # This represents the value of a stable, happy customer.
        # Let's try 50.0 to start.
        stability_bonus = 50.0

    return float(profit - instability_penalty + alpha * proxy_LTV + stability_bonus)

import numpy as np
import random


class LinUCB:
    """
    LinUCB algorithm for contextual bandits.
    """

    def __init__(self, n_arms, d, alpha=0.3):
        self.n_arms = n_arms
        self.d = d
        self.alpha = alpha
        self.A = [np.identity(d) for _ in range(n_arms)]
        self.b = [np.zeros((d, 1)) for _ in range(n_arms)]

    def select_arm(self, x):
        x = x.reshape(-1, 1)
        p_values = []
        for a in range(self.n_arms):
            A_inv = np.linalg.inv(self.A[a])
            theta = A_inv @ self.b[a]
            p = float(theta.T @ x + self.alpha * np.sqrt(x.T @ A_inv @ x))
            p_values.append(p)
        return int(np.argmax(p_values))

    def update(self, chosen_arm, x, reward):
        x = x.reshape(-1, 1)
        self.A[chosen_arm] += x @ x.T
        self.b[chosen_arm] += reward * x


def extract_features(month, stock):
    """
    Extract features from the data row.
    Context should only be external factors, not price.
    """
    month_norm = month / 12.0
    stock_norm = stock / 100.0

    # The context is 2-dimensional: demand, month, stock
    return np.array([month_norm, stock_norm])


def compute_reward(price, quantity, price_change, avg_prev_price, alpha=0.1):
    """
    Compute the reward. Let's use a simple, small penalty.
    """
    profit = price * quantity

    # We use a simple, small penalty to start
    instability_penalty = abs(price - avg_prev_price) * 0.5

    proxy_LTV = profit / 100.0

    return profit - instability_penalty + alpha * proxy_LTV

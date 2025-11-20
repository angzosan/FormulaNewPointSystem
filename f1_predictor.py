import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from collections import defaultdict
import time
import utils
import ast

# ---------------------------
# Feature Engineering
# ---------------------------

def extract_features(points):
    """Extract driver features from past race points."""
    arr = np.array(points, dtype=float)
    n = len(arr)
    if n == 0:
        return [0, 0, 0, 0, 0, 0]
    x = np.arange(n)
    slope = np.polyfit(x, arr, 1)[0] if n >= 2 else 0
    mean = float(arr.mean())
    last3 = float(arr[-3:].mean()) if n >= 3 else mean
    std = float(arr.std())
    best = float(arr.max())
    worst = float(arr.min())
    return [mean, last3, slope, std, best, worst]

# ---------------------------
# ML Monte Carlo Predictor (F1 points system)
# ---------------------------

def predict_champion_ml_positions(
    drivers_points, total_races, f1_points=None, sims=400, random_state=42
):
    """
    Predict F1 championship probabilities using ML + Monte Carlo.
    
    drivers_points: dict of driver -> list of past race points
    total_races: int, total races in the season
    f1_points: list of points by finishing position, e.g., [25,18,15,...]
    sims: Monte Carlo simulations
    """
    if f1_points is None:
        # Default F1 points (top 10)
        f1_points = [25, 18, 15, 12, 10, 8, 6, 4, 2, 1]
    # Extend to 20 drivers if needed
    f1_points += [0] * max(0, 20 - len(f1_points))

    # ---------------------------
    # Training ML model
    # ---------------------------
    X = []
    y = []

    for driver, pts in drivers_points.items():
        for i in range(1, len(pts)):
            X.append(extract_features(pts[:i]))
            y.append(pts[i])

    if len(X) < 10:
        raise ValueError("Not enough race data to train ML model.")

    X = np.array(X)
    y = np.array(y)

    model = RandomForestRegressor(
        n_estimators=30, random_state=random_state, n_jobs=-1
    )
    model.fit(X, y)

    # ---------------------------
    # Monte Carlo simulations
    # ---------------------------
    drivers = list(drivers_points.keys())
    current_points = {d: sum(drivers_points[d]) for d in drivers}
    remaining = {d: total_races - len(drivers_points[d]) for d in drivers}
    win_counts = defaultdict(int)
    expected_final = defaultdict(float)
    rng = np.random.default_rng(random_state)

    for sim_num in range(sims):

        start_time = time.time()
        sim_points = dict(current_points)
        histories = {d: drivers_points[d][:] for d in drivers}

        max_remaining = max(remaining.values())
        for r in range(max_remaining):
            predicted_scores = {}
            drivers_this_race = []

            # Generate predicted "performance" scores for each driver
            for d in drivers:
                if remaining[d] > r:
                    features = np.array(extract_features(histories[d])).reshape(1, -1)
                    pred = model.predict(features)[0]
                    pred += rng.normal(0, 3.0)  # randomness
                    pred = max(pred, 0)
                    predicted_scores[d] = pred
                    drivers_this_race.append(d)

            if not drivers_this_race:
                continue

            # Sort drivers by predicted score → finishing positions
            sorted_drivers = sorted(
                drivers_this_race, key=lambda d: predicted_scores[d], reverse=True
            )

            # Assign points based on F1 point system
            for pos, d in enumerate(sorted_drivers):
                pts = f1_points[pos] if pos < len(f1_points) else 0
                sim_points[d] += pts
                histories[d].append(pts)  # update history for next race

        # Determine winner(s)
        max_pts = max(sim_points.values())
        winners = [d for d, p in sim_points.items() if p == max_pts]
        for w in winners:
            win_counts[w] += 1 / len(winners)
        for d in drivers:
            expected_final[d] += sim_points[d]
        end_time = time.time()
        print(f"Simulation {sim_num} completed in {end_time - start_time:.2f} seconds.")

    # Normalize results
    win_prob = {d: win_counts[d] / sims for d in drivers}
    expected_pts = {d: expected_final[d] / sims for d in drivers}
    standings = sorted(expected_pts.items(), key=lambda x: -x[1])

    return {
        "win_probability": win_prob,
        "expected_points": expected_pts,
        "expected_standings": standings,
        "model_trained_on_samples": len(X),
        "sims": sims
    }
# Example usage:    
driver_points_df = pd.read_csv("drivers.csv")
for race_count in range(5,24):
    driver_points_map = utils.prepare_data_for_simulation(driver_points_df, race_count)
    results = predict_champion_ml_positions(drivers_points=driver_points_map, total_races=24)
    print(results)

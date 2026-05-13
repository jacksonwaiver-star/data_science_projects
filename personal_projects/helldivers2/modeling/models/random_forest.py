from sklearn.ensemble import RandomForestRegressor


def build_random_forest_model():

    model = RandomForestRegressor(
        n_estimators=200,
        random_state=42,
        n_jobs=-1
    )

    return model
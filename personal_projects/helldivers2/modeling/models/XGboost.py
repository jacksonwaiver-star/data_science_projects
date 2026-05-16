from xgboost import XGBRegressor


def build_xgboost_model():

    model = XGBRegressor(
        n_estimators=1000,
        learning_rate=0.03,
        max_depth=5,
    )

    return model
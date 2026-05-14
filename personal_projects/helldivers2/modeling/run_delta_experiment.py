# Delta Target Experiment Runner

# Full Delta Experiment File


import numpy as np
import pandas as pd

from helldivers2.load_data.load_data import (
    load_data
)

from helldivers2.preprocessing.preprocessing import (
    aggregate_total_players
)

from helldivers2.feature_engineering.features import (
    create_features
)

from helldivers2.modeling.train import (
    train_model
)

from helldivers2.modeling.evaluation import (
    evaluate_predictions
)

from helldivers2.modeling.models.linear_regression import (
    build_linear_regression_model
)

from helldivers2.modeling.models.random_forest import (
    build_random_forest_model
)

from helldivers2.modeling.models.XGboost import (
    build_xgboost_model
)

from helldivers2.modeling.plotting import (
    plot_predictions
)


def run_delta_experiment(

    experiment_name,

    model_type,

    features,

    feature_groups
):

    # =====================================
    # LOAD DATA
    # =====================================

    df_raw = load_data()

    # =====================================
    # PREPROCESS
    # =====================================

    ts_players = aggregate_total_players(
        df_raw
    )

    # =====================================
    # FEATURE ENGINEERING
    # =====================================

    df_features = create_features(

        ts_players,

        feature_groups=feature_groups
    )

    # =====================================
    # DELTA TARGET
    # Predict NEXT HOUR CHANGE
    # =====================================

    df_features["target"] = (

        df_features["total_players"]
        .shift(-1)

        - df_features["total_players"]
    )

    # =====================================
    # CLEAN DATA
    # =====================================

    df_model = (

        df_features
        .dropna()
        .reset_index(drop=True)
    )

    # =====================================
    # X / y
    # =====================================

    X = df_model[features]

    y = df_model["target"]

    # =====================================
    # TRAIN TEST SPLIT
    # =====================================

    split_index = int(
        len(df_model) * 0.8
    )

    X_train = X.iloc[:split_index]
    X_test = X.iloc[split_index:]

    y_train = y.iloc[:split_index]
    y_test = y.iloc[split_index:]

    # =====================================
    # MODEL SELECTION
    # =====================================

    if model_type == "linear_regression":

        model = build_linear_regression_model()

    elif model_type == "random_forest":

        model = build_random_forest_model()

    elif model_type == "xgboost":

        model = build_xgboost_model()

    else:

        raise ValueError(
            f"Unknown model_type: {model_type}"
        )

    # =====================================
    # TRAIN MODEL
    # =====================================

    model = train_model(

        model,

        X_train,

        y_train,

        X_test,

        y_test
    )

    # =====================================
    # PREDICT DELTA
    # =====================================

    predicted_delta = model.predict(X_test)

    # =====================================
    # RECONSTRUCT PLAYER COUNTS
    # =====================================

    current_players_test = (

        df_model
        .iloc[split_index:]["total_players"]
    )

    preds_eval = (
        current_players_test
        + predicted_delta
    )

    # =====================================
    # TRUE NEXT-HOUR PLAYER COUNTS
    # =====================================

    y_eval = (

        df_model
        .iloc[split_index:]["total_players"]
        .shift(-1)
    )

    # =====================================
    # REMOVE FINAL NaN
    # =====================================

    valid_mask = y_eval.notna()

    preds_eval = preds_eval[valid_mask]

    y_eval = y_eval[valid_mask]

    timestamps_eval = (

        df_model
        .iloc[split_index:]["timestamp"]
        [valid_mask]
    )

    # =====================================
    # EVALUATE
    # =====================================

    metrics = evaluate_predictions(

        y_eval,

        preds_eval
    )

    # =====================================
    # PLOT RESULTS
    # =====================================

    plot_predictions(

        timestamps=timestamps_eval,

        y_true=y_eval,

        preds=preds_eval,

        title=experiment_name
    )

    # =====================================
    # RETURN RESULTS
    # =====================================

    return {

        "experiment_name": experiment_name,

        "model_name": type(model).__name__,

        "model": model,

        "metrics": metrics,

        "predictions": preds_eval,

        "y_test": y_eval,

        "timestamps": timestamps_eval,

        "features": features,

        "target_type": "delta"
    }


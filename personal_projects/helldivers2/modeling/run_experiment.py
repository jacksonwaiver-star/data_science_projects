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

from sklearn.model_selection import (
    TimeSeriesSplit
)

def run_experiment(

    experiment_name,

    model_type,

    features,

    feature_groups,

    use_log_target=False
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
    # TARGET
    # =====================================

    if use_log_target:

        df_features["target"] = np.log1p(

            df_features["total_players"]
            .shift(-1)
        )

    else:

        df_features["target"] = (

            df_features["total_players"]
            .shift(-1)
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
    # PREDICT
    # =====================================

    preds = model.predict(X_test)

    # =====================================
    # UNDO LOG TARGET
    # =====================================

    if use_log_target:

        preds = np.expm1(preds)

        y_eval = np.expm1(y_test)

    else:

        y_eval = y_test

    # =====================================
    # EVALUATE
    # =====================================

    metrics = evaluate_predictions(

        y_eval,

        preds
    )

    # =====================================
    # PLOT RESULTS
    # =====================================

    plot_predictions(

        timestamps=(
            df_model
            .iloc[split_index:]["timestamp"]
        ),

        y_true=y_eval,

        preds=preds,

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

        "predictions": preds,

        "y_test": y_eval,

        "timestamps": (
            df_model
            .iloc[split_index:]["timestamp"]
        ),

        "features": features,

        "use_log_target": use_log_target
    }
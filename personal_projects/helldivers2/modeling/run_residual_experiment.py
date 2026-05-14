import numpy as np
import pandas as pd

from helldivers2.modeling.models.linear_regression import (
    build_linear_regression_model
)

from helldivers2.modeling.models.XGboost import (
    build_xgboost_model
)

from helldivers2.load_data.load_data import (
    load_data
)

from helldivers2.preprocessing.preprocessing import (
    aggregate_total_players
)

from helldivers2.feature_engineering.features import (
    create_features
)

from helldivers2.modeling.evaluation import (
    evaluate_predictions
)

from helldivers2.modeling.plotting import (
    plot_predictions
)


def run_residual_experiment(

    experiment_name,

    features,

    feature_groups,
    
    residual_weight=1,

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
    # PRINT FEATURES
    # =====================================

    print(df_features.columns.tolist())

    # =====================================
    # TARGET
    # Predict NEXT hour total_players
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
    # BASE MODEL
    # LINEAR REGRESSION
    # =====================================

    linear_model = build_linear_regression_model()

    linear_model.fit(

        X_train,

        y_train
    )

    # =====================================
    # LINEAR PREDICTIONS
    # =====================================

    linear_train_preds = (
        linear_model.predict(X_train)
    )

    linear_test_preds = (
        linear_model.predict(X_test)
    )

    # =====================================
    # RESIDUAL TARGET
    # What linear regression missed
    # =====================================

    residual_train = (
        y_train
        - linear_train_preds
    )

    # =====================================
    # RESIDUAL MODEL
    # XGBOOST
    # =====================================

    residual_model = build_xgboost_model()

    residual_model.fit(

        X_train,

        residual_train
    )

    # =====================================
    # PREDICT RESIDUALS
    # =====================================

    residual_preds = (
        residual_model.predict(X_test)
    )

    # =====================================
    # FINAL PREDICTIONS
    # Linear + Residual Correction
    # =====================================

    preds = (

        linear_test_preds
        + (residual_preds * residual_weight)
    )

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

        "model_name": "LinearPlusResidualXGBoost",

        "linear_model": linear_model,

        "residual_model": residual_model,

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
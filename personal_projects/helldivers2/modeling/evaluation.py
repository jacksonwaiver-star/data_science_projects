from sklearn.metrics import (
    mean_absolute_error,
    root_mean_squared_error
)


def evaluate_predictions(
    y_true,
    preds
):

    mae = mean_absolute_error(
        y_true,
        preds
    )

    rmse = root_mean_squared_error(
        y_true,
        preds
    )

    return {
        "mae": mae,
        "rmse": rmse
    }
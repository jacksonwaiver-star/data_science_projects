import numpy as np


def train_model(
    model,
    X_train,
    y_train,
    X_test=None,
    y_test=None
):

    # XGBoost special handling
    if hasattr(model, "early_stopping_rounds"):

        model.fit(
            X_train,
            y_train,
            eval_set=[(X_test, y_test)],
            verbose=True
        )

    else:

        model.fit(
            X_train,
            y_train
        )

    return model
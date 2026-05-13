import matplotlib.pyplot as plt
import pandas as pd


def plot_predictions(
    timestamps,
    y_true,
    preds,
    title="Actual vs Predicted"
):

    plot_df = pd.DataFrame({

        "timestamp": timestamps,

        "actual": y_true,

        "predicted": preds
    })

    plt.figure(figsize=(14, 6))

    plt.plot(
        plot_df["timestamp"],
        plot_df["actual"],
        label="Actual"
    )

    plt.plot(
        plot_df["timestamp"],
        plot_df["predicted"],
        label="Predicted"
    )

    plt.title(title)

    plt.xlabel("Timestamp")

    plt.ylabel("Players")

    plt.legend()

    plt.xticks(rotation=45)

    plt.tight_layout()

    plt.show()
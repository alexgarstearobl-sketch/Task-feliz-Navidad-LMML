from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def main():
    folder = Path(__file__).resolve().parent
    purchases = pd.read_csv(folder / "purchases.csv")
    price_guide = pd.read_csv(folder / "office_price_guide.csv")

    merged = pd.merge(purchases, price_guide, on="Product")
    for column in ("Total_paid_eur", "Quantity", "Fair_min_eur", "Fair_max_eur", "Pilot_no", "List_no"):
        merged[column] = pd.to_numeric(merged[column], errors="coerce")

    merged["unit_price"] = merged["Total_paid_eur"] / merged["Quantity"]
    valid = merged[
        (merged["City"] == merged["Home_city"])
        & (merged["unit_price"] >= merged["Fair_min_eur"])
        & (merged["unit_price"] <= merged["Fair_max_eur"])
        & merged["Pilot_no"].between(1, 21)
        & merged["List_no"].between(1, 6)
    ]

    board = (
        valid.assign(found=1)
        .pivot_table(
            index="List_no",
            columns="Pilot_no",
            values="found",
            aggfunc="max",
            fill_value=0,
        )
        .reindex(index=range(1, 7), columns=range(1, 22), fill_value=0)
        .astype(int)
    )

    print("Board (List_no 1 at top; # = valid purchase):")
    for product_number, row in board.iterrows():
        print(f"{product_number}: {''.join('#' if value else '.' for value in row)}")

    fig, axis = plt.subplots(figsize=(13, 4.5))
    axis.imshow(
        board.to_numpy(),
        cmap="Greens",
        vmin=0,
        vmax=1,
        interpolation="none",
        aspect="auto",
        origin="upper",
    )
    axis.set_xticks(np.arange(21), labels=np.arange(1, 22))
    axis.set_yticks(np.arange(6), labels=np.arange(1, 7))
    axis.set_xlabel("Pilot_no")
    axis.set_ylabel("List_no")
    axis.set_xticks(np.arange(-0.5, 21, 1), minor=True)
    axis.set_yticks(np.arange(-0.5, 6, 1), minor=True)
    axis.grid(which="minor", color="white", linewidth=1.5)
    axis.tick_params(which="minor", bottom=False, left=False)
    fig.tight_layout()
    fig.savefig(folder / "board.png", bbox_inches="tight", dpi=200)
    plt.show()


if __name__ == "__main__":
    main()
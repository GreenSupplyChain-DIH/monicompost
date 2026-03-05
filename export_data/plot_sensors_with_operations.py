import pathlib

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import pandas as pd

BASE_DIR = pathlib.Path(__file__).resolve().parents[1]

# Paths
PH_PATH = BASE_DIR / "export_data" / "ThingsBoards-PH-01.csv"
SOIL_PATH = BASE_DIR / "export_data" / "ThingBoard-Humidity-01.csv"
CLOUD_OPS_PATH = BASE_DIR / "cloud_pile_log.csv"
EDGE_OPS_PATH = BASE_DIR / "edge_pile_log.csv"


def load_sensor_data():
    ph_df = pd.read_csv(PH_PATH)
    soil_df = pd.read_csv(SOIL_PATH)

    # ThingsBoard exports use a timestamp_UTC column; parse and store in a common
    # "Time" column so the rest of the code can treat TB and other sources
    # uniformly.
    ph_df["Time"] = pd.to_datetime(ph_df["timestamp_UTC"], utc=True, format='mixed').dt.tz_convert(None)
    soil_df["Time"] = pd.to_datetime(soil_df["timestamp_UTC"], utc=True, format='mixed').dt.tz_convert(None)
    return ph_df, soil_df


def load_operations():
    cloud = pd.read_csv(CLOUD_OPS_PATH)
    edge = pd.read_csv(EDGE_OPS_PATH)

    cloud["pile"] = "cloud"
    edge["pile"] = "edge"

    ops = pd.concat([cloud, edge], ignore_index=True)
    ops["timestamp"] = pd.to_datetime(ops["timestamp"])

    # Drop exact duplicates (same timestamp, operation, parameter, value, pile)
    ops = ops.drop_duplicates()
    return ops


def _operation_style(operation: str):
    """Map raw operation text to a category and plotting style."""
    op = (operation or "").lower()

    if "add raw material" in op:
        return "Add raw material", {"color": "tab:green"}
    if "irrigation" in op:
        return "Irrigation", {"color": "tab:blue"}
    if "turning" in op:
        return "Turning", {"color": "tab:orange"}
    if "npk" in op or "analysis" in op:
        return "Analysis / NPK", {"color": "tab:red"}
    if "ph" in op:
        return "pH correction", {"color": "tab:purple"}

    return "Other operation", {"color": "grey"}


def plot_soil_moisture(soil_df: pd.DataFrame, ops: pd.DataFrame):
    fig, ax1 = plt.subplots(figsize=(12, 6))

    ax1.plot(
        soil_df["Time"],
        soil_df["data_water_SOIL"],
        label="Soil water (TB)",
        color="tab:blue",
    )
    ax1.set_xlabel("Time")
    ax1.set_ylabel("Soil moisture", color="tab:blue")

    # Optional: add soil temperature on secondary axis
    ax2 = ax1.twinx()
    ax2.plot(
        soil_df["Time"],
        soil_df["data_temp_SOIL"],
        label="Soil temperature (TB)",
        color="tab:orange",
        alpha=0.5,
    )
    ax2.set_ylabel("Temperature (°C)", color="tab:orange")

    # Overlay operations as vertical lines, color-coded by type
    legend_handles = {}
    y_top = ax1.get_ylim()[1]

    for _, row in ops.iterrows():
        ts = row["timestamp"]
        op_cat, style = _operation_style(str(row["operation"]))
        color = style["color"]

        ax1.axvline(ts, color=color, linestyle="--", alpha=0.4)
        ax1.scatter(ts, y_top, color=color, marker="v", s=25)

        if op_cat not in legend_handles:
            legend_handles[op_cat] = Line2D(
                [0],
                [0],
                color=color,
                linestyle="--",
                marker="v",
                markersize=6,
                label=op_cat,
            )

    # Legend: sensor series + operation categories
    handles = [
        Line2D([0], [0], color="tab:blue", label="Soil water (TB)"),
    ] + list(legend_handles.values())
    ax1.legend(handles=handles, loc="upper left")

    ax1.set_title("Soil moisture & temperature with operations")
    fig.autofmt_xdate()
    fig.tight_layout()


def plot_ph(ph_df: pd.DataFrame, ops: pd.DataFrame):
    fig, ax1 = plt.subplots(figsize=(12, 6))

    # ThingsBoard pH sensor columns
    ph_col = "data_PH1_SOIL"
    temp_col = "data_TEMP_SOIL"

    ax1.plot(ph_df["Time"], ph_df[ph_col], label="Soil pH (TB)", color="tab:green")
    ax1.set_xlabel("Time")
    ax1.set_ylabel("pH", color="tab:green")

    ax2 = ax1.twinx()
    ax2.plot(
        ph_df["Time"],
        ph_df[temp_col],
        label="Soil temperature",
        color="tab:purple",
        alpha=0.5,
    )
    ax2.set_ylabel("Temperature (°C)", color="tab:purple")

    legend_handles = {}
    y_top = ax1.get_ylim()[1]

    for _, row in ops.iterrows():
        ts = row["timestamp"]
        op_cat, style = _operation_style(str(row["operation"]))
        color = style["color"]

        ax1.axvline(ts, color=color, linestyle="--", alpha=0.4)
        ax1.scatter(ts, y_top, color=color, marker="v", s=25)

        if op_cat not in legend_handles:
            legend_handles[op_cat] = Line2D(
                [0],
                [0],
                color=color,
                linestyle="--",
                marker="v",
                markersize=6,
                label=op_cat,
            )

    handles = [
        Line2D([0], [0], color="tab:green", label="Soil pH (TB)"),
    ] + list(legend_handles.values())
    ax1.legend(handles=handles, loc="upper left")

    ax1.set_title("Soil pH & temperature with operations")
    fig.autofmt_xdate()
    fig.tight_layout()


def main():
    ph_df, soil_df = load_sensor_data()
    ops = load_operations()

    plot_soil_moisture(soil_df, ops)
    plot_ph(ph_df, ops)

    plt.show()


if __name__ == "__main__":
    main()

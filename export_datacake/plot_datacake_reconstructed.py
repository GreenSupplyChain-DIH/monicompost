"""
Plot Datacake reconstructed + original sensor data with compost operations overlay.

Generates four subplots:
  1. Soil Conductivity
  2. Soil Moisture
  3. Soil Temperature (from moisture sensor)
  4. Soil pH & pH-sensor Temperature

Operations from cloud_pile_log.csv and edge_pile_log.csv are drawn as
colour-coded vertical lines.
"""

import pathlib

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.lines import Line2D
import pandas as pd

BASE_DIR = pathlib.Path(__file__).resolve().parents[1]

# --- data paths ---
SOIL_PATH = BASE_DIR / "export_data" / "Datacake_soil_moisture_reconstructed_stat_peaks.csv"
PH_PATH   = BASE_DIR / "export_data" / "Datacake_ph_sensor_reconstructed_stat_peaks.csv"
CLOUD_OPS = BASE_DIR / "cloud_pile_log.csv"
EDGE_OPS  = BASE_DIR / "edge_pile_log.csv"


# ── loaders ──────────────────────────────────────────────────────────────────

def load_soil() -> pd.DataFrame:
    df = pd.read_csv(SOIL_PATH)
    df.columns = df.columns.str.strip().str.strip('"')
    df["Time"] = pd.to_datetime(df["Time"], format="%a, %d %b %Y %H:%M:%S")
    for c in ["AgriFood Soil Moisture EC / Soil Conductivity",
              "AgriFood Soil Moisture EC / Soil Moisture",
              "AgriFood Soil Moisture EC / Soil Temperature"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    return df


def load_ph() -> pd.DataFrame:
    df = pd.read_csv(PH_PATH)
    df.columns = df.columns.str.strip().str.strip('"')
    df["Time"] = pd.to_datetime(df["Time"], format="%a, %d %b %Y %H:%M:%S")
    for c in ["AgriFood Soil PH / PH1_SOIL",
              "AgriFood Soil PH / TEMP_SOIL"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    return df


def load_operations() -> pd.DataFrame:
    cloud = pd.read_csv(CLOUD_OPS)
    edge  = pd.read_csv(EDGE_OPS)
    cloud["pile"] = "cloud"
    edge["pile"]  = "edge"
    ops = pd.concat([cloud, edge], ignore_index=True).drop_duplicates()
    ops["timestamp"] = pd.to_datetime(ops["timestamp"])
    return ops


# ── styling helpers ──────────────────────────────────────────────────────────

OP_STYLES = {
    "add raw material": ("Add raw material",  "tab:green"),
    "irrigation":       ("Irrigation",         "tab:blue"),
    "turning":          ("Turning",            "tab:orange"),
    "analysis":         ("Analysis / NPK",     "tab:red"),
    "npk":              ("Analysis / NPK",     "tab:red"),
    "ph":               ("pH correction",      "tab:purple"),
}

def _op_style(operation: str):
    op = (operation or "").lower()
    for key, (cat, col) in OP_STYLES.items():
        if key in op:
            return cat, col
    return "Other", "grey"


def _draw_operations(ax, ops: pd.DataFrame, legend_handles: dict):
    """Draw operation vertical lines on an axes and collect legend handles."""
    for _, row in ops.iterrows():
        ts = row["timestamp"]
        cat, color = _op_style(str(row["operation"]))
        ax.axvline(ts, color=color, linestyle="--", alpha=0.35, linewidth=0.8)
        if cat not in legend_handles:
            legend_handles[cat] = Line2D(
                [0], [0], color=color, linestyle="--",
                marker="v", markersize=5, label=cat)


def _shade_sources(ax, df: pd.DataFrame):
    """Lightly shade 'reconstructed' vs 'original' spans."""
    src = df["source"].str.strip().str.strip('"')
    recon_mask = src == "reconstructed"
    if recon_mask.any():
        t0 = df.loc[recon_mask, "Time"].iloc[0]
        t1 = df.loc[recon_mask, "Time"].iloc[-1]
        ax.axvspan(t0, t1, color="lightyellow", alpha=0.35, zorder=0)
    orig_mask = src == "original"
    if orig_mask.any():
        t0 = df.loc[orig_mask, "Time"].iloc[0]
        t1 = df.loc[orig_mask, "Time"].iloc[-1]
        ax.axvspan(t0, t1, color="lightcyan", alpha=0.30, zorder=0)


# ── main plotting ────────────────────────────────────────────────────────────

def main():
    soil_df = load_soil()
    ph_df   = load_ph()
    ops     = load_operations()

    fig, axes = plt.subplots(4, 1, figsize=(16, 18), sharex=True)
    fig.suptitle("Datacake Reconstructed Sensor Data with Compost Operations",
                 fontsize=14, fontweight="bold", y=0.995)

    op_legend = {}  # shared operation legend entries

    # SHORT aliases
    cond_col  = "AgriFood Soil Moisture EC / Soil Conductivity"
    moist_col = "AgriFood Soil Moisture EC / Soil Moisture"
    temp_col  = "AgriFood Soil Moisture EC / Soil Temperature"
    ph_col    = "AgriFood Soil PH / PH1_SOIL"
    ph_temp   = "AgriFood Soil PH / TEMP_SOIL"

    # ── 1. Soil Conductivity ─────────────────────────────────────────────
    ax = axes[0]
    _shade_sources(ax, soil_df)
    ax.plot(soil_df["Time"], soil_df[cond_col],
            linewidth=0.6, color="tab:brown", label="Conductivity (µS/cm)")
    ax.set_ylabel("Conductivity (µS/cm)")
    ax.set_title("Soil Conductivity")
    _draw_operations(ax, ops, op_legend)
    ax.legend(loc="upper left", fontsize=8)
    ax.grid(True, alpha=0.3)

    # ── 2. Soil Moisture ─────────────────────────────────────────────────
    ax = axes[1]
    _shade_sources(ax, soil_df)
    ax.plot(soil_df["Time"], soil_df[moist_col],
            linewidth=0.6, color="tab:blue", label="Moisture (%)")
    ax.set_ylabel("Moisture (%)")
    ax.set_title("Soil Moisture")
    _draw_operations(ax, ops, op_legend)
    ax.legend(loc="upper left", fontsize=8)
    ax.grid(True, alpha=0.3)

    # ── 3. Soil Temperature (moisture sensor) ────────────────────────────
    ax = axes[2]
    _shade_sources(ax, soil_df)
    ax.plot(soil_df["Time"], soil_df[temp_col],
            linewidth=0.6, color="tab:red", label="Temperature (°C)")
    ax.set_ylabel("Temperature (°C)")
    ax.set_title("Soil Temperature (moisture sensor)")
    _draw_operations(ax, ops, op_legend)
    ax.legend(loc="upper left", fontsize=8)
    ax.grid(True, alpha=0.3)

    # ── 4. pH + pH-sensor temperature ────────────────────────────────────
    ax = axes[3]
    _shade_sources(ax, ph_df)
    ax.plot(ph_df["Time"], ph_df[ph_col],
            linewidth=0.6, color="tab:green", label="pH")
    ax.set_ylabel("pH", color="tab:green")
    ax.set_title("Soil pH & pH-sensor Temperature")
    ax.grid(True, alpha=0.3)

    ax2 = ax.twinx()
    ax2.plot(ph_df["Time"], ph_df[ph_temp],
             linewidth=0.5, color="tab:purple", alpha=0.6, label="Temp (pH sensor)")
    ax2.set_ylabel("Temperature (°C)", color="tab:purple")

    _draw_operations(ax, ops, op_legend)

    # combine legends for the twin axes
    lines1, labels1 = ax.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax.legend(lines1 + lines2, labels1 + labels2, loc="upper left", fontsize=8)

    # ── shared X-axis format ─────────────────────────────────────────────
    axes[-1].set_xlabel("Date")
    axes[-1].xaxis.set_major_locator(mdates.WeekdayLocator(interval=2))
    axes[-1].xaxis.set_major_formatter(mdates.DateFormatter("%d %b"))
    fig.autofmt_xdate(rotation=45)

    # ── operation legend (shared, at bottom) ─────────────────────────────
    if op_legend:
        source_handles = [
            Line2D([0], [0], color="khaki", linewidth=6, alpha=0.5, label="Reconstructed period"),
            Line2D([0], [0], color="lightcyan", linewidth=6, alpha=0.5, label="Original period"),
        ]
        fig.legend(
            handles=list(op_legend.values()) + source_handles,
            loc="lower center", ncol=len(op_legend) + 2,
            fontsize=8, frameon=True,
        )

    fig.tight_layout(rect=[0, 0.04, 1, 0.98])

    out_path = BASE_DIR / "export_data" / "DC_reconstructed_overview.png"
    fig.savefig(out_path, dpi=150)
    print(f"Saved → {out_path}")
    plt.show()


if __name__ == "__main__":
    main()

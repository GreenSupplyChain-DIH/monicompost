"""
Comparative plot: ThingsBoard vs Datacake (reconstructed) sensor data.

Layout (6 subplots, 2 columns):
  Left column  – pH sensor comparison (pH, Temperature)
  Right column – Soil moisture sensor comparison (Moisture, Temperature, Conductivity)
  Plus one shared panel for source-period legend.
"""

import pathlib

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
import pandas as pd

BASE_DIR = pathlib.Path(__file__).resolve().parents[1]
EXPORT = BASE_DIR / "export_data"

# ── file paths ───────────────────────────────────────────────────────────────
TB_PH   = EXPORT / "ThingsBoards-PH-01.csv"
TB_SOIL = EXPORT / "ThingBoard-Humidity-01.csv"
DC_PH   = EXPORT / "Datacake_ph_sensor_reconstructed_stat_peaks.csv"
DC_SOIL = EXPORT / "Datacake_soil_moisture_reconstructed_stat_peaks.csv"


# ── loaders ──────────────────────────────────────────────────────────────────

def load_tb_ph() -> pd.DataFrame:
    df = pd.read_csv(TB_PH)
    df["Time"] = pd.to_datetime(df["timestamp_UTC"], utc=True, format="mixed").dt.tz_convert(None)
    return df


def load_tb_soil() -> pd.DataFrame:
    df = pd.read_csv(TB_SOIL)
    df["Time"] = pd.to_datetime(df["timestamp_UTC"], utc=True, format="mixed").dt.tz_convert(None)
    return df


def load_dc_ph() -> pd.DataFrame:
    df = pd.read_csv(DC_PH)
    df.columns = df.columns.str.strip().str.strip('"')
    df["Time"] = pd.to_datetime(df["Time"], format="%a, %d %b %Y %H:%M:%S")
    for c in ["AgriFood Soil PH / PH1_SOIL", "AgriFood Soil PH / TEMP_SOIL"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df["source"] = df["source"].str.strip().str.strip('"')
    return df


def load_dc_soil() -> pd.DataFrame:
    df = pd.read_csv(DC_SOIL)
    df.columns = df.columns.str.strip().str.strip('"')
    df["Time"] = pd.to_datetime(df["Time"], format="%a, %d %b %Y %H:%M:%S")
    for c in [
        "AgriFood Soil Moisture EC / Soil Conductivity",
        "AgriFood Soil Moisture EC / Soil Moisture",
        "AgriFood Soil Moisture EC / Soil Temperature",
    ]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df["source"] = df["source"].str.strip().str.strip('"')
    return df


# ── helpers ──────────────────────────────────────────────────────────────────

TB_COLOR = "tab:blue"
DC_RECON_COLOR = "tab:orange"
DC_ORIG_COLOR = "tab:green"
LW = 0.6


def _plot_dc_by_source(ax, dc_df, col, recon_kw=None, orig_kw=None):
    """Plot Datacake data split by source with different colours."""
    recon = dc_df[dc_df["source"] == "reconstructed"]
    orig  = dc_df[dc_df["source"] == "original"]

    rkw = {"color": DC_RECON_COLOR, "linewidth": LW, "label": "DC reconstructed"}
    if recon_kw:
        rkw.update(recon_kw)
    okw = {"color": DC_ORIG_COLOR, "linewidth": LW, "label": "DC original"}
    if orig_kw:
        okw.update(orig_kw)

    if not recon.empty:
        ax.plot(recon["Time"], recon[col], **rkw)
    if not orig.empty:
        ax.plot(orig["Time"], orig[col], **okw)


def _fmt(ax):
    ax.grid(True, alpha=0.25)
    ax.legend(loc="upper left", fontsize=7, framealpha=0.85)


# ── main ─────────────────────────────────────────────────────────────────────

def main():
    tb_ph   = load_tb_ph()
    tb_soil = load_tb_soil()
    dc_ph   = load_dc_ph()
    dc_soil = load_dc_soil()

    fig, axes = plt.subplots(3, 2, figsize=(18, 14), sharex=True)
    fig.suptitle("ThingsBoard vs Datacake – Sensor Comparison",
                 fontsize=15, fontweight="bold", y=0.995)

    # ── LEFT COLUMN: pH sensor ───────────────────────────────────────────

    # Row 0, Col 0 — pH value
    ax = axes[0, 0]
    ax.set_title("pH Sensor – pH Value", fontsize=11)
    ax.plot(tb_ph["Time"], tb_ph["data_PH1_SOIL"],
            color=TB_COLOR, linewidth=LW, label="TB pH")
    _plot_dc_by_source(ax, dc_ph, "AgriFood Soil PH / PH1_SOIL")
    ax.set_ylabel("pH")
    _fmt(ax)

    # Row 1, Col 0 — pH sensor temperature
    ax = axes[1, 0]
    ax.set_title("pH Sensor – Temperature", fontsize=11)
    ax.plot(tb_ph["Time"], tb_ph["data_TEMP_SOIL"],
            color=TB_COLOR, linewidth=LW, label="TB temp")
    _plot_dc_by_source(ax, dc_ph, "AgriFood Soil PH / TEMP_SOIL")
    ax.set_ylabel("Temperature (°C)")
    _fmt(ax)

    # Row 2, Col 0 — empty / residual
    ax = axes[2, 0]
    # Show pH difference (DC original − TB) where both have data
    dc_orig_ph = dc_ph[dc_ph["source"] == "original"].set_index("Time")["AgriFood Soil PH / PH1_SOIL"]
    tb_ph_s = tb_ph.set_index("Time")["data_PH1_SOIL"]
    # Resample both to common 20-min grid to align
    dc_orig_20 = dc_orig_ph.resample("20min").mean().dropna()
    tb_ph_20   = tb_ph_s.resample("20min").mean().dropna()
    common = dc_orig_20.index.intersection(tb_ph_20.index)
    if len(common) > 0:
        diff = dc_orig_20.loc[common] - tb_ph_20.loc[common]
        ax.plot(common, diff, color="tab:red", linewidth=0.5, alpha=0.7)
        ax.axhline(0, color="grey", linestyle="--", linewidth=0.5)
        ax.set_title("pH Difference (DC original − TB)", fontsize=11)
        ax.set_ylabel("ΔpH")
    else:
        ax.set_title("pH Difference (no overlapping data)", fontsize=11)
    _fmt(ax)

    # ── RIGHT COLUMN: Soil moisture / EC sensor ─────────────────────────

    # Row 0, Col 1 — Soil Moisture
    ax = axes[0, 1]
    ax.set_title("Soil Moisture Sensor – Moisture", fontsize=11)
    ax.plot(tb_soil["Time"], tb_soil["data_water_SOIL"],
            color=TB_COLOR, linewidth=LW, label="TB moisture")
    _plot_dc_by_source(ax, dc_soil, "AgriFood Soil Moisture EC / Soil Moisture")
    ax.set_ylabel("Moisture (%)")
    _fmt(ax)

    # Row 1, Col 1 — Soil Temperature
    ax = axes[1, 1]
    ax.set_title("Soil Moisture Sensor – Temperature", fontsize=11)
    ax.plot(tb_soil["Time"], tb_soil["data_temp_SOIL"],
            color=TB_COLOR, linewidth=LW, label="TB temp")
    _plot_dc_by_source(ax, dc_soil, "AgriFood Soil Moisture EC / Soil Temperature")
    ax.set_ylabel("Temperature (°C)")
    _fmt(ax)

    # Row 2, Col 1 — Soil Conductivity
    ax = axes[2, 1]
    ax.set_title("Soil Moisture Sensor – Conductivity", fontsize=11)
    ax.plot(tb_soil["Time"], tb_soil["data_conduct_SOIL"],
            color=TB_COLOR, linewidth=LW, label="TB conductivity")
    _plot_dc_by_source(ax, dc_soil, "AgriFood Soil Moisture EC / Soil Conductivity")
    ax.set_ylabel("Conductivity (µS/cm)")
    _fmt(ax)

    # ── X-axis formatting ────────────────────────────────────────────────
    for ax in axes[-1, :]:
        ax.set_xlabel("Date")
        ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=2))
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%d %b"))

    fig.autofmt_xdate(rotation=45)

    # ── shared legend at bottom ──────────────────────────────────────────
    legend_elements = [
        Line2D([0], [0], color=TB_COLOR, linewidth=2, label="ThingsBoard"),
        Line2D([0], [0], color=DC_RECON_COLOR, linewidth=2, label="Datacake reconstructed"),
        Line2D([0], [0], color=DC_ORIG_COLOR, linewidth=2, label="Datacake original"),
    ]
    fig.legend(handles=legend_elements, loc="lower center", ncol=3,
               fontsize=10, frameon=True)

    fig.tight_layout(rect=[0, 0.04, 1, 0.97])

    out = EXPORT / "TB_vs_DC_comparison.png"
    fig.savefig(out, dpi=150)
    print(f"Saved → {out}")
    plt.show()


if __name__ == "__main__":
    main()

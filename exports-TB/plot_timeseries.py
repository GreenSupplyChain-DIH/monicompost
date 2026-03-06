#!/usr/bin/env python3
"""
Flexible timeseries plotting script for CSV files.
Automatically detects timestamp and data columns, creates subplots for each.

Usage:
    python plot_timeseries.py <csv_file> [--output <output_file>] [--title <title>]
    
Examples:
    python plot_timeseries.py Humidity-01.csv
    python plot_timeseries.py PH-01.csv --output ph_plot.png --title "pH Sensor Data"
"""

import argparse
import sys
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


def detect_timestamp_column(df: pd.DataFrame) -> str:
    """Detect the timestamp column by name pattern or datetime type."""
    timestamp_patterns = ['timestamp', 'time', 'date', 'datetime']
    
    for col in df.columns:
        col_lower = col.lower()
        if any(pattern in col_lower for pattern in timestamp_patterns):
            return col
    
    # Fallback: try to parse first column as datetime
    try:
        pd.to_datetime(df.iloc[:, 0])
        return df.columns[0]
    except Exception:
        pass
    
    raise ValueError("Could not detect timestamp column. Ensure CSV has a timestamp/date column.")


def get_data_columns(df: pd.DataFrame, timestamp_col: str) -> list:
    """Get all numeric data columns excluding the timestamp."""
    data_cols = []
    for col in df.columns:
        if col != timestamp_col:
            if pd.api.types.is_numeric_dtype(df[col]):
                data_cols.append(col)
    return data_cols


def format_column_name(col_name: str) -> str:
    """Format column name for display (cleaner labels)."""
    # Remove common prefixes
    name = col_name
    for prefix in ['data_', 'DATA_']:
        if name.startswith(prefix):
            name = name[len(prefix):]
    
    # Replace underscores with spaces and title case
    name = name.replace('_', ' ').title()
    return name


def plot_timeseries(csv_path: str, output_path: str = None, title: str = None, dpi: int = 150):
    """
    Create timeseries plot from CSV file.
    
    Args:
        csv_path: Path to the CSV file
        output_path: Output PNG path (default: <csv_name>_timeseries.png)
        title: Plot title (default: derived from filename)
        dpi: Output resolution
    """
    csv_path = Path(csv_path)
    
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_path}")
    
    # Read CSV
    df = pd.read_csv(csv_path)
    
    # Detect timestamp column and parse dates
    ts_col = detect_timestamp_column(df)
    df[ts_col] = pd.to_datetime(df[ts_col], format='mixed', utc=True)
    
    # Get data columns
    data_cols = get_data_columns(df, ts_col)
    
    if not data_cols:
        raise ValueError("No numeric data columns found in CSV.")
    
    # Set default output path
    if output_path is None:
        output_path = csv_path.with_name(f"{csv_path.stem}_timeseries.png")
    
    # Set default title
    if title is None:
        title = f"{csv_path.stem} Timeseries"
    
    # Color palette
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', 
              '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
    
    # Create subplots
    n_plots = len(data_cols)
    fig, axes = plt.subplots(n_plots, 1, figsize=(14, 3 * n_plots + 1), sharex=True)
    
    # Handle single subplot case
    if n_plots == 1:
        axes = [axes]
    
    fig.suptitle(title, fontsize=14, fontweight='bold')
    
    for i, col in enumerate(data_cols):
        ax = axes[i]
        color = colors[i % len(colors)]
        
        ax.plot(df[ts_col], df[col], color=color, linewidth=0.8)
        ax.set_ylabel(format_column_name(col))
        ax.grid(True, alpha=0.3)
        
        # Add min/max/mean annotation
        valid_data = df[col].dropna()
        if len(valid_data) > 0:
            stats_text = f"Min: {valid_data.min():.2f}  Max: {valid_data.max():.2f}  Mean: {valid_data.mean():.2f}"
            ax.text(0.02, 0.95, stats_text, transform=ax.transAxes, fontsize=8,
                   verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    # Format x-axis on bottom subplot
    axes[-1].set_xlabel('Date (UTC)')
    axes[-1].xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    axes[-1].xaxis.set_major_locator(mdates.AutoDateLocator())
    plt.xticks(rotation=45)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=dpi, bbox_inches='tight')
    plt.close()
    
    print(f"Plot saved: {output_path}")
    return output_path


def main():
    parser = argparse.ArgumentParser(
        description='Create timeseries plots from CSV files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument('csv_file', help='Path to the CSV file')
    parser.add_argument('--output', '-o', help='Output PNG file path')
    parser.add_argument('--title', '-t', help='Plot title')
    parser.add_argument('--dpi', type=int, default=150, help='Output resolution (default: 150)')
    
    args = parser.parse_args()
    
    try:
        plot_timeseries(args.csv_file, args.output, args.title, args.dpi)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()

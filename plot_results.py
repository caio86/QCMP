import argparse
from pathlib import Path

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from matplotlib.axes import Axes


def plot_h3_rx(h3_rx_stat_path, ax: Axes | None = None, pps=400):
    df = pd.read_csv(h3_rx_stat_path)

    df["time_diff"] = df["timestamp"].diff()
    df["packets_diff"] = df["rx_packets"].diff()
    df["pps"] = df["packets_diff"] / df["time_diff"]
    df["pps"] = df["pps"].fillna(0)

    df.loc[df["pps"] < 0, "pps"] = 0

    df["relative_time"] = df["timestamp"] - df["timestamp"].iloc[0]

    QCMP_values = df["pps"].to_list()
    time = df["relative_time"].to_list()

    QCMP_df = pd.DataFrame({'values': QCMP_values})
    QCMP_ma = QCMP_df.rolling(window=10, min_periods=1).mean()

    queue = 0
    QCMP_drops = []
    for i in QCMP_values:
        queue += pps - i
        QCMP_drops.append(max(0, queue - 100))
        queue = min(queue, 100)


    QCMP_drops_df = pd.DataFrame({'values': QCMP_drops})
    QCMP_drops_ma = QCMP_drops_df.rolling(window=10, min_periods=1).mean()

    standalone = ax is None

    if standalone:
        fig, ax = plt.subplots(figsize=(8, 8))

    ax.set_xlim(left=0, right=max(time))
    ax.set_ylim(bottom=0, top=pps+20)
    ax.plot(time, QCMP_ma, color='b', label = "QCMP")
    ax.plot(time, QCMP_drops_ma, color='b', label = "QCMP Drops", linestyle='--')
    # ax.set_title("Packets per Second")
    ax.legend(loc=4, bbox_to_anchor=(1, 0.1))
    ax.grid(alpha=0.3)
    ax.set_xlabel('Time (s)')
    ax.set_ylabel('Packets per Second')

    if standalone:
        return fig
    return None


def plot_path_weights(path_weights_path, ax: Axes | None = None):
    df = pd.read_csv(path_weights_path)

    df["relative_time"] = df["timestamp"] - df["timestamp"].iloc[0]

    standalone = ax is None
    if standalone:
        fig, ax = plt.subplots(figsize=(8,8))

    ax.set_xlim(left=0, right=max(df["relative_time"]))
    ax.set_ylim(bottom=0, top=110)
    ax.set_yticks(np.arange(0, 110, 10))
    ax.plot(df["relative_time"], df["path1_weight"], color="b", label="path1")
    ax.axhline(df["path1_weight"].mean(), linestyle="--", alpha=0.6, color="b", label="path1 mean")
    ax.plot(df["relative_time"], df["path2_weight"], color="g", label="path2")
    ax.axhline(df["path2_weight"].mean(), linestyle="--", alpha=0.6, color="g", label="path2 mean")
    # ax.set_title("Path Weights")
    ax.legend(loc=4, bbox_to_anchor=(1, 0.1))
    ax.grid(alpha=0.3)
    ax.set_xlabel('Time (s)')
    ax.set_ylabel('Path Weight')

    if standalone:
        return fig
    return None


def plot_path_queues(path_queues_path, ax: Axes | None =None):
    df = pd.read_csv(path_queues_path)

    df["relative_time"] = df["timestamp"] - df["timestamp"].iloc[0]

    standalone = ax is None
    if standalone:
        fig, ax = plt.subplots(figsize=(8,8))

    ax.set_xlim(left=0, right=max(df["relative_time"]))
    ax.plot(df["relative_time"], df["path1_queue"], color="b", label="path1")
    ax.plot(df["relative_time"], df["path2_queue"], color="g", label="path2")
    # ax.set_title("Path Queues")
    ax.legend(loc=4, bbox_to_anchor=(1, 0.1))
    ax.grid(alpha=0.3)
    ax.set_xlabel('Time (s)')
    ax.set_ylabel('Path Queue')

    if standalone:
        return fig
    return None


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("-o", "--output-dir", help="Output dir to store plotted results", required=True)
    parser.add_argument("-P", "--pps", help="Packets per second", type=int, required=False)
    parser.add_argument("path_weights_path", help="Path to path weights csv data")
    parser.add_argument("h3_rx_stat_path", help="Path to h3 rx stat csv data")

    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    h3_rx_stat_path = Path(args.h3_rx_stat_path)
    path_weights_path = Path(args.path_weights_path)

    output_dir.mkdir(parents=True, exist_ok=True)

    fig1 = plot_h3_rx(h3_rx_stat_path, pps=args.pps)
    fig1.tight_layout()
    fig1.savefig(output_dir / "pps.png", dpi=300)
    plt.close(fig1)

    fig2 = plot_path_weights(path_weights_path)
    fig2.tight_layout()
    fig2.savefig(output_dir / "path_weight.png", dpi=300)
    plt.close(fig2)

    fig3 = plot_path_queues(path_weights_path)
    fig3.tight_layout()
    fig3.savefig(output_dir / "path_queue.png", dpi=300)
    plt.close(fig3)

    fig = plt.figure(figsize=(14, 5*2))
    gs = fig.add_gridspec(2, 2)
    # axes = gs.subplots(sharex=True)

    ax_h3 = fig.add_subplot(gs[0:2, 0])
    ax_weights = fig.add_subplot(gs[0, 1])
    ax_queues = fig.add_subplot(gs[1, 1], sharex=ax_weights)

    plot_h3_rx(h3_rx_stat_path, ax=ax_h3, pps=args.pps)
    plot_path_weights(path_weights_path, ax=ax_weights)
    plot_path_queues(path_weights_path, ax=ax_queues)

    fig.tight_layout()

    fig.savefig(output_dir / "all.png", dpi=300)
    plt.close(fig)


if __name__ == "__main__":
    main()

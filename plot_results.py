from pathlib import Path
import argparse
import pandas as pd
from matplotlib import pyplot as plt

def plot_h3_rx(output_dir, h3_rx_stat_path):
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
        queue += 380 - i
        QCMP_drops.append(max(0, queue - 100))
        queue = min(queue, 100)


    QCMP_drops_df = pd.DataFrame({'values': QCMP_drops})
    QCMP_drops_ma = QCMP_drops_df.rolling(window=10, min_periods=1).mean()

    fig, ax = plt.subplots(figsize=(14, 6))
    ax.set_xlim(left=0, right=max(time))
    ax.set_ylim(bottom=0, top=420)
    ax.plot(time, QCMP_ma, color='b', label = "QCMP")
    ax.plot(time, QCMP_drops_ma, color='b', label = "QCMP Drops", linestyle='--')
    ax.legend(loc=4, bbox_to_anchor=(1, 0.1))
    ax.set_xlabel('Time (s)')
    ax.set_ylabel('Packets per Second')
    # plt.show()
    plt.savefig(f"{output_dir}/pps.png")

    QCMP_sorted = QCMP_ma.sort_values('values')
    QCMP_cdf = [x/(len(QCMP_sorted.values)-1) for x in range(len(QCMP_sorted.values))]
    QCMP_sorted['cdf'] = QCMP_cdf

    plt.axvline(x=252, color='red', linestyle=':')
    plt.axvline(x=351, color='blue', linestyle=':')

    plt.axvline(x=380, color='grey', linestyle='--')
    plt.axvline(x=361, color='grey', linestyle='--')
    plt.axhline(y=0.78, color='grey', linestyle='--')
    plt.axhline(y=0.38, color='grey', linestyle='--')
    plt.axhline(y=0.0095, color='grey', linestyle='--')

    plt.tick_params(axis='y', left=True, right=False)
    plt.tick_params(axis='x', bottom=True, top=False)
    plt.ylabel('CDF')
    plt.ylim(bottom=0, top=1)
    plt.xlabel('Packets per Second')
    plt.xlim(left=150, right=400)
    plt.legend(loc=2)

    ax2 = plt.twinx()
    yticks = [0.010, 0.38, 0.78]
    yticklabels = ['0.010', '0.38', '0.78']
    ax2.set_yticks(yticks)
    ax2.set_yticklabels(yticklabels)
    plt.tick_params(axis='y', left=False, right=True, labelright=True)

    ax3 = plt.twiny()
    xticks = [0.844, 0.92]
    xticklabels = ['95%', '100%']
    ax3.set_xticks(xticks)
    ax3.set_xticklabels(xticklabels)
    plt.tick_params(axis='x', bottom=False, top=True, labeltop=True)

    # plt.show()
    plt.savefig(f"{output_dir}/cdf.png")


def plot_path_weights(output_dir, path_weights_path):
    df = pd.read_csv(path_weights_path)

    df["relative_time"] = df["timestamp"] - df["timestamp"].iloc[0]

    plt.figure(figsize=(14,6))
    plt.plot(df["relative_time"], df["path1_weight"], color="b", label="path1")
    plt.plot(df["relative_time"], df["path2_weight"], color="g", label="path2")
    plt.legend(loc=4, bbox_to_anchor=(1, 0.1))
    plt.xlabel('Time (s)')
    plt.ylabel('Path Weight')
    # plt.show()
    plt.savefig(f"{output_dir}/path_weight.png")


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("-o", "--output-dir", help="Output dir to store plotted results", required=True)
    parser.add_argument("path_weights_path", help="Path to path weights csv data")
    parser.add_argument("h3_rx_stat_path", help="Path to h3 rx stat csv data")

    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    h3_rx_stat_path = Path(args.h3_rx_stat_path)
    path_weights_path = Path(args.path_weights_path)

    output_dir.mkdir(parents=True, exist_ok=True)

    plot_h3_rx(output_dir, h3_rx_stat_path)
    plot_path_weights(output_dir, path_weights_path)

if __name__ == "__main__":
    main()

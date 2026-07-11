import time
import os

log_file = "./logs/h3_rx_stats.csv"

with open(log_file, "w") as f:
    f.write("timestmap,rx_packets\n")

while True:
    try:
        with open("/sys/class/net/eth0/statistics/rx_packets", "r") as f:
            rx_packets = f.read().strip()

        with open(log_file, "r") as f:
            f.write(f"{time.time()},{rx_packets}\n")

    except KeyboardInterrupt:
        break
    except Exception:
        pass

    time.sleep(1)

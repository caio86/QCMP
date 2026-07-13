import time
import sys

log_file = "./data/h3_rx_stats.csv"

with open(log_file, "w") as f:
    f.write("timestmap,rx_packets\n")

while True:
    try:
        with open("/sys/class/net/eth0/statistics/rx_packets", "r") as f:
            rx_packets = f.read().strip()

        print("Rx packets:", rx_packets)

        with open(log_file, "a") as f:
            f.write(f"{time.time()},{rx_packets}\n")

    except KeyboardInterrupt:
        print("Exiting")
    except Exception as e:
        print("Error: ", e, file=sys.stderr)

    time.sleep(1)

TOTAL=200
get_rate() {
    local val=$1
    if [[ "$val" =~ ^[0-9]+%$ ]]; then
        local pct="${val%\%}"
        echo $(( (TOTAL * pct) / 100 ))
    elif [[ "$val" =~ ^[0-9]+$ ]]; then
        echo "$val"
    else
        echo "INVALID"
    fi
}


RATE_P3=$(get_rate "$1")
RATE_P4=$(get_rate "$2")

if [[ "$RATE_P3" = "INVALID" || $RATE_P4 = "INVALID" ]]; then
    echo "INVALID input" >&2
    exit 1
fi

echo "Using configuration:"
echo " -> Port 3 Queue Rate: $RATE_P3 pps"
echo " -> Port 4 Queue Rate: $RATE_P4 pps"

TIME=$(date +%s)

mkdir logs 2>/dev/null
mkdir data 2>/dev/null

MININET_FIFO="./logs/mininet_input.fifo"
rm -f $MININET_FIFO
mkfifo $MININET_FIFO


echo "Creating topology"
tail -f "$MININET_FIFO" | make run > logs/mininet_runtime.log 2> logs/mininet_runtime.err &
MININET_PID=$!

sleep 8

echo "Starting control plane on switch 1"
echo "s1 ./set_switches.sh $RATE_P3 $RATE_P4 > logs/s1_runtime.log 2> logs/s1_runtime.err &" > "$MININET_FIFO"

sleep 1

echo "Initiating Telemetry on host 2"
echo "h2 python3 get_queues_layer1.py > logs/h2_runtime.log 2> logs/h2_runtime.err &" > "$MININET_FIFO"

sleep 1

echo "Executing traffic monitor on host 3"
echo "h3 python3 monitor_h3.py > logs/h3_monitor.log 2> logs/h3_monitor.err &" > "$MININET_FIFO"

sleep 5

echo "Begin main payload on host 1"
echo "h1 python3 send.py > logs/h1_runtime.log 2> logs/h1_runtime.err &" > "$MININET_FIFO"

sleep 5

echo "Experiment runnning"
echo "  Monitoring send.py execution on h1"

ELAPSED=0
while pgrep -f "python3 send.py" > /dev/null; do
    sleep 10
    ELAPSED=$((ELAPSED + 10))
    echo "  -> send.py is active (${ELAPSED}s elapsed)..."
done

echo "send.py is not active"
echo "Shutting down topology"

echo "exit" > "$MININET_FIFO"
sleep 2

make stop
kill $MININET_PID 2>/dev/null
rm -f "$MININET_FIFO"

DATA_DIR="./data/P3_${RATE_P3}_P4_${RATE_P4}_${TIME}"

mkdir $DATA_DIR

mv "./data/h3_rx_stats.csv" "./data/path_weights.csv" -t "$DATA_DIR"

python3 ./plot_results.py -o "$DATA_DIR" --pps $TOTAL "$DATA_DIR/path_weights.csv" "$DATA_DIR/h3_rx_stats.csv"

echo "Saving collected data to ${DATA_DIR}/"
sleep 1

echo "Done"

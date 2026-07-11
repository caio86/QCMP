RATE_P3=200
RATE_P4=200

echo "Using configuration:"
echo " -> Port 3 Queue Rate: $RATE_P3 pps"
echo " -> Port 4 Queue Rate: $RATE_P4 pps"

mkdir logs 2>/dev/null

MININET_FIFO="./logs/mininet_input.fifo"
rm -f $MININET_FIFO
mkfifo $MININET_FIFO


echo "Creating topology"
tail -f "$MININET_FIFO" | make run > logs/mininet_runtime.log 2> logs/mininet_runtime.err &
MININET_PID=$!

sleep 8

echo "Starting control plane on switch 1"
echo "s1 ./set_switches.sh $RATE_P3 $RATE_P4 > logs/s1_runtime.log 2> logs/s1_runtime.err &" > "$MININET_FIFO"

sleep 3

echo "Initiating Telemetry on host 2"
echo "h2 python3 get_queues_layer1.py > logs/h2_runtime.log 2> logs/h2_runtime.err &" > "$MININET_FIFO"

sleep 3

echo "Executing traffic monitor on host 3"
echo "h3 python3 monitor_h3.py > logs/h3_monitor.log 2> logs/h3_monitor.err &" > "$MININET_FIFO"

sleep 1

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

echo "Done"
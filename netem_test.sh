#!/bin/bash
# This script is used to test the network emulation function of netem.
TEST_OBJECT="speed-test-medium.html"
TEST_TIMES=10

SERVER_IP=111.229.132.28
SERVER_PORT=443


# output dir with timestamp
output_dir="netem_test_$(date +%Y%m%d%H%M%S)"
mkdir -p $output_dir
H1_dir="$output_dir/http1.1"
H2_dir="$output_dir/http2"
H3_dir="$output_dir/http3"
mkdir -p $H1_dir
mkdir -p $H2_dir
mkdir -p $H3_dir

# curl time output format
output_header="time_namelookup,time_connect,time_appconnect,time_pretransfer,time_starttransfer,time_total"
output_format="%{time_namelookup},%{time_connect},%{time_appconnect},%{time_pretransfer},%{time_starttransfer},%{time_total}\n"

# delay array (ms)
delay=(0 10 20 30 40 50 60 70 80 90 100 110 120 130 140 150)

# loss array (%)
loss=(0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15)

# total test times
total_times=$((${#delay[@]} * ${#loss[@]} * $TEST_TIMES))

# use netem to emulate the network
for i in ${delay[@]}
do
    for j in ${loss[@]}
    do
        echo "delay: $i ms, loss: $j %"
        sudo tc qdisc add dev eth0 root netem delay ${i}ms loss ${j}%

        # run the test
        # http1.1
        output_file="$H1_dir/delay_${i}_loss_${j}.csv"
        echo $output_header > $output_file
        for k in $(seq 1 $TEST_TIMES)
        do
            # show a process bar
            echo  ">>> progress: $((k + (j + i * ${#loss[@]}) * $TEST_TIMES)) / $total_times"
            curl --http1.1 -k https://$SERVER_IP:80/$TEST_OBJECT -w "$output_format" -o /dev/null >> $output_file
        done

        # http2
        output_file="$H2_dir/delay_${i}_loss_${j}.csv"
        echo $output_header > $output_file
        for k in $(seq 1 $TEST_TIMES)
        do
            # show a process bar
            echo  ">>> progress: $((k + (j + i * ${#loss[@]}) * $TEST_TIMES)) / $total_times"
            curl --http2 -k https://$SERVER_IP:$SERVER_PORT/$TEST_OBJECT -w "$output_format" -o /dev/null >> $output_file
        done

        # http3
        output_file="$H3_dir/delay_${i}_loss_${j}.csv"
        echo $output_header > $output_file
        for k in $(seq 1 $TEST_TIMES)
        do
            # show a process bar
            echo  ">>> progress: $((k + (j + i * ${#loss[@]}) * $TEST_TIMES)) / $total_times"
            curl --http3-only -k https://$SERVER_IP:$SERVER_PORT/$TEST_OBJECT -w "$output_format" -o /dev/null >> $output_file
        done

        sudo tc qdisc del dev eth0 root netem
    done
done
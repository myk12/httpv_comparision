#!/bin/bash
# This script is used to test the network emulation function of netem.
TEST_OBJECT="speed-test-medium.html"
TEST_TIMES=3

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
delay=(0 50 100 150 200 250 300)

# loss array (%)
loss=(0 5 10 15 20)

# total test times
total_times=$((${#delay[@]} * ${#loss[@]} * $TEST_TIMES))

# use netem to emulate the network
cycle_cnt=0
for i in ${delay[@]}
do
    for j in ${loss[@]}
    do
        cycle_cnt=$(($cycle_cnt + 1))
        echo "delay: $i ms, loss: $j %"
        sudo tc qdisc add dev eth0 root netem delay ${i}ms loss ${j}%

        # run the test
        # http1.1
        output_file="$H1_dir/delay_${i}_loss_${j}.csv"
        echo $output_header > $output_file

        # output current progress
        echo "progress http1.1: $cycle_cnt / $total_times"
        for k in $(seq 1 $TEST_TIMES)
        do
            # show a process bar
            curl --http1.1 -k https://$SERVER_IP:80/$TEST_OBJECT -w "$output_format" -o /dev/null >> $output_file
        done

        # http2
        output_file="$H2_dir/delay_${i}_loss_${j}.csv"
        echo $output_header > $output_file
        echo "progress http2: $cycle_cnt / $total_times"
        for k in $(seq 1 $TEST_TIMES)
        do
            # show a process bar
            curl --http2 -k https://$SERVER_IP:$SERVER_PORT/$TEST_OBJECT -w "$output_format" -o /dev/null >> $output_file
        done

        # http3
        output_file="$H3_dir/delay_${i}_loss_${j}.csv"
        echo $output_header > $output_file
        echo "progress http3: $cycle_cnt / $total_times"
        for k in $(seq 1 $TEST_TIMES)
        do
            # show a process bar
            curl --http3-only -k https://$SERVER_IP:$SERVER_PORT/$TEST_OBJECT -w "$output_format" -o /dev/null >> $output_file
        done

        sudo tc qdisc del dev eth0 root netem
    done
done
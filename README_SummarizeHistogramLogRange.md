SummarizeHistogramLogRange.jar is used to produce convinient data format for python from HdrHistograms.
More information about HdhrHistogram can be found here http://hdrhistogram.org/

USAGE OF SummarizeHistogramLogRange.jar:

java -jar ./SummarizeHistogramLogRange.jar -s $start_time -e $end_time -ip $path -if $fullname -v -of $out_path$new_name.rd

-s hdrh start time
-e hdrh end time
-ip input folder
-if input file
-v adds verbousity
-of output file name with path

========================================================================================================================

OUTPUT FILE FORMAT:

TotalCount=949876
Period(ms)=100000
Throughput(ops/sec)=9498,76
Min=164
Mean=695,57
50.000ptile=287
90.000ptile=370
99.000ptile=20255
99.900ptile=44383
99.990ptile=52831
99.999ptile=57471
Max=59679
0,0
1,0
2,0

12 lines in the beggining are header lines and afterwards the main data goes. Each line contains the the X value at the first place, and the amount of the events corresponding to this X value at the second. Also anything separated with "," can be aded to the end of each line. 
In this example first number is latency, second is amount of request with this latency.

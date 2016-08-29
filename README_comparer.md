comparer.py is a script, used to compare noisy distributions by their percentiles values. 
For any questions please write: anton.rykachevskiy@yandex.ru


INSTALLATION:

Python 2.7 is required.
The list of packages to install is in the requirments.txt

The other way is to install Anaconda python from https://www.continuum.io/downloads

===============================================================================================================================


USAGE:

optional arguments:
  -h, --help            show this help message and exit
  -if INPUT_FOLDERS INPUT_FOLDERS
                        Two folders where data is strored, use space to
                        separate them from each other. (See the description about file format below)
  -rq REQUIRED_NAME_PART
                        Required string in the name of the file.
  -bn BUILDS_NAMES BUILDS_NAMES
                        Name of builds, use space to separate one from
                        another.
  -v VERBOUSE           Verbousity level, should be 0, 1, 2, 3, where 0 is for
                        no information and 3 is all posible information.
  -ot OUTLIERS_TREASHOLD
                        Set outliers treashold. 1.0 - no outliers, 0.0 - every
                        point is an outlier
  -p                    Plot percentile values in separate window. 
  -chp [PERCENTILES_SET [PERCENTILES_SET ...]]
                        Change default percentile set.
  -of OUTPUT_FILE       Output file name with path.
  -oi OUTPUT_IMAGE      Output image name with path.

=================================================================================================================================

EXAMPLE OF USAGE:

$~: python ./comparer.py -if ./first_build ./second_build -rq READ -bn First_build Second_build -v 3 -ot 0.95 -p -chp 90 99 99.99 -of ./log.out -oi ./first_vs_second.jpg

In this example all files from ./first_build folder will be considered as the first build samples, and files from ./second_build will be considered as the second build samples. Only files which contain READ in file name will be taken to consideration. Verbousity is set to maximum posible value, read the description of the output below. Threashold is set to 0.95, which means percentiles values which do not lie in 95% probability interval would be dropped from consideration. -p means the second window will be opened with ploted percentiles, be careful using this flag, when running the script many times from bash. -chp flag sets the comparasing set to three values, the default is: [50, 90, 99, 99.9, 99.99]. Results will be printed to log.out and the percentiles plots will be saved to first_vs_second.jpg

==================================================================================================================================

OUTPUT EXAMPLE:

percentile value: 99.0
first folder mean and std: 449.75, 3.30718913883
second folder mean and std: 449.75, 3.1124748995
Probability of being drown from different distr.: 0.0142547351923

number of data points to compare: 8, 4
dropped runs names: ['300_400_d-2016.06.22-18.27.49-ycsb-run-READ.rd', '200_300_d-2016.06.22-18.11.16-ycsb-run-READ.rd', '200_300_d-2016.06.22-18.27.49-ycsb-run-READ.rd', '300_400_d-2016.06.22-18.11.16-ycsb-run-READ.rd']
dropped runs names: ['200_400_d-2016.06.22-18.11.16-ycsb-run-READ.rd', '200_400_d-2016.06.22-18.27.49-ycsb-run-READ.rd']
KS_values : 0.967853515059, 0.941244292293

First four lines are the default ones. The main value is the 4th, if it's large we expect the difference in two builds. 
5th line shows how many data points are taken from the first group of runs and from the second one after the outliers are dropped
6th and 7th lines show names of runs where the outliers where
8-th line, called KS_values shows probability of percentiles being normaly distrbed. If this value is very small (0.2 - 0.1), than the behavior
of the build is unusuall around this percentile, so you better take a look at the plots or do investigate it somehow else.

====================================================================================================================================

INPUT FILE FORMAT:

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

=======================================================================================================================================


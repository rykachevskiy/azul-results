#!/bin/bash
python .././plotter.py -if ./data/$1 ./data/$2 ./data/$3 -bn $1 $2 $3 -rq READ -al 0 800 0 0.02 -p -oi $1_$2.jpg

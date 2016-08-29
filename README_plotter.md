Plotter is a script which plots probability density functions. 
You can input any number of folders, each of which contains any number of exact build runs. 
Everything will be plotted on the same figure, different colors for different builds.
Output image can be set up using -oi flag.

INSTALLATION:
comparer.py is required in the same folder. 

Python 2.7 is required.
The list of packages to install is in the requirments.txt

The other way is to install Anaconda python from https://www.continuum.io/downloads

===================================================================================================================================

USAGE:

usage: plotter.py [-h] [-if [INPUT_FOLDERS [INPUT_FOLDERS ...]]]
                  [-rq REQUIRED_NAME_PART]
                  [-bn [BUILDS_NAMES [BUILDS_NAMES ...]]] [-oi OUTPUT_IMAGE]
                  [-al AXES_LIMITS AXES_LIMITS AXES_LIMITS AXES_LIMITS] [-aa]
                  [-p]

Process some integers.

optional arguments:
  -h, --help            show this help message and exit
  -if [INPUT_FOLDERS [INPUT_FOLDERS ...]]
                        Folders where data is stored, use space to separate
                        them from each other.
  -rq REQUIRED_NAME_PART
                        Required string in the names of the all files.
  -bn [BUILDS_NAMES [BUILDS_NAMES ...]]
                        Name of builds, use space to separate one from
                        another. Should be the same amount as input folders
  -oi OUTPUT_IMAGE      Output image name with path.
  -al AXES_LIMITS AXES_LIMITS AXES_LIMITS AXES_LIMITS
                        Axes limits.
  -aa                   Set axes limits automaticly. X is 0 to 99tile, Y is 0
                        to 1.2*max
  -p                    Plot in external window.

======================================================================================================================================

EXAMPLE OF USAGE:

python ./plotter.py -if ./data/$1 ./data/$2 -bn $1 $2 -rq READ -al 0 800 0 0.02 -p -oi $1_$2.jp



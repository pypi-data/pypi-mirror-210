# OKNPATCH PYTHON PACKAGE LIBRARY MANUAL
## Description
This program will fix or rerun the web experiment related functions.

There are 2 types of oknpatch which are:
1.  **trial_data_lost** which is to fix the data lost of trial csv by referencing the gaze.csv.  
2.  **update** which is to rerun the given trial csv by the updater function of the oknserver.  

## Installation requirements and guide
### Anaconda
To install this program, `Anaconda python distributing program` and `Anaconda Powershell Prompt` are needed.  
If you do not have `Anaconda`, please use the following links to download and install:  
Download link: https://www.anaconda.com/products/distribution  
Installation guide link: https://docs.anaconda.com/anaconda/install/  
### PIP install
To install `oknpatch`, you have to use `Anaconda Powershell Prompt`.  
After that, you can use the `oknpatch` from any command prompt.  
In `Anaconda Powershell Prompt`:
```
pip install oknpatch
```  
## Usage guide
### Example usage
```
oknpatch -t "(type)" -i "(first input)" -si "(second input)" -ti "(third input)"
```
### The usage will be depend on the type of oknpatch. 
There is a example folder under `development` folder.  
If you want to test this program, you can clone this repository, install `oknpatch` and run the following command:  
For **trial_data_lost** oknpatch type  
```
oknpatch -t trial_data_lost -i development/example/trial-2_disk-condition-1-1.csv -si development/example/gaze.csv
```
For **update** oknpatch type  
```
oknpatch -t update -i development/example/trial-2_disk-condition-1-1.csv
```
That will rerun the updater function of oknserver and produce `updated_trial-2_disk-condition-1-1.csv`.  
Since there is only input (-i) in the command line, it will use default `extra_string` which is "updated_" to give the output csv name and it will use build-in config to update the given csv.  
If you want to give your custom `extra_string`, use (-si):  
If you want to use your own config to update, use (-ti):
```
oknpatch -t update -i development/example/trial-2_disk-condition-1-1.csv -si "(custom extra string)" -ti "(directory to your custom config)"
```
### To upgrade version  
In `Anaconda Powershell Prompt`,
```
pip install -U oknpatch
```
or
```
pip install --upgrade oknpatch
```

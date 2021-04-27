# AI4RO2_E
Repo for group E project related to the 1st AI4RO2 assignment


## Content

```
AI4RO2_E/
	|
	domains/
		|
		<pddl domain and problem files with fluents only for metric-ff solver (basic specifics of the assignment)>
		dom_APE/
		       |
		       <pddl domain and problem files including actions, processes and events (full specifics of the assignment including extensions)>
	lib/
	   |
	   <sensitivity analysis dataset containing the relevant pices of information and results for each problem run>
	output/
	      |
	      <ouput file of solved pddl problems>
	script/
	      |				
	      <python scripts for automatic generation, running and post-processing of pddl problems>
		templates/
			 |
			 <templates of the pddl problem file components for the automatic generation of the problems>
								
```

### domains

Multiple domains and problems formulation are here presented.
The files suitable for enhsp are stored in the folder **dom_APE** 
The folder **dom_Metric** contains the pddl problems and 

### lib

This folder conteins the datasets for the sensityivity analysis of the problem to the main input parameters.

### output

This folder is intended for storing the ouptut files of the planning problems solved by the planning engine. 

### script

In this folder are stored the python scripts for performing an automatic run of a .

## ENHSP

The APE domains and problems generated via the python scripts are suitable to be tested with the ENHSP planning engine, which can be found 

[here](https://gitlab.com/enricos83/ENHSP-Public/-/tree/enhsp-20).

That planners has been tested on Ubuntu 18.04 and 20.04 and different .

Note: 
- both the versions of enhsp 19 and 20 version have been tested but, due to performance reasons on most of the generate problems (not generalizable to any problem),
the release 20 has been chosen in this specific application.
- the off-the-shelf compiled version was discarded due to it not managing to set hw, gw appropriately (despite passing them from command line)

### Compiling enhsp-20

- Cloning the repository from the above mentioned link.
- Pulling the "enhsp-20" branch
- Install the dependencies 
```
$ sudo apt-get install openjdk-8-jdk
$ sudo apt-get update
```
- Run the "compile" and the "install" script
- Add the "enhsp" path in the ".bashrc" file 

The planner can be then executed from the root folder using the following command:
```
./enhsp -o <domain_file> -f <problem_file> -planner <string> (main options: sat, aibr, opt, lm_opt)
```
## Metric-FF

DA VALUTARE SE TENERE O MENO

### Compiling Metric-FF

From within the *Metric-FF* folder simply invoke the make command
```
$ cd Metric-FF
$ make
```
which will create the executable **ff**

### Running Metric-FF

The command **ff** needs to be run from within th *Metric-FF* folder.
If you want to be able tu run it from everywhere on your system add it to your user path like this, supposing to have this folder installed in your system HOME directory
```
$ echo 'export PATH="${HOME}/AI4RO2_E/Metric-FF:${PATH}"' >> ~/.bashrc
$ source ~/.bashrc
```
(Change the "${HOME}" accordingly to where you put clone repo)
The syntax to run the engine (assuming to have added **ff** to the path) is
```
$ ff -o <path/to/domain> -f <path/to/problem>
```
Specifically, in our case can be used in this fashion
```
.../AI4RO2_E/domains/$ ff -o numeric_domain.pddl -f numeric_problem.pddl -O
```
Where the '-O' flag is necessary to instruct ff to use a metric explicitly defined inside the problem file (otherwise it would simply use the plan length).

### New option: Print Fluents value

After 18 years it's now possibile to print fluents values at each traversed state!
The command line option "-s" has been added among those accepted by the code; by specifying a string after it
only the fluents whose name starts with such string (a de facto prefix) will be printed. Specifying '-' as that string
will print all present "interesting" fluents. Notice that this check is not case sensitive (since the inner representations
of fluents in Metric-FF have Upper Case names).
For example, to see all the fluents regarding the internal clock of the waiter we can use
```
.../AI4RO2_E/domains/$ ff -o numeric_domain.pddl -f numeric_problem.pddl -O -s TIME-WAITER
```


## TODO

- Why is problem APE3_full so much harder to deal with compared with AP2_full? Is it the fact that all 4 drinks are hot, or is it because they are spread between tables? Investigate.
- Test APE_full domain substituting pick-N, drop-N with fluents (Tested by Marco and underperforming the case with 2  different dedicated actions for picking up and dropping more than one drink/bisquit)
- A lot of the efficiency depends on the gw value... is it possible to find a correlation between some problem variables and its "close-to-optimal" value? ... Some ML agent perhaps? Multi linear interpolation perhaps?

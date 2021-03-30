# AI4RO2_E
Repo for group E project related to the 1st AI4RO2 assignment

## Content

```
AI4RO2_E/
	|
	Metric-FF/
		|
		<stuff to compile>
	domains/
		|
		<domain and problem files>
```

## Compiling Metric-FF

From within the *Metric-FF* folder simply invoke the make command
```
$ cd Metric-FF
$ make
```
which will create the executable **ff**

## Running Metric-FF

The command **ff** needs to be run from within th *Metric-FF* folder.
If you want to be able tu run it from everywhere on your system add it to your user path like this
```
$ echo 'export PATH="<path/to/Metric-FF>:${PATH}"' >> ~/.bash_profile
$ source ~/.bash_profile
```
In which 'path/to/Metric-FF' is the absolute path to the Metric-FF folder in your system.
The syntax to run the engine (assuming to have added **ff** to the path) is
```
$ ff -o <path/to/domain> -f <path/to/problem>
```
Specifically, in our case can be used in this fashion
```
.../AI4RO2_E/domains/$ ff -o numeric_domain.pddl -f numeric_problem.pddl -O
```
Where the '-O' flag is necessary to instruct ff to use a metric explicitly defined inside the problem file (otherwise it would simply use the plan length).

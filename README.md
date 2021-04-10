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

### Domains

Multiple domains are presented, from the original one up to the one having bothe the cooling and drink consumption
extensions (as specified in the name).

### Problems

The 4 problem files presented are those expressed in the assignment requirements.

## Metric-FF

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

## ENHSP

The domains and problems are suitable to be tested with the ENHSP planning engine, which can be found 
[here](https://gitlab.com/enricos83/ENHSP-Public/-/tree/enhsp-19).
That planners has been tested on Ubuntu 18.04 and 20.04.
Notice that, while enhsp-20 version exists, it resulted in having almost half the performances of -19 version for the presented domain, as shown in the tables reported in the "considerations.md" file.

## TODO

- Test APE_full domain substituting pick-N, drop-N with fluents
- Python script to easily generate a problem file given some human readable specs
- A lot of the efficiency depends on the gw value... is it possible to find a correlation between some problem variables and its "close-to-optimal" value? ... Some ML agent perhaps? Multi linear interpolation perhaps?
-   Add an option for ff command line that toggles the display of actions

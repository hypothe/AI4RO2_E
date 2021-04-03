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

## New option: Print Fluents value

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

- Add an option for ff command line that toggles the display of actions
- find a possible implementation for 2 waiters synchronization
- Try to install ENHSP and see how it behaves on the docker


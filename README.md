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
        dom_numeric/
               |
               <pddl domain and problem files including fluents, compatible with metric-ff (full specifics of the assignment, not including the two waiters and the buiscut                     extensions)>
    lib/
       |
       <sensitivity analysis dataset containing the relevant pieces of information and results for each problem run>
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

This folder contains the datasets for the sensitivity analysis of the problem to the main input parameters.

### output

This folder is intended for storing the output files of the planning problems solved by the planning engine.

### script

In this folder are stored the python scripts for performing an automatic run of a .

## ENHSP

The APE domains and problems generated via the python scripts are suitable to be tested with the ENHSP planning engine, which can be found

[here](https://gitlab.com/enricos83/ENHSP-Public/-/tree/enhsp-20).

That planners has been tested on Ubuntu 18.04 and 20.04 and different planning engines have been evaluated as well.

Note:
- both the enhsp 19 and 20 have been tested but, due to performance reasons on most of the generate problems (not generalizable to any problem),
the release 20 has been chosen for this specific application.
- the off-the-shelf compiled version was discarded due to it not managing to set hw, gw appropriately (despite passing them from command line).
- metric-ff has been used for a numeric like description of the problem but, due to difficulties in the implementation of the second waiter extension, this
  planning engine has been abandoned.

### Compiling enhsp-20

- Cloning the repository from the above mentioned link.
- Pulling the "enhsp-20" branch
- Install the java 1.8 dependencies
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


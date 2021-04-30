# Domains and Problems presented

## PDDL+

All files written with the PDDL+ formalism used by ENHSP can be found under `dom_APE` (_Action, Processes, Events_).
All files with suffix "full" integrate all 4 extensions to the problem.
In this folder one domain is present (`numeric_domain_APE_full.pddl`) together with the four problems described in the assignment (`numeric_problem_APE#_full.pddl`, where _#_ indicates the number of the problem as reported on the assignment text).
Furthermore, a file `Custom.pddl` is present and is where, by default, problems generated through the script `build.py` will be saved.
Additional temporary files will be generated if the script `test_data.py` is run representing the random problem generated by it.

Variations on the basic version are present under the subfolder `dom_APE/vars`. These are:

- `numeric_problem_APE#.pddl`: the description of the four problems without extensions under PDDL+ formalism
- `numeric_domain_APE_cool_cons.pddl`: the description of the domain with only the "cooling" and "consumption" extensions, under PDDL+ formalism
- `numeric_domain_APE_pred_full.pddl`: the description of the domain with all the extensions, under PDDL+ formalism, but avoiding to use fluents in the preconditions of actions. It was made for evaluating those predicates impact on ENHSP solution speed: results showed to achieve worst results in both planning time and quality of the plan with respect to the main version.
- `numeric_domain_APE_fluent_full.pddl`: the description of the domain with all the extensions, under PDDL+ formalism, but using fluents to describe the number of drinks on a tray in order to re-use the same actions for putting a drink on the tray or removing it. It was made for evaluating those predicates impact on ENHSP solution speed: results showed to achieve worst results in both planning time and quality of the plan with respect to the main version.

## PDDL2.1

All files written with the PDDL2.1 Numeric formalism used by either ENHSP or Metric-FF can be found under `dom_numeric`.
They were the first to be written and have not been updated after the shift of the project to PDDL+ formalism; nonetheless they're here provided as reference (and as a testament of what has been the development process).

The files presented are:

- `numeric_domain_cool_cons.pddl`: the description of the domain with only the "cooling" and "consumption" extensions, under PDDL2.1 (Numeric) formalism
- `numeric_domain_cooling.pddl`: the description of the domain with only the "cooling" extension, under PDDL2.1 (Numeric) formalism
- `numeric_domain_original.pddl`: the description of the domain without extensions, under PDDL2.1 (Numeric) formalism
- `numeric_problem#.pddl`: the description of the four problems with only the "cooling" and "consumption" extensions, under PDDL2.1 (Numeric) formalism

> NOTE: Although these files can be executed with ENHSP planner they yield far worse results for these four problems than what can be achiedeved using the more rich PDDL+ formalism.
# Metric-FF

1. h optimal around 3 -> still need to test time taken by h=4;
2. Number of states evaluated goes up by almost an order of magnitude with h size

# ENHSP

1. using fluents instead of has3, has2, has1 for tray usage makes the problem harder to solve, taking more time and resources (almost double) -> to avoid
2. using "hot" predicate instead of "fl-hot" fluent

**Testing with enhsp-20 on Ubuntu 18.04, planner "opt" (both cold drinks)**
|      /         | Predicate | Fluent    | Fluent (hrmax)    |
|    ---         | ---       | ----      |   ---             |
|Planning Time   |   7969    |   8184    |   8139            |
|Heuristic Time  |   4899    |   5193    |   5030            |
|Search Time     |   7668    |   7907    |   7860            |
|Expanded Nodes  |   171456  |   171456  |   171456          |
|States Evaluated|   254197  |   254197  |   254197          |

Fluents should thus be avoided when possible, even if that introduces more actions... but these results hold only for
the scenario of two drinks, both cold. When using one cold and one hot drink both domains perform better, with a slight
advantage of the one using fluents. At this scale it seems therefore the difference is negligible.
This result should be tested on larger problems

**Testing with enhsp-19 on Ubuntu 20.04, problem file: "numeric_problem.pddl" domain file: "numeric_domain.pddl", planner opt (heuristic specified in column) (both cold drinks)**
|     /          | opt-hrmax | opt-hmax  | opt-blind |
|   ---          | ---       |  ---      |   ---     |
|Planning Time   |   5506    |   5176    |   4547    |
|Heuristic Time  |   3566    |   3258    |   58      |
|Search Time     |   5220    |   4882    |   4296    |
|Expanded Nodes  |   171456  |   171456  |   466167  |
|States Evaluated|   254197  |   254197  |   633913  |


**Testing with enhsp-19 on Ubuntu 20.04, problem file: "numeric_problem_APE.pddl" domain file: "numeric_domain_APE.pddl", planner opt (heuristic specified in column), -delta 0.5 (both cold drinks)**
|      /         | opt-hrmax | opt-hmax  | opt-blind |
|  ---           | ---       |  ---      |   ---     |
|Planning Time   |   2368    |   2399    |   1118    |
|Heuristic Time  |   1306    |   1315    |   13      |
|Search Time     |   2022    |   2061    |   765     |
|Expanded Nodes  |   52386   |   52386   |   52210   |
|States Evaluated|   52739   |   52739   |   52607   |

**Stress test comparison, PDDL2.1 formulation vs. PDDL+, satisfiability of problem 4**
|        /       | APE (+)       |   Numeric |
|   ---          | ---           |  ---      |
|Planning Time   |   10668       |   1350170 |
|Heuristic Time  |   10009       |   1321470 |
|Search Time     |   10241       |   1349779 |
|Expanded Nodes  |     971       |   1366450 |
|States Evaluated|    4215       |   2327617 |
|Metric          |   67.0        |   41.5    |

It appears PDDL+ syntax can be resolved way faster (130x), although producing results with inferior quality, at least with the default settings.

**Effect of g_weight on PDDL+ (APE), satisfiability of problem 4**
|     -gw        |   1       |   2       |  5        | 10      | 12      |
|   ---          | ---       |    ---    |   ---     |  ---    |  ---    |
|Planning Time   |   10668   |   11729   |   48506   | 67359   | 84253   |
|Heuristic Time  |   10009   |   11046   |   47421   | 66101   | 82737   |
|Search Time     |   10241   |   11286   |   48062   | 66929   | 83810   |
|Expanded Nodes  |     971   |    1037   |    4372   | 8632    | 11896   |
|States Evaluated|    4215   |    4503   |   19548   | 28384   | 36013   |
|Metric          |    67.0   |    66.0   |    60.5   | 52.5    |  48.0   |

Therefore small values of gw (not far from 1) guarantee to find a solution in an amount of time compatible with the real world application of the system (roughly ten seconds between the order being made and it being started). It should be however taken into account that this can resort in a plan being highly unoptimized (almost 30 time units higher than the ideal one), with better sat solutions requiring way more initial computational overhead (at the moment, to gain 20 time units in the plan duration 70+ seconds more of pre-computation are needed).
Work should be done on the model in order to push the first solutions toward better quality ones (eg. making actions such as taking a tray more appealing).

## ENHSP FULL DOMAIN - all extensions implemented

**Effect of g_weight on PDDL+ (APE), satisfiability of problem 1 (with all extensions)**
delta = 1.0 (analogous results for the more appropriate delta_val 0.5, delta-max 0.5)
|     -gw        |   1       |   2       |  5        | 10      | 20      |
|   ---          | ---       |    ---    |   ---     |  ---    |  ---    |
|Planning Time   |    5758   |    5674   |    4721   |  4609   |  3688   |
|Heuristic Time  |    5109   |    5019   |    4042   |  3978   |  3103   |
|Search Time     |    5368   |    5284   |    4307   |  4200   |  3288   |
|Expanded Nodes  |    2684   |    1781   |    2657   |  1846   |  1335   |
|States Evaluated|    5966   |    4914   |    5292   |  4302   |  2900   |
|Metric          |    21.0   |    29.0   |    21.0   |  20.0   |  15.0   |


**Effect of g_weight on PDDL+ (APE), satisfiability of problem 2 (with all extensions)**
delta_val 0.5, delta-max 0.5
|     -gw        |   1       | 10      | 15      | 20      |
|   ---          | ---       |  ---    |  ---    |  ---    |
|Planning Time   |   88495   |  13948  |  14922  |  15203  |
|Heuristic Time  |   86594   |  13045  |  14021  |  14267  |
|Search Time     |   88036   |  13505  |  14482  |  14713  |
|Expanded Nodes  |    9760   |   3195  |   3987  |   4142  |
|States Evaluated|   43141   |   7711  |   8638  |   8619  |
|Metric          |    41.0   |  34.0   |   31.0  |   33.0  |

**Effect of g_weight on PDDL+ (APE), satisfiability of problem 3 (with all extensions)**
delta_val 0.5, delta-max 0.5
|     -gw        |   1    | 10   |   
|   ---          | ---    |  --- |   
|Planning Time   |   //   |  //  | 
|Heuristic Time  |   //   |  //  |
|Search Time     |   //   |  //  |
|Expanded Nodes  |   //   |  //  |
|States Evaluated|   //   |  //  |
|Metric          |   //   |  //  |

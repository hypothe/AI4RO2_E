# Metric-FF

1. h optimal around 3 -> still need to test time taken by h=4;
2. Number of states evaluated goes up by almost an order of magnitude with h size

# ENHSP

1. using fluents instead of has3, has2, has1 for tray usage makes the problem harder to solve, taking more time and resources (almost double) -> to avoid
2. using "hot" predicate instead of "fl-hot" fluent

* Testing with enhsp-20 on Ubuntu 18.04, planner "opt" (both cold drinks)*
 ---            | Predicate | Fluent    | Fluent (hrmax)    |
                | ---       | ----      |   ---             |
Planning Time   |   7969    |   8184    |   8139            |
Heuristic Time  |   4899    |   5193    |   5030            |
Search Time     |   7668    |   7907    |   7860            |
Expanded Nodes  |   171456  |   171456  |   171456          |
States Evaluated|   254197  |   254197  |   254197          |

Fluents should thus be avoided when possible, even if that introduces more actions... but these results hold only for
the scenario of two drinks, both cold. When using one cold and one hot drink both domains perform better, with a slight
advantage of the one using fluents. At this scale it seems therefore the difference is negligible.
This result should be tested on larger problems

* Testing with enhsp-19 on Ubuntu 20.04, problem file: "numeric_problem.pddl" domain file: "numeric_domain.pddl", planner opt (heuristic specified in column) (both cold drinks)*
 ---            | opt-hrmax | opt-hmax  | opt-blind |
                | ---       | ----      |   ---     |
Planning Time   |   5506    |   5176    |   4547    |
Heuristic Time  |   3566    |   3258    |   58      |
Search Time     |   5220    |   4882    |   4296    |
Expanded Nodes  |   171456  |   171456  |   466167  |
States Evaluated|   254197  |   254197  |   633913  |


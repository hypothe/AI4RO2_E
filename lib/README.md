#Brief files description

- `regr_model.pkl`: contains the dictionary of the Ridge linear regression models trained on the output features of the run, indexed by (hw, gw)x(goal). Written by `correlation.py` and read by `run.py`
- `hg_val_20_300.csv`: CSV file containing the results of the runs performed with gw up to 20 (7 values linearly spaced between 1.0 and 20.0) with a timeout of 300 seconds (_use this as the default one when calling_ `correlation.py`)
- `hg_val.csv`: CSV file containing the results of the runs performed with gw up to 15 (5 values geometrically spaced between 1.0 and 15.0) with a timeout of 120 seconds (_it's not recommended to use this when calling_ `correlation.py`, kept as an example)
- `drinks_explored_20_300.pkl` collection of all the configurations (number of waiters, drinks for table, hot drinks for table) already explored during the test performed with gw up to 20.0 and timeout 300 seconds (as already mentioned). Written and read by `test_data.py`
- `drinks_explored.pkl` collection of all the configurations (number of waiters, drinks for table, hot drinks for table) already explored during the test performed with gw up to 15.0 and timeout 120 seconds (as already mentioned). Written and read by `test_data.py`

import pytest
import os, glob
from simba.data_processors.agg_clf_calculator import AggregateClfCalculator
from simba.data_processors.fsttc_calculator import FSTTCCalculator

@pytest.mark.parametrize("config_path, data_measures, classifiers", [('/Users/simon/Desktop/envs/simba_dev/tests/data/test_projects/two_c57/project_folder/project_config.ini', ['Bout count'], ['Attack']),
                                                                     ('/Users/simon/Desktop/envs/simba_dev/tests/data/test_projects/two_c57/project_folder/project_config.ini', ['Total event duration (s)'], ['Attack'])])
def test_create_clf_log_use_case(config_path, data_measures, classifiers):

    clf_log_creator = AggregateClfCalculator(config_path=config_path,
                                             data_measures=data_measures, classifiers=classifiers)
    clf_log_creator.run()
    clf_log_creator.save()
    assert len(clf_log_creator.results_df) == len(data_measures)
    for f in glob.glob(clf_log_creator.targets_folder + '/*.csv'): os.remove(f)

@pytest.mark.parametrize("config_path, time_window, behavior_lst, create_graph", [('/Users/simon/Desktop/envs/simba_dev/tests/data/test_projects/two_c57/project_folder/project_config.ini', 2000, ['Attack', 'Sniffing'], False)])
def test_fsttc_calculator_use_case(config_path, time_window, behavior_lst, create_graph):
    fsttc_calculator = FSTTCCalculator(config_path=config_path, time_window=time_window, behavior_lst=behavior_lst, create_graphs=create_graph)
    fsttc_calculator.run()
    assert len(fsttc_calculator.out_df) == len(behavior_lst)
    if create_graph:
        assert os.path.isfile(fsttc_calculator.save_plot_path)
    os.remove(fsttc_calculator.file_save_path)
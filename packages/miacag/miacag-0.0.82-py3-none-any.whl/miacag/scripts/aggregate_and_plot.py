import uuid
import os
import socket
from datetime import datetime, timedelta
import yaml
from miacag.preprocessing.split_train_val import splitter
from miacag.utils.sql_utils import copy_table, add_columns, \
    copyCol, changeDtypes

import pandas as pd
from miacag.postprocessing.append_results import appendDataFrame
import torch
from miacag.trainer import train
from miacag.tester import test
from miacag.configs.config import load_config, maybe_create_tensorboard_logdir
from miacag.configs.options import TrainOptions
import argparse
from miacag.preprocessing.labels_map import labelsMap
from miacag.preprocessing.utils.check_experiments import checkExpExists, \
    checkCsvExists
from miacag.plots.plotter import plot_results
import pandas as pd
from miacag.preprocessing.transform_thresholds import transformThreshold
from miacag.preprocessing.transform_missing_floats import transformMissingFloats
from miacag.utils.script_utils import create_empty_csv, mkFolder, maybe_remove, test_for_file, write_file
from miacag.postprocessing.aggregate_pr_group import Aggregator
from miacag.postprocessing.count_stenosis_pr_group \
    import CountSignificantStenoses

def aggregate_plt(config_path, table_name_input=None):

    config_path = [
        os.path.join(config_path, i) for i in os.listdir(config_path)]

    for i in range(0, len(config_path)):
        print('loading config:', config_path[i])
        with open(config_path[i]) as file:
            config = yaml.load(file, Loader=yaml.FullLoader)
      #  mkFolder(config['output'])
       # csv_exists, output_csv_test = checkCsvExists(config['output'])
        
       # exp_exists = checkExpExists(config_path[i], config['output'])
      #  if exp_exists is False:

       # config['master_port'] = os.environ['MASTER_PORT']
        #  config['num_workers'] = num_workers
        # tensorboard_comment = os.path.basename(config_path[i])[:-5]
        temp_file = os.path.join(config['output'], 'temp.txt')
        experiment_name = "classification_config_angio_SEP_Jan10_16-49-37"
        # experiment_name = test_for_file(temp_file)[0]
        output_directory = os.path.join(
                    config['output'],
                    experiment_name)
        output_config = os.path.join(output_directory,
                                        os.path.basename(config_path[i]))

        output_table_name = table_name_input

        output_plots = os.path.join(output_directory, 'plots')

        output_plots_train = os.path.join(output_plots, 'train')
        output_plots_val = os.path.join(output_plots, 'val')
        output_plots_test = os.path.join(output_plots, 'test')


        # rename labels and add columns;
        trans_label = [i + '_transformed' for i in config['labels_names']]
        labels_names_original = config['labels_names']
        config['labels_names'] = trans_label
        # add placeholder for confidences
        conf = [i + '_confidences' for i in config['labels_names']]
        conf_agg = [i + '_confidences_aggregated' for i in config['labels_names']]
        # add placeholder for predictions
        pred = [i + '_predictions' for i in config['labels_names']]


        # 4. Train model
      #  torch.distributed.barrier()
        config['output'] = output_directory
        config['output_directory'] = output_directory
        config['table_name'] = output_table_name
        config['use_DDP'] = 'True'
        config['datasetFingerprintFile'] = None
        #  train(config)

        # 5 eval model

        config['model']['pretrain_model'] = output_directory
        # test({**config, 'query': config["query_test"], 'TestSize': 1})



        # torch.distributed.barrier()
        # torch.distributed.destroy_process_group()
        # torch.cuda.empty_cache()

        # plotting results
        #torch.distributed.barrier()
        #if torch.distributed.get_rank() == 0:
        # 6 plot results:
        # train
        plot_results({
                    'database': config['database'],
                    'username': config['username'],
                    'password': config['password'],
                    'host': config['host'],
                    'labels_names': config['labels_names'],
                    'table_name': output_table_name,
                    'schema_name': config['schema_name'],
                    'query': config['query_train_plot']},
                    config['labels_names'],
                    [i + "_predictions" for i in
                        config['labels_names']],
                    output_plots_train,
                    config['model']['num_classes'],
                    config,
                    [i + "_confidences" for i in
                        config['labels_names']]
                    )

        # aggregate stenosis for all groups :
        # entryids or (PatientID, StudyInstanceUID)
        agg = Aggregator({
                            'labels_names': config['labels_names'],
                            'database': config['database'],
                            'username': config['username'],
                            'password': config['password'],
                            'host': config['host'],
                            'schema_name': config['schema_name'],
                            'table_name': output_table_name,
                            'query':
                            config['query_train_plot'],
                            "num_classes":
                            config["model"]["num_classes"],
                            "loss_name": config['loss']['name']
                            },
                            [i + "_confidences" for i in
                            config['labels_names']])
        agg()
        # plot results for entire cag
        cag_segment = os.path.join(output_plots_train, 'cag_segment')
        mkFolder(cag_segment)

        plot_results({
                    'database': config['database'],
                    'username': config['username'],
                    'password': config['password'],
                    'host': config['host'],
                    'schema_name': config['schema_name'],
                    'labels_names': config['labels_names'],
                    'table_name': output_table_name,
                    'query': config['query_count_stenosis_train']},
                    config['labels_names'],
                    [i + "_predictions" for i in
                        config['labels_names']],
                    cag_segment,
                    config['model']['num_classes'],
                    config,
                    [i + "_confidences" for i in
                        config['labels_names']],
                    group_aggregated=True
                    )

        # val
        plot_results({
                    'database': config['database'],
                    'username': config['username'],
                    'password': config['password'],
                    'host': config['host'],
                    'schema_name': config['schema_name'],
                    'labels_names': config['labels_names'],
                    'table_name': output_table_name,
                    'query': config['query_val_plot']},
                    config['labels_names'],
                    [i + "_predictions" for i in
                        config['labels_names']],
                    output_plots_val,
                    config['model']['num_classes'],
                    config,
                    [i + "_confidences" for i in
                        config['labels_names']]
                    )

        # aggregate stenosis for all groups :
        # entryids or (PatientID, StudyInstanceUID)
        agg = Aggregator({
                            'labels_names': config['labels_names'],
                            'database': config['database'],
                            'username': config['username'],
                            'password': config['password'],
                            'host': config['host'],
                            'schema_name': config['schema_name'],
                            'table_name': output_table_name,
                            'query':
                            config['query_val_plot'],
                            "num_classes":
                            config["model"]["num_classes"],
                            "loss_name": config['loss']['name']},
                            [i + "_confidences" for i in
                            config['labels_names']])
        agg()
        # plot results for entire cag
        cag_segment = os.path.join(output_plots_val, 'cag_segment')
        mkFolder(cag_segment)

        plot_results({
                    'database': config['database'],
                    'username': config['username'],
                    'password': config['password'],
                    'host': config['host'],
                    'labels_names': config['labels_names'],
                    'table_name': output_table_name,
                    'schema_name': config['schema_name'],
                    'query': config['query_count_stenosis_val']},
                    config['labels_names'],
                    [i + "_predictions" for i in
                        config['labels_names']],
                    cag_segment,
                    config['model']['num_classes'],
                    config,
                    confidence_names=[i + "_confidences" for i in
                                        config['labels_names']],
                    group_aggregated=True
                    )

        # test
        plot_results({
                    'database': config['database'],
                    'username': config['username'],
                    'password': config['password'],
                    'host': config['host'],
                    'labels_names': config['labels_names'],
                    'schema_name': config['schema_name'],
                    'table_name': output_table_name,
                    'query': config['query_test_plot']},
                    config['labels_names'],
                    [i + "_predictions" for i in
                        config['labels_names']],
                    output_plots_test,
                    config['model']['num_classes'],
                    config,
                    [i + "_confidences" for i in
                        config['labels_names']]
                    )
        
        # aggregate stenosis for all groups :
        # entryids or (PatientID, StudyInstanceUID)
        
        agg = Aggregator({
                            'labels_names': config['labels_names'],
                            'database': config['database'],
                            'username': config['username'],
                            'password': config['password'],
                            'host': config['host'],
                            'schema_name': config['schema_name'],
                            'table_name': output_table_name,
                            'query':
                            config['query_test_plot'],
                            "num_classes":
                            config["model"]["num_classes"],
                            "loss_name": config['loss']['name']},
                            [i + "_confidences" for i in
                            config['labels_names']])
        agg()
        # plot results for entire cag
        cag_segment = os.path.join(output_plots_test, 'cag_segment')
        mkFolder(cag_segment)

        plot_results({
                    'database': config['database'],
                    'username': config['username'],
                    'password': config['password'],
                    'host': config['host'],
                    'labels_names': config['labels_names'],
                    'schema_name': config['schema_name'],
                    'table_name': output_table_name,
                    'query': config['query_count_stenosis_test']},
                    config['labels_names'],
                    [i + "_predictions" for i in
                        config['labels_names']],
                    cag_segment,
                    config['model']['num_classes'],
                    config,
                    confidence_names=[i + "_confidences" for i in
                                        config['labels_names']],
                    group_aggregated=True
                    )


        # # append results 
        # csv_results = appendDataFrame(sql_config={
        #                     'labels_names': config['labels_names'],
        #                     'database': config['database'],
        #                     'username': config['username'],
        #                     'password': config['password'],
        #                     'host': config['host'],
        #                     'schema_name': config['schema_name'],
        #                     'table_name': output_table_name,
        #                     'query': config['query_test_plot']},
        #                 df_results=df_results,
        #                 experiment_name=experiment_name)
        print('config files processed', str(i+1))
        print('config files to process in toal:', len(config_path))


if __name__ == '__main__':
    #args = parser.parse_args()
    config_path = "/home/alatar/miacag/my_configs/stenosis"
    table_name_input = "classification_config_angio_SEP_Jan10_16-49-37_dicom_table2x"
    aggregate_plt(config_path, table_name_input)
    #stenosis_identifier(args.cpu, args.num_workers, args.config_path)

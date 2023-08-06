import uuid
import os
import socket
from datetime import datetime, timedelta
import yaml
from miacag.preprocessing.split_train_val import splitter
from miacag.utils.sql_utils import copy_table, add_columns, \
    copyCol, changeDtypes
import copy
import numpy as np
import pandas as pd
from miacag.postprocessing.append_results import appendDataFrame
import torch
from miacag.trainer import train
from miacag.tester import test
from miacag.configs.config import load_config, maybe_create_tensorboard_logdir
from miacag.configs.options import TrainOptions
import argparse
from miacag.preprocessing.labels_map import labelsMap
from sklearn.preprocessing import LabelBinarizer
from sklearn.metrics import roc_auc_score
from miacag.preprocessing.utils.check_experiments import checkExpExists, \
    checkCsvExists
from miacag.plots.plotter import plot_results, plotRegression
import pandas as pd
from miacag.preprocessing.transform_thresholds import transformThresholdRegression
from miacag.preprocessing.transform_missing_floats import transformMissingFloats
from miacag.utils.script_utils import create_empty_csv, mkFolder, maybe_remove, write_file, test_for_file
from miacag.postprocessing.aggregate_pr_group import Aggregator
from miacag.postprocessing.count_stenosis_pr_group \
    import CountSignificantStenoses
from miacag.models.dino_utils import dino_pretrained
from miacag.models.dino_utils.dino_pretrained import FeatureForwarder
from miacag.utils.sql_utils import getDataFromDatabase
from miacag.plots.plot_predict_coronary_pathology import run_plotter_ruc_multi_class
parser = argparse.ArgumentParser(
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument(
    '--cpu', type=str,
    help="if cpu 'True' else 'False'")
parser.add_argument(
    "--local_rank", type=int,
    help="Local rank: torch.distributed.launch.")
parser.add_argument(
            "--local-rank", type=int,
            help="Local rank: torch.distributed.launch.")
parser.add_argument(
    "--num_workers", type=int,
    help="Number of cpu workers for training")
parser.add_argument(
    '--config_path', type=str,
    help="path to folder with config files")


def stenosis_identifier(cpu, num_workers, config_path, table_name_input=None):
    if table_name_input is None:
        torch.distributed.init_process_group(
                backend="nccl" if cpu == "False" else "Gloo",
                init_method="env://",
                timeout=timedelta(seconds=1800000)
                )
    config_path = [
        os.path.join(config_path, i) for i in os.listdir(config_path)]

    for i in range(0, len(config_path)):
        print('loading config:', config_path[i])
        with open(config_path[i]) as file:
            config = yaml.load(file, Loader=yaml.FullLoader)
        mkFolder(config['output'])
        config['master_port'] = os.environ['MASTER_PORT']
        config['num_workers'] = num_workers
        config['cpu'] = cpu
        tensorboard_comment = os.path.basename(config_path[i])[:-5]
        temp_file = os.path.join(config['output'], 'temp.txt')
        torch.distributed.barrier()
        if torch.distributed.get_rank() == 0:
            maybe_remove(temp_file)
            experiment_name = tensorboard_comment + '_' + \
                "SEP_" + \
                datetime.now().strftime('%b%d_%H-%M-%S')
            write_file(temp_file, experiment_name)
        torch.distributed.barrier()
        experiment_name = test_for_file(temp_file)[0]
        output_directory = os.path.join(
                    config['output'],
                    experiment_name)
        mkFolder(output_directory)
        output_config = os.path.join(output_directory,
                                        os.path.basename(config_path[i]))
        if table_name_input is None:
            output_table_name = \
                experiment_name + "_" + config['table_name']
        else:
            output_table_name = table_name_input

        output_plots = os.path.join(output_directory, 'plots')
        mkFolder(output_plots)

        output_plots_train = os.path.join(output_plots, 'train')
        output_plots_val = os.path.join(output_plots, 'val')
        output_plots_test = os.path.join(output_plots, 'test')

        mkFolder(output_plots_train)
        mkFolder(output_plots_test)
        mkFolder(output_plots_val)

        # begin pipeline
        # 1. copy table
        os.system("mkdir -p {output_dir}".format(
            output_dir=output_directory))
        torch.distributed.barrier()
        if torch.distributed.get_rank() == 0:
            if table_name_input is None:
                copy_table(sql_config={
                    'database': config['database'],
                    'username': config['username'],
                    'password': config['password'],
                    'host': config['host'],
                    'schema_name': config['schema_name'],
                    'table_name_input': config['table_name'],
                    'table_name_output': output_table_name})

            # # 2. copy config
            os.system(
                "cp {config_path} {config_file_temp}".format(
                    config_path=config_path[i],
                    config_file_temp=output_config))


        torch.distributed.barrier()
        if torch.distributed.get_rank() == 0:
            # TODO dont split on labels names
            splitter_obj = splitter(
                {
                    'labels_names': config['labels_names'],
                    'database': config['database'],
                    'username': config['username'],
                    'password': config['password'],
                    'host': config['host'],
                    'schema_name': config['schema_name'],
                    'table_name': output_table_name,
                    'query': config['query_split'],
                    'TestSize': config['TestSize']})
            splitter_obj()
            # ...and map data['labels'] test
        # 4.1 Pretrain encoder model
        ## TODO add pretrain model
        if not config['model']['freeze_backbone']:
            print('ssl pretraining')
            # train here...
            config['freeze_backbone'] = True
            
        # loop through all indicator tasks
        unique_index = list(dict.fromkeys(config['task_indicator']))
        for task_index in unique_index:
            config_new = copy.deepcopy(config)
            run_task(config_new, task_index, output_directory, output_table_name,
                    output_plots_train, output_plots_val, output_plots_test,
                    cpu)
            

    print('config files processed', str(i+1))
    print('config files to process in toal:', len(config_path))
    return None

def run_task(config, task_index, output_directory, output_table_name,
             output_plots_train, output_plots_val, output_plots_test, cpu):
    task_names = [
        name for i, name in zip(config['task_indicator'],
                                config['labels_names']) if i == task_index]
    loss_names = [
        name for i, name in zip(config['task_indicator'],
                                config['loss']['name']) if i == task_index]
    eval_names_train = [
        name for i, name in zip(
            config['task_indicator'],
            config['eval_metric_train']['name']) if i == task_index]
    eval_names_val = [
        name for i, name in zip(
            config['task_indicator'],
            config['eval_metric_val']['name']) if i == task_index]
    eval_names_val = [
        name for i, name in zip(
            config['task_indicator'],
            config['eval_metric_val']['name']) if i == task_index]
    # declare updated config
    config_task = config.copy()
    config_task['labels_names'] = task_names
    config_task['loss']['name'] = loss_names
    config_task['eval_metric_train']['name'] = eval_names_train
    config_task['eval_metric_val']['name'] = eval_names_val
    
    torch.distributed.barrier()
    config_task['output'] = output_directory
    config_task['output_directory'] = output_directory
    config_task['table_name'] = output_table_name
    config_task['use_DDP'] = 'True'
    config_task['datasetFingerprintFile'] = None
        # rename labels and add columns;
    trans_label = [i + '_transformed' for i in config_task['labels_names']]
    labels_names_original = config_task['labels_names']
    config_task['labels_names'] = trans_label
    # add placeholder for confidences
    conf = [i + '_confidences' for i in config_task['labels_names']]
    # add placeholder for predictions
    pred = [i + '_predictions' for i in config_task['labels_names']]
    #

    
    # test if loss is regression type
    if loss_names[0] in ['L1smooth', 'MSE']:
        change_dtype_add_cols(config_task, output_table_name, trans_label, labels_names_original, conf, pred, "float8")
        transform_regression_data(config_task, output_table_name, trans_label)
    elif loss_names[0] in ['CE']:
        change_dtype_add_cols_ints(config_task, output_table_name, trans_label, labels_names_original, conf, pred, "int8")
        config_task['weighted_sampler'] == "True"
    train(config_task)
    # 5 eval model
    test(config_task)

    print('kill gpu processes')
    torch.distributed.barrier()
    # clear gpu memory
    torch.cuda.empty_cache()

    # plot results
    if loss_names[0] in ['L1smooth', 'MSE']:
        plot_regression_tasks(config_task, output_plots_train, output_plots_val, output_plots_test)
    elif loss_names[0] in ['CE']:
        plot_classification_tasks(config_task, output_table_name,
                                  output_plots_train, output_plots_val, output_plots_test)
        


def change_dtype_add_cols_ints(config, output_table_name, trans_label, labels_names_original, conf, pred, type):
    add_columns({
        'database': config['database'],
        'username': config['username'],
        'password': config['password'],
        'host': config['host'],
        'schema_name': config['schema_name'],
        'table_name': output_table_name,
        'table_name_output': output_table_name},
                trans_label,
                ['VARCHAR'] * len(trans_label))
    # copy content of labels
    copyCol(
        {'database': config["database"],
            'username': config["username"],
            'password': config['password'],
            'host': config['host'],
            'schema_name': config['schema_name'],
            'table_name': output_table_name,
            'query': config['query_transform']},
        labels_names_original,
        trans_label)
    mapper_obj = labelsMap(
                {
                    'labels_names': labels_names_original,
                    'database': config['database'],
                    'username': config['username'],
                    'password': config['password'],
                    'host': config['host'],
                    'schema_name': config['schema_name'],
                    'table_name': output_table_name,
                    'query': config['query_test'],
                    'TestSize': 1},
                config['labels_dict'])
    mapper_obj()
    changeDtypes(
        {'database': config["database"],
            'username': config["username"],
            'password': config['password'],
            'host': config['host'],
            'schema_name': config['schema_name'],
            'table_name': output_table_name,
            'query': config['query_transform']},
        trans_label,
        ["int8"] * len(trans_label))

    add_columns({
        'database': config['database'],
        'username': config['username'],
        'password': config['password'],
        'host': config['host'],
        'schema_name': config['schema_name'],
        'table_name': output_table_name,
        'table_name_output': output_table_name},
                conf,
                ["VARCHAR"] * len(conf))
    add_columns({
        'database': config['database'],
        'username': config['username'],
        'password': config['password'],
        'host': config['host'],
        'schema_name': config['schema_name'],
        'table_name': output_table_name,
        'table_name_output': output_table_name},
                pred,
                [type] * len(pred))


def transform_regression_data(config, output_table_name, trans_label):
    trans = transformMissingFloats({
        'labels_names': config['labels_names'],
        'database': config['database'],
        'username': config['username'],
        'password': config['password'],
        'host': config['host'],
        'schema_name': config['schema_name'],
        'table_name': output_table_name,
        'query': config['query_transform'],
        'TestSize': config['TestSize']})
    trans()

    trans_thres = transformThresholdRegression({
        'labels_names': config['labels_names'],
        'database': config['database'],
        'username': config['username'],
        'password': config['password'],
        'host': config['host'],
        'schema_name': config['schema_name'],
        'table_name': output_table_name,
        'query': config['query_transform'],
        'TestSize': config['TestSize']},
        config)
    trans_thres()

    # change dtypes for label


def plot_regression_tasks(config_task, output_table_name, output_plots_train,
                          output_plots_val, output_plots_test, conf):
    # 6 plot results:
    # train
    plot_results({
                'database': config_task['database'],
                'username': config_task['username'],
                'password': config_task['password'],
                'host': config_task['host'],
                'labels_names': config_task['labels_names'],
                'schema_name': config_task['schema_name'],
                'table_name': output_table_name,
                'query': config_task['query_train_plot']},
                config_task['labels_names'],
                [i + "_predictions" for i in
                    config_task['labels_names']],
                output_plots_train,
                config_task['model']['num_classes'],
                config_task,
                [i + "_confidences" for i in
                    config_task['labels_names']]
                )

    plotRegression({
                'database': config_task['database'],
                'username': config_task['username'],
                'password': config_task['password'],
                'host': config_task['host'],
                'labels_names': config_task['labels_names'],
                'schema_name': config_task['schema_name'],
                'table_name': output_table_name,
                'query': config_task['query_train_plot'],
                'loss_name': config_task['loss']['name'],
                'task_type': config_task['task_type']
                },
                config_task['labels_names'],
                conf,
                output_plots_train,
                group_aggregated=False)
        
    # # val
    # plot_results({
    #             'database': config_task['database'],
    #             'username': config_task['username'],
    #             'password': config_task['password'],
    #             'host': config_task['host'],
    #             'labels_names': config_task['labels_names'],
    #             'schema_name': config_task['schema_name'],
    #             'table_name': output_table_name,
    #             'query': config_task['query_val_plot']},
    #             config_task['labels_names'],
    #             [i + "_predictions" for i in
    #                 config_task['labels_names']],
    #             output_plots_val,
    #             config_task['model']['num_classes'],
    #             config_task,
    #             [i + "_confidences" for i in
    #                 config_task['labels_names']]
    #             )

    # plotRegression({
    #             'database': config_task['database'],
    #             'username': config_task['username'],
    #             'password': config_task['password'],
    #             'host': config_task['host'],
    #             'labels_names': config_task['labels_names'],
    #             'schema_name': config_task['schema_name'],
    #             'table_name': output_table_name,
    #             'query': config_task['query_val_plot'],
    #             'loss_name': config_task['loss']['name'],
    #             'task_type': config_task['task_type']
    #             },
    #             config_task['labels_names'],
    #             conf,
    #             output_plots_val,
    #             group_aggregated=False)

    # # test
    # plot_results({
    #             'database': config_task['database'],
    #             'username': config_task['username'],
    #             'password': config_task['password'],
    #             'host': config_task['host'],
    #             'labels_names': config_task['labels_names'],
    #             'schema_name': config_task['schema_name'],
    #             'table_name': output_table_name,
    #             'query': config_task['query_test_plot']},
    #             config_task['labels_names'],
    #             [i + "_predictions" for i in
    #                 config_task['labels_names']],
    #             output_plots_test,
    #             config_task['model']['num_classes'],
    #             config_task,
    #             [i + "_confidences" for i in
    #                 config_task['labels_names']]
    #             )

    # plotRegression({
    #             'database': config_task['database'],
    #             'username': config_task['username'],
    #             'password': config_task['password'],
    #             'host': config_task['host'],
    #             'labels_names': config_task['labels_names'],
    #             'schema_name': config_task['schema_name'],
    #             'table_name': output_table_name,
    #             'query': config_task['query_test_plot'],
    #             'loss_name': config_task['loss']['name'],
    #             'task_type': config_task['task_type']
    #             },
    #             config_task['labels_names'],
    #             conf,
    #             output_plots_test,
    #             group_aggregated=False)


def plot_classification_tasks(config,
                             output_table_name,
                             output_plots_train, output_plots_val, output_plots_test):
    df, conn = getDataFromDatabase({
                            'database': config['database'],
                            'username': config['username'],
                            'password': config['password'],
                            'host': config['host'],
                            'labels_names': config['labels_names'],
                            'schema_name': config['schema_name'],
                            'table_name': output_table_name,
                            'query': config['query_train_plot']})
    # test if _confidences exists
    if config['labels_names'][0] +"_confidences" in df.columns:
        labels_names = config['labels_names'][0] +"_confidences"
    elif config['labels_names'][0] +"_confid" in df.columns:
        labels_names = config['labels_names'][0] +"_confid"
    else:
        raise ValueError("No confidence column found in database")
        
    df = df.dropna(subset=[labels_names], how="any")
    y_scores = convert_string_to_numpy(df, column='koronarpatologi_nativekar_udfyldesforallept__transformed_confid')
    label_binarizer = LabelBinarizer().fit(df[config['labels_names']])
    y_onehot_test = label_binarizer.transform(df[config['labels_names']])
    random_array = np.random.rand(4, 3)
    y_scores = random_array / random_array.sum(axis=1, keepdims=True)
    y_onehot_test = np.transpose(np.array([[1, 0, 2, 0]]))
    label_binarizer = LabelBinarizer().fit(y_onehot_test)
    y_onehot_test = label_binarizer.transform(y_onehot_test)
    run_plotter_ruc_multi_class(y_scores, y_onehot_test,
                                "corornay_pathology", "model",
                                "roc_curve_coronar",
                                output_plots_train)
    #(y_score, y_onehot_test,
                             #   type_outcome, model_name,
                             #   ax, save_name, output_path):
    print('hej')
    return None


def convert_string_to_numpy(df, column='koronarpatologi_nativekar_udfyldesforallept__transformed_confid'):
    list_values = []

    for row in df[column]:
        # Transforming the string to a dictionary
        row_dict = {int(k):float(v) for k,v in  (item.split(':') for item in row.strip('{}').split(';'))}
        # Adding the values to a list
        list_values.append(list(row_dict.values()))

    # Transforming the list of lists to a numpy array
    np_array = np.array(list_values)
    
    return np_array
if __name__ == '__main__':
    args = parser.parse_args()
    stenosis_identifier(args.cpu, args.num_workers, args.config_path)

import matplotlib.pyplot as plt
import matplotlib
from miacag.utils.sql_utils import getDataFromDatabase
import pandas as pd
import seaborn as sns
from miacag.plots.plotter import rename_columns, mkFolder
from sklearn.metrics import f1_score, \
     accuracy_score, confusion_matrix, plot_confusion_matrix
import statsmodels.api as sm
from sklearn.linear_model import LogisticRegression, LogisticRegressionCV
import os
import numpy as np
matplotlib.use('Agg')

def plot_waterfall(df, title, xlabel, ylabel, save_path, f1):
    # clip all values to 0-1
    df[ylabel] = df[ylabel].clip(0, 1)
    df, ylabel_ren = rename_columns(df, ylabel)
  #  g = sns.catplot(data=df, x=xlabel, y=ylabel_ren, hue=xlabel, kind="swarm")
   # g = sns.catplot(data=df, x=ylabel_ren, y=xlabel, kind="violin", inner=None, orient="h")
    # sns.swarmplot(
    #     data=df, x=ylabel_ren, y=xlabel,
    #     hue=xlabel, size=3, ax=g.ax, orient="h", color="black")
  # plt.axhline(y=0.7, color='r', linestyle='--', linewidth=1.0, label='Significant stenosis threshold (0.70)')
    sns.set_context("talk", font_scale=1.1)
    plt.figure(figsize=(8,6))
    sns.violinplot(y=ylabel_ren, 
                    x=xlabel, 
                    data=df,
                    orient="h")
    sns.stripplot(y=ylabel_ren, 
                    x=xlabel, 
                    data=df,
                    orient="h",
                color="black", edgecolor="gray") 
    plt.xlabel("Predicted stenosis on: " + ylabel_ren)

   # plt.legend(loc='upper left')
    plt.show()
    
    plt.savefig(save_path + "sten_vs_interv.png")
    plt.savefig(save_path + "sten_vs_interv.pdf")
    plt.close()
    sns.set_context("talk", font_scale=1.1)
    plt.figure(figsize=(8,6))
    sns.violinplot(y=ylabel_ren, 
                    x=xlabel, 
                    data=df,
                    orient="h")
    sns.stripplot(y=ylabel_ren, 
                    x=xlabel, 
                    data=df,
                    orient="h",
                color="black", edgecolor="gray") 
    
    plt.xlabel("Predicted stenosis on: " + ylabel_ren)
    plt.title("F1")
  #  plt.legend(loc='upper left')
    plt.savefig(save_path + "sten_vs_interv_f1.png")
    plt.show()
    plt.close()
    


def clip_predictions(df, prediction_names):
    for prediction_name in prediction_names:
        df[prediction_name] = df[prediction_name].clip(0, 1)
   # df[label_name] = df[label_name].clip(0, 1)
    return df



def getNormConfMat(df, labels_col, preds_col,
                   f1, output, num_classes, support, c, x_axis):
    num_classes_for_plot = num_classes[c]
    if num_classes_for_plot == 1:
        num_classes_for_plot = 2
    labels = [i for i in range(0, num_classes_for_plot)]
    df[labels_col] = df[labels_col].astype(int)
    df[preds_col] = df[preds_col].astype(int)
    conf_arr = confusion_matrix(df[labels_col], df[preds_col], labels=labels)
    sum = conf_arr.sum()
    # Normalized confusion matrix???
    #conf_arr = conf_arr * 100.0 / (1.0 * sum)
    df_cm = pd.DataFrame(
        conf_arr,
        index=[
            str(i) for i in range(0, num_classes_for_plot)],
        columns=[
            str(i) for i in range(0, num_classes_for_plot)])
    fig = plt.figure()
    plt.clf()
    ax = fig.add_subplot(111)
    ax.set_aspect(1)
    cmap = sns.cubehelix_palette(light=1, as_cmap=True)
    res = sns.heatmap(df_cm, annot=True, vmin=0.0, fmt='g',
                      square=True, linewidths=0.1, annot_kws={"size": 8},
                      cmap=cmap)
    res.invert_yaxis()
    f1 = np.round(f1, 3)
    plt.title(
        x_axis + ' vs confusion matrix')
    plt.xlabel(x_axis)
    plt.ylabel("Actual")

    plt.savefig(os.path.join(output, '_cmat.png'), dpi=100,
                bbox_inches='tight')
    plt.close()

    fig = plt.figure()
    plt.clf()
    ax = fig.add_subplot(111)
    ax.set_aspect(1)
    cmap = sns.cubehelix_palette(light=1, as_cmap=True)
    res = sns.heatmap(df_cm, annot=True, vmin=0.0, fmt='g',
                      square=True, linewidths=0.1, annot_kws={"size": 8},
                      cmap=cmap)
    res.invert_yaxis()
    f1 = np.round(f1, 3)

    plt.title(
        x_axis + ' confusion Matrix, F1-macro:' + str(f1) +
        ',support(N)=' + str(support))
    plt.xlabel(x_axis)
    plt.ylabel("Actual")

    plt.savefig(os.path.join(output, '_cmat_support.png'), dpi=100,
                bbox_inches='tight')
    plt.close()
    

def compute_logistic_regression(df, label_name, prediction_names, dominans, output_path, x_axis):
    df = clip_predictions(df, prediction_names)
    x = df[prediction_names + [dominans]]
    y = df[label_name]
    
    model_sk =  LogisticRegressionCV().fit(x,y)
    preds = model_sk.predict(x)
    f1 = f1_score(y, preds, average='macro')
    df_results = pd.DataFrame()
    df_results["preds"] = preds.tolist()
    df_results["y"] = y.tolist()
    getNormConfMat(df_results, "y", "preds",
                   f1, output_path,
                   [3], len(df_results), c=0, x_axis=x_axis)
    print(y)
    print('df')
if __name__ == '__main__':
    sql_config = {
                    'database': 'mydb',
                    'username': 'alatar',
                    'password': '123qweasd',
                    'host': 'localhost',
                    'schema_name': "cag",
                    'table_name': "classification_config_angio_SEP_Feb27_13-12-52_dicom_table2x",
                    'query': "SELECT * FROM ?schema_name.?table_name"}
    df, conn = getDataFromDatabase(sql_config=sql_config)
    output = "/home/alatar/Music/Pictures/violin/"
    predictor_name = ["sten_proc_1_prox_rca_transformed"]
    dominans = "labels"
    target = "dominans"
    mkFolder(output)
    # df["indication_for_ffr"] = (~df["ffr_proc_1_prox_rca_transformed"].isna()).astype(int)
    
    replace_dict = {
        "Balanceret (PDA fra RCA/PLA fra LCX)": 0,
        "Venstre dominans (PDA+PLA fra LCX)": 2,
        "Højre dominans (PDA+PLA fra RCA)": 1,
        "None": 0,
        "Nan": 0,
        "NULL": 0,
        "nan": 0,
        "Null": 0,
        "NaN": 0,
        "NAN": 0,
        "NONE": 0,
        "np.nan": 0}
   # df[tar] = (~df["ffr_proc_1_prox_rca_transformed"].isna()).astype(int)
    df = df[~df[target].isna()]
    df[target] = df[target].replace(replace_dict)

    compute_logistic_regression(df, target, predictor_name, dominans, output, x_axis="Stenosis eyeball")
    
    # merge dataframes based on "entryid"
    
    df_merged = df.merge(df2, on="entryid")

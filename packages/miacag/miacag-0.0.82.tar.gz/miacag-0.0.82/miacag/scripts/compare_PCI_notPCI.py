import matplotlib.pyplot as plt
import matplotlib
from miacag.utils.sql_utils import getDataFromDatabase
import pandas as pd
import seaborn as sns
from miacag.plots.plotter import rename_columns, mkFolder
from sklearn.metrics import f1_score
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
    label_name = "sten_proc_1_prox_rca_transformed"
    ffr_name = "ffr" + label_name[4:]
    intervention = "dominans"
    mkFolder(output)
    df["indication_for_ffr"] = (~df["ffr_proc_1_prox_rca_transformed"].isna()).astype(int)
    
    replace_dict = {
        "Balanceret (PDA fra RCA/PLA fra LCX)": 0,
        "Venstre dominans (PDA+PLA fra LCX)": 0,
        "Højre dominans (PDA+PLA fra RCA)": 1}
    df[intervention] = df[intervention].replace(replace_dict)
    df = df[~df[intervention].isna()]
    df[intervention] = (df[intervention] + df["indication_for_ffr"]>=1).astype("int")
    

    df[label_name + "_threshold"] = (df[label_name]>=0.7).astype('int')
    
    f1 = f1_score(df[label_name + "_threshold"],
                      df[intervention], average='macro')
    
    plot_waterfall(
        df, "Predicted stenosis (%) vs PCI actual performed", intervention,
        label_name, output, f1)
        
    # output = "violin.pdf"
    # plot_waterfall(
    #     df, "Predicted stenosis (%) vs PCI actual performed", "labels",
    #     "sten_proc_1_prox_rca_transformed", output)

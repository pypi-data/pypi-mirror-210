
def do_plot():
    phase = 'test'
    query = """
    SELECT DISTINCT ON (t.\"PatientID\", t.\"StudyInstanceUID\") t.\"PatientID\", t.\"StudyInstanceUID\",
    t2.phase, t.\"sten_proc_1_prox_rca_transformed_confidences\", t.\"sten_proc_2_midt_rca_transformed_confidences\"
    , t.\"sten_proc_3_dist_rca_transformed_confidences\", t.\"sten_proc_4_pda_transformed_confidences\",
    t.\"sten_proc_16_pla_rca_transformed_confidences\", t2.\"sten_proc_1_prox_rca_transformed\",
    t2.\"sten_proc_2_midt_rca_transformed\", t2.\"sten_proc_3_dist_rca_transformed\",
    t2.\"sten_proc_4_pda_transformed\", t2.\"sten_proc_16_pla_rca_transformed\"
    t2.\"ffr_sten_proc_1_prox_rca_transformed\", t2.\"ffr_sten_proc_2_midt_rca_transformed\",
    t2.\"ffr_sten_proc_3_dist_rca_transformed\", t2.\"ffr_sten_proc_4_pda_transformed\",
    t2.\"ffr_sten_proc_16_pla_rca_transformed\", t2.\"dominans\", t2.\"labels_predictions\", \"entryid\"
    FROM (
    SELECT '{0:'||MAX((right(left(\"sten_proc_2_midt_rca_transformed_confidences\",9),6)::numeric))::varchar||'}' AS \"sten_proc_2_midt_rca_transformed_confidences\",
        '{0:'||MAX((right(left(\"sten_proc_1_prox_rca_transformed_confidences\",9),6)::numeric))::varchar||'}' AS \"sten_proc_1_prox_rca_transformed_confidences\",
        '{0:'||MAX((right(left(\"sten_proc_3_dist_rca_transformed_confidences\",9),6)::numeric))::varchar||'}' AS \"sten_proc_3_dist_rca_transformed_confidences\",
        '{0:'||MAX((right(left(\"sten_proc_4_pda_transformed_confidences\",9),6)::numeric))::varchar||'}' AS \"sten_proc_4_pda_transformed_confidences\",
        '{0:'||MAX((right(left(\"sten_proc_16_pla_rca_transformed_confidences\",9),6)::numeric))::varchar||'}' AS \"sten_proc_16_pla_rca_transformed_confidences\",


        \"PatientID\", \"StudyInstanceUID\"
    FROM cag.\"classification_config_angio_SEP_Jan24_14-52-21_dicom_table2x\"
    GROUP BY \"StudyInstanceUID\", \"PatientID\"
    ) AS t JOIN cag.\"classification_config_angio_SEP_Jan24_14-52-21_dicom_table2x\" AS t2 ON t.\"StudyInstanceUID\" = t2.\"StudyInstanceUID\" AND t.\"PatientID\" = t2.\"PatientID\"
    WHERE (t2.phase={insert}) AND (labels_predictions IS NOT NULL);
    """.format(insert=phase)

    # query = """
    # SELECT DISTINCT ON (t.\"PatientID\", t.\"StudyInstanceUID\") t.\"PatientID\", t.\"StudyInstanceUID\",
    # t2.phase, t.\"sten_proc_1_prox_rca_transformed_confidences\", t.\"sten_proc_2_midt_rca_transformed_confidences\"
    # , t.\"sten_proc_3_dist_rca_transformed_confidences\", t.\"sten_proc_4_pda_transformed_confidences\",
    # t.\"sten_proc_16_pla_rca_transformed_confidences\", t2.\"sten_proc_1_prox_rca_transformed\",
    # t2.\"sten_proc_2_midt_rca_transformed\", t2.\"sten_proc_3_dist_rca_transformed\",
    # t2.\"sten_proc_4_pda_transformed\", t2.\"sten_proc_16_pla_rca_transformed\"
    # t2.\"ffr_sten_proc_1_prox_rca_transformed\", t2.\"ffr_sten_proc_2_midt_rca_transformed\",
    # t2.\"ffr_sten_proc_3_dist_rca_transformed\", t2.\"ffr_sten_proc_4_pda_transformed\",
    # t2.\"ffr_sten_proc_16_pla_rca_transformed\", t2.\"dominans\", t2.\"labels_predictions\", \"entryid\"
    # FROM (
    # SELECT '{0:'||MAX((right(left(\"sten_proc_2_midt_rca_transformed_confidences\",9),6)::numeric))::varchar||'}' AS \"sten_proc_2_midt_rca_transformed_confidences\",
    #     '{0:'||MAX((right(left(\"sten_proc_1_prox_rca_transformed_confidences\",9),6)::numeric))::varchar||'}' AS \"sten_proc_1_prox_rca_transformed_confidences\",
    #     '{0:'||MAX((right(left(\"sten_proc_3_dist_rca_transformed_confidences\",9),6)::numeric))::varchar||'}' AS \"sten_proc_3_dist_rca_transformed_confidences\",
    #     '{0:'||MAX((right(left(\"sten_proc_4_pda_transformed_confidences\",9),6)::numeric))::varchar||'}' AS \"sten_proc_4_pda_transformed_confidences\",
    #     '{0:'||MAX((right(left(\"sten_proc_16_pla_rca_transformed_confidences\",9),6)::numeric))::varchar||'}' AS \"sten_proc_16_pla_rca_transformed_confidences\",


    #     \"PatientID\", \"StudyInstanceUID\"
    # FROM cag.\"classification_config_angio_SEP_Jan24_14-52-21_dicom_table2x\"
    # GROUP BY \"StudyInstanceUID\", \"PatientID\"
    # ) AS t JOIN cag.\"classification_config_angio_SEP_Jan24_14-52-21_dicom_table2x\" AS t2 ON t.\"StudyInstanceUID\" = t2.\"StudyInstanceUID\" AND t.\"PatientID\" = t2.\"PatientID\"
    # WHERE (t2.phase={insert}) AND (labels_predictions IS NOT NULL);
    # """.format(insert=phase)
    print('query', query)

if __name__ == '__main__':
    hej = """
    paitent "id"
    """
    print(hej)
    do_plot()
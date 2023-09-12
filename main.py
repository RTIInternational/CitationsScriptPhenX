# Script generates SQL text that updates the publications table in PhenX.
# The input Excel (.xlsx) file contains "citing phenx curation" data.
# @author Iris Glaze

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.
import pandas as pd
# pip install openpyxl
import openpyxl
import csv


def correct_nan(input_val, replacement_text=""):
    return input_val if pd.isna(input_val) is False else replacement_text


def remove_newline_chars(input_string):
    return input_string.replace('\n', '') if type(input_string) is str else input_string

def escape_single_quotes(input_string):
    return input_string.replace("'", "''") if type(input_string) is str else input_string

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    f = open('output_sql.sql', 'w', encoding='utf-8')
    col_names_from_input = ["citation_id", "citation_label", "Date (year)", "PhenX Measures", "Study Name",
                            "Study Acronym", "Study type (epidemiological, GWAS, clinical trial, etc)",
                            "Disease/Phenotype", "Primary Research Focus", "Funding Source", "Award #", "FOA"]
    df = pd.read_excel('./Paper_citing_phenx_curation_Aug15_2023.xlsx', sheet_name="Citation Info")
    protocol_list_df = pd.read_excel('./Paper_citing_phenx_curation_Aug15_2023.xlsx', sheet_name="Protocol List")
    protocol_usage_df = pd.read_excel('./Paper_citing_phenx_curation_Aug15_2023.xlsx',
                                      sheet_name="Protocol Usage").dropna(subset=["protocol.id"])
    protocol_list_df['name'] = protocol_list_df['name'].str.title()
    protocol_list_dict = pd.Series(protocol_list_df.id.values, index=protocol_list_df.name).to_dict()
    df_specified_cols = df.loc[:, col_names_from_input]
    sql_text = ""
    citation_table_name = "publications"

    rows = []
    for index, citation_row in df_specified_cols.iterrows():
        citation_id = citation_row["citation_id"]
        citation_label = citation_row["citation_label"]
        date_year = correct_nan(citation_row["Date (year)"])
        phenx_measures = str(correct_nan(citation_row["PhenX Measures"])).split(";")
        # removes empty strings
        phenx_measures = list(filter(None, phenx_measures))
        protocol_ids_string = ""
        protocol_ids_array = []

        if citation_label in protocol_usage_df.columns:
            protocol_ids_by_citation_df = protocol_usage_df[protocol_usage_df[citation_label] == 1].loc[:,
                                          ["protocol.id", "protocol.name"]].astype({'protocol.id': 'int'})
            protocol_ids_array = protocol_ids_by_citation_df["protocol.id"].values

        if len(protocol_ids_array) > 0:
            protocol_ids_string = '|'.join(str(x) for x in protocol_ids_array)

        study_name = remove_newline_chars(escape_single_quotes(correct_nan(citation_row["Study Name"])))
        study_acronym = remove_newline_chars(escape_single_quotes(correct_nan(citation_row["Study Acronym"])))
        study_type = remove_newline_chars(escape_single_quotes(correct_nan(citation_row["Study type (epidemiological, GWAS, clinical trial, etc)"])))
        disease_phenotype = remove_newline_chars(escape_single_quotes(correct_nan(citation_row["Disease/Phenotype"])))
        primary_research_focus = remove_newline_chars(escape_single_quotes(correct_nan(citation_row["Primary Research Focus"])))
        funding_source = remove_newline_chars(escape_single_quotes(correct_nan(citation_row["Funding Source"])))
        award_num = escape_single_quotes(correct_nan(citation_row["Award #"]))
        foa = remove_newline_chars(escape_single_quotes(correct_nan(citation_row["FOA"])))
        new_row = {'citation_id': citation_id, 'citation_label': citation_label, 'date_year': str(date_year),
                   'protocol_ids': protocol_ids_string, 'study_name': study_name,
                   'study_acronym': study_acronym, 'study_type': study_type, 'disease_phenotype': disease_phenotype,
                   'primary_research_focus': primary_research_focus, 'funding_source': funding_source,
                   'award_num': remove_newline_chars(str(award_num)), 'foa': foa}
        new_row_list = list(pd.Series([citation_id, citation_label, str(date_year), protocol_ids_string, study_name,
                   study_acronym, study_type, disease_phenotype,
                   primary_research_focus, funding_source,
                   remove_newline_chars(str(award_num)), foa]))

        #data_df = data_df.append(pd.DataFrame(pd.Series(new_row)), ignore_index=True)
        rows.append(new_row_list)
        #data_df.loc[len(data_df)] = pd.Series(new_row)

        sql_text_line = "UPDATE " + citation_table_name + " SET date_year = \'" + str(date_year) \
            + "\', protocol_ids = \'" + protocol_ids_string + "\', study_name = \'" + study_name + "\'" \
            ", study_acronym = \'" + study_acronym + "\', study_type = \'" \
            + study_type + "\'" \
            ", disease_phenotype = \'" + disease_phenotype + "\', primary_research_focus = \'" \
            + primary_research_focus + "\', funding_source = \'" + funding_source + "\', award_num = \'" \
            + remove_newline_chars(str(award_num)) + "\', foa = \'" + foa + "\'" \
            " WHERE id = " + str(citation_id) + "; \n"
        f.write(sql_text_line)
    f.close()
    output_file_cols_arr = ['citation_id', 'citation_label', 'date_year', 'protocol_ids', 'study_name', 'study_acronym', 'study_type', 'disease_phenotype', 'primary_research_focus', 'funding_source', 'award_num', 'foa']
    data_df = pd.DataFrame(rows, columns=output_file_cols_arr)
    #data_df['primary_research_focus'].apply(lambda x: len(x)).max()
    data_df.to_csv('output_csv.csv', encoding='utf-8', index=False)
    col_max_lengths_file = open('col_max_lengths.txt', 'w', encoding='utf-8')
    output_file_cols_arr_str_type = ['protocol_ids', 'study_name', 'study_acronym', 'study_type', 'disease_phenotype', 'primary_research_focus', 'funding_source', 'award_num', 'foa']
    for val in output_file_cols_arr_str_type:
        col_max_lengths_file.write(val + '\n')
        col_max_lengths_file.write(str(data_df[val].apply(lambda x: len(x)).max()) + '\n')
    col_max_lengths_file.close()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/

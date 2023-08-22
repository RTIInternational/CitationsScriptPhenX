# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.
import pandas as pd
import math
# pip install openpyxl
import openpyxl

def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press ⌘F8 to toggle the breakpoint.

def correct_nan(input_val, replacement_text = ""):
    return input_val if pd.isna(input_val) is False else replacement_text

def convert_measure_to_protocol_id(measure, protocol_list_dict):
    #TODO implement
    result = None
    if measure != '':
        prop_case_measure = measure.title()
        if protocol_list_dict.get(prop_case_measure) is not None:
            result = str(protocol_list_dict[prop_case_measure])
        else:
            result = False
            # result = "ERROR: " + prop_case_measure
    return result

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm')
    f = open('output_sql.txt', 'w', encoding='utf-8')
    df = pd.read_excel('./Paper_citing_phenx_curation_Aug15_2023.xlsx', sheet_name="Citation Info")
    protocol_list_df = pd.read_excel('./Paper_citing_phenx_curation_Aug15_2023.xlsx', sheet_name="Protocol List")
    protocol_usage_df = pd.read_excel('./Paper_citing_phenx_curation_Aug15_2023.xlsx', sheet_name="Protocol Usage").dropna(subset=["protocol.id"])
    protocol_list_df['name'] = protocol_list_df['name'].str.title()
    protocol_list_dict = pd.Series(protocol_list_df.id.values,index=protocol_list_df.name).to_dict()
    col_names_from_input = ["citation_id", "citation_label", "Date (year)", "PhenX Measures", "Study Name",
                            "Study Acronym", "Study type (epidemiological, GWAS, clinical trial, etc)",
                            "Disease/Phenotype", "Primary Research Focus", "Funding Source", "Award #", "FOA"]
    df_specified_cols = df.loc[:, col_names_from_input]
    sql_text = ""
    citation_table_name = "publications"
    error_input_measures_arr = []
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
            protocol_ids_by_citation_df = protocol_usage_df[protocol_usage_df[citation_label] == 1].loc[:, ["protocol.id", "protocol.name"]].astype({'protocol.id': 'int'})
            protocol_ids_array = protocol_ids_by_citation_df["protocol.id"].values

        # if len(phenx_measures) > 0:
        #     for measure in phenx_measures:
        #         protocol_id = convert_measure_to_protocol_id(measure, protocol_list_dict)
        #         if protocol_id is False:
        #             protocol_ids_array.append("ERROR: " + measure)
        #             if measure not in error_input_measures_arr:
        #                 error_input_measures_arr.append(measure)
        #         elif protocol_id is not None:
        #             protocol_ids_array.append(protocol_id)
        if len(protocol_ids_array) > 0:
            protocol_ids_string = '|'.join(str(x) for x in protocol_ids_array)

        study_name = correct_nan(citation_row["Study Name"])
        study_acronym = correct_nan(citation_row["Study Acronym"])
        study_type = correct_nan(citation_row["Study type (epidemiological, GWAS, clinical trial, etc)"])
        disease_phenotype = correct_nan(citation_row["Disease/Phenotype"])
        primary_research_focus = correct_nan(citation_row["Primary Research Focus"])
        funding_source = correct_nan(citation_row["Funding Source"])
        award_num = correct_nan(citation_row["Award #"])
        foa = correct_nan(citation_row["FOA"])
        sql_text_line = "UPDATE " + citation_table_name + " SET date_year = \"" + str(date_year) \
                        + "\", protocol_ids = \"" + protocol_ids_string + "\", study_name = \"" + study_name + "\"" \
                    ", study_acronym = \"" + study_acronym + "\", study_type = \"" + study_type + "\"" \
                    ", disease_phenotype = \"" + disease_phenotype + "\", primary_research_focus = \"" + primary_research_focus + "\"" \
                    ", funding_source = \"" + funding_source + "\", award_num = \"" + str(award_num) + "\", foa = \"" + foa + "\"" \
                    " WHERE id = " + str(citation_id) + "; \n"
        #print(sql_text_line)
        f.write(sql_text_line)
    #print(sql_text)
    f.close()
    print(';\n'.join(error_input_measures_arr))

# See PyCharm help at https://www.jetbrains.com/help/pycharm/

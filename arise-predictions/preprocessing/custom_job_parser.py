from abc import ABC, abstractmethod
import pandas as pd
import json
from arise.utils import constants, utils
from arise.preprocessing import job_parser


class JsonJobParser(ABC):

    def __init__(self, columns, start_time_field_name, end_time_field_name):
        self.columns = columns
        self.start_time_field_name = start_time_field_name
        self.end_time_field_name = end_time_field_name

    @abstractmethod
    def get_history_json(self, json_file):
        pass


class DefaultJsonJobParser(JsonJobParser):

    def get_history_json(self, json_file):
        with open(json_file) as json_data:
            data = dict(json.load(json_data))

        execution_data = pd.DataFrame(columns=self.columns)
        for job in data.items():
            row = []
            complete_row = True
            for field in self.columns:
                if field == constants.JOB_DURATION_FIELD_NAME:
                    try:
                        duration = job_parser.get_job_duration_from_json(job[1], self.start_time_field_name,
                                                                         self.end_time_field_name)
                        row.append(duration)
                    except Exception:
                        complete_row = False
                        break  # continue to the jobs loop
                else:
                    row.append(utils.find_item(job[1], field))
            if complete_row:
                row_df = pd.DataFrame([row], columns=self.columns)
                row_df = row_df.dropna(how='all')  # remove 'all nan' rows
                if not row_df.empty:
                    if execution_data.empty:
                        execution_data = row_df
                    else:
                        execution_data = pd.concat([execution_data, row_df], ignore_index=True)

        return execution_data


def find_hierarchy_item(obj, key1, key2):

    metrics_list = obj['metrics']

    for metric in metrics_list:
        if metric["name"] == key1:
            if key2 in metric:
                return metric[key2]
            else:
                return None
    return None


class SAJsonJobParser(JsonJobParser):

    """
    Contains one execution per json file
    """

    def get_history_json(self, json_file):
        with open(json_file) as json_data:
            data = dict(json.load(json_data))

        row = get_history_from_dict(self.columns, data, self.start_time_field_name, self.end_time_field_name)

        if len(row):
            row_df = pd.DataFrame([row], columns=self.columns)
            row_df = row_df.dropna(how='all')  # remove 'all nan' rows
            if not row_df.empty:
                return row_df

        return pd.DataFrame(columns=self.columns)


def get_history_from_dict(columns, data, start_time_field_name=None, end_time_field_name=None):
    row = []
    complete_row = True

    for field in columns:
        if field == constants.JOB_DURATION_FIELD_NAME and start_time_field_name is not None:
            try:
                duration = job_parser.get_job_duration_from_json(data, start_time_field_name, end_time_field_name)
                row.append(duration)
            except Exception:
                complete_row = False
                break  # continue to the jobs loop
        else:
            if '.' in field:
                keys = field.split('.')
                row.append(find_hierarchy_item(data, keys[0], keys[1]))
            else:
                row.append(utils.find_item(data, field))

    return row if complete_row else []


class JsonInCSVJobParser:

    """ Assumes start and end time are given as explicit CSV fields, and all other fields are inside json fields"""

    def __init__(self, columns, start_time_field_name, end_time_field_name):
        self.columns = columns
        self.start_time_field_name = start_time_field_name
        self.end_time_field_name = end_time_field_name

    def get_history_csv(self, raw_df_file_name):

        raw_df = pd.read_csv(raw_df_file_name, sep='\t')

        history_df = pd.DataFrame(columns=self.columns)

        dict_fields = []
        standalone_fields = []

        for col in raw_df.columns.values.tolist():
            if col in self.columns:
                standalone_fields.append(col)
            else:
                try:
                    json.loads(raw_df[col].iloc[0])
                    dict_fields.append(col)
                except Exception:
                    continue

        for index, orig_row in raw_df.iterrows():

            start_time = orig_row[self.start_time_field_name]
            end_time = orig_row[self.end_time_field_name]

            merged_dict = dict()

            for field in dict_fields:
                merged_dict[field] = json.loads(orig_row[field])

            history_row = []

            for field in standalone_fields:
                history_row.append(orig_row[field])

            # remove last column - duration, to be added next from non-json fields
            dict_cols = [field for field in self.columns[:-1] if field not in standalone_fields]
            history_row.extend(get_history_from_dict(dict_cols, merged_dict))

            try:
                duration = utils.get_duration(start_time, end_time)
                if duration == 0:
                    continue # to next orig_row
                else:
                    history_row.append(duration)
            except Exception:
                continue # to next orig_row

            if len(history_row):
                row_df = pd.DataFrame([history_row], columns=self.columns)
                row_df = row_df.dropna(how='all')  # remove 'all nan' rows

                if not row_df.empty:
                    if history_df.empty:
                        history_df = row_df
                    else:
                        history_df = pd.concat([history_df, row_df], ignore_index=True)

        return history_df

class FinetuningMetadataParser:

    def get_metadata_df(self, raw_metadata_file_name):

        raw_df = pd.read_csv(raw_metadata_file_name, sep=',')

        metadata_df = pd.DataFrame()

        dict_fields = []
        standalone_fields = []

        for col in raw_df.columns.values.tolist():
            try:
                json.loads(raw_df[col].iloc[0])
                dict_fields.append(col)
            except Exception:
                standalone_fields.append(col)

        for index, orig_row in raw_df.iterrows():

            metadata_row = []

            for field in standalone_fields:
                metadata_row.append(orig_row[field])

            metadata_dict = get_metadata_from_dict(dict_fields, orig_row)

            metadata_row.extend(metadata_dict.values())

            if len(metadata_row):
                row_df = pd.DataFrame([metadata_row], columns=standalone_fields+list(metadata_dict.keys()))

                if not row_df.empty:
                    if metadata_df.empty:
                        metadata_df = row_df
                    else:
                        metadata_df = pd.concat([metadata_df, row_df], ignore_index=True)

        return metadata_df

def get_metadata_from_dict(dict_fields, row):

    metadata_dict_row = dict()

    for field in dict_fields:
        values = json.loads(row[field])
        for value in values:
            if '==' in value:
                key_value = value.split("==")
                metadata_dict_row[key_value[0]+"_"+field] = key_value[1]

    return metadata_dict_row
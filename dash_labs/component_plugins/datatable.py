import math

from dash_labs.dependency import Output, Input
from dash_labs.util import build_id, filter_kwargs
from .base import ComponentPlugin
from dash_labs.templates import FlatDiv
import pandas as pd
from dash_table import DataTable


class DataTablePlugin(ComponentPlugin):
    def __init__(
            self, df, columns=None, page_size=5, sort_mode=None, filterable=False,
            serverside=False, template=None
    ):
        if template is None:
            template = FlatDiv()

        if columns is None:
            columns = list(df.columns)

        self.page_size = page_size
        self.sort_mode = sort_mode
        self.filterable = filterable

        self.serverside = serverside
        self.page_count = self._compute_page_count(df)

        if self.serverside:
            self.full_df = df
            self.df = self._compute_serverside_dataframe_slice(df)
        else:
            self.full_df = df
            self.df = df

        self.data, self.columns = self.convert_data_columns(self.df, columns)

        self.template = template
        self.datatable_id = build_id()

        self._output = template._datatable_class()(
            id=self.datatable_id,
        )

    def _compute_serverside_dataframe_slice(self, full_df, page_current=None):
        if page_current is None:
            page_current = 0

        start_ind = page_current * self.page_size
        end_ind = start_ind + self.page_size
        return full_df.iloc[start_ind:end_ind]

    def _compute_page_count(self, full_df):
        return math.ceil(len(full_df) / self.page_size)

    def convert_data_columns(self, df, columns=None):
        # Handle DataFrame input
        if isinstance(df, pd.DataFrame):
            if columns is None:
                columns = df.columns.tolist()
            df = df.to_dict("records")

        # Handle columns as list
        if isinstance(columns, list) and columns and not isinstance(columns[0], dict):
            columns = [{"name": col, "id": col} for col in columns]

        return df, columns

    # Serverside helpers
    def _build_serverside_input(self):
        return {
            "page_current": Input(self.datatable_id, "page_current"),
            "sort_by": Input(self.datatable_id, "sort_by"),
            "filter_query": Input(self.datatable_id, "filter_query"),
        }

    def _build_serverside_output(self):
        data, columns = self.convert_data_columns(self.df, self.columns)
        result = Output(DataTable(
            data=data, columns=columns, id=self.datatable_id,
            page_current=0,
            page_size=self.page_size,
            page_action="custom",
            page_count=self._compute_page_count(self.full_df),
            **filter_kwargs(
                sort_action=None if self.sort_mode is None else "custom",
                sort_mode=self.sort_mode,
                filter_action="custom" if self.filterable else None,
                filter_query="" if self.filterable else None,
            )
        ), component_property=dict(
            data="data", columns="columns", page_count="page_count",
        ))
        return result

    def _build_serverside_result(self, inputs_value, df, preprocessed=False):
        page_current = inputs_value["page_current"]

        if not preprocessed:
            df = self.get_processed_dataframe(inputs_value, df)

        df_slice = self._compute_serverside_dataframe_slice(
            df, page_current=page_current
        )

        data, columns = self.convert_data_columns(df_slice)
        page_count = self._compute_page_count(df)
        return dict(data=data, columns=columns, page_count=page_count)

    # Clientside helpers
    def _build_clientside_input(self):
        return ()

    def _build_clientside_output(self):
        data, columns = self.convert_data_columns(self.df, self.columns)
        return Output(DataTable(
            data=data, columns=columns, id=self.datatable_id,
            page_size=self.page_size,
            **filter_kwargs(
                sort_action=None if self.sort_mode is None else "native",
                sort_mode=self.sort_mode,
                filter_action="native" if self.filterable else None
            )
        ), component_property=dict(
            data="data", columns="columns"
        ))

    def _build_clientside_result(self, df):
        if df is not None:
            data, columns = self.convert_data_columns(df)
        else:
            data, columns = self.data, self.columns

        return dict(data=data, columns=columns)

    @property
    def args(self):
        if self.serverside:
            return self._build_serverside_input()
        else:
            return self._build_clientside_input()

    @property
    def output(self):
        if self.serverside:
            return self._build_serverside_output()
        else:
            return self._build_clientside_output()

    def build(self, inputs_value, df=None, preprocessed=False):
        """

        :param inputs_value:
        :param df:
        :param preprocessed: Set to true if df was produced by get_processed_dataframe
        :return:
        """
        if self.serverside:
            return self._build_serverside_result(
                inputs_value, df, preprocessed=preprocessed
            )
        else:
            return self._build_clientside_result(df)

    def get_processed_dataframe(self, inputs_value, df):
        sort_by = inputs_value["sort_by"]
        # Get active dataframe
        if df is None:
            df = self.df
        # Perform filtering
        print("update serverside")
        if self.filterable and "filter_query" in inputs_value:
            filter_query = inputs_value["filter_query"]
            print(filter_query)
            df = _filter_serverside(df, filter_query)
        # Perform sorting
        if sort_by and len(sort_by):
            df = df.sort_values(
                [col['column_id'] for col in sort_by],
                ascending=[
                    col['direction'] == 'asc'
                    for col in sort_by
                ],
            )
        return df



operators = [['ge ', '>='],
             ['le ', '<='],
             ['lt ', '<'],
             ['gt ', '>'],
             ['ne ', '!='],
             ['eq ', '='],
             ['contains '],
             ['datestartswith ']]


def _split_filter_part(filter_part):
    for operator_type in operators:
        for operator in operator_type:
            if operator in filter_part:
                name_part, value_part = filter_part.split(operator, 1)
                name = name_part[name_part.find('{') + 1: name_part.rfind('}')]

                value_part = value_part.strip()
                v0 = value_part[0]
                if (v0 == value_part[-1] and v0 in ("'", '"', '`')):
                    value = value_part[1: -1].replace('\\' + v0, v0)
                else:
                    try:
                        value = float(value_part)
                    except ValueError:
                        value = value_part

                # word operators need spaces after them in the filter string,
                # but we don't want these later
                return name, operator_type[0].strip(), value

    return [None] * 3


def _filter_serverside(df, filter_query):
    filtering_expressions = filter_query.split(' && ')
    dff = df

    for filter_part in filtering_expressions:
        col_name, operator, filter_value = _split_filter_part(filter_part)

        if operator in ('eq', 'ne', 'lt', 'le', 'gt', 'ge'):
            # these operators match pandas series operator method names
            dff = dff.loc[getattr(dff[col_name], operator)(filter_value)]
        elif operator == 'contains':
            dff = dff.loc[dff[col_name].str.contains(filter_value)]
        elif operator == 'datestartswith':
            # this is a simplification of the front-end filtering logic,
            # only works with complete fields in standard format
            dff = dff.loc[dff[col_name].str.startswith(filter_value)]

    return dff

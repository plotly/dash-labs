import math

from dash_labs.dependency import Output, Input
from dash_labs.util import build_id, filter_kwargs
from .base import ComponentPlugin
from dash_labs.templates import FlatDiv
from dash.development.base_component import Component


operators = [
    ["ge ", ">="],
    ["le ", "<="],
    ["lt ", "<"],
    ["gt ", ">"],
    ["ne ", "!="],
    ["eq ", "="],
    ["contains "],
    ["datestartswith "],
]


class DataTablePlugin(ComponentPlugin):
    """
    Component plugin to make it easier to work with DataTables
    """

    def __init__(
        self,
        df,
        columns=None,
        page_size=5,
        sort_mode=None,
        filterable=False,
        serverside=False,
        template=None,
        location=Component.UNDEFINED,
    ):
        """

        :param df: Pandas DataFrame to be displayed in the DataTable
        :param columns: List of columns from df to display in the table. Defaults to
            all columns if not specified.
        :param page_size: The number of rows of df to display at once. If the number
            of rows exceeds this number, the table will display paging controls.
        :param sort_mode: Sort mode for table. One of:
            - None: no sorting
            - 'single': single column sorting
            - 'multi': multi-column sorting
        :param filterable: If True, display a filter box below each column in the
            table. If False (default), no filtering interface is displayed.
        :param serverside: If True, paging/sorting/filtering operations trigger
            a callback and are performed in Python and only the current displayed
            page is transferred to the client. If False (default), all rows of the table
            are sent to the client at startup and paging/sorting/filtering
            operations do not trigger a Python callback.
        :param template: Template to use to construct DataTable
        :param location: Template location that should be assigned to the constructed DataTable
        """
        if template is None:
            template = FlatDiv(None)

        if columns is None:
            columns = list(df.columns)

        self.page_size = page_size
        self.sort_mode = sort_mode
        self.filterable = filterable
        self.location = location

        self.serverside = serverside
        self.page_count = self._compute_page_count(df)

        if self.serverside:
            self.full_df = df
            self.df = self._compute_serverside_dataframe_slice(df)
        else:
            self.full_df = df
            self.df = df

        self.data, self.columns = self.convert_data_columns(self.df, columns)
        self.datatable_id = build_id()

        # Initialize args
        if self.serverside:
            args = self._build_serverside_input(template)
            output = self._build_serverside_output(template)
        else:
            args = self._build_clientside_input(template)
            output = self._build_clientside_output(template)

        super().__init__(args, output, template)

    def get_output_values(self, args_value, df=None, preprocessed=False):
        """
        :param args_value: Callback arguments corresponding to the args dependenc
            grouping
        :param df: DataFrame to use as input for the table
            (prior to paging/filtering/sorting). If not provided, the DataFrame passed
            to the constructor is used.
        :param preprocessed: Set to true if the df argument was produced by the
            get_processed_dataframe method. This will bypass the serverside filtering
            and sorting logic, since it was already applied by get_processed_dataframe
        :return: Grouping of values corresponding to the dependency grouping returned
            by the output property
        """
        if self.serverside:
            return self._build_serverside_result(
                args_value, df, preprocessed=preprocessed
            )
        else:
            return self._build_clientside_result(df)

    def get_processed_dataframe(self, args_value, df=None):
        """
        Retrieve the DataFrame produced by the serverside filtering and sorting
        operations.

        Note: This method is only supported when serverside=True

        :param args_value: Callback arguments corresponding to the args dependenc
            grouping
        :param df: DataFrame to use as input to the table filtering and sorting
            operations. If not provided, the DataFrame passed to the constructor is
            used.
        :return: DataFrame that has
        """
        if not self.serverside:
            raise ValueError(
                "get_processed_dataframe is only supported when serverside=True"
            )

        sort_by = args_value["sort_by"]
        # Get active dataframe
        if df is None:
            df = self.full_df
        # Perform filtering
        if self.filterable and "filter_query" in args_value:
            filter_query = args_value["filter_query"]
            df = _filter_serverside(df, filter_query)
        # Perform sorting
        if sort_by and len(sort_by):
            df = df.sort_values(
                [col["column_id"] for col in sort_by],
                ascending=[col["direction"] == "asc" for col in sort_by],
            )
        return df

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
        import pandas as pd

        if isinstance(df, pd.DataFrame):
            if columns is None:
                columns = df.columns.tolist()
            df = df.to_dict("records")

        # Handle columns as list
        if isinstance(columns, list) and columns and not isinstance(columns[0], dict):
            columns = [{"name": col, "id": col} for col in columns]

        return df, columns

    # Serverside helpers
    def _build_serverside_input(self, template):
        return {
            "page_current": Input(self.datatable_id, "page_current"),
            "sort_by": Input(self.datatable_id, "sort_by"),
            "filter_query": Input(self.datatable_id, "filter_query"),
        }

    def _build_serverside_output(self, template):
        data, columns = self.convert_data_columns(self.df, self.columns)
        result = Output(
            template._datatable_class()(
                data=data,
                columns=columns,
                id=self.datatable_id,
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
            ),
            component_property=dict(
                data="data",
                columns="columns",
                page_count="page_count",
            ),
            location=self.location,
        )
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
    def _build_clientside_input(self, template):
        return ()

    def _build_clientside_output(self, template):
        data, columns = self.convert_data_columns(self.df, self.columns)
        return Output(
            template._datatable_class()(
                data=data,
                columns=columns,
                id=self.datatable_id,
                page_size=self.page_size,
                **filter_kwargs(
                    sort_action=None if self.sort_mode is None else "native",
                    sort_mode=self.sort_mode,
                    filter_action="native" if self.filterable else None,
                )
            ),
            component_property=dict(data="data", columns="columns"),
            location=self.location,
        )

    def _build_clientside_result(self, df):
        if df is not None:
            data, columns = self.convert_data_columns(df)
        else:
            data, columns = self.data, self.columns

        return dict(data=data, columns=columns)


def _split_filter_part(filter_part):
    for operator_type in operators:
        for operator in operator_type:
            if operator in filter_part:
                name_part, value_part = filter_part.split(operator, 1)
                name = name_part[name_part.find("{") + 1 : name_part.rfind("}")]

                value_part = value_part.strip()
                v0 = value_part[0]
                if v0 == value_part[-1] and v0 in ("'", '"', "`"):
                    value = value_part[1:-1].replace("\\" + v0, v0)
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
    filtering_expressions = filter_query.split(" && ")
    dff = df

    for filter_part in filtering_expressions:
        col_name, operator, filter_value = _split_filter_part(filter_part)

        if operator in ("eq", "ne", "lt", "le", "gt", "ge"):
            # these operators match pandas series operator method names
            dff = dff.loc[getattr(dff[col_name], operator)(filter_value)]
        elif operator == "contains":
            dff = dff.loc[dff[col_name].str.contains(filter_value)]
        elif operator == "datestartswith":
            # this is a simplification of the front-end filtering logic,
            # only works with complete fields in standard format
            dff = dff.loc[dff[col_name].str.startswith(filter_value)]

    return dff

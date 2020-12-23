from dash.dependencies import Input
import dash_express as dx
from dash_table import DataTable
import math


def serverside_table(df, page_size=5):
    table_id = dx.build_component_id("table", "output-table")
    table = DataTable(
        id=table_id,
        columns=[
            {"name": i, "id": i} for i in sorted(df.columns)
        ],
        page_current=0,
        page_size=page_size,
        page_action='custom'
    )

    def update_table(df, page_current):
        page_count = math.ceil(len(df) / page_size)

        data = df.iloc[
            page_current*page_size:(page_current + 1) * page_size
        ].to_dict('records')

        return data, page_count

    inputs = Input(table_id, "page_current")
    return (table, ["data", "page_count"]), inputs, update_table

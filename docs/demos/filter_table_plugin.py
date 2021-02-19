from dash.dependencies import Input
import dash_express as dx
import plotly.express as px
from dash_express import ComponentPlugin


class FilterTable(ComponentPlugin):
    def __init__(self, df, px_kwargs=None, page_size=5, template=None):
        if px_kwargs is None:
            px_kwargs = dict(x=df.columns[0], y=df.columns[1])

        if template is None:
            template = dx.templates.FlatDiv()

        self.df = df
        self.px_kwargs = px_kwargs
        self.page_size = page_size
        self.template = template
        self._compute_props(template)

    def _compute_props(self, template):
        self.graph_id = dx.build_id(name="filter-table-graph")
        self.datatable_id = dx.build_id(name="filter-table-table")
        self._output = [
            dx.Output(template.Graph(id=self.graph_id), "figure"),
            dx.Output(template.DataTable(
                id=self.datatable_id,
                columns=[{"name": i, "id": i} for i in self.df.columns],
                page_size=self.page_size
            ), "data"),
        ]

        self._inputs = Input(self.graph_id, "selectedData")

    def _build(self, inputs_value, df=None):
        if df is None:
            df = self.df

        inds = self.selection_indices(inputs_value)
        if inds:
            filtered = df.iloc[inds]
        else:
            filtered = df

        figure = px.scatter(
            df, **self.px_kwargs
        ).update_traces(
            type="scatter", selectedpoints=inds
        ).update_layout(dragmode="select")

        return [figure, filtered.to_dict("records")]

    def selection_indices(self, inputs_value):
        selectedData = inputs_value
        if selectedData:
            inds = [p["pointIndex"] for p in selectedData["points"]]
        else:
            inds = None

        return inds

    @property
    def inputs(self):
        return self._inputs

    @property
    def output(self):
        return self._output

    def build(self, inputs_value, df=None):
        if df is None:
            df = self.df
        return self._build(inputs_value, df)

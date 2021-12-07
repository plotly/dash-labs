import dash


dash.register_page(__name__, path_template="/asset/<asset_id>/department/<dept_id>")


def layout(asset_id=None, dept_id=None, **other_unknown_query_strings):
    return dash.html.Div(
        [
            dash.dcc.Textarea(
                value=f"variables from pathname:  asset_id: {asset_id} dept_id: {dept_id}",
                style={"width": 450},
            ),
        ]
    )

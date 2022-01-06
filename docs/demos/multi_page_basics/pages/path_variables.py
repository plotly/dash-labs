import dash


dash.register_page(
    __name__,
    path_template="/asset/<asset_id>/department/<dept_id>",
    title="Asset by location analysis",
    description="This is a longer description",
    # path="/asset/inventory/department/branch-1001"
)


def layout(asset_id=None, dept_id=None, **other_unknown_query_strings):
    return dash.html.Div(
        f"variables from pathname:  asset_id: {asset_id} dept_id: {dept_id}"
    )

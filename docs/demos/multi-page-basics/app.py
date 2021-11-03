from dash import Dash, html, dcc
import dash
import dash_labs as dl

app = Dash(__name__, plugins=[dl.plugins.pages])


dash.register_page('another_page', layout='Another page', path='/another-page')
dash.register_page('and_again', layout='And again!', path='/and-again')


app.layout = html.Div([
	html.H1('App Frame'),

	html.Div(
		dcc.Link('Go back home', href=dash.page_registry['pages.home']['path'])
	),

	html.Div([
		html.Div(dcc.Link(
			f"{page['name']} - {page['path']}",
			href=page['path']
		))
		for page in dash.page_registry.values()
		if page['module'] != 'pages.not_found_404'
	]),
	dl.plugins.page_container
])


if __name__ == '__main__':
	app.run_server(debug=True)


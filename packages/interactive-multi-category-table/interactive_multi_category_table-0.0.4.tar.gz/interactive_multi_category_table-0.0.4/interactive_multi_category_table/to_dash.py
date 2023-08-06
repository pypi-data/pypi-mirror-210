import os
from dash import Dash, html, dcc, callback, Output, Input
from .utils import parse_json

def gen_html_table(contents, category_dict, row_category, column_category, checklist_value):
    width_row_category = len(category_dict[row_category])
    width_column_category = len(category_dict[column_category])
    depth_row_category = max([len(cl) for cl in category_dict[row_category]])
    depth_column_category = max([len(cl) for cl in category_dict[column_category]])

    def find_index_from_category(category, category_list_list):
        for i, category_list in enumerate(category_list_list):
            if category == category_list[-1]:
                return i
        raise RuntimeError
    content_list = [['']*width_column_category for _ in range(width_row_category)]
    for content in contents:
        if checklist_value==['all'] or len(set(content['tags']) & set(checklist_value)) > 0:
            row_index = find_index_from_category(content['categories'][row_category], category_dict[row_category])
            column_index = find_index_from_category(content['categories'][column_category], category_dict[column_category])
            if content_list[row_index][column_index]=='':
                content_list[row_index][column_index] = content['name']
            else:
                content_list[row_index][column_index] += '\n'+content['name']

    html_table = []
    for row in range(depth_column_category+width_row_category):
        html_tr = []
        for column in range(depth_row_category+width_column_category):
            if row<depth_column_category and column<depth_row_category:
                if row==0 and column==0:
                    html_tr.append(html.Td('', colSpan=depth_row_category, rowSpan=depth_column_category,
                                           style={"text-align": "center", "border":"1px solid", "white-space": "pre"}))
            elif row<depth_column_category and column>=depth_row_category:
                if len(category_dict[column_category][column-depth_row_category])<=row or \
                   (column-depth_row_category>0 and category_dict[column_category][column-depth_row_category][:(row+1)]==category_dict[column_category][column-depth_row_category-1][:(row+1)]):
                    pass
                else:
                    html_tr.append(html.Td(category_dict[column_category][column-depth_row_category][row],
                                           rowSpan=depth_column_category-len(category_dict[column_category][column-depth_row_category])+1 if len(category_dict[column_category][column-depth_row_category])==row+1 else 1,
                                           colSpan=sum([True if (len(category_dict[column_category][ci])>row)
                                                                and (category_dict[column_category][ci][:(row+1)] ==
                                                                     category_dict[column_category][column-depth_row_category][:(row+1)])
                                                        else False
                                                        for ci in range(column-depth_row_category, width_column_category)]),
                                           style={"text-align":"center", "border":"1px solid", "white-space": "pre"}))
            elif row>=depth_column_category and column<depth_row_category:
                if len(category_dict[row_category][row-depth_column_category])<=column or \
                   (row-depth_column_category>0 and category_dict[row_category][row-depth_column_category][:(column+1)]==category_dict[row_category][row-depth_column_category-1][:(column+1)]):
                    pass
                else:
                    html_tr.append(html.Td(category_dict[row_category][row-depth_column_category][column],
                                           colSpan=depth_row_category-len(category_dict[row_category][row-depth_column_category])+1 if len(category_dict[row_category][row-depth_column_category])==column+1 else 1,
                                           rowSpan=sum([True if (len(category_dict[row_category][ri])>column)
                                                                and (category_dict[row_category][ri][:(column+1)] ==
                                                                     category_dict[row_category][row-depth_column_category][:(column+1)])
                                                        else False
                                                        for ri in range(row-depth_column_category, width_row_category)]),
                                           style={"text-align":"center", "border":"1px solid", "white-space": "pre"}))
            elif row>=depth_column_category and column>=depth_row_category:
                html_tr.append(html.Td(content_list[row-depth_column_category][column-depth_row_category], style={"border": "1px solid", "white-space": "pre"}))
        html_table.append(html.Tr(html_tr))
    table = html.Table(html_table)
    return table

def get_radioitems_options(category_list, row_category_value, column_category_value):
    row_category_options = [{'label': category,
                             'value': category,
                             'disabled': True if category==column_category_value else False} for category in category_list]
    column_category_options = [{'label': category,
                                'value': category,
                                'disabled': True if category==row_category_value else False} for category in category_list]
    return row_category_options, column_category_options

def run_dash_app(json_file_path, encoding='utf-8'):
    category_list, tag_list, category_dict, contents = parse_json(json_file_path, encoding)

    row_category_value_init = category_list[0]
    column_category_value_init = category_list[1]
    row_category_options, column_category_options = get_radioitems_options(category_list, row_category_value_init, column_category_value_init)
    checklist_options = ['all'] + tag_list
    checklist_value_init = ['all']
    global checklist_value_previous
    checklist_value_previous = checklist_value_init

    app = Dash()
    app.title = os.path.split(json_file_path)[-1][:-5]
    app.layout = html.Div([
        html.Div([
            html.Div([
                html.H3('Categories:'),
                'Row:',
                dcc.RadioItems(row_category_options, row_category_value_init,
                               id='radioitems_row_category', inline=True),
                'Column:',
                dcc.RadioItems(column_category_options, column_category_value_init,
                               id='radioitems_column_category', inline=True),
            ], style={"padding": "10px", "margin": "10px"}),
            html.Div([
                html.H3('Tags:'),
                dcc.Checklist(checklist_options, checklist_value_init,
                              id='checklist_tags', inline=True),
            ], style={"padding": "10px", "margin": "10px"}),
        ], id='div-console',
           style={"display": "flex", "flex-direction": "row",
                  "padding": "10px", "margin": "10px",
                  "background": "#f1f1f1"}),
        html.Div([gen_html_table(contents, category_dict, row_category_value_init, column_category_value_init, checklist_value_init)],
           id='div-table',
           style={"padding": "10px", "margin": "10px",
                  "background": "#f1f1f1"})
    ], id='div-container',
    style={"display": "flex", "flex-direction": "column"})

    @callback(
        Output('div-table', 'children'),
        Output('radioitems_row_category', 'options'),
        Output('radioitems_column_category', 'options'),
        Output('checklist_tags', 'value'),
        Input('radioitems_row_category', 'value'),
        Input('radioitems_column_category', 'value'),
        Input('checklist_tags', 'value')
    )
    def update_table(row_category_value, column_category_value, checklist_value):
        row_category_options, column_category_options = get_radioitems_options(category_list, row_category_value, column_category_value)
        global checklist_value_previous
        if 'all' not in checklist_value_previous and 'all' in checklist_value:
            checklist_value_previous = ['all']
        elif 'all' in checklist_value_previous and 'all' in checklist_value:
            if checklist_value_previous != checklist_value:
                checklist_value_previous = [i for i in checklist_value if i!='all']
        elif 'all' in checklist_value_previous and 'all' not in checklist_value:
            checklist_value_previous = ['all']
        else:
            checklist_value_previous = checklist_value
        return [gen_html_table(contents, category_dict, row_category_value, column_category_value, checklist_value_previous)], row_category_options, column_category_options, checklist_value_previous

    app.run_server(debug=True)

if __name__=='__main__':
    json_file_path = "../examples/dinner.json"
    run_dash_app(json_file_path)

import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import requests

# --- Настройки ---
API_TEMPLATES_BASE = "http://127.0.0.1:8090/api/report_templates/"
API_REPORTS_BASE = "http://127.0.0.1:8090/api/reports/"

# Функции для запросов к API
def get_active_templates():
    """
    Получаем список активных шаблонов отчетов:
    /api/report_templates/?active=true
    Возвращает список объектов с полями: id, title, is_active, ...
    """
    params = {"active": "true"}
    try:
        r = requests.get(API_TEMPLATES_BASE, params=params)
        if r.status_code == 200:
            return r.json()  # список шаблонов
        else:
            print("Ошибка при запросе шаблонов:", r.status_code)
            return []
    except Exception as e:
        print("Исключение при запросе шаблонов:", e)
        return []

def get_all_reports():
    """
    Получаем список ВСЕХ созданных отчетов:
    /api/reports/
    Возвращает список с полями: id, template, date, ...
    """
    try:
        r = requests.get(API_REPORTS_BASE)
        if r.status_code == 200:
            return r.json()
        else:
            print("Ошибка при запросе отчетов:", r.status_code)
            return []
    except Exception as e:
        print("Исключение при запросе отчетов:", e)
        return []

def get_template_detail(template_id):
    """
    Получаем структуру конкретного шаблона:
    /api/report_templates/{template_id}/
    Возвращает объект с полями: id, title, tables, rows, columns, ...
    """
    url = f"{API_TEMPLATES_BASE}{template_id}/"
    try:
        r = requests.get(url)
        if r.status_code == 200:
            return r.json()
        else:
            print("Ошибка при запросе шаблона:", r.status_code)
            return {}
    except Exception as e:
        print("Исключение при запросе шаблона:", e)
        return {}

def get_report_data(report_id):
    """
    Получаем данные (ReportData) для конкретного отчета:
    /api/reports/{report_id}/data/
    Возвращает список, где каждый элемент содержит:
      id, report, row, column, value
    """
    url = f"{API_REPORTS_BASE}{report_id}/data/"
    try:
        r = requests.get(url)
        if r.status_code == 200:
            return r.json()
        else:
            print("Ошибка при запросе данных отчета:", r.status_code)
            return []
    except Exception as e:
        print("Исключение при запросе данных отчета:", e)
        return []

# Создаем Dash-приложение
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Просмотр/заполнение отчётов"

# Получаем начальные списки (активные шаблоны и все отчеты)
TEMPLATES = get_active_templates()  # [{'id':..., 'title':..., 'is_active':...}, ...]
REPORTS = get_all_reports()         # [{'id':..., 'template':..., 'date':...}, ...]

# Формируем опции для первого dropdown (выбор шаблона)
template_options = [
    {"label": f"{tpl['title']} (ID={tpl['id']})", "value": tpl["id"]} for tpl in TEMPLATES
]

app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H2("Просмотр/заполнение отчётов"), width=12)
    ], className="mt-3"),

    dbc.Row([
        dbc.Col([
            html.Label("Шаблон отчёта:"),
            dcc.Dropdown(
                id="template-dropdown",
                placeholder="Выберите шаблон",
                options=template_options
            )
        ], width=6),
        dbc.Col([
            html.Label("Сохранённый отчёт (Report):"),
            dcc.Dropdown(
                id="report-dropdown",
                placeholder="Сначала выберите шаблон отчёта",
                options=[]  # Заполним динамически
            )
        ], width=6),
    ], className="mt-2"),

    dbc.Row([
        dbc.Col(html.Div(id="table-container"), width=12)
    ], className="mt-4"),
])

# 1) Callback: обновляем список "сохранённых отчётов" при выборе шаблона
@app.callback(
    Output("report-dropdown", "options"),
    Input("template-dropdown", "value")
)
def update_report_dropdown(selected_template):
    if not selected_template:
        return []
    # Фильтруем все отчеты, у которых report['template'] == selected_template
    filtered_reports = [r for r in REPORTS if r["template"] == selected_template]
    # Формируем опции: label = "Отчёт {id} от {date}", value = id
    options = [
        {
            "label": f"Отчёт {rep['id']} от {rep.get('date','')}",
            "value": rep["id"]
        }
        for rep in filtered_reports
    ]
    return options

# 2) Callback: при выборе отчёта строим таблицу, объединив структуру шаблона и данные отчёта
@app.callback(
    Output("table-container", "children"),
    Input("report-dropdown", "value"),
    State("template-dropdown", "value")
)
def build_report_tables(selected_report_id, selected_template_id):
    if not selected_report_id or not selected_template_id:
        return "Сначала выберите шаблон и отчёт."

    # 1) Запрашиваем структуру выбранного шаблона
    template_detail = get_template_detail(selected_template_id)
    tables = template_detail.get("tables", [])
    if not tables:
        return "В шаблоне нет таблиц."

    # 2) Запрашиваем данные (ReportData) для выбранного отчёта
    data_list = get_report_data(selected_report_id)
    # Превратим список в словарь вида data_map[(row_id, col_id)] = value
    data_map = {}
    for d in data_list:
        row_id = d["row"]
        col_id = d["column"]
        val = d.get("value", "")
        data_map[(row_id, col_id)] = val

    # 3) Для каждой таблицы формируем HTML
    all_tables_html = []
    for tbl in tables:
        tbl_title = tbl.get("title", "Без названия")
        rows = tbl.get("rows", [])
        columns = tbl.get("columns", [])

        # Формируем заголовок таблицы (шапка)
        header = html.Thead(html.Tr(
            [html.Th("Строка")] + [html.Th(col["title"]) for col in columns]
        ))

        # Формируем тело таблицы
        body_rows = []
        for row_obj in rows:
            row_id = row_obj["id"]
            row_title = row_obj["title"]
            row_cells = [html.Td(row_title)]
            for col_obj in columns:
                col_id = col_obj["id"]
                cell_value = data_map.get((row_id, col_id), "")
                row_cells.append(html.Td(cell_value))
            body_rows.append(html.Tr(row_cells))

        table_html = dbc.Table(
            [header, html.Tbody(body_rows)],
            bordered=True, hover=True, responsive=True,
            style={'margin-bottom': '30px'}
        )

        # Добавляем заголовок и готовую таблицу в список
        all_tables_html.append(
            html.Div([
                html.H4(f"Таблица: {tbl_title}"),
                table_html
            ])
        )

    # Возвращаем все таблицы подряд
    return all_tables_html


if __name__ == "__main__":
    # Пользователь просил использовать именно app.run(...), а не app.run_server(...)
    app.run(debug=True, host="0.0.0.0", port=5050)

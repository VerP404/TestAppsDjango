import json

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


def create_new_report(template_id, report_date):
    """
    Создает новый отчет через API:
    POST /api/reports/
    Тело запроса: {"template": template_id, "date": report_date}
    Возвращает ID созданного отчета или None в случае ошибки.
    """
    url = API_REPORTS_BASE
    payload = {
        "template": template_id,
        "date": report_date
    }
    try:
        r = requests.post(url, json=payload)
        if r.status_code == 201:  # Успешное создание
            return r.json().get("id")  # Возвращаем ID нового отчета
        else:
            print("Ошибка при создании отчета:", r.status_code, r.text)
            return None
    except Exception as e:
        print("Исключение при создании отчета:", e)
        return None


def get_auth_token(username, password):
    """
    Получаем токен авторизации через API.
    POST /api/token/
    Тело запроса: {"username": username, "password": password}
    Возвращает токен или None в случае ошибки.
    """
    url = "http://127.0.0.1:8090/api/token/"
    payload = {
        "username": username,
        "password": password
    }
    try:
        r = requests.post(url, json=payload)
        if r.status_code == 200:
            return r.json().get("access")  # Предполагается, что API возвращает поле "access"
        else:
            print("Ошибка при получении токена:", r.status_code, r.text)
            return None
    except Exception as e:
        print("Исключение при получении токена:", e)

        return None


# Создаем Dash-приложение
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True,
    prevent_initial_callbacks='initial_duplicate'  # Разрешаем дублирование с первоначальным вызовом
)
app.title = "Просмотр/заполнение отчётов"

# Получаем начальные списки (активные шаблоны и все отчеты)
TEMPLATES = get_active_templates()  # [{'id':..., 'title':..., 'is_active':...}, ...]
REPORTS = get_all_reports()  # [{'id':..., 'template':..., 'date':...}, ...]

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
                options=[]
            )
        ], width=6),
    ], className="mt-2"),
    dbc.Row([
        dbc.Col([
            html.Label("Дата нового отчёта:"),
            dcc.DatePickerSingle(
                id="new-report-date",
                date=None,
                display_format="YYYY-MM-DD",
                placeholder="Выберите дату"
            ),
        ], width=6),
        dbc.Col([
            dbc.Button(
                "Создать отчёт",
                id="create-report-button",
                color="primary",
                className="mt-4"
            ),
        ], width=6),
    ], className="mt-3"),
    dbc.Row([
        dbc.Col([
            html.Label("Статус отчёта:"),
            dbc.RadioItems(
                id="report-status-toggle",
                options=[
                    {"label": "Черновик", "value": "draft"},
                    {"label": "Для утверждения", "value": "for_approval"},
                    {"label": "Утвержден", "value": "approved"}
                ],
                value="draft",
                inline=True
                # свойство disabled убрано
            )
        ], width=6),
        dbc.Col([
            dbc.Alert("Утвержденный отчет отменяется администратором", color="warning"),
        ], width=6),
    ], className="mt-3"),

    dbc.Row([
        dbc.Col(dbc.Button(
            "Сохранить изменения",
            id="save-button",
            color="success",
            className="mt-4"
        ), width=12),
    ], className="mt-3"),
    dbc.Row([
        dbc.Col(html.Div(id="create-report-message", style={"color": "red"}), width=12)
    ], className="mt-3"),
    dbc.Row([
        dbc.Col(html.Div(id="table-container"), width=12)
    ], className="mt-4"),
    dcc.Interval(id="reset-interval", interval=3000, n_intervals=0, disabled=True),
    # Хранилища
    dcc.Store(id="reset-flag", storage_type="memory"),
    dcc.Store(id='templates-store', storage_type='memory'),
    dcc.Store(id='reports-store', storage_type='memory'),
    dcc.Store(id="changes-store", storage_type="memory")
])


# Callback для первоначального заполнения данных при загрузке страницы
@app.callback(
    [Output('templates-store', 'data'),
     Output('reports-store', 'data')],
    Input('template-dropdown', 'options')  # Любое "фиктивное" Input, чтобы запустить при загрузке
)
def load_initial_data(_):
    templates = get_active_templates()
    reports = get_all_reports()
    return templates, reports


# 1) Callback: обновляем список "сохранённых отчётов" при выборе шаблона
status_map = {
    "draft": "Черновик",
    "for_approval": "Для утверждения",
    "approved": "Утвержден"
}


@app.callback(
    [Output("report-status-toggle", "value"),
     Output("report-status-toggle", "style")],
    [Input("report-dropdown", "value"),
     Input("reports-store", "data")],
    prevent_initial_call=True
)
def update_status_toggle(report_id, reports_data):
    if not report_id or not reports_data:
        return "draft", {}
    current_status = "draft"
    for rep in reports_data:
        if rep["id"] == report_id:
            current_status = rep.get("status", "draft")
            break
    # Блокировка переключателя применяется только если статус в БД равен "approved"
    style = {"pointerEvents": "none", "opacity": 0.5} if current_status == "approved" else {}
    return current_status, style


    # Ищем статус отчёта в хранилище
    current_status = "draft"
    for rep in reports_data:
        if rep["id"] == report_id:
            current_status = rep.get("status", "draft")
            break

    # Логика блокировки
    def make_locked():
        style = {"pointerEvents": "none", "opacity": 0.5}
        return "approved", style

    # Если вызвано изменением отчёта (report-dropdown) или обновлением списка (reports-store)
    # то мы игнорируем старое radio_value и ставим переключатель на current_status
    if trigger_id in ["report-dropdown", "reports-store"]:
        if current_status == "approved":
            return make_locked()
        # Иначе возвращаем статус из базы
        return current_status, {}

    # Если же триггер — это сам переключатель (radio_value), значит пользователь кликнул в UI
    if trigger_id == "report-status-toggle":
        # Если отчёт уже approved или пользователь только что выбрал approved, блокируем
        if current_status == "approved" or radio_value == "approved":
            return make_locked()
        # Иначе оставляем radio_value
        return radio_value, {}

    # На всякий случай, если что-то не учли
    return radio_value, {}



@app.callback(
    Output("report-dropdown", "options"),
    [Input("template-dropdown", "value"),
     Input('reports-store', 'data')]
)
def update_report_dropdown(selected_template, reports_data):
    if not selected_template or not reports_data:
        return []
    filtered_reports = [r for r in reports_data if r["template"] == selected_template]
    # Сортируем по id (предполагается, что более высокий id — более новый отчет)
    filtered_reports.sort(key=lambda r: r["id"], reverse=True)
    return [
        {"label": f"Отчёт {rep['id']} от {rep.get('date', '')} ({status_map.get(rep.get('status', 'draft'), 'Черновик')})",
         "value": rep["id"]}
        for rep in filtered_reports
    ]


# 2) Callback: при выборе отчёта строим таблицу, объединив структуру шаблона и данные отчёта
@app.callback(
    Output("table-container", "children"),
    [Input("report-dropdown", "value"),
     Input("reports-store", "data")],
    State("template-dropdown", "value")
)
def build_report_tables(selected_report_id, reports_data, selected_template_id):
    if not selected_report_id or not selected_template_id:
        return "Сначала выберите шаблон и отчёт."

    # Определяем текущий статус выбранного отчёта из reports-store
    current_status = "draft"
    if reports_data:
        for rep in reports_data:
            if rep["id"] == selected_report_id:
                current_status = rep.get("status", "draft")
                break
    # Если статус не "draft", редактирование ячеек запрещено
    input_disabled = (current_status != "draft")

    # Получаем структуру шаблона
    template_detail = get_template_detail(selected_template_id)
    tables = template_detail.get("tables", [])
    if not tables:
        return "В шаблоне нет таблиц."

    # Получаем данные отчёта
    data_list = get_report_data(selected_report_id)
    data_map = {}
    for d in data_list:
        row_id = d["row"]
        col_id = d["column"]
        val = d.get("value", "")
        data_map[(row_id, col_id)] = val

    # Строим HTML-таблицы
    all_tables_html = []
    for tbl in tables:
        tbl_title = tbl.get("title", "Без названия")
        rows = tbl.get("rows", [])
        columns = tbl.get("columns", [])

        header = html.Thead(html.Tr(
            [html.Th("Строка")] + [html.Th(col["title"]) for col in columns]
        ))

        body_rows = []
        for row_obj in rows:
            row_id = row_obj["id"]
            row_title = row_obj["title"]
            row_cells = [html.Td(row_title)]
            for col_obj in columns:
                col_id = col_obj["id"]
                cell_value = data_map.get((row_id, col_id), "")
                input_id = {"type": "cell-input", "index": f"{row_id}-{col_id}"}
                row_cells.append(
                    html.Td(
                        dcc.Input(
                            id=input_id,
                            type="text",
                            value=cell_value,
                            style={"width": "100px"},
                            disabled=input_disabled
                        )
                    )
                )
            body_rows.append(html.Tr(row_cells))

        table_html = dbc.Table(
            [header, html.Tbody(body_rows)],
            bordered=True, hover=True, responsive=True,
            style={'margin-bottom': '30px'}
        )

        all_tables_html.append(
            html.Div([
                html.H4(f"Таблица: {tbl_title}"),
                table_html
            ])
        )

    return all_tables_html


@app.callback(
    [Output('reports-store', 'data', allow_duplicate=True),
     Output('report-dropdown', 'value'),
     Output('create-report-message', 'children'),
     Output("reset-flag", "data", allow_duplicate=True)],
    Input('create-report-button', 'n_clicks'),
    [State('template-dropdown', 'value'),
     State('new-report-date', 'date'),
     State('reports-store', 'data')],
    prevent_initial_call=True
)
def create_report(n_clicks, selected_template, new_report_date, current_reports):
    if not n_clicks or not selected_template or not new_report_date:
        return dash.no_update, dash.no_update, "", dash.no_update

    new_report_id = create_new_report(selected_template, new_report_date)
    if not new_report_id:
        return dash.no_update, dash.no_update, "Ошибка: Не удалось создать отчет.", dash.no_update

    new_report = {
        "id": new_report_id,
        "template": selected_template,
        "date": new_report_date
    }
    updated_reports = current_reports + [new_report] if current_reports else [new_report]
    return updated_reports, new_report_id, "Отчет успешно создан!", True


@app.callback(
    Output("changes-store", "data"),
    Input({"type": "cell-input", "index": dash.ALL}, "value"),
    State("changes-store", "data")
)
def update_changes(all_values, current_changes):
    if not current_changes:
        current_changes = {}
    # Используем dash.callback_context.inputs, который возвращает ключи в виде строки JSON
    for key, value in dash.callback_context.inputs.items():
        comp_id_str = key.split('.')[0]
        comp_id = json.loads(comp_id_str)
        # Сохраняем ключ как строку, напр., "1-2"
        index = comp_id["index"]
        current_changes[index] = value
    return current_changes


@app.callback(
    Output("reset-interval", "disabled"),
    Input("reset-flag", "data")
)
def enable_reset_interval(reset_flag):
    # Если флаг True, interval включается (disabled=False)
    return not bool(reset_flag)


@app.callback(
    [Output("save-button", "children", allow_duplicate=True),
     Output("create-report-message", "children", allow_duplicate=True),
     Output("reset-flag", "data", allow_duplicate=True),
     Output("reset-interval", "n_intervals"),
     Output("reports-store", "data", allow_duplicate=True)],
    [Input("save-button", "n_clicks"),
     Input("reset-interval", "n_intervals")],
    [State("changes-store", "data"),
     State("report-dropdown", "value"),
     State("report-status-toggle", "value"),
     State("reports-store", "data"),
     State("reset-flag", "data")]
)
def save_and_reset(n_clicks, n_intervals, changes, report_id, new_status, reports_store, reset_flag):
    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update

    trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]

    # Если вызов с кнопки "Сохранить изменения"
    if trigger_id == "save-button":
        if not report_id:
            return "Сохранить изменения", dash.no_update, dash.no_update, dash.no_update, dash.no_update

        # Обновляем данные ячеек
        for key, new_value in changes.items():
            row_id, col_id = map(int, key.split("-"))
            url = f"{API_REPORTS_BASE}{report_id}/data/{row_id}/{col_id}/"
            payload = {"value": new_value}
            try:
                r = requests.patch(url, json=payload)
                if r.status_code != 200:
                    print(f"Ошибка при обновлении данных ({row_id}, {col_id}):", r.status_code, r.text)
            except Exception as e:
                print(f"Исключение при обновлении данных ({row_id}, {col_id}):", e)

        # Определяем текущий статус отчёта из reports_store
        current_status = None
        for rep in reports_store:
            if rep["id"] == report_id:
                current_status = rep.get("status", "draft")
                break

        # Если отчёт уже утвержден, не разрешаем изменение статуса
        if current_status != "approved" and new_status != current_status:
            url = f"{API_REPORTS_BASE}{report_id}/"
            payload = {"status": new_status}
            try:
                r = requests.patch(url, json=payload)
                if r.status_code == 200:
                    print("Статус обновлен")
                else:
                    print("Ошибка обновления статуса:", r.status_code, r.text)
            except Exception as e:
                print("Исключение при обновлении статуса:", e)

        # Обновляем список отчетов после сохранения
        updated_reports = get_all_reports()
        # Устанавливаем временное сообщение и сигнал для сброса (reset_flag = True)
        return "Изменения сохранены!", "", True, 0, updated_reports

    # Если сработал интервал (reset-interval)
    elif trigger_id == "reset-interval":
        if reset_flag:
            # Сбрасываем надписи и очищаем флаг, сбрасываем счетчик interval
            return "Сохранить изменения", "", False, 0, dash.no_update
        else:
            return dash.no_update, dash.no_update, reset_flag, dash.no_update, dash.no_update

    return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update


if __name__ == "__main__":
    # Пользователь просил использовать именно app.run(...), а не app.run_server(...)
    app.run(debug=True, host="0.0.0.0", port=5050)

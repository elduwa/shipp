import os
import pandas as pd
import plotly.express as px
import pytz
import dash_mantine_components as dmc
from dash import Dash, html, dcc, Output, Input
from flask import render_template_string, current_app
from app.extensions import db
from app.models import Device
from app.monitors.pihole_monitor import last_24h_summary
from datetime import datetime, timedelta


def init_dashboard(server):
    """"Create a Plotly Dash dashboard."""
    dash_app = Dash(
        title="Dashboard",
        server=server,
        routes_pathname_prefix='/dash/',
        external_stylesheets=["/static/dist/dashboard.css"],
    )

    # FYI, you need both an app context and a request context to use url_for() in the Jinja2 templates
    with server.app_context(), server.test_request_context():
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
        layout_dash = os.path.join(base_dir, "templates", "dashboard.html")

        with open(layout_dash, "r") as f:
            html_body = render_template_string(f.read())

        comments_to_replace = ("metas", "title", "favicon", "css", "app_entry", "config", "scripts", "renderer")
        for comment in comments_to_replace:
            html_body = html_body.replace(f"<!-- {comment} -->", "{%" + comment + "%}")

        dash_app.index_string = html_body

        current_app.logger.info("Building dashboard layout")
        dash_app.layout = build_dashboard_layout()

        init_callbacks(dash_app)

        return dash_app.server


def build_dashboard_layout():
    client_list = get_all_clients()
    layout = html.Div(className="h-w-full",
                      children=[
                          html.H5(className="dash-h5", children=[
                              html.Span("Dashboard", className="dash-title"),
                              html.Small("last 24h", className="dash-subtitle")
                          ]),
                          html.Div(className="dash-container", children=[
                              html.Div(className="graph-div", children=[
                                  dmc.MantineProvider(
                                      theme={
                                          "colors": {
                                              "reddish": [
                                                  "#F0E7E5",
                                                  "#E4CEC6",
                                                  "#DCB4A7",
                                                  "#DB9B85",
                                                  "#E1805F",
                                                  "#EF6334",
                                                  "#D8592E",
                                                  "#B65635",
                                                  "#98533C",
                                                  "#814F3E",
                                                  "#6E4A3E",
                                                  "#5F453C"
                                              ]
                                          },
                                      },
                                      children=[
                                          dmc.Tabs(className="tabs h-w-full", value="1", id="graph-tabs",
                                                   variant="pills",
                                                   color="reddish",
                                                   children=[
                                                       dmc.TabsList(className="tabs-list", children=[
                                                           dmc.Tab("Total queries", value="1", className="tab"),
                                                           dmc.Tab("Domains", value="2", className="tab"), ]),
                                                       html.Div(className="tabs-content h-w-full", children=[
                                                           dcc.Graph(className="h-w-full", figure={}, id="main-plot",
                                                                     responsive=True,
                                                                     config={'displaylogo': False})])])])]),
                              html.Div(className="card-div", children=[
                                  create_card("card-1-text", "card-1-subtext")
                              ]),
                              html.Div(className="card-div", children=[
                                  create_card("card-2-text", "card-2-subtext")
                              ]),
                              html.Div(className="card-div", children=[
                                  create_card("card-3-text", "card-3-subtext")
                              ]),
                              html.Div(className="multiselect-div", children=[
                                  dmc.MultiSelect(
                                      label="Select clients",
                                      placeholder="Select all you like!",
                                      id="client-multi-select",
                                      clearable=True,
                                      value=[client["value"] for client in
                                             client_list] if client_list is not None and len(
                                          client_list) > 0 else [],
                                      data=client_list,
                                  ),
                              ])
                          ])]
                      )
    return layout


def create_card(text_id: str, subtext_id: str):
    return dmc.Card(className="h-w-full card",
                    children=[
                        dmc.Title(
                            children={},
                            order=2,
                            id=text_id,
                        ),
                        dmc.Text(
                            children={},
                            size="md",
                            color="dimmed",
                            id=subtext_id,
                        ),
                    ],
                    withBorder=True,
                    shadow="sm",
                    radius="md",
                    )


def init_callbacks(dash_app):
    @dash_app.callback(
        Output(component_id="main-plot", component_property="figure"),
        Output(component_id="card-1-text", component_property="children"),
        Output(component_id="card-1-subtext", component_property="children"),
        Output(component_id="card-2-text", component_property="children"),
        Output(component_id="card-2-subtext", component_property="children"),
        Output(component_id="card-3-text", component_property="children"),
        Output(component_id="card-3-subtext", component_property="children"),
        Output(component_id="client-multi-select", component_property="data"),
        Input(component_id="client-multi-select", component_property="value"),
        Input(component_id="graph-tabs", component_property="value"))
    def update_graph(client_ips, tab):
        df = last_24h_summary()
        ip_set = set(client_ips)
        ip_label_list = get_all_clients()
        ip_to_label = dict()
        for ip_label in ip_label_list:
            if ip_label["label"] in ip_to_label.values():
                ip_to_label[ip_label["value"]] = ip_label["label"] + " (" + ip_label["value"] + ")"
            else:
                ip_to_label[ip_label["value"]] = ip_label["label"]

        df = df[df["client"].isin(ip_set)]
        df['time_of_day'] = df['timestamp'].dt.floor('H').dt.time
        df["client_label"] = df["client"].map(ip_to_label)

        timezone = current_app.config['TZ']
        if timezone:
            current_time = datetime.now(pytz.timezone(timezone))
            current_hour = current_time.replace(minute=0, second=0, microsecond=0)
            start_time = current_hour - timedelta(hours=23)
            df = df[df['timestamp'] > start_time]

        fig = create_plot(df, tab)

        total_queries = df.count()["domain"]
        total_queries_text = "total queries"
        unique_domains = df["domain"].nunique()
        unique_domains_text = "unique domains"
        status = pd.to_numeric(df["status"], errors="coerce").dropna()
        num_blocked = status[status.isin([1, 4, 5, 6, 7, 8, 9, 10, 11, 15, 16])].count()
        percentage_blocked = 0
        if num_blocked > 0:
            percentage_blocked = num_blocked / status.count() * 100
        percentage_blocked = round(percentage_blocked, 2)
        percentage_blocked = f"{percentage_blocked} %"
        percentage_blocked_text = "requests blocked"

        return fig, total_queries, total_queries_text, unique_domains, unique_domains_text, percentage_blocked, percentage_blocked_text, ip_label_list

    def create_plot(df, tab):
        if tab == "1":
            df_plot = df.set_index("timestamp")
            df_plot = df_plot.sort_index()
            df_plot = df_plot.groupby(["client_label", "time_of_day"], sort=False).agg(
                count=pd.NamedAgg(column="client_label", aggfunc="count"))
            fig = px.histogram(df_plot, x=df_plot.index.get_level_values(1), y="count",
                               color=df_plot.index.get_level_values(0), barmode="group", height=800,
                               labels={"x": "Time of day", "count": "queries"})
            fig.update_layout(dict(autosize=True))
            return fig
        elif tab == "2":
            df_plot = df.groupby(["client_label", "domain"]).agg(
                count=pd.NamedAgg(column="domain", aggfunc="count")).reset_index()
            df_plot = df_plot.groupby("client_label").apply(lambda x: x.nlargest(10, "count")).reset_index(drop=True)

            fig = px.sunburst(df_plot, path=["client_label", "domain"], values="count", height=800)
            fig.update_layout(dict(autosize=True))
            return fig
        return None


def get_all_clients():
    try:
        client_list = []
        devices = db.session.execute(db.select(Device)).scalars().all()
        for device in devices:
            name = device.device_name
            ip = device.get_current_config().ip_address
            if name is not None and name != "":
                label = name
            else:
                label = ip
            client_list.append({"value": f"{ip}", "label": f"{label}"})
        db.session.commit()
        return client_list
    except Exception as e:
        current_app.logger.error(f"Could not load devices: {e}")

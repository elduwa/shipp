import os
import pandas as pd
import plotly.express as px
import dash_mantine_components as dmc
from dash import Dash, html, dcc, Output, Input
from flask import render_template_string, current_app
from app.extensions import db
from app.models.database_model import Device
from app.monitors.pihole_monitor import last_24h_summary


def init_dashboard(server):
    """"Create a Plotly Dash dashboard."""
    dash_app = Dash(
        title="Dashboard",
        server=server,
        routes_pathname_prefix='/dash/',
        external_stylesheets=["/static/dist/dashboard.css"],
        # external_scripts=["https://cdn.tailwindcss.com"],
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

        dash_app.layout = build_dashboard_layout()

        init_callbacks(dash_app)

        return dash_app.server


def build_dashboard_layout():
    client_list = get_all_clients()
    layout = html.Div(className="h-w-full",
                      children=[html.Div(className="dash-container", children=[
                          html.Div(className="graph-div", children=[
                              dmc.Tabs(className="tabs h-w-full", value="1", id="graph-tabs", variant="pills", color="gray",
                                       children=[
                                          dmc.TabsList(className="tabs-list", children=[
                                              dmc.Tab("Total queries", value="1"),
                                              dmc.Tab("Domains", value="2"), ]),
                                          html.Div(className="tabs-content h-w-full", children=[
                                              dcc.Graph(className="h-w-full", figure={}, id="main-plot", responsive=True)])])]),
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
                                  value=[client_list[0]["value"], ] if len(client_list) > 0 else [],
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
        Input(component_id="client-multi-select", component_property="value"),
        Input(component_id="graph-tabs", component_property="value"))
    def update_graph(clients, tab):
        df = last_24h_summary()
        ip_set = set(clients)
        df = df[df["client"].isin(ip_set)]
        df['time_of_day'] = df['timestamp'].dt.floor('1H').dt.time

        fig = create_plot(df, tab)

        total_queries = df.count()["domain"]
        total_queries_text = "total queries"
        unique_domains = df["domain"].nunique()
        unique_domains_text = "unique domains"
        percentage_blocked = df[df["status"].isin([1, 4, 5, 6, 7, 8, 9, 10, 11, 15, 16])].count()["status"] / \
                             df.count()["status"]
        percentage_blocked = round(percentage_blocked, 2)
        percentage_blocked = f"{percentage_blocked} %"
        percentage_blocked_text = "requests blocked"

        return fig, total_queries, total_queries_text, unique_domains, unique_domains_text, percentage_blocked, percentage_blocked_text

    def create_plot(df, tab):
        if tab == "1":
            df_plot = df.groupby(["client", "time_of_day"]).agg(count=pd.NamedAgg(column="client", aggfunc="count"))
            fig = px.histogram(df_plot, x=df_plot.index.get_level_values(1), y="count",
                               color=df_plot.index.get_level_values(0), barmode="group", height=800)
            fig.update_layout(dict(autosize=True))
            return fig
        elif tab == "2":
            df_plot = df.groupby(["client", "domain"]).agg(
                count=pd.NamedAgg(column="domain", aggfunc="count")).reset_index()
            df_plot = df_plot.groupby("client").apply(lambda x: x.nlargest(10, "count")).reset_index(drop=True)

            fig = px.sunburst(df_plot, path=["client", "domain"], values="count", height=800)
            fig.update_layout(dict(autosize=True))
            return fig
        return None


def get_all_clients():
    client_list = []
    try:
        devices = db.session.execute(db.select(Device)).scalars().all()
        for device in devices:
            name = device.device_name
            ip = device.get_current_config().ip_address
            if name is not None and name != "":
                label = name
            else:
                label = ip
            client_list.append({"value": f"{ip}", "label": f"{label}"})
    except Exception as e:
        current_app.logger.error(f"Could not load devices: {e}")
    return client_list

import plotly.graph_objects as go
import plotly.express as px


def create_stacked_bar_chart(df):
    # Create time of day column with 1-hour buckets
    df['time_of_day'] = df['timestamp'].dt.floor('1H').dt.time

    # Group DNS requests by time of day and client, and calculate the total queries per client
    requests_by_time_of_day_client = df.groupby(['time_of_day', 'client']).size().unstack(fill_value=0)

    # Create the stacked bar chart
    fig = go.Figure()

    for client in requests_by_time_of_day_client.columns:
        fig.add_trace(go.Bar(
            x=requests_by_time_of_day_client.index,
            y=requests_by_time_of_day_client[client],
            name=client
        ))

    # Define layout and axis labels
    fig.update_layout(
        title='Total Queries per Client Grouped by Time of Day',
        xaxis_title='Time of Day',
        yaxis_title='Count',
        barmode='stack'
    )
    return fig


def create_horizontal_bar_chart(df):
    top_clients = df['client'].value_counts().nlargest(10)

    fig = px.bar(top_clients, y=top_clients.index, x=top_clients.values, labels={'y': 'Client', 'x': 'Count'},
                 title='Top 10 Clients with Most DNS Requests', orientation='h')
    return fig


def create_pie_chart(df):
    top_clients = df['client_name'].value_counts().nlargest(5).index.tolist()
    # Replace other clients with "Rest"
    df.loc[~df['client_name'].isin(top_clients), 'client_name'] = 'Rest'
    df["count"] = 1

    fig = px.pie(df, names="client_name", values="count", hole=.3)
    return fig


def figure_to_byte_img(figure):
    img_bytes = figure.to_image(format="png", engine="kaleido")
    return img_bytes

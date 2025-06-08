import dash
from dash import dcc, html, Input, Output, State
import plotly.graph_objs as go
import pandas as pd
import requests

# Fetch top 10 cryptocurrencies from CoinGecko
url = "https://api.coingecko.com/api/v3/coins/markets"
params = {
    "vs_currency": "usd",
    "order": "market_cap_desc",
    "per_page": 10,
    "page": 1,
}
response = requests.get(url, params=params)
data = pd.DataFrame(response.json())

# Descriptions for selected cryptos
crypto_descriptions = {
    "bitcoin": "Bitcoin is the first decentralized digital currency.",
    "ethereum": "Ethereum is a platform for decentralized applications.",
    "tether": "Tether is a stablecoin pegged to the US dollar.",
    "binancecoin": "Binance Coin is the native token of Binance exchange.",
    "ripple": "Ripple is focused on real-time global payments.",
    "cardano": "Cardano is a proof-of-stake blockchain platform.",
    "solana": "Solana is a high-performance blockchain supporting smart contracts.",
    "polkadot": "Polkadot enables cross-blockchain transfers of data and assets.",
    "dogecoin": "Dogecoin started as a meme but has a strong community.",
    "usd-coin": "USD Coin is a stablecoin pegged to the US dollar."
}

# Dropdown options
crypto_options = [{'label': f"{row['name']} ({row['symbol'].upper()})", 'value': row['id']} for _, row in data.iterrows()]

# Static portfolio: general investor including crypto
balanced_labels = ['Stocks', 'Bonds', 'Real Estate', 'Commodities', 'Cash', 'Crypto']
balanced_values = [40, 30, 15, 10, 5, 10]

balanced_fig = go.Figure(go.Pie(
    labels=balanced_labels,
    values=balanced_values,
    hole=0.4,
    marker=dict(line=dict(color='#000000', width=2)),
    textinfo='label+percent',
))
balanced_fig.update_layout(
    title="Balanced Investor Portfolio Including Crypto (Static Example)",
    template='plotly_dark'
)

# Static crypto-only balanced wallet
crypto_only_labels = ['Bitcoin', 'Ethereum', 'Tether', 'Solana', 'Other']
crypto_only_values = [35, 30, 10, 10, 15]

crypto_only_fig = go.Figure(go.Pie(
    labels=crypto_only_labels,
    values=crypto_only_values,
    hole=0.3,
    marker=dict(line=dict(color='#000000', width=2)),
    textinfo='label+percent',
))
crypto_only_fig.update_layout(
    title="Example Balanced Crypto-Only Wallet (Static)",
    template='plotly_dark'
)

# Dash App
app = dash.Dash(__name__)
app.title = "Crypto Dashboard"

app.layout = html.Div(style={'backgroundColor': '#111', 'color': '#fff', 'font-family': 'Arial, sans-serif', 'padding': '20px'}, children=[
    html.H1("Top 10 Cryptocurrencies Dashboard", style={'color': '#0ff'}),

    html.Div(id='crypto-info-div', style={'marginBottom': '30px', 'whiteSpace': 'pre-line'}),

    html.Div([
        html.Label("Select Cryptocurrency:", style={'fontSize': 18}),
        dcc.Dropdown(
            id='crypto-dropdown',
            options=crypto_options,
            value=crypto_options[0]['value'],
            clearable=False,
            style={'width': '300px', 'color': '#000'}
        ),
    ], style={'marginBottom': '30px'}),

    dcc.Graph(id='price-chart'),
    dcc.Graph(id='marketcap-chart'),
    dcc.Graph(id='volume-chart'),

    html.H2("Example Balanced Crypto-Only Wallet"),
    dcc.Graph(id='static-crypto-wallet', figure=crypto_only_fig),

    html.H2("Example Balanced Investor Portfolio Including Crypto"),
    dcc.Graph(id='balanced-investor-portfolio', figure=balanced_fig),

    html.H2("Your Custom Crypto Wallet (Interactive)"),
    html.Div([
        html.Label("Select Crypto to Add:", style={'marginRight': '10px'}),
        dcc.Dropdown(
            id='wallet-crypto-dropdown',
            options=crypto_options,
            value=crypto_options[0]['value'],
            clearable=False,
            style={'width': '200px', 'color': '#000', 'marginRight': '20px'}
        ),

        html.Label("Amount in USD:", style={'marginRight': '10px'}),
        html.Div([
            dcc.Slider(
                id='add-amount-slider',
                min=0,
                max=10000,
                step=10,
                value=0,
                marks={0: '0', 2500: '2.5k', 5000: '5k', 7500: '7.5k', 10000: '10k'},
                tooltip={"placement": "bottom", "always_visible": True},
                updatemode='mouseup'
            )
        ], style={'width': '400px', 'marginRight': '20px'}),

        html.Button("Add to Wallet", id='add-to-wallet-btn', n_clicks=0)
    ], style={
        'display': 'flex',
        'flexWrap': 'wrap',
        'alignItems': 'center',
        'gap': '15px',
        'marginBottom': '30px'
    }),

    dcc.Graph(id='wallet-pie-chart'),

    dcc.Store(id='wallet-store', data={})
])


@app.callback(
    [Output('price-chart', 'figure'),
     Output('marketcap-chart', 'figure'),
     Output('volume-chart', 'figure'),
     Output('crypto-info-div', 'children')],
    [Input('crypto-dropdown', 'value')]
)
def update_graphs(selected_id):
    crypto = data[data['id'] == selected_id].iloc[0]

    # Price chart
    price_fig = go.Figure()
    price_fig.add_trace(go.Bar(
        x=data['name'],
        y=data['current_price'],
        marker_color='orange',
        opacity=0.5,
        name='Others',
    ))
    price_fig.add_trace(go.Bar(
        x=[crypto['name']],
        y=[crypto['current_price']],
        marker_color='red',
        name=crypto['name']
    ))
    price_fig.update_layout(title="Current Price (USD, Log Scale)", template='plotly_dark',
                            yaxis_type="log", yaxis_title="Price (log scale)", xaxis_title="Cryptocurrency")

    # Market Cap chart
    marketcap_fig = go.Figure(go.Pie(
        labels=data['name'],
        values=data['market_cap'],
        hole=0.4,
        marker=dict(line=dict(color='#000000', width=2))
    ))
    marketcap_fig.update_traces(
        pull=[0.1 if x == crypto['name'] else 0 for x in data['name']],
        marker_colors=['red' if x == crypto['name'] else 'mediumturquoise' for x in data['name']]
    )
    marketcap_fig.update_layout(title="Market Capitalization Share", template='plotly_dark')

    # Volume chart
    volume_fig = go.Figure()
    volume_fig.add_trace(go.Bar(
        x=data['name'],
        y=data['total_volume'],
        marker_color='tomato',
        opacity=0.5,
        name='Others',
    ))
    volume_fig.add_trace(go.Bar(
        x=[crypto['name']],
        y=[crypto['total_volume']],
        marker_color='red',
        name=crypto['name']
    ))
    volume_fig.update_layout(title="24h Trading Volume (USD)", template='plotly_dark')

    description = crypto_descriptions.get(selected_id, "No description available for this cryptocurrency.")

    info_text = (f"{crypto['name']} ({crypto['symbol'].upper()})\n\n"
                 f"{description}\n\n"
                 f"Current Price: ${crypto['current_price']:,}\n"
                 f"Market Cap: ${crypto['market_cap']:,}\n"
                 f"24h Volume: ${crypto['total_volume']:,}\n"
                 f"Circulating Supply: {crypto['circulating_supply']:,} coins")

    return price_fig, marketcap_fig, volume_fig, info_text


@app.callback(
    [Output('wallet-store', 'data'),
     Output('wallet-pie-chart', 'figure')],
    [Input('add-to-wallet-btn', 'n_clicks')],
    [State('wallet-store', 'data'),
     State('wallet-crypto-dropdown', 'value'),
     State('add-amount-slider', 'value')]
)
def update_wallet(n_clicks, wallet_data, crypto_id, amount):
    if wallet_data is None:
        wallet_data = {}

    if n_clicks > 0 and amount > 0:
        crypto_row = data[data['id'] == crypto_id]
        if not crypto_row.empty:
            crypto_name = crypto_row.iloc[0]['name']
            wallet_data[crypto_name] = wallet_data.get(crypto_name, 0) + amount

    if wallet_data:
        wallet_fig = go.Figure(go.Pie(
            labels=list(wallet_data.keys()),
            values=list(wallet_data.values()),
            hole=0.3,
            marker=dict(line=dict(color='#000000', width=2)),
            textinfo='label+percent',
        ))
        wallet_fig.update_layout(
            title="Your Crypto Wallet Allocation (USD)",
            template='plotly_dark'
        )
    else:
        wallet_fig = go.Figure(go.Pie(
            labels=["Empty Wallet"],
            values=[1],
            hole=0.3,
            marker=dict(colors=['#444']),
            textinfo='label',
        ))
        wallet_fig.update_layout(
            title="Your Crypto Wallet Allocation (USD)",
            template='plotly_dark'
        )

    return wallet_data, wallet_fig


if __name__ == '__main__':
    app.run(debug=True)

from dash import Dash, dcc, html, Input, Output
import os

import plotly.express as px
import pandas as pd
import firebase_admin
from firebase_admin import credentials, firestore
import dash_bootstrap_components as dbc


external_stylesheets = ['../assets/style.css']

app = Dash(__name__, external_stylesheets=external_stylesheets)

server = app.server


# TẢI DỮ LIỆU TỪ FIRESTORE
cred = credentials.Certificate("./firebase.json")
app = firebase_admin.initialize_app(cred)
dbFireStore = firestore.client()

queryResults = list(dbFireStore.collection(u'tbl-20031381').stream())
listQueryResults = list(map(lambda x : x.to_dict(), queryResults))
df = pd.DataFrame(listQueryResults)


df["YEAR_ID"] = df["YEAR_ID"].astype("str")
df["QTR_ID"] = df["QTR_ID"].astype("str")
df["SALES"] = df["SALES"].astype("float")
df["QUANTITYORDERED"] = df["QUANTITYORDERED"].astype("float")
df["PRICEEACH"] = df["PRICEEACH"].astype("float")


df["LoiNhuan"] = df["SALES"] - (df["QUANTITYORDERED"] * df["PRICEEACH"])
dfGroup = df.groupby("YEAR_ID").sum()
dfGroup["YEAR_ID"] = dfGroup.index


# TRỰC QUAN HÓA DỮ LIỆU WEB APP
app = Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

app.title = "Finance Data Analysis"


figDoanhSoBanHangTheoNam = px.bar(dfGroup, x='YEAR_ID', y="SALES",
                                  title='doanh so ban hang theo nam', color='YEAR_ID',
                                  labels={'YEAR_ID': 'Từ năm 2003, 2004 và 2005', 'QTR_ID': 'Quý trong năm', 'Sum': 'Tổng số lượng sản phẩm'})
figLoiNhuanBanHangTheoNam = px.line(dfGroup, x='YEAR_ID', y="LoiNhuan",
                                    title='doanh so ban hang theo nam',
                                    )


figTileDoanhSo = px.sunburst(df, path=['YEAR_ID', 'MONTH_ID'], values='SALES',
                             color='SALES',
                             labels={'parent': 'Năm', 'id': 'Year / month'},
                             title='Ti le dong gop cua doanh so theo tung danh muc trong tung nam')

figTileLoiNhuan = px.sunburst(df, path=['YEAR_ID', 'MONTH_ID'], values='LoiNhuan',
                              color='LoiNhuan',
                              labels={'parent': 'Năm', 'id': 'Year / month'},
                              title='Ti le dong gop cua loi nhuan theo tung danh muc trong tung nam')


doanhso = round(df["SALES"].sum(), 2)
loinhuan = round(df['LoiNhuan'].sum(), 2)

topDoanhSo = df['SALES'].max()

topLoiNhuan = round(df['LoiNhuan'].max(), 2)

app.layout = dbc.Container(
    children=[
        html.Div(
            className="row",
            children=[
                html.Div(
                    className="col-12 title-table",
                    children=html.H3(
                        children="XAY DUNG DANH MUC SAN PHAM TIEM NANG"
                    )
                ),
                html.Div(
                    className="col-md-3 col-6 col-sm-6 row1_col4",
                    children=["Doanh so sale",
                              html.Br(), html.H3(
                                  children=doanhso
                              )
                              ]
                ),
                html.Div(
                    className="col-md-3 col-6 col-sm-6 row1_col4",
                    children=["Loi nhuan",
                              html.Br(), html.H3(
                                  children=loinhuan
                              )]
                ),
                html.Div(
                    className="col-md-3 col-6 col-sm-6 row1_col4",
                    children=["Top doanh so",
                              html.Br(), html.H3(
                                  children=topDoanhSo
                              )]
                ),
                html.Div(
                    className="col-md-3 col-6 col-sm-6 row1_col4",
                    children=["Top loi nhuan",
                              html.Br(), html.H3(
                                  children=topLoiNhuan
                              )]
                ),
                html.Div(
                    className="col-md-6 col-sm-12 row2",
                    children=[
                        html.Div(
                            children=dcc.Graph(
                                id='figDoanhSoBanHangTheoNam-graph',
                                figure=figDoanhSoBanHangTheoNam),
                            className="mycard"
                        ),
                    ]
                ),
                html.Div(
                    className="col-md-6 col-sm-12 row2",
                    children=[
                        html.Div(
                            children=dcc.Graph(
                                id='figTileDoanhSo-graph',
                                figure=figTileDoanhSo),
                            className="mycard"
                        ),
                    ]
                ),
                html.Div(
                    className="col-md-6 col-sm-12 row2",
                    children=[
                        html.Div(
                            children=dcc.Graph(
                                id='figLoiNhuanBanHangTheoNam-graph',
                                figure=figLoiNhuanBanHangTheoNam),
                            className="mycard"
                        ),
                    ]
                ),
                html.Div(
                    className="col-md-6 col-sm-12 row2",
                    children=[
                        html.Div(
                            children=dcc.Graph(
                                id='figTileLoiNhuan-graph',
                                figure=figTileLoiNhuan),
                            className="mycard"
                        ),
                    ]

                )
            ]
        )
    ]
)

@app.callback(Output('display-value', 'children'),
                [Input('dropdown', 'value')])
def display_value(value):
    return f'You have selected {value}'

if __name__ == '__main__':
    app.run_server(debug=True)
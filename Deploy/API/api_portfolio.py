import pandas as pd
from flask import Flask, jsonify
import requests
from flask_restful import Resource, Api
from pandas.io.parsers import read_csv
import json


app = Flask(__name__)
api = Api(app)


@app.route('/get_portfolios', methods = ['GET'])
def get_portfolios():
        
    df_portfolios_escolhidos = pd.read_csv("dataframes/df_portfolios_escolhidos.csv", index_col=0)
    
    df_portfolios_escolhidos_json = df_portfolios_escolhidos.to_json(orient = "index")
    
    df_portfolios_escolhidos_json = json.loads(df_portfolios_escolhidos_json)
    
    df_portfolios_escolhidos_json = json.dumps(df_portfolios_escolhidos_json, indent=0) 
    
    return df_portfolios_escolhidos_json


@app.route('/update_portfolios', methods = ['GET', 'POST'])
def update_portfolios():

    from gerador_portfolios import gera_portfolios

    horizonte = 10
    lista_pesos = [0.05, 0.1 ,0.15, 0.2, 0.25, 0.3, 0.35, 0.4]
    n_componentes = 5 # qtd. de ativos no portfolio.
    n_iter = 1 # calibra a quantidade de arranjos aleatórios que cada combinação que soma 100% de pesos vai dar origem (valor ideal: 100)
    risk_free = 0.03
    target = 0.15

    ativos = ['BTC-USD',
    'DOGE-USD',
    'XMR-USD',
    'LTC-USD',
    'DASH-USD',
    'XLM-USD',
    'XRP-USD',
    'USDT-USD',
    'ETH-USD',
    'ETC-USD',
    'NEO-USD',
    'MKR-USD',
    'MIOTA-USD',
    'EOS-USD',
    'BCH-USD',
    'BNB-USD',
    'TRX-USD',
    'LINK-USD',
    'ADA-USD',
    'XTZ-USD',
    'FIL-USD',
    'THETA-USD']


    df_retornos = pd.read_csv("dataframes/df_retornos.csv")

    gera_portfolios(lista_ativos= ativos, df_retornos = df_retornos, lista_pesos=lista_pesos, n_componentes=n_componentes, n_iter=n_iter)
    return "Criptofolio atualizado!"


if __name__ == '__main__':
    app.run()

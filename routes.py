from flask import render_template, request,Flask
import numpy as np
import re
import requests
import pandas as pd
import json
from pandas.io.parsers import read_csv

#Iniciando a aplicação Flask
app = Flask(__name__)
#Endpoint Main - Direto no questionário do perfil
@app.route('/')
def perfil_questions():
    return render_template('home.html')

#Perfil Home, onde vamos explicar e apresentar o projeto.
@app.route('/home')
def home_page():
   return render_template('home.html')

#Página sobre a equipe que realizou o projeto
@app.route('/about_us')
def about_us_page():
    return render_template('about_us.html')
@app.route('/perfil')
def perfil():
    return render_template('quest_perfil.html')
#Aqui será a rota onde após pegar todos os dados do questionário, vamos criar a página de portfolio.
@app.route('/quest_perfil',methods = ['POST'])
def quest_perfil_page():
    #pesos = [3,2,2,4,2,3,2,3,2,2,2,2]
    #Peso atribuido a cada umas das 7 perguntas do questionário.
    pesos = [3,4,6,3,5,4,4]
    #a página retorna um dict com key = p* sendo * o número da pergunta, e value o valor númerio da resposta
    resposta_forms= list()
    for key, val in request.form.items():
        resposta_forms.append(val)
    #transformando lista de respostas em valores númericos.
    for i in range(0, len(resposta_forms)):
        resposta_forms[i] = int(resposta_forms[i])
    #aplicando peso de cada pergunta, e inserindo o perfil
    produto = np.multiply(pesos,resposta_forms)
    nota_perfil = sum(produto)
    if nota_perfil <= 52:
        perfil_final = "Aversão muito alta a risco: Você é uma pessoa tipicamente conservadora, é do tipo que mesmo com um sol gigante, consulta a meteorologia antes de sair de casa. Já que sua grana tá embaixo do colchão ou na poupança,vai devagar e sempre com crypto"
        indice_perfil = "Conservador"   
    elif nota_perfil <= 65:
        perfil_final ="Vamos pular de paraquedas? Não, mas eu vou no avião pra ver, vai que dá vontade: Você normalmente usa a razão para tomar suas decisões, mas tem sempre aquele diabinho falando no seu ouvido. Não se iluda, as cryptos são esse diabinho."
        indice_perfil ="Moderado"
    elif nota_perfil <= 71:
        perfil_final ="Tá em cima do muro né? Você não necessariamente sabe o que quer, mas tem mente aberta: Você gosta de equilibrio nos seus investimentos, porém entende que crypto pode trazer novas oportunidades"
        indice_perfil ="Dinamico"
    elif nota_perfil <= 83:
        perfil_final ="Tu gosta, que eu sei. RAMBO/XENA: Não dispensa uma batalha desde que tenha uma estratégia vencedora. Gosta de ter uma opção ALL IN, mas jamais entraria no jogo com todas as suas fichas."
        indice_perfil ="Arrojado"
    else:
       perfil_final = "Apetite altissímo ao risco AKA, CHUCK NORRIS: YOLO, Você é uma pessoa que aceita e entende que 'com grandes poderes, vem grandes perdas', Uncle Ben. Mas vamos combinar, caso fique milionário, me chama pro churras. Mas se perder tudo amanhã, não chama a mamãe."
       indice_perfil ="Agressivo"
    #buscando os 5 portfolio do JSON criado no gerador_portfolios.py
    portfolios = requests.get("https://criptofolio.herokuapp.com/get_portfolios")#https://criptofolio.herokuapp.com/get_portfolios
    portfolio_dict=portfolios.json()
    # Selecionando o portfolio que foi adequado ao questionário
    lista_peso_raw =portfolio_dict[indice_perfil]["pesos"]
    #regex visto que a saira era uma string "[]"
    lista_peso = re.findall('[\-\+]?[0-9]*(\.[0-9]+)',lista_peso_raw)
    lista_peso =list(map(float,lista_peso))
    lista_crypto_raw = portfolio_dict[indice_perfil]["cryptos"]
    lista_crypto =  re.findall('[A-Z]+-[A-Z]+',lista_crypto_raw)
    dict_portfolio ={}
    dict_portfolio_legenda={}
    #Add Description from csv and Link
    df = pd.read_csv('dados/df_eligible.csv')
    #df['link']=df['description'].str.extract(r'(https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9][com|org|io|info|link|network|tech.]{1,})')
    dict_description = dict(zip(df.ticker,df.description))
    dict_link =  dict(zip(df.ticker,df.link))
    dic_final_desc = {}
    dic_link = {}
    for i in range(0,len(lista_crypto)):
        if lista_crypto[i]  in dict_description:
            dic_final_desc[lista_crypto[i]] = dict_description[lista_crypto[i]]
        if lista_crypto[i] in dict_link:
            dic_link[lista_crypto[i]] = dict_link[lista_crypto[i]]
    #Dicionário novo criado somente para uso da API google de gráficos.
    dict_portfolio_legenda['Ativo']='Peso' 
    for i in range(0,len(lista_peso)):
        dict_portfolio[lista_crypto[i]] = lista_peso[i]
        dict_portfolio_legenda[lista_crypto[i]] = lista_peso[i]
    
    
    return render_template('perfil.html',indice_perfil=indice_perfil,dict_portfolio = dict_portfolio, perfil_final=perfil_final,
                            dict_portfolio_legenda=dict_portfolio_legenda, dic_final_desc=dic_final_desc,dic_link=dic_link)

@app.route('/get_portfolios', methods = ['GET'])
def get_portfolios():
        
    df_portfolios_escolhidos = pd.read_csv("dataframes/df_portfolios_escolhidos.csv", index_col=0)
    
    df_portfolios_escolhidos_json = df_portfolios_escolhidos.to_json(orient = "index")
    
    df_portfolios_escolhidos_json = json.loads(df_portfolios_escolhidos_json)
    
    df_portfolios_escolhidos_json = json.dumps(df_portfolios_escolhidos_json, indent=0) 
    
    return df_portfolios_escolhidos_json


@app.route('/update_portfolios', methods = ['GET'])
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
    app.run(debug=True)
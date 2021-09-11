import pandas as pd
import numpy as np
import yfinance as yf
import datetime as dt
import random

from joblib import load

from itertools import combinations_with_replacement, product

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


def gera_portfolios(lista_ativos, df_retornos, lista_pesos, n_componentes, n_iter):
    
    df_portfolios = pd.DataFrame(columns = ['pesos', 'cryptos', 'retorno', 'risco', 'sharpe', 'sortino', 'roy_safety_first', 'pesos_all'])
    
    dict_models = {}

    for crypto in lista_ativos:

        nome = "modelos/modelo_" + str(crypto) + "_final.joblib"

        dict_models[crypto] = load(nome)

        #print(f"{nome} carregado.")

    retornos_avg = df_retornos.mean()
    matriz_covar = df_retornos.cov()

    df_fin = pd.DataFrame(index = lista_ativos)

    df_fin['ret_avg_dia_passado'] = retornos_avg

    yesterday = dt.date.today() - dt.timedelta(days=1)
    yesterday = yesterday.strftime('%Y-%m-%d')

    inicio =  dt.date.today() - dt.timedelta(days = 15) #é preciso acessar dados de 15 dias atrás para montar as features necessárias
    inicio = inicio.strftime('%Y-%m-%d')

    df_features = pd.DataFrame(columns = ['Ativo', 'Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume'])

    for ativo in lista_ativos:
        
        
        print(f"Iniciando coleta do ativo {ativo}")
        
        dados = yf.download(ativo, inicio, yesterday)
        dados['Ativo'] = ativo
        
        df_features = pd.concat([df_features, dados])

    df_features.sort_index(inplace=True) #Organizando o df por datas
    df_features.drop(columns = 'Adj Close', inplace=True)
    df_features['Volume'] = df_features['Volume'].astype(float)

    def relative_strength_idx(df, ativo, n): #MUDAR PARAM "n" AQUI PARA VARIAR A MÉDIA MÓVEL
        close = df[df['Ativo']==ativo]['Close']
        delta = close.diff()
        pricesUp = delta.copy()
        pricesDown = delta.copy()
        pricesUp[pricesUp < 0] = 0
        pricesDown[pricesDown > 0] = 0
        rollUp = pricesUp.rolling(n).mean()
        rollDown = pricesDown.abs().rolling(n).mean()
        rs = rollUp / rollDown
        rsi = 100 - (100 / (1 + rs))
        return rsi

    for ativo in lista_ativos:
        
        df_features.loc[df_features['Ativo'] == ativo,'1: ln(C/C-1)'] = np.log(df_features.loc[df_features['Ativo'] == ativo]['Close'] / df_features.loc[df_features['Ativo'] == ativo,'Close'].shift(1))
        df_features.loc[df_features['Ativo'] == ativo,'2: ln(C-1/C-2)'] = np.log(df_features.loc[df_features['Ativo'] == ativo]['Close'].shift(1)/df_features.loc[df_features['Ativo'] == ativo]['Close'].shift(2))
        df_features.loc[df_features['Ativo'] == ativo,'3: ln(C-2/C-3)'] = np.log(df_features.loc[df_features['Ativo'] == ativo]['Close'].shift(2)/df_features.loc[df_features['Ativo'] == ativo]['Close'].shift(3))
        df_features.loc[df_features['Ativo'] == ativo,'4: ln(C-3/C-4)'] = np.log(df_features.loc[df_features['Ativo'] == ativo]['Close'].shift(3)/df_features.loc[df_features['Ativo'] == ativo]['Close'].shift(4))
        df_features.loc[df_features['Ativo'] == ativo,'5: ln(H/O)'] = np.log(df_features.loc[df_features['Ativo'] == ativo]['High']/df_features.loc[df_features['Ativo'] == ativo]['Open'])
        df_features.loc[df_features['Ativo'] == ativo,'6: ln(H/O-1)'] = np.log(df_features.loc[df_features['Ativo'] == ativo]['High']/df_features.loc[df_features['Ativo'] == ativo]['Open'].shift(1))
        df_features.loc[df_features['Ativo'] == ativo,'7: ln(H/O-2)'] = np.log(df_features.loc[df_features['Ativo'] == ativo]['High']/df_features.loc[df_features['Ativo'] == ativo]['Open'].shift(2))
        df_features.loc[df_features['Ativo'] == ativo,'8: ln(H/O-3)'] = np.log(df_features.loc[df_features['Ativo'] == ativo]['High']/df_features.loc[df_features['Ativo'] == ativo]['Open'].shift(3))
        df_features.loc[df_features['Ativo'] == ativo,'9: ln(H-1/O-1)'] = np.log(df_features.loc[df_features['Ativo'] == ativo]['High'].shift(1)/df_features.loc[df_features['Ativo'] == ativo]['Open'].shift(1))
        df_features.loc[df_features['Ativo'] == ativo,'10: ln(H-2/O-2)'] = np.log(df_features.loc[df_features['Ativo'] == ativo]['High'].shift(2)/df_features.loc[df_features['Ativo'] == ativo]['Open'].shift(2))
        df_features.loc[df_features['Ativo'] == ativo,'11: ln(H-3/O-3)'] = np.log(df_features.loc[df_features['Ativo'] == ativo]['High'].shift(3)/df_features.loc[df_features['Ativo'] == ativo]['Open'].shift(3))
        df_features.loc[df_features['Ativo'] == ativo,'12: ln(L/O)'] = np.log(df_features.loc[df_features['Ativo'] == ativo]['Low']/df_features.loc[df_features['Ativo'] == ativo]['Open'])
        df_features.loc[df_features['Ativo'] == ativo,'13: ln(L-1/O-1)'] = np.log(df_features.loc[df_features['Ativo'] == ativo]['Low'].shift(1)/df_features.loc[df_features['Ativo'] == ativo]['Open'].shift(1))
        df_features.loc[df_features['Ativo'] == ativo,'14: ln(L-2/O-2)'] = np.log(df_features.loc[df_features['Ativo'] == ativo]['Low'].shift(2)/df_features.loc[df_features['Ativo'] == ativo]['Open'].shift(2))
        df_features.loc[df_features['Ativo'] == ativo,'15: ln(L-3/O-3)'] = np.log(df_features.loc[df_features['Ativo'] == ativo]['Low'].shift(3)/df_features.loc[df_features['Ativo'] == ativo]['Open'].shift(3))
        
        
        df_features.loc[df_features['Ativo'] == ativo,'16: True Range'] = np.nanmax([np.abs(df_features.loc[df_features['Ativo'] == ativo, 'High'] - df_features.loc[df_features['Ativo'] == ativo, 'Low']), 
                                                                                np.abs(df_features.loc[df_features['Ativo'] == ativo, 'High'] - df_features.loc[df_features['Ativo'] == ativo, 'Close'].shift(1)), 
                                                                                np.abs(df_features.loc[df_features['Ativo'] == ativo, 'Low'] - df_features.loc[df_features['Ativo'] == ativo, 'Close'].shift(1))], axis=0)
        
        
        df_features.loc[df_features['Ativo'] == ativo,'17: ATR 5d'] = df_features.loc[df_features['Ativo'] == ativo,'16: True Range'].rolling(window=5).mean()
        df_features.loc[df_features['Ativo'] == ativo,'17b: ATR 10d'] = df_features.loc[df_features['Ativo'] == ativo,'16: True Range'].rolling(window=10).mean()
        df_features.loc[df_features['Ativo'] == ativo,'17c: ATR 14d'] = df_features.loc[df_features['Ativo'] == ativo,'16: True Range'].rolling(window=14).mean()
        
        df_features.loc[df_features['Ativo'] == ativo,'18: MI 3d'] = df_features.loc[df_features['Ativo'] == ativo, 'Close'] - df_features.loc[df_features['Ativo'] == ativo, 'Close'].shift(3)
        df_features.loc[df_features['Ativo'] == ativo,'18b: MI 7d'] = df_features.loc[df_features['Ativo'] == ativo, 'Close'] - df_features.loc[df_features['Ativo'] == ativo, 'Close'].shift(7)

        df_features.loc[df_features['Ativo'] == ativo,'19: RSI 5d'] = relative_strength_idx(df_features,ativo, n=5)
        df_features.loc[df_features['Ativo'] == ativo,'19b: RSI 10d'] = relative_strength_idx(df_features,ativo, n=10)
        df_features.loc[df_features['Ativo'] == ativo,'19c: RSI 14d'] = relative_strength_idx(df_features,ativo, n=14)
        
        df_features.loc[df_features['Ativo'] == ativo,'20: ln(Vol/Vol-1)'] = np.log(df_features.loc[df_features['Ativo'] == ativo, 'Volume'] / df_features.loc[df_features['Ativo'] == ativo,'Volume'].shift(1))
        
        df_features.loc[df_features['Ativo'] == ativo,'21: ln(Vol-1/Vol-2)'] = np.log(df_features.loc[df_features['Ativo'] == ativo, 'Volume'].shift(1) / df_features.loc[df_features['Ativo'] == ativo,'Volume'].shift(2))

        
        #Vamos manter o preço de fechamento ('Close') para, a partir das previsões, podermos calcular o retorno esperado para o horizonte, de forma a calcular o retorno total esperado para o ativo, mesclando passado e projeções. 
        

    df_features.drop(columns = ['Open', 'High', 'Low'], inplace=True) #Dropando colunas inúteis.
    df_features.dropna(inplace=True)


    df_pred = pd.DataFrame(columns = ['Close_10d', 'Close'], index = lista_ativos)


    for ativo in lista_ativos:
        
        X = df_features[df_features['Ativo'] == ativo].drop(['Close', 'Ativo'], axis = 1)

        model = dict_models[ativo]

        df_pred.loc[ativo,'Close_10d'] = model.predict(X)[0]
        
        df_pred.loc[ativo,'Close'] = df_features[df_features['Ativo']==ativo]['Close'][0]


    df_fin['ret_futuro_dia'] = (df_pred['Close_10d'] / df_pred['Close'] - 1)/10

    df_fin['retorno_dia_esperado'] = df_fin['ret_avg_dia_passado'] * 0.95 + df_fin['ret_futuro_dia'] * 0.05
    
    
    
    comb = product(lista_pesos, repeat = n_componentes) # 32768 possíveis combinações desses elementos, 5 a 5, com repetição.
    
    lista_c = []
    lista_p = []
    lista_p_all = []
    lista_cryptos = []
    lista_retorno = []
    lista_risco = []
    lista_sharpe = []
    lista_sortino = []
    lista_roys = []
    
    
    
    
    for p in comb:
    
        lista_c.append(p) #Todas as combinações possíveis de pesos
    
    
    for r in range(0, len(lista_c)):
        
        pesos_total_1 = []
        
        if sum(lista_c[r]) == 1: #Quero apenas as combinações que somam 100% (São 1976 possíveis a cada 5 ativos)

            cont = 0
            while cont < n_componentes:
            #pesos_total_1.append([lista_c[r][0], lista_c[r][1], lista_c[r][2], lista_c[r][3], lista_c[r][4]])
                pesos_total_1.append(lista_c[r][cont])
                
                cont += 1    
   
                #print(f"Pesos total 1.1: {pesos_total_1}")
                #print(f"cont: {cont}")
        
            pesos_all = []
             
            pesos_all.extend(pesos_total_1) #Atribuindo os pesos apenas aos ativos da combinação atual.
            pesos_all.extend(np.zeros(len(lista_ativos)-n_componentes)) #Gerando a quantidade de zeros correspondente aos ativos que estão depois da combinação atual.
            
           
                
            for i in range(0, n_iter):
            
                lista_p.append(pesos_total_1)
                pesos_all_shuffle = random.sample(pesos_all, len(pesos_all))
                #print(f"pesos_all_shuffle: {pesos_all_shuffle}")
                
                lista_p_all.append(pesos_all_shuffle) #Armazeno a lista com a combinação e com a complementação de array de zeros, para mirar apenas nos 5 ativos específcos. -> Armazenar na coluna 'pesos_all' do df final

                crypto_sel = []


                for index in np.nonzero(pesos_all_shuffle)[0]:

                    crypto_sel.append(lista_ativos[index])

                lista_cryptos.append(crypto_sel) #Armazeno a lista com as 5 cryptos que fazem parte da combinação específica. -> Armazenar na coluna 'cryptos' do df final

                #Cálculo do retorno:
                retorno_aa = np.sum(df_fin['retorno_dia_esperado']*pesos_all_shuffle)*365
                lista_retorno.append(retorno_aa) #-> Armazenar na coluna 'retorno' do df final

                #Cálculo do risco:
                portfolio_var = np.dot(pesos_all_shuffle, np.dot(matriz_covar, pesos_all_shuffle))
                portfolio_std_dev = np.sqrt(portfolio_var) * np.sqrt(365)
                lista_risco.append(portfolio_std_dev) #-> Armazenar na coluna 'risco' do df final

                #Sharpe Ratio
                sharpe_ratio = (retorno_aa - risk_free) / portfolio_std_dev
                lista_sharpe.append(sharpe_ratio) #-> Armazenar na coluna 'sharpe' do df final

                #Sortino Ratio
                downside_std_dev = np.nanstd(np.where(np.array((df_retornos[[lista_ativos][0]]*pesos_all_shuffle).T.sum())>0,np.nan,np.array((df_retornos[[lista_ativos][0]]*pesos_all_shuffle).T.sum())))* np.sqrt(365) #calculamos o desvio padrão dos retornos para o portfolio apenas nos casos onde o retorno foi negativo.
                sortino_ratio = (retorno_aa - target) / downside_std_dev
                lista_sortino.append(sortino_ratio) #-> Armazenar na coluna 'sortino' do df final

                #Roy's Safety First Ratio
                roys_ratio = (retorno_aa - target) / (portfolio_std_dev) #Incluí um fator no cálculo porque muitas vezes esse índice fica igualzinho ao Sharpe. Sharpe fica como Dinâmico e Roy's como Moderado.
                lista_roys.append(roys_ratio) #-> Armazenar na coluna 'roy_safety_first' do df final 


    df_portfolios['pesos_all'] = lista_p_all
    df_portfolios['cryptos'] = lista_cryptos     
    df_portfolios['retorno'] = lista_retorno
    df_portfolios['risco'] = lista_risco
    df_portfolios['sharpe'] = lista_sharpe
    df_portfolios['sortino'] = lista_sortino
    df_portfolios['roy_safety_first'] = lista_roys
    
    list_novos_pesos = []

    for index_pesos in range(0, len(df_portfolios['pesos_all'])):

        aux_pesos = []

        for index_peso in range(0, len(df_portfolios['pesos_all'][index_pesos])):

            if df_portfolios['pesos_all'][index_pesos][index_peso]!=0:

                aux_pesos.append(df_portfolios['pesos_all'][index_pesos][index_peso])

        list_novos_pesos.append(aux_pesos)
    
    
    
    df_portfolios['pesos'] = list_novos_pesos
    
    risco_min = df_portfolios.iloc[df_portfolios['risco'].astype(float).idxmin()]
    risco_min.name = "Conservador" #'risco_min'

    roy_max = df_portfolios.iloc[df_portfolios['roy_safety_first'].astype(float).idxmax()]
    roy_max.name = "Moderado" #'roy_max'

    sharpe_max = df_portfolios.iloc[df_portfolios['sharpe'].astype(float).idxmax()]
    sharpe_max.name = "Dinamico" #'sharpe_max'

    sortino_max = df_portfolios.iloc[df_portfolios['sortino'].astype(float).idxmax()]
    sortino_max.name = "Arrojado" #'sortino_max'

    retorno_max = df_portfolios.iloc[df_portfolios['retorno'].astype(float).idxmax()]
    retorno_max.name = "Agressivo" #'retorno_max'

    df_portfolios_escolhidos = pd.DataFrame([risco_min, roy_max, sharpe_max, sortino_max, retorno_max])

    df_portfolios_escolhidos.drop(columns=['retorno', 'risco', 'sharpe', 'sortino', 'roy_safety_first', 'pesos_all'],inplace=True)
    df_portfolios_escolhidos['indicador'] = ["risco_min", "roys_safety_max", "sharpe_max", "sortino_max", "retorno_max"]

    df_portfolios_escolhidos.to_csv("dataframes/df_portfolios_escolhidos.csv", index = True)

    return print(df_portfolios_escolhidos)


gera_portfolios(lista_ativos=ativos, df_retornos = df_retornos, lista_pesos=lista_pesos, n_componentes=n_componentes, n_iter=n_iter)
#df_portfolios = 


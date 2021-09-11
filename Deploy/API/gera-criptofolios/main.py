import pandas as pd
from os import read
from flask import Flask
from flask_restful import Resource, Api
import json



app = Flask(__name__)
api = Api(app)




class status (Resource):
    def get(self):
        try:
            return {'E ai?': 'API ta on, papai.'}
        except:
            return {'Vixi...': 'Deu ruim...'}


class get_portfolios(Resource):
    def get(self):
        
        df_portfolios_escolhidos = pd.read_csv("dataframes/df_portfolios_escolhidos.csv", index_col=0)
        df_portfolios_escolhidos.drop(columns = [])

        df_portfolios_escolhidos_json = df_portfolios_escolhidos.to_json(orient = "index")
        
        df_portfolios_escolhidos_json = json.loads(df_portfolios_escolhidos_json)
        
        #df_portfolios_escolhidos_json = json.dumps(df_portfolios_escolhidos_json, indent=0) 
        
        return df_portfolios_escolhidos_json


api.add_resource(status, '/')
api.add_resource(get_portfolios, '/portfolios')

if __name__ == '__main__':
    app.run()
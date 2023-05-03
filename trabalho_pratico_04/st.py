from functools import cache
import streamlit as st
import numpy as np
import pandas as pd
import math
import datetime 
from scipy import stats
from bokeh.plotting import figure

pd.set_option('display.float_format', lambda x: '%.8f' % x)

@st.cache_data
def retorno_lg(df, ticker):
    return np.log(df[ticker]/df[ticker].shift(1)).dropna().mean()

@st.cache_data
def retorno(df, ticker):
    return ((df[ticker]/df[ticker].shift(1)) -1).dropna().mean()
    #return df[ticker].pct_change().dropna().mean() * 100

@st.cache_data
def arithmetic_return(df, ticker):   
    return df[ticker].pct_change(1).dropna().mean()

@st.cache_data
def log_returns(df, ticker):
    return (np.log(df[ticker]) - np.log(df[ticker].shift(1))).dropna().mean()
    #np.log(SP500['Adj Close']) - np.log(SP500['Adj Close'].shift(1))

@st.cache_data
def difference(df, ticker):
    #SP500['Difference'] = abs(SP500['Arithmetic_Returns'] - SP500['Log_Returns'])

    art = arithmetic_return(df,ticker)
    lg = log_returns(df, ticker)

    return abs( art - lg  )

@st.cache_data
def load_data(filename):
    df = pd.read_excel(filename, sheet_name=[0,2,3], skiprows=1)
    df[1] = pd.read_excel(filename, sheet_name=[1])
    
    return df



# def betaAlpha(df):
#     beta,alpha,_,_,_=linregress(SPY['Daily Ret'], df['Daily Ret'])
#     return beta,alpha

# def retorno_acumulado(df, get_absolute=True):
#     start_price= df['Adj Close'].iloc[0]
#     end_price=df['Adj Close'].iloc[-1]
#     if get_absolute:
#         return end_price-start_price
#     else:
#         return ((end_price-start_price)/start_price)*100
    
    #Absolute is for the dollar gain
    #Typically we just want the normalized percent gain


#Carrega os dados da planilha
df = load_data('mod_4.xlsx')

st.markdown('# Trabalho prático n° 4')

portfolio_names = df[1][1].columns
option = st.selectbox('Selecione o portifólio', portfolio_names, index=0)
options = df[1][1][option]

cols = st.columns(2)
start_date = cols[0].date_input('Data inicial',value=datetime.date(2019, 12, 31))
end_date = cols[1].date_input('Data final',value=datetime.date(2023, 3, 31))


selected_stocks  = st.multiselect('Selecione os ativos para analisar', options, default=options)

print(selected_stocks)


prelast = df[2]
prelast['Data'] = pd.to_datetime(prelast['Data'], infer_datetime_format=True).dt.date



options = options.tolist()
options.insert(0, 'Data')

st.divider()
st.markdown('## Dados da planilha[prelast]')
origin = prelast.loc[(prelast['Data'] >= start_date) & (prelast['Data'] <= end_date)][options]    

origin



processed = pd.DataFrame(columns=['Ativo', 'Retorno.art', 'Retorno', 'Retorno_log','Alfa', 'Beta', 'Sharp', 'Sortino', 'Diff'], index=['Ativo'])

min_date = origin['Data'].min()
max_date = origin['Data'].max()

#origin[ (origin['Data'] >= min_date) & (origin['Data'] <= max_date)]['VALE3.SA']


for ticker in selected_stocks:
    if ticker != 'Data':
        dados = {'Ativo': ticker,
                'Retorno.art': arithmetic_return(origin, ticker),                  
                'Retorno': retorno(origin, ticker), 
                'Retorno_log': log_returns(origin, ticker) ,
                'Alfa':.0, 
                'Beta':.0, 
                'Sharp':.0, 
                'Sortino':0.0,
                'Diff': difference(origin, ticker)
                }

        #processed = processed.append(dados, ignore_index=True).dropna()
        processed = pd.concat([processed, pd.DataFrame(dados,index=[ticker])], ignore_index=True).dropna()

st.markdown('## Análises')

processed 


for ticker in selected_stocks:
    origin[ticker + '.LG'] = np.log(origin[ticker]) - np.log(origin[ticker].shift(1)).dropna()  
    st.line_chart( origin[['Data',ticker + '.LG']],x='Data', y=origin[[ticker + '.LG']][ticker + '.LG'].all(),use_container_width =True)
    st.divider()


import streamlit as st
import pandas as pd
import plotly.express as px
import streamviz

st.set_page_config(
    layout="wide",
    page_title="Pacheco Solar PP"
)
st.sidebar.header("Pacheco Solar PP", divider=True)

@st.cache_data
def load_data():
    # Load the CSV data into a DataFrame
    df = pd.read_csv('/Users/carloscarvalho/PycharmProjects/Usina_Solar_Dashboard/first_dashboard_db.csv')   # 'https://raw.githubusercontent.com/loscarlo/solar_pp_monitor/main/first_dashboard_db.csv'
    df['data'] = pd.to_datetime(df['data'], dayfirst=True)  # Convert the 'data' column to datetime
    df['month_year'] = df['data'].dt.to_period('M')  # Extract the month and year from the 'data' column
    df['valor_pago'] = df['valor_pago'].str.replace('R$', '').str.replace(',', '.').astype(float) # cleaning '%', 'R$',',' and converting to float
    df['custo_kWh'] = df['custo_kWh'].str.replace('R$', '').str.replace(',', '.').astype(float)
    df['economia'] = df['energia_inj'] * df['custo_kWh'] # creating column Economia
    df['inv_consumo'] = df['consumo'].apply(lambda x: -(x))

    return df

df = load_data()
st.session_state["df_usina"] = df

# Define month filter for month_year and unidade
filtro_mes = st.sidebar.selectbox('Período até:', df['month_year'].unique(),index=len(df['month_year'].unique())-1)
# filtro_unidade = st.sidebar.selectbox('unidade', df['unidade'].unique())

# Filtered DataFrame
df_filtrada_main = df[df['month_year'] <= filtro_mes]

# Define layout
col1, col2, col3 = st.columns([1.5,0.6,1])
col4, col5 = st.columns([0.5, 0.5])
col6, col7, col8 = st.columns([2,1,1])
# area chart for 'energia_gerada' vs 'consumo'
col1.subheader('Geração vs Consumo (kWh)', divider=True)
df_x = df_filtrada_main.groupby('data')[['energia_gerada','inv_consumo']].sum()
# df_x['delta']=df_x['energia_gerada'] + df_x['inv_consumo']
col1.bar_chart(df_x, color=["#4682B4", "#F08080"])

# Calculo do Geraçao média
geracao_avg = df_filtrada_main.groupby('month_year')['energia_gerada'].sum().mean()
geracao_delta =((geracao_avg / df_filtrada_main.groupby('month_year')['energia_gerada'].sum()[:-1].mean()) - 1)*100

# Calculo do consumo médio
consumo_avg = df_filtrada_main.groupby('month_year')['consumo'].sum().mean()
consumo_delta =((consumo_avg / df_filtrada_main.groupby('month_year')['consumo'].sum()[:-1].mean()) - 1)*100

# container Geracao e Consumo média

col2.write(' ')
col2.write(' ')
col2.write(' ')
col2.write(' ')
container_consumo = col2.container(border=True)
# col2.write("This is outside the container$$$$$")
# container.write("This is inside the container")
container_consumo.metric(label="Geração Média", value=f'{geracao_avg:.0f} kWh', delta=f'{geracao_delta:.1f} %', delta_color='normal')
container_consumo.metric(label="Consumo Médio", value=f'{consumo_avg:.0f} kWh', delta=f'{consumo_delta:.1f} %', delta_color='inverse')


# Pie chart for 'saldo_credito' vs unidade

col3.subheader('Consumo por Unidade', divider=True)
doughnut_fig = px.pie(df_filtrada_main, names='unidade', values='consumo', color='unidade',hole=0.90, width=500, height=350)
col3.plotly_chart(doughnut_fig)

# area chart for 'data' vs 'saldo_credito'
col4.subheader('Créditos de Energia', divider=True)
col4.area_chart(df_filtrada_main, x='data', y='saldo_credito',color='unidade')

# Calculo do estoque de creditos e delta mes

estoque_credito = df_filtrada_main['credito_mes'].sum()
# duracao_estoque = estoque_credito / consumo_avg
estoque_delta =((estoque_credito / df_filtrada_main['credito_mes'][:-1].sum()) - 1)*100


# container Estoque de Creditos
col5.write(' ')
col5.write(' ')
col5.write(' ')
col5.write(' ')
container_estoque = col5.container(border=True)
container_estoque.metric(label="Estoque de Energia", value=f'{estoque_credito:.0f} kWh', delta=f'{estoque_delta:.1f} %', delta_color='normal')
# container_estoque.write(' ')
# container_estoque.write(' ')
col5.write(' ')
col5.write(' ')
col5.write(' ')
col5.write(' ')
col5.write(' ')
col5.write(' ')
col5.write(' ')
col5.write(' ')
col5.write(' ')
col5.write(' ')
# col5.write(' ')
# col5.write(' ')
# col5.write(' ')
# col5.write(' ')

# # area chart for 'data' vs 'valor_pago'
# col4.bar_chart(df_filtrada_main, x='data', y='valor_pago',color='unidade')

# Calculo das medias mensais de despesa e economia com energia
gasto_avg = df_filtrada_main.groupby('month_year')['valor_pago'].sum().mean()
gasto_delta =((gasto_avg / df_filtrada_main.groupby('month_year')['valor_pago'].sum()[:-1].mean()) - 1)*100

economia_avg = df_filtrada_main.groupby('month_year')['economia'].sum().mean()
economia_delta =((economia_avg / df_filtrada_main.groupby('month_year')['economia'].sum()[:-1].mean()) - 1)*100

# container Despesa e economia média
col7.write(' ')
col7.write(' ')
col7.write(' ')
col7.write(' ')
container_financeiro = col7.container(border=True)
# col2.write("This is outside the container$$$$$")
# container.write("This is inside the container")
container_financeiro.metric(label="Economia Média", value=f'R$ {economia_avg:.2f}', delta=f'{economia_delta:.1f} %', delta_color='normal')
container_financeiro.metric(label="Despesa Média", value=f'R$ {gasto_avg:.2f}', delta=f'{gasto_delta:.1f} %', delta_color='inverse')

# area chart for 'data' vs 'economia'
col6.subheader('Economia & Despesa', divider=True)
col6.bar_chart(df_filtrada_main, x='data', y=['economia','valor_pago'])

# Calculando o % do investimento recuperado e o tempo pendente para o payback

invest_total = 75203.66
economia_total_acum = df_filtrada_main['economia'].sum()

pb_percent_global = (economia_total_acum / invest_total)
pb_status_global = invest_total - economia_total_acum
time_to_pb_global = pb_status_global / consumo_avg

# container payback
container_payback = col8.container(border=True)

#Pay Back Status gauge chart :
if time_to_pb_global > 0:
    with col8:
        st.subheader('Payback', divider=True)
        # st.write(' ')
        st.markdown(f"Faltam **:blue-background[{time_to_pb_global:.0f}]** *meses*.")
        streamviz.gauge(pb_percent_global,
                    # gTitle='Payback',
                    gMode='gauge+number',
                    gSize='SML',
                    sFix='%',
                    gTheme='#d6d6d6'
                    )
else:
    with col8:
        st.subheader('Payback', divider=True)
        # st.write(' ')
        st.markdown(f"Concluído há **:blue-background[{-(time_to_pb_global):.0f}]** *meses*.")
        streamviz.gauge(pb_percent_global,
                    # gTitle='Payback',
                    gMode='gauge+number',
                    gSize='SML',
                    sFix='%',
                    gTheme='#d6d6d6'
                    )
st.divider()
# row1 = st.columns(1)
# row2 = st.columns(1)
#
# for col in row1 + row2:
#     tile = col.container(height=120)
#     tile.metric(label="Temperature", value="70 °F", delta="1.2 °F")

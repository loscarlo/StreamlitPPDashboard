import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamviz

df = st.session_state["df_usina"]
st.sidebar.header("Pacheco Solar PP", divider=True)

# Define month filter for month_year and unidade

filtro_unidade = st.sidebar.selectbox('Unidade', df['unidade'].unique())
filtro_mes = st.sidebar.selectbox('Período até:', df['month_year'].unique(), index=len(df['month_year'].unique())-1)

# Filtered DataFrame
df_filtrada_uc = df[(df['month_year'] <= filtro_mes) & (df['unidade'] == filtro_unidade)]

# Define layout
col1, col2 = st.columns([0.5, 0.5])
col3, col4 = st.columns([0.5, 0.5])
col6, col7, col8 = st.columns([2,1,1])

# area chart for 'consumo' over time
col1.subheader('Consumo (kWh)', divider=True)
col1.bar_chart(df_filtrada_uc.groupby('data')[['consumo']].sum(), color="#F08080")

# Calculo do consumo médio
consumo_avg_uc = df_filtrada_uc.groupby('month_year')['consumo'].sum().mean()
consumo_delta_uc = ((consumo_avg_uc / df_filtrada_uc.groupby('month_year')['consumo'].sum()[:-1].mean()) - 1)*100

# container Consumo média
# col2.write(' ')
# col2.write(' ')
# col2.write(' ')
col2.write(' ')
col2.write(' ')
col2.write(' ')
col2.write(' ')
container_consumo_uc = col2.container(border=True)
container_consumo_uc.metric(label="Consumo Médio", value=f'{consumo_avg_uc:.0f} kWh', delta=f'{consumo_delta_uc:.1f} %', delta_color='inverse')
col2.write(' ')
col2.write(' ')
col2.write(' ')
col2.write(' ')
col2.write(' ')
col2.write(' ')
col2.write(' ')
col2.write(' ')
col2.write(' ')
col2.write(' ')

# area chart for 'data' vs 'saldo_credito'
col3.subheader('Créditos de Energia', divider=True)
col3.area_chart(df_filtrada_uc, x='data', y='saldo_credito')

# Calculo do estoque de creditos e delta mes
estoque_credito_uc = df_filtrada_uc['credito_mes'].sum()
estoque_delta_uc = ((estoque_credito_uc / df_filtrada_uc['credito_mes'][:-1].sum()) - 1)*100

# Calculo da duracao do estoque de creditos e delta mes
duracao_estoque_uc = estoque_credito_uc / consumo_avg_uc
duracao_estoque_uc_prior = df_filtrada_uc['credito_mes'][:-1].sum() / df_filtrada_uc.groupby('month_year')['consumo'].sum()[:-1].mean()
duracao_delta_uc = (duracao_estoque_uc / duracao_estoque_uc_prior - 1)*100

# container Estoque de Energia e duracao
col4.write(' ')
col4.write(' ')
col4.write(' ')
col4.write(' ')
# col4.write(' ')
# col4.write(' ')
# col4.write(' ')
# col4.write(' ')
# col4.write(' ')
container_estoque_uc = col4.container(border=True)
container_estoque_uc.metric(label="Estoque de Energia", value=f'{estoque_credito_uc:.0f} kWh', delta=f'{estoque_delta_uc:.1f} %', delta_color='normal')
container_estoque_uc.metric(label="Duração", value=f'{duracao_estoque_uc:.1f} Meses', delta=f'{duracao_delta_uc:.1f} %', delta_color='normal')
col4.write(' ')
col4.write(' ')
col4.write(' ')
col4.write(' ')
col4.write(' ')
col4.write(' ')

# area chart for 'economia' vs despesa mensal
col6.subheader('Economia & Despesa', divider=True)
col6.bar_chart(df_filtrada_uc, x='data', y=['economia', 'valor_pago'])

# Calculo das medias mensais de despesa e economia com energia
gasto_avg_uc = df_filtrada_uc.groupby('month_year')['valor_pago'].sum().mean()
gasto_delta_uc =((gasto_avg_uc / df_filtrada_uc.groupby('month_year')['valor_pago'].sum()[:-1].mean()) - 1)*100

economia_avg_uc = df_filtrada_uc.groupby('month_year')['economia'].sum().mean()
economia_delta_uc =((economia_avg_uc / df_filtrada_uc.groupby('month_year')['economia'].sum()[:-1].mean()) - 1)*100

# container Despesa e economia média
col7.write(' ')
col7.write(' ')
col7.write(' ')
col7.write(' ')
container_financeiro_uc = col7.container(border=True)
container_financeiro_uc.metric(label="Economia Média", value=f'R$ {economia_avg_uc:.2f}', delta=f'{economia_delta_uc:.1f} %', delta_color='normal')
container_financeiro_uc.metric(label="Despesa Média", value=f'R$ {gasto_avg_uc:.2f}', delta=f'{gasto_delta_uc:.1f} %', delta_color='inverse')

# Calculando o % do investimento recuperado e o tempo pendente para o payback

# correlacionando numero do medidor com propritario da unidade
invest_uc = None
# df['unidade'] == filtro_unidade
# uc_filtrada = df_filtrada_uc['unidade'][0]
if filtro_unidade == 'Valdione':
    invest_uc = 21928.08

elif filtro_unidade == 'Luciana':
    invest_uc = 17542.46

elif filtro_unidade == 'Ju&Rafael':
    invest_uc = 21928.08

elif filtro_unidade == 'Carlos':
    invest_uc = 13805.04

economia_total_acum = df_filtrada_uc['economia'].sum()

pb_percent_global = (economia_total_acum / invest_uc)
pb_status_global = invest_uc - economia_total_acum
time_to_pb_global = pb_status_global / consumo_avg_uc

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

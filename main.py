import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import json
import openai

# Configuración de la página
st.set_page_config(page_title="Dashboard Financiero", layout="wide")

# Cargar datos
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/edgroma04/TrabajoFinal/refs/heads/main/Datos_proyecto_corregido.csv"
    df = pd.read_csv(url)
    return df

df = load_data()

# Calcular ratios
df['Ratio de Liquidez Corriente'] = df['Current_Assets'] / df['Current_Liabilities']
df['Ratio de Deuda a Patrimonio'] = (df['Short_Term_Debt'] + df['Long_Term_Debt']) / df['Equity']
df['Cobertura de Gastos Financieros'] = df['Total_Revenue'] / df['Financial_Expenses']

# Título del dashboard
st.title("Dashboard Financiero")

# Sección 1: Gráfica de barras apiladas por sector
st.header("Análisis por Sector")

sector_metrics = df.groupby('Industry')[['Ratio de Liquidez Corriente', 'Ratio de Deuda a Patrimonio', 'Cobertura de Gastos Financieros']].mean().reset_index()

fig_sector = go.Figure(data=[
    go.Bar(name='Ratio de Liquidez Corriente', x=sector_metrics['Industry'], y=sector_metrics['Ratio de Liquidez Corriente']),
    go.Bar(name='Ratio de Deuda a Patrimonio', x=sector_metrics['Industry'], y=sector_metrics['Ratio de Deuda a Patrimonio']),
    go.Bar(name='Cobertura de Gastos Financieros', x=sector_metrics['Industry'], y=sector_metrics['Cobertura de Gastos Financieros'])
])

fig_sector.update_layout(barmode='stack', title='Ratios Financieros por Sector')
st.plotly_chart(fig_sector, use_container_width=True)

# Sección 2: Análisis Comparativo de Empresas
st.header("Análisis Comparativo de Empresas")

# Filtros interactivos
col1, col2, col3 = st.columns(3)
with col1:
    selected_companies = st.multiselect('Seleccionar Empresas', df['Company_ID'].unique())
with col2:
    selected_metric = st.selectbox('Seleccionar Métrica', ['Ratio de Liquidez Corriente', 'Ratio de Deuda a Patrimonio', 'Cobertura de Gastos Financieros'])
with col3:
    chart_type = st.radio('Tipo de Gráfico', ['Barras', 'Líneas','Pastel'])

# Filtrar datos
filtered_df = df[df['Company_ID'].isin(selected_companies)]

# Crear gráfico
if chart_type == 'Barras':
    fig_compare = px.bar(filtered_df, x='Company_ID', y=selected_metric, color='Industry', title=f'{selected_metric} por Empresa')
elif chart_type == 'Líneas':
    fig_compare = px.line(filtered_df, x='Company_ID', y=selected_metric, color='Industry', title=f'{selected_metric} por Empresa')
else:
    fig_compare = px.pie(filtered_df, values=selected_metric, color='Industry', title=f'{selected_metric} por Empresa')

st.plotly_chart(fig_compare, use_container_width=True)

# Sección 3: Integración de ChatGPT
st.header("Preguntas y Respuestas con ChatGPT")

# Configurar la API key de OpenAI
openai.api_key = "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"

def get_chatgpt_response(prompt):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",  # Use the full GPT-4 model
            messages=[
                {"role": "system", "content": "Eres un asistente financiero experto."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error al obtener respuesta de ChatGPT: {str(e)}"

user_question = st.text_input("Haz una pregunta sobre los datos financieros:")

if user_question:
    response = get_chatgpt_response(user_question)
    st.write("Respuesta de ChatGPT:")
    st.write(response)

# Ejemplos de preguntas
st.write("Ejemplos de preguntas que puedes hacer:")
st.write("- ¿Qué significa un ratio de liquidez menor a 1?")
st.write("- ¿Qué acciones puede tomar una empresa con un ratio de deuda elevado?")



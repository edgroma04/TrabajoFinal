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


# Instanciar el cliente de OpenAI
openai_api_key = st.secrets["OPENAI_API_KEY"]
client = openai.OpenAI(api_key=openai_api_key)

def obtener_respuesta(prompt):
  response = client.chat.completions.create(
      model="gpt-4o-mini",  # Ajusta el modelo según lo que necesites
      messages=[
          {"role": "system", "content": """
          Eres un financiero que trabaja para una aseguradora financiera, eres experto en el área de solvencia,
          entonces vas a responder todo desde la perspectiva de la aseguradora. Contesta siempre en español
          en un máximo de 50 palabras.
          """}, #Solo podemos personalizar la parte de content
          {"role": "user", "content": prompt}
      ]
  )
  output = response.choices[0].message.content
  return output

prompt_user= st.text_area("Haz una pregunta sobre los datos financieros: ")

# Obtener la respuesta del modelo
output_modelo = obtener_respuesta(prompt_user)

# Mostrar la respuesta del modelo
st.write(output_modelo)

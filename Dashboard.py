import streamlit as st
import pandas as pd
import requests
import plotly.express as px

# 1. Configuración de Seguridad y Credenciales
# En Streamlit Cloud, estas se configuran en "Secrets"
API_KEY = st.secrets["X_API_KEY"]
CLIENT_KEY = st.secrets["X_API_CLIENT_KEY"]
CLUB_ID = st.secrets["CLUB_IDENTIFICADOR"]

# 2. Función para obtener datos masivos (API de Reportes - pág 11)
def fetch_reporte_personas():
    url = f"https://consultas.ourclub.io/{CLUB_ID}/personas"
    headers = {
        "X-Api-Key": API_KEY,
        "X-Api-ClientKey": CLIENT_KEY,
        "Content-Type": "application/json"
    }
    
    # Payload simplificado para probar la conexión
    # Según pág 11, 'campos' es opcional. Si lo quitamos, trae los básicos por defecto.
    payload = {
        "csv": False,
        "socio_vigente": True  # Solo traemos los activos para reducir carga
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        
        # Si da error 500, imprimimos el texto del error para debuguear
        if response.status_code == 500:
            st.error(f"Error 500 del Servidor: {response.text}")
            return None
            
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Error de conexión: {e}")
        return None

# 3. Diseño del Dashboard Web
st.set_page_config(page_title="OurClub Decision Support", layout="wide")

st.title("📊 Panel de Control y Toma de Decisiones")
st.markdown("---")

# Carga de datos
data = fetch_reporte_personas()

if data and "items" in data:
    df = pd.DataFrame(data["items"])
    
    # --- FILTROS EN BARRA LATERAL ---
    st.sidebar.header("Filtros")
    categoria = st.sidebar.multiselect("Categoría de Socio", options=df["categoriasocio"].unique())
    
    if categoria:
        df = df[df["categoriasocio"].isin(categoria)]

    # --- MÉTRICAS DE ALTO NIVEL ---
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Socios", len(df))
    with col2:
        # Filtramos por el campo booleano según pág 14 del manual
        deudores = df[df["tieneDeuda"] == True].shape[0]
        st.metric("Socios con Deuda", deudores, delta=f"{(deudores/len(df)*100):.1f}%", delta_color="inverse")
    with col3:
        vigentes = df[df["socio_vigente"] == True].shape[0]
        st.metric("Socios Activos", vigentes)
    with col4:
        st.metric("Tasa de Cobrabilidad", f"{100 - (deudores/len(df)*100):.1f}%")

    st.markdown("---")

    # --- GRÁFICOS INTERACTIVOS ---
    c1, c2 = st.columns(2)
    
    with c1:
        st.subheader("Socios por Categoría")
        fig_cat = px.pie(df, names="categoriasocio", hole=0.4)
        st.plotly_chart(fig_cat, use_container_width=True)
        
    with c2:
        st.subheader("Estado de Pago")
        fig_deuda = px.bar(df["tieneDeuda"].value_counts(), labels={'value':'Cantidad', 'index':'Tiene Deuda'})
        st.plotly_chart(fig_deuda, use_container_width=True)

    # --- TABLA DE DATOS ---
    with st.expander("Ver detalle de registros encontrados"):
        st.dataframe(df)

else:

    st.warning("No se pudieron cargar los datos. Verifica tus credenciales.")

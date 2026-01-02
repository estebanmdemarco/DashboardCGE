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
    
    # Payload minimalista: solo lo indispensable para que no explote el servidor
    payload = {
        "csv": False,
        "socio_vigente": True
    }
    
    try:
        # Usamos POST como en tu Postman
        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            # Esto nos dirá qué dice el servidor exactamente antes del error 500
            st.error(f"Error {response.status_code}: {response.text}")
            return None
            
    except Exception as e:
        st.error(f"Error de conexión: {e}")
        return None

# --- Lógica de procesamiento ---
data = fetch_reporte_personas()

if data:
    # La API de reportes suele devolver un objeto con una propiedad 'items'
    if isinstance(data, dict) and "items" in data:
        df = pd.DataFrame(data["items"])
    else:
        # Si por alguna razón devuelve la lista directa
        df = pd.DataFrame(data)
    
    if not df.empty:
        st.success(f"¡Conexión exitosa! Se encontraron {len(df)} socios.")
        
        # Mostrar métricas básicas para confirmar
        c1, c2 = st.columns(2)
        c1.metric("Total Socios", len(df))
        if "tieneDeuda" in df.columns:
            deuda_count = df[df["tieneDeuda"] == True].shape[0]
            c2.metric("Con Deuda", deuda_count)
            
        st.write("### Vista previa de datos")
        st.dataframe(df.head(10))
    else:
        st.warning("No se encontraron registros con los filtros aplicados.")

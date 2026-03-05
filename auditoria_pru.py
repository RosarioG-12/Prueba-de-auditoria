import streamlit as st
import pandas as pd
from datetime import datetime
import os

# Configuración de página
st.set_page_config(page_title="Control de Flota Mensual", layout="wide")

# --- FUNCIONES DE BASE DE DATOS ---
DB_FILE = "datos_combustible.csv"

def cargar_datos():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    return pd.DataFrame(columns=["Fecha", "Mes", "Tecnico", "Vehiculo", "KM_Total", "KM_Laboral"])

def guardar_dato(nueva_fila):
    df = cargar_datos()
    df = pd.concat([df, pd.DataFrame([nueva_fila])], ignore_index=True)
    df.to_csv(DB_FILE, index=False)

# --- INTERFAZ ---
st.title("⛽ Auditoría de Técnicos")

# Sidebar para Configuración General
st.sidebar.header("⚙️ Configuración")
mes_seleccionado = st.sidebar.selectbox("Selecciona el Mes a Consultar", 
    ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"])
precio_gas = st.sidebar.number_input("Precio Gasolina ($)", value=24.5, step=0.1)

# Pestañas: Registro vs Reporte
tab1, tab2 = st.tabs(["📝 Registro Diario", "📊 Reporte Mensual"])

with tab1:
    st.header(f"Registrar datos para {mes_seleccionado}")
    with st.form("registro_diario"):
        col1, col2 = st.columns(2)
        with col1:
            fecha = st.date_input("Fecha del recorrido", datetime.now())
            tecnico = st.text_input("Nombre del Técnico")
            vehiculo = st.selectbox("Vehículo", ["Chevy", "Vocho"])
        with col2:
            km_t = st.number_input("KM Total del día (GPS)", min_value=0.0)
            km_l = st.number_input("KM Laboral del día (GPS)", min_value=0.0)
            
        btn_guardar = st.form_submit_button("Guardar Registro del Día")
        
        if btn_guardar:
            nueva_entrada = {
                "Fecha": str(fecha),
                "Mes": mes_seleccionado,
                "Tecnico": tecnico,
                "Vehiculo": vehiculo,
                "KM_Total": km_t,
                "KM_Laboral": km_l
            }
            guardar_dato(nueva_entrada)
            st.success("✅ Datos guardados correctamente.")

with tab2:
    st.header(f"Resultados Generales - {mes_seleccionado}")
    df_historico = cargar_datos()
    
    # Filtrar por el mes seleccionado
    df_mes = df_historico[df_historico["Mes"] == mes_seleccionado]
    
    if not df_mes.empty:
        # Agrupar por Técnico y Vehículo
        resumen = df_mes.groupby(['Tecnico', 'Vehiculo']).agg({
            'KM_Total': 'sum',
            'KM_Laboral': 'sum'
        }).reset_index()
        
        # Aplicar lógica de rendimiento
        resumen['Rendimiento'] = resumen['Vehiculo'].apply(lambda x: 12.5 if x == "Chevy" else 9.0)
        resumen['KM_Extra'] = resumen['KM_Total'] - resumen['KM_Laboral']
        resumen['Litros_Extra'] = resumen['KM_Extra'] / resumen['Rendimiento']
        resumen['Gasto_Extra_$'] = resumen['Litros_Extra'] * precio_gas
        
        # Mostrar métricas totales del mes
        total_recuperar = resumen['Gasto_Extra_$'].sum()
        st.metric("Total a Recuperar en el Mes", f"${total_recuperar:,.2f}")
        
        # Tabla detallada
        st.subheader("Desglose por Técnico")
        st.dataframe(resumen.style.format({
            'KM_Total': '{:.1f}', 'KM_Laboral': '{:.1f}', 
            'KM_Extra': '{:.1f}', 'Gasto_Extra_$': '${:,.2f}'
        }))
        
        # Opción para borrar datos si es necesario
        if st.button("Limpiar todos los datos (Reiniciar)"):
            if os.path.exists(DB_FILE):
                os.remove(DB_FILE)
                st.rerun()
    else:
        st.info(f"No hay datos registrados para {mes_seleccionado}.")
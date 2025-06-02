import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os

# --- Configuración Inicial ---
DATA_FILE = 'planner_data.csv' # Archivo donde se guardarán los datos

# Cargar datos existentes o crear un DataFrame vacío
if os.path.exists(DATA_FILE):
    df = pd.read_csv(DATA_FILE)
    # Asegurarse de que la columna 'Fecha' sea tipo datetime, manejando errores si los hay
    df['Fecha'] = pd.to_datetime(df['Fecha'], errors='coerce')
    # Eliminar filas con fechas no válidas si 'coerce' falla (por ejemplo, si el archivo está corrupto)
    df.dropna(subset=['Fecha'], inplace=True)
else:
    # Definir columnas para el DataFrame
    columns = [
        'Fecha', 'Entrenamiento', 'Comida Saludable', 'Agua', 'Horas Extra',
        'Otorrino (vos)', 'Otorrino (Guille)', 'Dentista (vos)', 'Dentista (Guille)',
        'Neumonólogo (Guille)', 'Brackets (averiguar - ambos)', 'Rinoseptoplastia (consulta)',
        'App ingresos y salidas', 'App progreso personal'
    ]
    df = pd.DataFrame(columns=columns)
    # Establecer el tipo de dato para 'Fecha' a datetime en un DataFrame vacío
    df['Fecha'] = pd.to_datetime(df['Fecha']) # <-- Añadido para asegurar el tipo
    
    # Inicializar columnas booleanas a False
    for col in ['Entrenamiento', 'Comida Saludable', 'Agua',
                'Otorrino (vos)', 'Otorrino (Guille)', 'Dentista (vos)', 'Dentista (Guille)',
                'Neumonólogo (Guille)', 'Brackets (averiguar - ambos)', 'Rinoseptoplastia (consulta)']:
        df[col] = df[col].astype(bool)
    # Inicializar columnas de proyectos a 'Pendiente'
    for col in ['App ingresos y salidas', 'App progreso personal']:
        df[col] = 'Pendiente'
    df['Horas Extra'] = 0.0

# Función para guardar los datos
def save_data(dataframe):
    dataframe.to_csv(DATA_FILE, index=False)

# --- Título de la Aplicación ---
st.title("🗓️ Mi Planner Mensual Interactivo")

# --- Pestañas de Navegación ---
tab1, tab2, tab3, tab4 = st.tabs(["Seguimiento Diario", "Salud / Turnos", "Proyectos", "Resumen y Bonificación"])

# --- Pestaña 1: Seguimiento Diario ---
with tab1:
    st.header("Seguimiento Diario")

    today = datetime.now().date()
    # Asegurarse de que tengamos una fila para hoy
    if today not in df['Fecha'].dt.date.values:
        new_row = pd.DataFrame([{
            'Fecha': today,
            'Entrenamiento': False,
            'Comida Saludable': False,
            'Agua': False,
            'Horas Extra': 0.0,
            'Otorrino (vos)': False, 'Otorrino (Guille)': False, 'Dentista (vos)': False, 'Dentista (Guille)': False,
            'Neumonólogo (Guille)': False, 'Brackets (averiguar - ambos)': False, 'Rinoseptoplastia (consulta)': False,
            'App ingresos y salidas': 'Pendiente', 'App progreso personal': 'Pendiente'
        }])
        # Concatenar la nueva fila y ordenar por fecha
        df = pd.concat([df, new_row], ignore_index=True).sort_values(by='Fecha').reset_index(drop=True)
        save_data(df) # Guardar inmediatamente la nueva fila

    # Obtener la fila de hoy
    row_index = df[df['Fecha'].dt.date == today].index[0]

    st.write(f"### Hoy es: {today.strftime('%d/%m/%Y')}")

    # Checkboxes para objetivos diarios
    entrenamiento = st.checkbox("✅ Entrenamiento", value=df.loc[row_index, 'Entrenamiento'], key='entrenamiento_daily')
    comida_saludable = st.checkbox("✅ Comida Saludable", value=df.loc[row_index, 'Comida Saludable'], key='comida_daily')
    agua = st.checkbox("✅ Agua", value=df.loc[row_index, 'Agua'], key='agua_daily')

    df.loc[row_index, 'Entrenamiento'] = entrenamiento
    df.loc[row_index, 'Comida Saludable'] = comida_saludable
    df.loc[row_index, 'Agua'] = agua

    # Horas extra
    horas_extra = st.number_input("Horas Extra:", value=float(df.loc[row_index, 'Horas Extra']), min_value=0.0, step=0.5, key='horas_extra_daily')
    df.loc[row_index, 'Horas Extra'] = horas_extra

    st.write("---")
    st.subheader("Registro Diario (últimos 7 días)")
    # Mostrar el registro de los últimos 7 días para referencia
    df_display = df.tail(7)[['Fecha', 'Entrenamiento', 'Comida Saludable', 'Agua', 'Horas Extra']].copy()
    df_display['Fecha'] = df_display['Fecha'].dt.strftime('%d/%m/%Y')
    st.dataframe(df_display.set_index('Fecha'))

    # Guardar cambios al final de la interacción diaria
    save_data(df)


# --- Pestaña 2: Salud / Turnos ---
with tab2:
    st.header("Salud / Turnos")

    st.subheader("Marcar Turnos Completados:")

    # Objetivos de Salud
    salud_objetivos = {
        'Otorrino (vos)': 'Otorrino (vos)',
        'Otorrino (Guille)': 'Otorrino (Guille)',
        'Dentista (vos)': 'Dentista (vos)',
        'Dentista (Guille)': 'Dentista (Guille)',
        'Neumonólogo (Guille)': 'Neumonólogo (Guille)',
        'Brackets (averiguar - ambos)': 'Brackets (averiguar - ambos)',
        'Rinoseptoplastia (consulta)': 'Rinoseptoplastia (consulta)'
    }

    # Asumimos que los objetivos de salud se marcan una vez al mes
    # Usaremos el último registro disponible para el estado
    # Si quieres que sean por día, la lógica cambia, pero para "turnos" una vez al mes tiene más sentido

    st.write("Marque los turnos que ya se han completado este mes:")
    # Para simplificar y asegurar que se guarde el estado del mes actual,
    # actualizaremos el estado en la fila más reciente (asumiendo que es la del mes actual)
    if not df.empty:
        last_row_index = df.index[-1] # Última fila del DataFrame
        for key, display_text in salud_objetivos.items():
            current_value = df.loc[last_row_index, key] if key in df.columns else False
            new_value = st.checkbox(f"✅ {display_text}", value=current_value, key=f'salud_{key}')
            df.loc[last_row_index, key] = new_value
    else:
        st.info("Aún no hay datos. Registra algo en 'Seguimiento Diario' para que aparezcan las opciones de salud.")

    save_data(df) # Guardar cambios en salud

# --- Pestaña 3: Proyectos ---
with tab3:
    st.header("Proyectos")

    st.subheader("Estado de Proyectos:")

    proyectos = {
        'App ingresos y salidas': 'App ingresos y salidas',
        'App progreso personal': 'App progreso personal'
    }

    # También actualizamos el estado en la última fila del DataFrame
    if not df.empty:
        last_row_index = df.index[-1]
        for key, display_text in proyectos.items():
            current_value = df.loc[last_row_index, key] if key in df.columns else 'Pendiente'
            option = st.selectbox(f"**{display_text}**", ['Pendiente', 'En Curso', 'Completado ✅'], index=['Pendiente', 'En Curso', 'Completado ✅'].index(current_value), key=f'proyecto_{key}')
            df.loc[last_row_index, key] = option
    else:
        st.info("Aún no hay datos. Registra algo en 'Seguimiento Diario' para que aparezcan las opciones de proyectos.")

    save_data(df) # Guardar cambios en proyectos

# --- Pestaña 4: Resumen y Bonificación ---
with tab4:
    st.header("Resumen y Bonificación")

    st.subheader("Progreso General del Mes:")

    # Filtrar datos solo para el mes actual
    current_month_start = datetime(today.year, today.month, 1).date()
    df_current_month = df[df['Fecha'].dt.date >= current_month_start].copy()

    if not df_current_month.empty:
        # Calcular objetivos diarios
        total_days_logged = len(df_current_month)
        if total_days_logged > 0:
            avg_entrenamiento = df_current_month['Entrenamiento'].mean()
            avg_comida = df_current_month['Comida Saludable'].mean()
            avg_agua = df_current_month['Agua'].mean()
        else:
            avg_entrenamiento, avg_comida, avg_agua = 0, 0, 0

        # Horas extra acumuladas
        total_horas_extra = df_current_month['Horas Extra'].sum()

        # Objetivos de salud (contamos los TRUEs del último registro del mes)
        # Esto asume que el estado de salud se marca una vez y es válido para el mes
        salud_completados = 0
        if not df_current_month.empty:
            last_month_row = df_current_month.iloc[-1]
            for obj in salud_objetivos.keys():
                if last_month_row[obj]:
                    salud_completados += 1
        total_salud_objetivos = len(salud_objetivos)

        # Proyectos (contamos los 'Completado ✅' del último registro del mes)
        proyectos_completados = 0
        if not df_current_month.empty:
            last_month_row = df_current_month.iloc[-1]
            for proj in proyectos.keys():
                if last_month_row[proj] == 'Completado ✅':
                    proyectos_completados += 1
        total_proyectos = len(proyectos)

        # --- Cálculo del Porcentaje de Progreso ---
        # Asignamos un peso a cada categoría
        # Puedes ajustar estos pesos según lo que consideres más importante
        peso_diario = 0.4 # Entrenamiento, Comida, Agua
        peso_horas_extra = 0.2
        peso_salud = 0.2
        peso_proyectos = 0.2

        # Progreso diario: promedio de los 3 objetivos diarios
        progreso_diario = (avg_entrenamiento + avg_comida + avg_agua) / 3 if total_days_logged > 0 else 0

        # Progreso horas extra: Asumiendo 20 horas por quincena, 40 horas al mes como objetivo
        objetivo_horas_extra_mensual = 40 # Puedes ajustar este objetivo
        progreso_horas_extra = min(total_horas_extra / objetivo_horas_extra_mensual, 1.0) if objetivo_horas_extra_mensual > 0 else 0

        # Progreso salud
        progreso_salud = salud_completados / total_salud_objetivos if total_salud_objetivos > 0 else 0

        # Progreso proyectos
        progreso_proyectos = proyectos_completados / total_proyectos if total_proyectos > 0 else 0

        # Progreso total ponderado
        overall_progress = (progreso_diario * peso_diario) + \
                           (progreso_horas_extra * peso_horas_extra) + \
                           (progreso_salud * peso_salud) + \
                           (progreso_proyectos * peso_proyectos)

        st.metric(label="Progreso General del Mes", value=f"{overall_progress:.1%}")
        st.progress(overall_progress)

        st.write("---")
        st.subheader("Detalle del Progreso:")
        st.write(f"- **Objetivos Diarios (Entrenamiento, Comida, Agua):** {progreso_diario:.1%}")
        st.write(f"- **Horas Extra Acumuladas:** {total_horas_extra} hrs (Meta: {objetivo_horas_extra_mensual} hrs) - Progreso: {progreso_horas_extra:.1%}")
        st.write(f"- **Objetivos de Salud Completados:** {salud_completados} de {total_salud_objetivos} - Progreso: {progreso_salud:.1%}")
        st.write(f"- **Proyectos Completados:** {proyectos_completados} de {total_proyectos} - Progreso: {progreso_proyectos:.1%}")

        st.write("---")
        st.subheader("Bonificación:")
        if overall_progress >= 0.85:
            st.success("¡🎉 Felicidades! Has cumplido con al menos el 85% de tus objetivos.")
            st.write("**Recompensa desbloqueada:** ¡Felicitaciones por tu esfuerzo! Aquí puedes escribir la recompensa que te diste.")
            st.markdown("---")
            st.balloons() # Pequeña animación de celebración
        else:
            st.info("Sigue trabajando. ¡Estás cerca de alcanzar tus metas!")
            st.write(f"Necesitas un {0.85 - overall_progress:.1%} más para la bonificación del 85%.")

    else:
        st.info("Aún no hay datos para calcular el progreso. Empieza a registrar tus actividades.")

# Guardar los datos al final de la ejecución del script (Streamlit recarga el script en cada interacción)
save_data(df)
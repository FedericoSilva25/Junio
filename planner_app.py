import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os

# --- Configuración Inicial ---
DATA_FILE = 'planner_data.csv' # Archivo donde se guardarán los datos

# --- Definición de columnas de la aplicación ---
# Define todas las columnas esperadas, con sus tipos de datos iniciales
APP_COLUMNS = {
    'Fecha': 'date',
    'Entrenamiento_Hecho': 'bool', # Checkbox para entrenamiento
    'Entrenamiento_Minutos': 'float', # Minutos de entrenamiento
    'Comida Saludable': 'bool',
    'Agua_Litros': 'float', # Litros de agua
    'Horas Extra': 'float',
    'Meditacion_Minutos': 'float', # Nuevo: Meditación
    'Lectura_Paginas': 'int', # Nuevo: Lectura

    # Objetivos de Salud (siguen siendo booleanos para el último registro del mes)
    'Otorrino (vos)': 'bool',
    'Otorrino (Guille)': 'bool',
    'Dentista (vos)': 'bool',
    'Dentista (Guille)': 'bool',
    'Neumonólogo (Guille)': 'bool',
    'Brackets (averiguar - ambos)': 'bool',
    'Rinoseptoplastia (consulta)': 'bool',

    # Proyectos (estados)
    'App ingresos y salidas': 'str',
    'App progreso personal': 'str'
}


# Cargar datos existentes o crear un DataFrame vacío
if os.path.exists(DATA_FILE):
    df = pd.read_csv(DATA_FILE)
    # Convertir 'Fecha' a datetime y luego a formato de fecha (naive) para consistencia
    df['Fecha'] = pd.to_datetime(df['Fecha'], errors='coerce').dt.date
    df.dropna(subset=['Fecha'], inplace=True) # Eliminar filas con fechas no válidas
    
    # Asegurar que todas las columnas esperadas existan y tengan el tipo correcto
    for col, dtype in APP_COLUMNS.items():
        if col not in df.columns:
            # Si la columna no existe, añadirla con el tipo de dato inicial
            if dtype == 'bool':
                df[col] = False
            elif dtype == 'float':
                df[col] = 0.0
            elif dtype == 'int':
                df[col] = 0
            elif dtype == 'str':
                if col in ['App ingresos y salidas', 'App progreso personal']:
                    df[col] = 'Pendiente'
                else:
                    df[col] = '' # Default vacío para otros strings
        else:
            # Intentar convertir al tipo correcto si ya existe la columna
            if dtype == 'bool':
                df[col] = df[col].fillna(False).astype(bool)
            elif dtype == 'float':
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0.0)
            elif dtype == 'int':
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
            # 'str' y 'date' ya se manejan arriba
            
else:
    # Crear un DataFrame vacío con las columnas y tipos de datos definidos
    df = pd.DataFrame({col: pd.Series(dtype=dt) for col, dt in APP_COLUMNS.items()})
    # Ajustar valores iniciales para booleanos y strings por defecto
    for col, dtype in APP_COLUMNS.items():
        if dtype == 'bool':
            df[col] = False
        elif dtype == 'float':
            df[col] = 0.0
        elif dtype == 'int':
            df[col] = 0
        elif dtype == 'str':
            if col in ['App ingresos y salidas', 'App progreso personal']:
                df[col] = 'Pendiente'
            else:
                df[col] = ''


# Función para guardar los datos
def save_data(dataframe):
    temp_df = dataframe.copy()
    # Asegurarse de que la columna 'Fecha' sea un string compatible antes de guardar
    if 'Fecha' in temp_df.columns:
        temp_df['Fecha'] = temp_df['Fecha'].astype(str)
    temp_df.to_csv(DATA_FILE, index=False)


# --- Título de la Aplicación ---
st.title("🗓️ Mi Planner Mensual Interactivo")

# --- Pestañas de Navegación ---
tab1, tab2, tab3, tab4, tab5 = st.tabs(["Seguimiento Diario", "Salud / Turnos", "Proyectos", "Resumen y Bonificación", "Mi Guía Espiritual"])

# --- Pestaña 1: Seguimiento Diario ---
with tab1:
    st.header("Seguimiento Diario")

    today = datetime.now().date() # Esto es un objeto date, naive

    # Asegurarse de que tengamos una fila para hoy
    if today not in df['Fecha'].values:
        new_row_data = {col: APP_COLUMNS[col] for col in APP_COLUMNS.keys()} # Iniciar con valores por defecto del diccionario
        
        # Ajustar los valores por defecto específicos para la nueva fila
        new_row_data['Fecha'] = today
        for col, dtype in APP_COLUMNS.items():
            if dtype == 'bool' and col != 'Fecha': # Excluir 'Fecha' que ya se seteó
                new_row_data[col] = False
            elif dtype == 'float':
                new_row_data[col] = 0.0
            elif dtype == 'int':
                new_row_data[col] = 0
            elif dtype == 'str':
                 if col in ['App ingresos y salidas', 'App progreso personal']:
                    new_row_data[col] = 'Pendiente'
                 else:
                    new_row_data[col] = ''
        
        new_row = pd.DataFrame([new_row_data])
        
        # Asegurarse de que el tipo de la columna 'Fecha' sea el mismo antes de concatenar
        # Convertir a object si es necesario para evitar TypeError si el DataFrame base es de tipo mixto
        # Sin embargo, con los cambios anteriores, 'Fecha' debería ser 'object' (containing date objects)
        # o 'datetime64[ns]' (if pd.to_datetime makes it so). Aquí lo tenemos como date objects.
        
        df = pd.concat([df, new_row], ignore_index=True).sort_values(by='Fecha', ascending=True).reset_index(drop=True)
        save_data(df) # Guardar inmediatamente la nueva fila

    # Obtener la fila de hoy
    row_index = df[df['Fecha'] == today].index[0]

    st.write(f"### Hoy es: {today.strftime('%d/%m/%Y')}")

    # Checkboxes y campos para objetivos diarios
    entrenamiento_hecho = st.checkbox("✅ Entrenamiento Hecho", value=df.loc[row_index, 'Entrenamiento_Hecho'], key='entrenamiento_checkbox')
    df.loc[row_index, 'Entrenamiento_Hecho'] = entrenamiento_hecho

    entrenamiento_minutos = st.number_input("Minutos de Entrenamiento:", value=float(df.loc[row_index, 'Entrenamiento_Minutos']), min_value=0.0, step=15.0, key='entrenamiento_min')
    df.loc[row_index, 'Entrenamiento_Minutos'] = entrenamiento_minutos

    comida_saludable = st.checkbox("✅ Comida Saludable", value=df.loc[row_index, 'Comida Saludable'], key='comida_daily')
    df.loc[row_index, 'Comida Saludable'] = comida_saludable

    agua_litros = st.number_input("Litros de Agua:", value=float(df.loc[row_index, 'Agua_Litros']), min_value=0.0, step=0.5, key='agua_litros')
    df.loc[row_index, 'Agua_Litros'] = agua_litros

    horas_extra = st.number_input("Horas Extra:", value=float(df.loc[row_index, 'Horas Extra']), min_value=0.0, step=0.5, key='horas_extra_daily')
    df.loc[row_index, 'Horas Extra'] = horas_extra
    
    meditacion_minutos = st.number_input("Minutos de Meditación:", value=float(df.loc[row_index, 'Meditacion_Minutos']), min_value=0.0, step=5.0, key='meditacion_min')
    df.loc[row_index, 'Meditacion_Minutos'] = meditacion_minutos

    lectura_paginas = st.number_input("Páginas Leídas:", value=int(df.loc[row_index, 'Lectura_Paginas']), min_value=0, step=10, key='lectura_paginas')
    df.loc[row_index, 'Lectura_Paginas'] = lectura_paginas


    st.write("---")
    st.subheader("Registro Diario (últimos 7 días)")
    # Mostrar el registro de los últimos 7 días para referencia
    # Asegurarse de que solo se muestren las columnas relevantes para el seguimiento diario
    daily_display_cols = [
        'Fecha', 'Entrenamiento_Hecho', 'Entrenamiento_Minutos', 'Comida Saludable',
        'Agua_Litros', 'Horas Extra', 'Meditacion_Minutos', 'Lectura_Paginas'
    ]
    df_display = df.tail(7)[daily_display_cols].copy()
    df_display['Fecha'] = df_display['Fecha'].astype(str) # Mostrar como string para evitar problemas de formato
    st.dataframe(df_display.set_index('Fecha'))

    save_data(df) # Guardar cambios al final de la interacción diaria


# --- Pestaña 2: Salud / Turnos ---
with tab2:
    st.header("Salud / Turnos")

    st.subheader("Marcar Turnos Completados:")

    salud_objetivos = {
        'Otorrino (vos)': 'Otorrino (vos)',
        'Otorrino (Guille)': 'Otorrino (Guille)',
        'Dentista (vos)': 'Dentista (vos)',
        'Dentista (Guille)': 'Dentista (Guille)',
        'Neumonólogo (Guille)': 'Neumonólogo (Guille)',
        'Brackets (averiguar - ambos)': 'Brackets (averiguar - ambos)',
        'Rinoseptoplastia (consulta)': 'Rinoseptoplastia (consulta)'
    }

    st.write("Marque los turnos que ya se han completado este mes:")
    if not df.empty:
        current_day_row_index = df[df['Fecha'] == today].index[0] # Usar today (objeto date)
        
        for key, display_text in salud_objetivos.items():
            current_value = df.loc[current_day_row_index, key] if key in df.columns else False
            new_value = st.checkbox(f"✅ {display_text}", value=current_value, key=f'salud_{key}')
            df.loc[current_day_row_index, key] = new_value
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

    if not df.empty:
        current_day_row_index = df[df['Fecha'] == today].index[0] # Usar today (objeto date)
        for key, display_text in proyectos.items():
            current_value = df.loc[current_day_row_index, key] if key in df.columns else 'Pendiente'
            option = st.selectbox(f"**{display_text}**", ['Pendiente', 'En Curso', 'Completado ✅'], index=['Pendiente', 'En Curso', 'Completado ✅'].index(current_value), key=f'proyecto_{key}')
            df.loc[current_day_row_index, key] = option
    else:
        st.info("Aún no hay datos. Registra algo en 'Seguimiento Diario' para que aparezcan las opciones de proyectos.")

    save_data(df) # Guardar cambios en proyectos

# --- Pestaña 4: Resumen y Bonificación ---
with tab4:
    st.header("Resumen y Bonificación")

    st.subheader("Progreso General del Mes:")

    current_month_start = datetime(today.year, today.month, 1).date() 
    df_current_month = df[df['Fecha'] >= current_month_start].copy()

    if not df_current_month.empty:
        # --- Cálculo de objetivos diarios (ahora con promedios y sumas) ---
        total_days_logged = len(df_current_month)
        
        # Entrenamiento: Contar días "hechos" y sumar minutos
        entrenamiento_dias_hechos = df_current_month['Entrenamiento_Hecho'].sum()
        entrenamiento_minutos_total = df_current_month['Entrenamiento_Minutos'].sum()

        avg_comida = df_current_month['Comida Saludable'].mean() # Sigue siendo promedio de checkboxes
        avg_agua_litros = df_current_month['Agua_Litros'].mean() # Promedio de litros de agua
        avg_meditacion_minutos = df_current_month['Meditacion_Minutos'].mean() # Promedio de minutos de meditación
        total_lectura_paginas = df_current_month['Lectura_Paginas'].sum() # Total de páginas leídas

        # Horas extra acumuladas
        total_horas_extra = df_current_month['Horas Extra'].sum()

        # Objetivos de salud (contamos los TRUEs del último registro del mes)
        salud_completados = 0
        if not df_current_month.empty:
            last_month_row = df_current_month[df_current_month['Fecha'] == today].iloc[0] if today in df_current_month['Fecha'].values else df_current_month.iloc[-1]
            for obj in salud_objetivos.keys():
                if last_month_row[obj]:
                    salud_completados += 1
        total_salud_objetivos = len(salud_objetivos)

        # Proyectos (contamos los 'Completado ✅' del último registro del mes)
        proyectos_completados = 0
        if not df_current_month.empty:
            last_month_row = df_current_month[df_current_month['Fecha'] == today].iloc[0] if today in df_current_month['Fecha'].values else df_current_month.iloc[-1]
            for proj in proyectos.keys():
                if last_month_row[proj] == 'Completado ✅':
                    proyectos_completados += 1
        total_proyectos = len(proyectos)

        # --- Cálculo del Porcentaje de Progreso ---
        # Definimos metas para los nuevos objetivos
        meta_entrenamiento_minutos_mensual = 15 * 60 # 15 entrenamientos de 60 minutos (900 minutos)
        meta_meditacion_minutos_mensual = 30 * 10 # 30 días x 10 minutos (300 minutos)
        meta_lectura_paginas_mensual = 30 * 10 # 30 días x 10 páginas (300 páginas)
        objetivo_horas_extra_mensual = 40 # 20 horas por quincena -> 40 horas al mes

        # Progreso de cada categoría
        progreso_entrenamiento = min(entrenamiento_minutos_total / meta_entrenamiento_minutos_mensual, 1.0) if meta_entrenamiento_minutos_mensual > 0 else 0
        progreso_comida = avg_comida # Porcentaje de días que comiste saludable
        progreso_agua = min(avg_agua_litros / 2.0, 1.0) # Asumiendo 2 litros/día como meta promedio
        progreso_meditacion = min(avg_meditacion_minutos / 10.0, 1.0) # Asumiendo 10 minutos/día como meta
        progreso_lectura = min(total_lectura_paginas / meta_lectura_paginas_mensual, 1.0) if meta_lectura_paginas_mensual > 0 else 0
        
        progreso_horas_extra = min(total_horas_extra / objetivo_horas_extra_mensual, 1.0) if objetivo_horas_extra_mensual > 0 else 0
        progreso_salud = salud_completados / total_salud_objetivos if total_salud_objetivos > 0 else 0
        progreso_proyectos = proyectos_completados / total_proyectos if total_proyectos > 0 else 0

        # Nuevos pesos para la ponderación (ajusta a tu gusto)
        peso_entrenamiento = 0.15
        peso_comida = 0.10
        peso_agua = 0.05
        peso_meditacion = 0.10
        peso_lectura = 0.10
        peso_horas_extra = 0.15
        peso_salud = 0.15
        peso_proyectos = 0.20 # Le damos más peso a los proyectos como metas concretas

        overall_progress = (progreso_entrenamiento * peso_entrenamiento) + \
                           (progreso_comida * peso_comida) + \
                           (progreso_agua * peso_agua) + \
                           (progreso_meditacion * peso_meditacion) + \
                           (progreso_lectura * peso_lectura) + \
                           (progreso_horas_extra * peso_horas_extra) + \
                           (progreso_salud * peso_salud) + \
                           (progreso_proyectos * peso_proyectos)

        st.metric(label="Progreso General del Mes", value=f"{overall_progress:.1%}")
        st.progress(overall_progress)

        st.write("---")
        st.subheader("Detalle del Progreso:")
        st.write(f"- **Entrenamiento:** {entrenamiento_minutos_total:.0f} min (Meta: {meta_entrenamiento_minutos_mensual:.0f} min) - Progreso: {progreso_entrenamiento:.1%}")
        st.write(f"- **Comida Saludable (promedio días):** {progreso_comida:.1%}")
        st.write(f"- **Agua (promedio litros/día):** {avg_agua_litros:.1f} L (Meta: 2.0 L/día) - Progreso: {progreso_agua:.1%}")
        st.write(f"- **Meditación:** {avg_meditacion_minutos:.1f} min/día (Meta: 10 min/día) - Progreso: {progreso_meditacion:.1%}")
        st.write(f"- **Lectura:** {total_lectura_paginas:.0f} págs (Meta: {meta_lectura_paginas_mensual:.0f} págs) - Progreso: {progreso_lectura:.1%}")
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

# --- Pestaña 5: Mi Guía Espiritual ---
with tab5:
    st.header("✨ Mi Guía Espiritual de Objetivos Personales ✨")
    st.markdown("""
    Aquí encontrarás reflexiones y consejos para mantener tu mente y espíritu alineados con tus metas.
    Recuerda que el progreso no siempre es lineal, y cada paso, por pequeño que sea, te acerca a tu mejor versión.
    """)

    st.subheader("Consejos del Día:")
    # Podrías expandir esto con una lista de consejos o una función que elija uno aleatorio
    consejos = [
        "**Persistencia es clave:** Recuerda que cada día es una nueva oportunidad para empezar de nuevo y hacer las cosas mejor. No te castigues por los deslices, aprende de ellos.",
        "**Escucha a tu cuerpo:** Tu cuerpo es tu templo. Entiende sus señales, descansa cuando sea necesario y nútrelo con lo mejor.",
        "**La mente es tu aliada:** La visualización y la meditación no son solo para la calma, sino para enfocar tu energía y atraer tus objetivos. Dedica esos minutos de meditación a construir tu futuro.",
        "**Pequeñas victorias:** Celebra cada logro, por insignificante que parezca. Cada página leída, cada minuto de entrenamiento, cada hora extra, te acerca a tu meta.",
        "**Enfócate en el proceso, no solo en el resultado:** Disfruta el camino de crecimiento. La disciplina y la consistencia son los verdaderos maestros.",
        "**Sé amable contigo mismo:** Habla contigo como le hablarías a un buen amigo. La autocompasión es un pilar fundamental del bienestar mental.",
        "**Define tu 'por qué':** Cuando la motivación flaquea, recuerda la razón profunda detrás de tus objetivos. ¿Por qué quieres esto? Conéctate con esa energía.",
        "**El progreso es personal:** No te compares con nadie más. Tu camino es único y tus victorias son tuyas.",
        "**Respira y reconecta:** Si te sientes abrumado, tómate un momento para respirar profundamente. Un minuto de conexión contigo mismo puede resetear tu día.",
        "**El aprendizaje es infinito:** Cada desafío es una oportunidad para aprender algo nuevo sobre ti y sobre cómo superar obstáculos."
    ]
    
    # Elegir un consejo aleatorio para el día
    import random
    st.info(random.choice(consejos))

    st.subheader("Tu Espacio para Reflexionar:")
    st.write("¿Qué aprendizaje te dejó el día de hoy? ¿Qué te impulsó o te frenó?")
    # Puedes usar un st.text_area para que escriba una reflexión diaria si lo deseas
    # reflexion_diaria = st.text_area("Escribe aquí tu reflexión del día...", key="daily_reflection")
    # Si quisieras guardar esto, necesitarías otra columna en el DataFrame.

    st.markdown("""
    ---
    Recuerda: **Eres el arquitecto de tu destino.** Cada acción que marques en este planner es un ladrillo más en la construcción de la persona que quieres ser.
    """)

# Guardar los datos al final de la ejecución del script (Streamlit recarga el script en cada interacción)
save_data(df)
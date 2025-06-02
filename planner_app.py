import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os
import matplotlib.pyplot as plt
import random 


# --- Configuración Inicial ---
DATA_FILE = 'planner_data.csv' 
FINANCIAL_DATA_FILE = 'financial_transactions.csv' 

# --- Definición de columnas de la aplicación ---
APP_OBJECTIVES_CONFIG = {
    # Objetivos Diarios
    'Entrenamiento_Hecho': {'display': '✅ Entrenamiento Hecho', 'type': 'bool', 'section': 'daily'},
    'Entrenamiento_Minutos': {'display': 'Minutos de Entrenamiento', 'type': 'float', 'section': 'daily', 'step': 15.0, 'goal_monthly': 900}, 
    'Comida Saludable': {'display': '✅ Comida Saludable', 'type': 'bool', 'section': 'daily'},
    'Agua_Litros': {'display': 'Litros de Agua', 'type': 'float', 'section': 'daily', 'step': 0.5, 'goal_daily_avg': 2.0}, 
    'Horas Extra': {'display': 'Horas Extra', 'type': 'float', 'section': 'daily', 'step': 0.5, 'goal_monthly': 40}, 
    'Meditacion_Minutos': {'display': 'Minutos de Meditación', 'type': 'float', 'section': 'daily', 'step': 5.0, 'goal_daily_avg': 10.0}, 
    'Lectura_Paginas': {'display': 'Páginas Leídas', 'type': 'int', 'section': 'daily', 'step': 10, 'goal_monthly': 300}, 

    # Objetivos de Salud
    'Otorrino (vos)': {'display': 'Otorrino (vos)', 'type': 'bool', 'section': 'health'},
    'Otorrino (Guille)': {'display': 'Otorrino (Guille)', 'type': 'bool', 'section': 'health'},
    'Dentista (vos)': {'display': 'Dentista (vos)', 'type': 'bool', 'section': 'health'},
    'Dentista (Guille)': {'display': 'Dentista (Guille)', 'type': 'bool', 'section': 'health'},
    'Neumonólogo (Guille)': {'display': 'Neumonólogo (Guille)', 'type': 'bool', 'section': 'health'},
    'Brackets (averiguar - ambos)': {'display': 'Brackets (averiguar - ambos)', 'type': 'bool', 'section': 'health'},
    'Rinoseptoplastia (consulta)': {'display': 'Rinoseptoplastia (consulta)', 'type': 'bool', 'section': 'health'},

    # Proyectos
    'App ingresos y salidas': {'display': 'App ingresos y salidas', 'type': 'str', 'section': 'projects', 'options': ['Pendiente', 'En Curso', 'Completado ✅']},
    'App progreso personal': {'display': 'App progreso personal', 'type': 'str', 'section': 'projects', 'options': ['Pendiente', 'En Curso', 'Completado ✅']},

    # Finanzas - Balance Inicial
    'Balance_Inicial': {'display': 'Balance Inicial del Mes', 'type': 'float', 'section': 'finance', 'default': 0.0}
}

# Generar la lista de nombres de columnas a partir de la configuración
APP_COLUMNS_NAMES = ['Fecha'] + list(APP_OBJECTIVES_CONFIG.keys())

# --- Funciones para Guardar y Cargar Datos ---
def save_main_data(dataframe):
    temp_df = dataframe.copy()
    if 'Fecha' in temp_df.columns:
        temp_df['Fecha'] = temp_df['Fecha'].astype(str)
    temp_df.to_csv(DATA_FILE, index=False)

def load_financial_data():
    if os.path.exists(FINANCIAL_DATA_FILE):
        financial_df = pd.read_csv(FINANCIAL_DATA_FILE)
        financial_df['Fecha'] = pd.to_datetime(financial_df['Fecha']).dt.date
        return financial_df
    else:
        return pd.DataFrame(columns=['Fecha', 'Tipo', 'Categoría', 'Monto', 'Descripción'])

def save_financial_data(financial_df_to_save): 
    financial_df_to_save['Fecha'] = financial_df_to_save['Fecha'].astype(str)
    financial_df_to_save.to_csv(FINANCIAL_DATA_FILE, index=False)


# --- Cargar/Inicializar el DataFrame Principal ---
# TODO: Verificar si esta indentación es la causa raíz
if os.path.exists(DATA_FILE):
    df = pd.read_csv(DATA_FILE)
    df['Fecha'] = pd.to_datetime(df['Fecha'], errors='coerce').dt.date
    df.dropna(subset=['Fecha'], inplace=True)
    
    for col_name in APP_COLUMNS_NAMES:
        if col_name == 'Fecha':
            continue
        
        config = APP_OBJECTIVES_CONFIG.get(col_name)
        if not config: 
            continue

        col_type = config['type']
        
        if col_name not in df.columns:
            if col_type == 'bool':
                df[col_name] = False
            elif col_type == 'float':
                df[col_name] = config.get('default', 0.0)
            elif col_type == 'int':
                df[col_name] = config.get('default', 0)
            elif col_type == 'str':
                df[col_name] = config.get('options', [''])[0] if config.get('options') else ''
        else:
            if col_type == 'bool':
                df[col_name] = df[col_name].fillna(False).astype(bool)
            elif col_type == 'float':
                df[col_name] = pd.to_numeric(df[col_name], errors='coerce').fillna(config.get('default', 0.0))
            elif col_type == 'int':
                df[col_name] = pd.to_numeric(df[col_name], errors='coerce').fillna(config.get('default', 0)).astype(int)

else: # Este 'else' debe estar al mismo nivel que el 'if os.path.exists'
    initial_data = {col: [] for col in APP_COLUMNS_NAMES}
    df = pd.DataFrame(initial_data)
    
    for col_name in APP_COLUMNS_NAMES:
        if col_name == 'Fecha':
            continue
        config = APP_OBJECTIVES_CONFIG.get(col_name)
        if config:
            col_type = config['type']
            if col_type == 'bool':
                df[col_name] = False
            elif col_type == 'float':
                df[col_name] = config.get('default', 0.0)
            elif col_type == 'int':
                df[col_name] = config.get('default', 0)
            elif col_type == 'str':
                df[col_name] = config.get('options', [''])[0] if config.get('options') else ''

# Cargar los datos financieros al inicio del script.
# Este bloque DEBE estar al mismo nivel que la carga/inicialización de df.
if 'financial_df' not in st.session_state:
    st.session_state.financial_df = load_financial_data() 

# --- Título de la Aplicación ---
st.title("🗓️ Mi Planner Mensual Interactivo")

# Obtener la fecha de hoy y el inicio del mes actual
# Estos también deben estar al mismo nivel global.
today = datetime.now().date()
current_month_start = datetime(today.year, today.month, 1).date()

# --- Pestañas de Navegación ---
# Esta definición también debe estar al mismo nivel global.
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "Seguimiento Diario", "Salud / Turnos", "Proyectos", 
    "Control Financiero", "Resumen y Bonificación", "Mi Guía Espiritual"
])

# --- Pestaña 1: Seguimiento Diario ---
with tab1:
    st.header("Seguimiento Diario")

    if today not in df['Fecha'].values:
        new_row_data = {'Fecha': today}
        for col_name, config in APP_OBJECTIVES_CONFIG.items():
            if col_name == 'Fecha': continue 
            if config['type'] == 'bool':
                new_row_data[col_name] = False
            elif config['type'] == 'float':
                new_row_data[col_name] = config.get('default', 0.0)
            elif config['type'] == 'int':
                new_row_data[col_name] = config.get('default', 0)
            elif config['type'] == 'str':
                 new_row_data[col_name] = config.get('options', [''])[0] if config.get('options') else ''
        
        new_row = pd.DataFrame([new_row_data])
        df = pd.concat([df, new_row], ignore_index=True).sort_values(by='Fecha', ascending=True).reset_index(drop=True)
        save_main_data(df)

    row_index = df[df['Fecha'] == today].index[0]

    st.write(f"### Hoy es: {today.strftime('%d/%m/%Y')}")

    daily_columns_for_display = []
    for col_name, config in APP_OBJECTIVES_CONFIG.items():
        if config['section'] == 'daily':
            current_value = df.loc[row_index, col_name]
            if config['type'] == 'bool':
                new_value = st.checkbox(config['display'], value=current_value, key=f'daily_{col_name}')
                df.loc[row_index, col_name] = new_value
            elif config['type'] == 'float':
                new_value = st.number_input(config['display'], value=float(current_value), min_value=0.0, step=config.get('step', 0.5), key=f'daily_{col_name}')
                df.loc[row_index, col_name] = new_value
            elif config['type'] == 'int':
                new_value = st.number_input(config['display'], value=int(current_value), min_value=0, step=config.get('step', 1), key=f'daily_{col_name}')
                df.loc[row_index, col_name] = new_value
            daily_columns_for_display.append(col_name)

    st.write("---")
    st.subheader("Registro Diario (últimos 7 días)")
    df_display = df.tail(7)[['Fecha'] + daily_columns_for_display].copy()
    df_display['Fecha'] = df_display['Fecha'].astype(str)
    st.dataframe(df_display.set_index('Fecha'))

    save_main_data(df)


# --- Pestaña 2: Salud / Turnos ---
with tab2:
    st.header("Salud / Turnos")
    st.subheader("Marcar Turnos Completados:")

    if not df.empty:
        current_day_row_index = df[df['Fecha'] == today].index[0]
        for col_name, config in APP_OBJECTIVES_CONFIG.items():
            if config['section'] == 'health' and config['type'] == 'bool':
                current_value = df.loc[current_day_row_index, col_name]
                new_value = st.checkbox(f"✅ {config['display']}", value=current_value, key=f'health_{col_name}')
                df.loc[current_day_row_index, col_name] = new_value
    else:
        st.info("Aún no hay datos. Registra algo en 'Seguimiento Diario' para que aparezcan las opciones de salud.")
    save_main_data(df)

# --- Pestaña 3: Proyectos ---
with tab3:
    st.header("Proyectos")
    st.subheader("Estado de Proyectos:")

    if not df.empty:
        current_day_row_index = df[df['Fecha'] == today].index[0]
        for col_name, config in APP_OBJECTIVES_CONFIG.items():
            if config['section'] == 'projects' and config['type'] == 'str':
                current_value = df.loc[current_day_row_index, col_name]
                option = st.selectbox(f"**{config['display']}**", config['options'], index=config['options'].index(current_value), key=f'project_{col_name}')
                df.loc[current_day_row_index, col_name] = option
    else:
        st.info("Aún no hay datos. Registra algo en 'Seguimiento Diario' para que aparezcan las opciones de proyectos.")
    save_main_data(df)

# --- Pestaña 4: Control Financiero ---
with tab4:
    st.header("💰 Control Financiero")

    # --- Balance Inicial ---
    st.subheader("Configuración de Balance Inicial")
    row_index = df[df['Fecha'] == today].index[0] 
    
    balance_inicial_config = APP_OBJECTIVES_CONFIG['Balance_Inicial']
    current_balance_inicial = df.loc[row_index, 'Balance_Inicial']

    new_balance_inicial = st.number_input(
        balance_inicial_config['display'],
        value=float(current_balance_inicial),
        min_value=0.0,
        step=100.0,
        key='set_balance_inicial'
    )
    if new_balance_inicial != current_balance_inicial:
        df.loc[row_index, 'Balance_Inicial'] = new_balance_inicial
        save_main_data(df)
        st.success(f"Balance inicial actualizado a ${new_balance_inicial:.2f}")

    st.write("---")

    # --- Registrar Transacciones ---
    st.subheader("Registrar Nueva Transacción")
    with st.form("transaction_form"):
        # Variables del formulario deben definirse dentro del 'with st.form'
        trans_type = st.radio("Tipo de Transacción", ["Gasto", "Ingreso"], key="trans_type_radio")
        trans_category = st.selectbox(
            "Categoría",
            [
                "Alimentos", "Transporte", "Vivienda", "Entretenimiento",
                "Salud", "Educación", "Servicios", "Ropa", "Deudas",
                "Sueldo", "Inversión", "Regalos", "Otros" 
            ],
            key="trans_category_select"
        )
        trans_amount = st.number_input("Monto ($)", min_value=0.01, step=1.0, key="trans_amount_input")
        trans_description = st.text_input("Descripción (opcional)", key="trans_description_input")
        trans_date = st.date_input("Fecha de la Transacción", value=today, key="trans_date_input")

        submit_button = st.form_submit_button("Guardar Transacción")

        if submit_button:
            if trans_amount <= 0:
                st.error("El monto debe ser mayor que cero.")
            else:
                new_transaction = pd.DataFrame([{
                    'Fecha': trans_date,
                    'Tipo': trans_type,
                    'Categoría': trans_category,
                    'Monto': trans_amount,
                    'Descripción': trans_description
                }])
                
                # Acceder al financial_df desde st.session_state
                st.session_state.financial_df = pd.concat([st.session_state.financial_df, new_transaction], ignore_index=True)
                save_financial_data(st.session_state.financial_df) 
                st.success("Transacción guardada exitosamente!")
                st.experimental_rerun() 

    st.write("---")

    # --- Resumen Financiero ---
    st.subheader("Resumen del Mes")
    
    # current_month_start está definido globalmente arriba.
    # Acceder a financial_df desde st.session_state
    financial_df_month = st.session_state.financial_df[st.session_state.financial_df['Fecha'] >= current_month_start].copy() 

    total_ingresos = financial_df_month[financial_df_month['Tipo'] == 'Ingreso']['Monto'].sum()
    total_gastos = financial_df_month[financial_df_month['Tipo'] == 'Gasto']['Monto'].sum()
    
    balance_actual = current_balance_inicial + total_ingresos - total_gastos

    st.metric(label="Balance Inicial del Mes", value=f"${current_balance_inicial:.2f}")
    st.metric(label="Total Ingresos (este mes)", value=f"${total_ingresos:.2f}", delta=f"${total_ingresos:.2f}")
    st.metric(label="Total Gastos (este mes)", value=f"${total_gastos:.2f}", delta=f"- ${total_gastos:.2f}")
    st.metric(label="Balance Actual", value=f"${balance_actual:.2f}")

    st.write("---")
    st.subheader("Gráficos de Gastos")

    if not financial_df_month.empty and total_gastos > 0:
        gastos_por_categoria = financial_df_month[financial_df_month['Tipo'] == 'Gasto'].groupby('Categoría')['Monto'].sum().sort_values(ascending=False)
        
        st.write("#### Gastos por Categoría (este mes)")
        fig_cat, ax_cat = plt.subplots(figsize=(10, 6))
        gastos_por_categoria.plot(kind='bar', ax=ax_cat, color='salmon')
        ax_cat.set_title("Distribución de Gastos por Categoría")
        ax_cat.set_xlabel("Categoría")
        ax_cat.set_ylabel("Monto ($)")
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        st.pyplot(fig_cat)

        if len(financial_df_month['Fecha'].unique()) > 1:
            gastos_por_dia = financial_df_month[financial_df_month['Tipo'] == 'Gasto'].groupby('Fecha')['Monto'].sum()
            st.write("#### Tendencia de Gastos Diarios (este mes)")
            fig_day, ax_day = plt.subplots(figsize=(10, 4))
            ax_day.plot(gastos_por_dia.index, gastos_por_dia.values, marker='o', linestyle='-')
            ax_day.set_title("Gastos Diarios")
            ax_day.set_xlabel("Fecha")
            ax_day.set_ylabel("Monto ($)")
            ax_day.grid(True)
            plt.xticks(rotation=45)
            plt.tight_layout()
            st.pyplot(fig_day)

    else:
        st.info("Aún no hay gastos registrados este mes para mostrar gráficos.")

    st.write("---")
    st.subheader("Historial de Transacciones")
    if not st.session_state.financial_df.empty: # Acceder desde session_state
        st.dataframe(st.session_state.financial_df.sort_values(by='Fecha', ascending=False).reset_index(drop=True))
    else:
        st.info("Aún no hay transacciones registradas.")

    st.write("---")
    st.subheader("📈 Consejos para Mejorar tus Finanzas")
    financial_tips = [
        "**Crea un Presupuesto:** Saber a dónde va tu dinero es el primer paso. ¡Este planner te ayudará!",
        "**Prioriza el Ahorro:** Considera el ahorro como un 'gasto' fijo más. Págate a ti mismo primero.",
        "**Registra TODO:** Cada peso cuenta. Sé minucioso al registrar tus ingresos y gastos.",
        "**Identifica Fugas de Dinero:** Los gráficos te mostrarán dónde gastas más. ¿Puedes reducirlo?",
        "**Metas Financieras Claras:** Define qué quieres lograr (ej. fondo de emergencia, viaje, inversión).",
        "**Evita Deudas Innecesarias:** Las deudas con intereses altos pueden ahogar tu progreso.",
        "**Invierte en ti mismo:** La educación y el desarrollo de habilidades pueden aumentar tus ingresos.",
        "**Revisa tus Finanzas Regularmente:** No basta con registrar; analiza tus números semanal o mensualmente."
    ]
    st.info(random.choice(financial_tips))


# --- Pestaña 5: Resumen y Bonificación ---
with tab5: 
    st.header("Resumen y Bonificación")

    st.subheader("Progreso General del Mes:")

    df_current_month = df[df['Fecha'] >= current_month_start].copy()

    if not df_current_month.empty:
        total_days_logged = len(df_current_month)
        
        category_progress = {}
        
        daily_quant_objectives = [
            'Entrenamiento_Minutos', 'Agua_Litros', 'Meditacion_Minutos', 'Lectura_Paginas', 'Horas Extra'
        ]
        
        for obj_name in daily_quant_objectives:
            config = APP_OBJECTIVES_CONFIG[obj_name]
            goal_monthly = config.get('goal_monthly')
            goal_daily_avg = config.get('goal_daily_avg')
            
            current_value = df_current_month[obj_name].sum()
            
            if goal_monthly:
                progress = min(current_value / goal_monthly, 1.0) if goal_monthly > 0 else 0
                st.write(f"- **{config['display']}:** {current_value:.1f} (Meta: {goal_monthly:.1f}) - Progreso: {progress:.1%}")
            elif goal_daily_avg:
                avg_value = df_current_month[obj_name].mean() if total_days_logged > 0 else 0
                progress = min(avg_value / goal_daily_avg, 1.0) if goal_daily_avg > 0 else 0
                st.write(f"- **{config['display']} (promedio/día):** {avg_value:.1f} (Meta: {goal_daily_avg:.1f}) - Progreso: {progress:.1%}")
            else:
                progress = 0
            
            category_progress[obj_name] = progress
            
        bool_daily_objectives = ['Entrenamiento_Hecho', 'Comida Saludable']
        for obj_name in bool_daily_objectives:
            config = APP_OBJECTIVES_CONFIG[obj_name]
            progress = df_current_month[obj_name].mean() if total_days_logged > 0 else 0
            st.write(f"- **{config['display']} (promedio días):** {progress:.1%}")
            category_progress[obj_name] = progress
        
        salud_completados = 0
        health_objectives_list = [name for name, config in APP_OBJECTIVES_CONFIG.items() if config['section'] == 'health']
        total_salud_objetivos = len(health_objectives_list)
        if not df_current_month.empty:
            last_month_row = df_current_month[df_current_month['Fecha'] == today].iloc[0] if today in df_current_month['Fecha'].values else df_current_month.iloc[-1]
            for obj in health_objectives_list:
                if last_month_row[obj]:
                    salud_completados += 1
        progreso_salud = salud_completados / total_salud_objetivos if total_salud_objetivos > 0 else 0
        st.write(f"- **Objetivos de Salud Completados:** {salud_completados} de {total_salud_objetivos} - Progreso: {progreso_salud:.1%}")
        category_progress['Salud_General'] = progreso_salud

        proyectos_completados = 0
        projects_objectives_list = [name for name, config in APP_OBJECTIVES_CONFIG.items() if config['section'] == 'projects']
        total_proyectos = len(projects_objectives_list)
        if not df_current_month.empty:
            last_month_row = df_current_month[df_current_month['Fecha'] == today].iloc[0] if today in df_current_month['Fecha'].values else df_current_month.iloc[-1]
            for proj in projects_objectives_list:
                if last_month_row[proj] == 'Completado ✅':
                    proyectos_completados += 1
        progreso_proyectos = proyectos_completados / total_proyectos if total_proyectos > 0 else 0
        st.write(f"- **Proyectos Completados:** {proyectos_completados} de {total_proyectos} - Progreso: {progreso_proyectos:.1%}")
        category_progress['Proyectos_General'] = progreso_proyectos

        pesos = {
            'Entrenamiento_Minutos': 0.15,
            'Entrenamiento_Hecho': 0.05,
            'Comida Saludable': 0.10,
            'Agua_Litros': 0.05,
            'Horas Extra': 0.10,
            'Meditacion_Minutos': 0.10,
            'Lectura_Paginas': 0.10,
            'Salud_General': 0.15,
            'Proyectos_General': 0.20
        }
        
        overall_progress = sum(category_progress.get(obj, 0) * pesos.get(obj, 0) for obj in pesos.keys())
        total_weight = sum(pesos.values())
        overall_progress = overall_progress / total_weight if total_weight > 0 else 0

        st.metric(label="Progreso General del Mes", value=f"{overall_progress:.1%}")
        st.progress(overall_progress)

        st.write("---")
        st.subheader("Gráficos de Progreso Mensual:")

        if not df_current_month.empty and 'Entrenamiento_Minutos' in df_current_month.columns:
            st.write("#### Minutos de Entrenamiento Diarios")
            fig, ax = plt.subplots(figsize=(10, 4))
            ax.plot(df_current_month['Fecha'], df_current_month['Entrenamiento_Minutos'], marker='o', linestyle='-')
            ax.set_xlabel("Día del Mes")
            ax.set_ylabel("Minutos")
            ax.set_title("Registro de Minutos de Entrenamiento")
            ax.grid(True)
            plt.xticks(rotation=45)
            plt.tight_layout()
            st.pyplot(fig)

        if not df_current_month.empty and 'Agua_Litros' in df_current_month.columns:
            st.write("#### Litros de Agua Diarios")
            fig, ax = plt.subplots(figsize=(10, 4))
            ax.bar(df_current_month['Fecha'], df_current_month['Agua_Litros'], color='skyblue')
            ax.axhline(y=APP_OBJECTIVES_CONFIG['Agua_Litros']['goal_daily_avg'], color='r', linestyle='--', label=f"Meta Diaria ({APP_OBJECTIVES_CONFIG['Agua_Litros']['goal_daily_avg']}L)")
            ax.set_xlabel("Día del Mes")
            ax.set_ylabel("Litros")
            ax.set_title("Consumo de Agua Diario")
            ax.legend()
            plt.xticks(rotation=45)
            plt.tight_layout()
            st.pyplot(fig)
            
        if not df_current_month.empty and 'Horas Extra' in df_current_month.columns:
            st.write("#### Horas Extra Diarias")
            fig, ax = plt.subplots(figsize=(10, 4))
            ax.bar(df_current_month['Fecha'], df_current_month['Horas Extra'], color='lightgreen')
            ax.set_xlabel("Día del Mes")
            ax.set_ylabel("Horas")
            ax.set_title("Registro de Horas Extra")
            plt.xticks(rotation=45)
            plt.tight_layout()
            st.pyplot(fig)

        st.write("---")
        st.subheader("Bonificación:")
        if overall_progress >= 0.85:
            st.success("¡🎉 Felicidades! Has cumplido con al menos el 85% de tus objetivos.")
            st.write("**Recompensa desbloqueada:** ¡Felicitaciones por tu esfuerzo! Aquí puedes escribir la recompensa que te diste.")
            st.markdown("---")
            st.balloons()
        else:
            st.info("Sigue trabajando. ¡Estás cerca de alcanzar tus metas!")
            st.write(f"Necesitas un {0.85 - overall_progress:.1%} más para la bonificación del 85%.")

    else:
        st.info("Aún no hay datos para calcular el progreso. Empieza a registrar tus actividades.")

# --- Pestaña 6: Mi Guía Espiritual ---
with tab6: 
    st.header("✨ Mi Guía Espiritual de Objetivos Personales ✨")
    st.markdown("""
    Aquí encontrarás reflexiones y consejos para mantener tu mente y espíritu alineados con tus metas.
    Recuerda que el progreso no siempre es lineal, y cada paso, por pequeño que sea, te acerca a tu mejor versión.
    """)

    st.subheader("Consejos del Día:")
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
    
    st.info(random.choice(consejos))

    st.subheader("Tu Espacio para Reflexionar:")
    st.write("¿Qué aprendizaje te dejó el día de hoy? ¿Qué te impulsó o te frenó?")

    st.markdown("""
    ---
    Recuerda: **Eres el arquitecto de tu destino.** Cada acción que marques en este planner es un ladrillo más en la construcción de la persona que quieres ser.
    """)

# Guardar los datos del planner principal al final
save_main_data(df)
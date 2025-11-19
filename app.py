import dash
from dash import dcc, html, Input, Output, callback
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime
import pyodbc

# Inicializar la app
app = dash.Dash(__name__, title='PRODHEG - Dashboard')
server = app.server

# Estilos
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>PRODHEG | Dashboard</title>
        {%favicon%}
        {%css%}
        <style>
            .dashboard-header {
                background: linear-gradient(135deg, #ffffff, #4B0E7D);
                color: black;
                padding: 20px;
                border-radius: 10px;
                margin-bottom: 20px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }
            .metric-card {
                background: white;
                padding: 15px;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                text-align: center;
                border-left: 4px solid #3498db;
            }
            .filter-section {
                background: #f8f9fa;
                padding: 15px;
                border-radius: 8px;
                margin-bottom: 20px;
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

# Cargar datos
def cargar_datos_access():
    archivo_access = 'D:/concentrado 2000-2025.mdb'
    conn_str = f'DRIVER={{Microsoft Access Driver (*.mdb, *.accdb)}};DBQ={archivo_access};'
    conn = pyodbc.connect(conn_str)
    quejas = pd.read_sql("SELECT * FROM [Quejas]", conn)
    expediente = pd.read_sql("SELECT * FROM [Expediente]", conn)
    conn.close()
        
    # Merge
    df = pd.merge(quejas, expediente, on='Expediente', how='inner', suffixes=('', '_expediente'))
    columnas_duplicadas = [col for col in df.columns if col.endswith('_expediente')]
    if columnas_duplicadas:
        print(f"🗑️ Eliminando columnas duplicadas: {columnas_duplicadas}")
        df = df.drop(columns=columnas_duplicadas)
    df2=df
    columnas = [
    'Expediente', 
    'SubProcu', 
    'FechaInicio', 
    'LugarProcedencia', 
    'Recepcion', 
    'Conclusión', 
    'F_Conclusion', 
    'GrupoVulnerable'
    ]
    columnas_finales = [col for col in columnas if col in df.columns]
    df = df[columnas_finales].drop_duplicates()

    # Ajustar fechas
    df['FechaInicio'] = pd.to_datetime(df['FechaInicio'], errors='coerce')
    df['Año'] = df['FechaInicio'].dt.year
    df['Mes'] = df['FechaInicio'].dt.month
    df = df[df['Año'].between(2009, 2025)]
    df = df.sort_values(['FechaInicio', 'Expediente'])
    df = df.reset_index(drop=True)
    df2['FechaInicio'] = pd.to_datetime(df2['FechaInicio'], errors='coerce')
    df2['Año'] = df2['FechaInicio'].dt.year
    df2['Mes'] = df2['FechaInicio'].dt.month
    df2 = df2[df2['Año'].between(2009, 2025)]
    df2 = df2.sort_values(['FechaInicio', 'Expediente'])
    df2 = df2.reset_index(drop=True)

    # Calcular tiempos
    mask_concluidos = df['F_Conclusion'].notna() & df['FechaInicio'].notna()
    df.loc[mask_concluidos, 'TiempoDias'] = (
        df.loc[mask_concluidos, 'F_Conclusion'] - df.loc[mask_concluidos, 'FechaInicio']
    ).dt.days
        
    return df,df2

def cargar_datos_csv():
    quejas = pd.read_csv('data/quejas.csv')
    expediente = pd.read_csv('data/expediente.csv')
        
    # Merge
    df = pd.merge(quejas, expediente, on='Expediente', how='inner', suffixes=('', '_expediente'))
    columnas_duplicadas = [col for col in df.columns if col.endswith('_expediente')]
    if columnas_duplicadas:
        print(f"🗑️ Eliminando columnas duplicadas: {columnas_duplicadas}")
        df = df.drop(columns=columnas_duplicadas)
    df2=df
    columnas = [
    'Expediente', 
    'SubProcu', 
    'FechaInicio', 
    'LugarProcedencia', 
    'Recepcion', 
    'Conclusión', 
    'F_Conclusion', 
    'GrupoVulnerable'
    ]
    columnas_finales = [col for col in columnas if col in df.columns]
    df = df[columnas_finales].drop_duplicates()

    # Ajustar fechas
    df['FechaInicio'] = pd.to_datetime(df['FechaInicio'], errors='coerce')
    df['F_Conclusion'] = pd.to_datetime(df['F_Conclusion'], errors='coerce')
    df['Año'] = df['FechaInicio'].dt.year
    df['Mes'] = df['FechaInicio'].dt.month
    df = df[df['Año'].between(2009, 2025)]
    df = df.sort_values(['FechaInicio', 'Expediente'])
    df = df.reset_index(drop=True)
    df2['FechaInicio'] = pd.to_datetime(df2['FechaInicio'], errors='coerce')
    df2['Año'] = df2['FechaInicio'].dt.year
    df2['Mes'] = df2['FechaInicio'].dt.month
    df2 = df2[df2['Año'].between(2009, 2025)]
    df2 = df2.sort_values(['FechaInicio', 'Expediente'])
    df2 = df2.reset_index(drop=True)

    # Calcular tiempos
    mask_concluidos = df['F_Conclusion'].notna() & df['FechaInicio'].notna()
    df.loc[mask_concluidos, 'TiempoDias'] = (
        df.loc[mask_concluidos, 'F_Conclusion'] - df.loc[mask_concluidos, 'FechaInicio']
    ).dt.days
        
    return df,df2

# Cargar datos
#df,df2 = cargar_datos_access()
df,df2 = cargar_datos_csv()

# Layout principal
app.layout = html.Div([
    # Header
    html.Div([
        # Logo y título en línea
        html.Div([
            html.Img(
                src='assets/logo_horizontal.png',
                style={
                    'height': '100px',
                    'marginRight': '20px',
                    'verticalAlign': 'middle'
                }
            ),
            html.Div([
                html.H1("Unidad de Estadística", 
                        style={'color': 'black', 'margin': '0', 'fontSize': '28px'}),
                html.P("Dashboard Interactivo de Gestión de Quejas", 
                       style={'color': 'black', 'opacity': '0.9', 'margin': '5px 0 0 0', 'fontSize': '16px'})
            ], style={'display': 'inline-block', 'verticalAlign': 'middle'})
        ], style={'textAlign': 'left'}),
    ], className='dashboard-header'),
    
    # Filtros
    html.Div([
        html.Div([
            html.Label("Rango de Años:", style={'fontWeight': 'bold'}),
            dcc.RangeSlider(
                id='year-slider',
                min=df['Año'].min(),
                max=df['Año'].max(),
                value=[df['Año'].min(), df['Año'].max()],
                marks={int(year): str(int(year)) for year in df['Año'].unique()},
                step=1
            )
        ], style={'width': '48%', 'display': 'inline-block'}),
        
        html.Div([
            html.Label("Subprocuraduría:", style={'fontWeight': 'bold'}),
            dcc.Dropdown(
                id='subprocu-dropdown',
                options=[{'label': 'Todas', 'value': 'all'}] + 
                        [{'label': zona, 'value': zona} for zona in sorted(df['SubProcu'].unique())],
                value='all',
                multi=False
            )
        ], style={'width': '48%', 'display': 'inline-block', 'float': 'right'})
    ], className='filter-section'),
    
    # Métricas principales
    html.Div([
        html.Div([
            html.H4("Total Expedientes", style={'color': '#2c3e50'}),
            html.H2(id='total-expedientes', style={'color': '#3498db'})
        ], className='metric-card', style={'width': '24%', 'display': 'inline-block', 'margin': '5px'}),
        
        html.Div([
            html.H4("Tasa Conclusión", style={'color': '#2c3e50'}),
            html.H2(id='tasa-conclusion', style={'color': '#27ae60'})
        ], className='metric-card', style={'width': '24%', 'display': 'inline-block', 'margin': '5px'}),
        
        html.Div([
            html.H4("Tiempo Promedio", style={'color': '#2c3e50'}),
            html.H2(id='tiempo-promedio', style={'color': '#e74c3c'})
        ], className='metric-card', style={'width': '24%', 'display': 'inline-block', 'margin': '5px'}),
        
        html.Div([
            html.H4("En Trámite", style={'color': '#2c3e50'}),
            html.H2(id='en-tramite', style={'color': '#f39c12'})
        ], className='metric-card', style={'width': '24%', 'display': 'inline-block', 'margin': '5px'})
    ], style={'textAlign': 'center', 'margin': '20px 0'}),
    
    # Primera fila de gráficas
    html.Div([
        html.Div([
            dcc.Graph(id='evolucion-temporal')
        ], style={'width': '48%', 'display': 'inline-block'}),
        
        html.Div([
            dcc.Graph(id='distribucion-conclusiones')
        ], style={'width': '48%', 'display': 'inline-block', 'float': 'right'})
    ]),
    
    # Segunda fila de gráficas
    html.Div([
        html.Div([
            dcc.Graph(id='eficiencia-zonas')
        ], style={'width': '48%', 'display': 'inline-block'}),
        
        html.Div([
            dcc.Graph(id='grupos-vulnerables')
        ], style={'width': '48%', 'display': 'inline-block', 'float': 'right'})
    ]),
    
    # mapa de calor
    html.Div([
        dcc.Graph(id='mapa-calor-tiempos')
    ]),

    # mapa geográfico
    html.Div([
    dcc.Graph(id='mapa-geografico')
    ], style={'marginTop': '25px'}),

])

# Callbacks para interactividad
@app.callback(
    [Output('total-expedientes', 'children'),
     Output('tasa-conclusion', 'children'),
     Output('tiempo-promedio', 'children'),
     Output('en-tramite', 'children')],
    [Input('year-slider', 'value'),
     Input('subprocu-dropdown', 'value')]
)
def actualizar_metricas(rango_anios, subprocu):
    df_filtrado = df[(df['Año'] >= rango_anios[0]) & (df['Año'] <= rango_anios[1])]
    
    if subprocu != 'all':
        df_filtrado = df_filtrado[df_filtrado['SubProcu'] == subprocu]
    
    total = len(df_filtrado)
    concluidos = len(df_filtrado[df_filtrado['F_Conclusion'].notna()])
    tasa = f"{(concluidos/total*100):.1f}%" if total > 0 else "0%"
    
    tiempos = df_filtrado[df_filtrado['F_Conclusion'].notna()]
    tiempo_promedio = f"{tiempos['TiempoDias'].mean():.0f} días" if len(tiempos) > 0 else "N/A"
    
    en_tramite = len(df_filtrado[df_filtrado['F_Conclusion'].isna()])
    
    return f"{total:,}", tasa, tiempo_promedio, f"{en_tramite:,}"

@app.callback(
    Output('evolucion-temporal', 'figure'),
    [Input('year-slider', 'value'),
     Input('subprocu-dropdown', 'value')]
)
def actualizar_evolucion(rango_anios, subprocu):
    df_filtrado = df[(df['Año'] >= rango_anios[0]) & (df['Año'] <= rango_anios[1])]
    
    if subprocu != 'all':
        df_filtrado = df_filtrado[df_filtrado['SubProcu'] == subprocu]

    # Método: Agrupar sin crear columnas duplicadas
    df_filtrado['AñoMes'] = df_filtrado['FechaInicio'].dt.to_period('M')
    mensual = df_filtrado.groupby('AñoMes').size().reset_index(name='Expedientes')
    mensual['Fecha'] = mensual['AñoMes'].dt.to_timestamp()
    mensual = mensual.drop('AñoMes', axis=1)
    
    fig = px.line(mensual, x='Fecha', y='Expedientes',
                  title='Evolución Temporal de Expedientes Recibidos',
                  template='plotly_white')
    fig.update_layout(
        xaxis_title="Fecha",
        yaxis_title="Número de Expedientes",
        hovermode='x unified'
    )
    
    return fig

@app.callback(
    Output('distribucion-conclusiones', 'figure'),
    [Input('year-slider', 'value'),
     Input('subprocu-dropdown', 'value')]
)
def actualizar_conclusiones(rango_anios, subprocu):
    df_filtrado = df[(df['Año'] >= rango_anios[0]) & (df['Año'] <= rango_anios[1])]
    
    if subprocu != 'all':
        df_filtrado = df_filtrado[df_filtrado['SubProcu'] == subprocu]
    
    conteo = df_filtrado['Conclusión'].value_counts()
    
    fig = px.pie(values=conteo.values, names=conteo.index,
                 title='Distribución de Tipos de Conclusión',
                 template='plotly_white')
    fig.update_traces(textposition='inside', textinfo='percent+label')
    
    return fig

@app.callback(
    Output('eficiencia-zonas', 'figure'),
    [Input('year-slider', 'value'),
     Input('subprocu-dropdown', 'value')]
)
def actualizar_eficiencia(rango_anios, subprocu):
    df_filtrado = df[(df['Año'] >= rango_anios[0]) & (df['Año'] <= rango_anios[1])]
    
    if subprocu != 'all':
        df_filtrado = df_filtrado[df_filtrado['SubProcu'] == subprocu]
    
    # Calcular eficiencia por zona
    eficiencia = df_filtrado.groupby('SubProcu').agg({
        'Expediente': 'count',
        'TiempoDias': 'mean'
    }).reset_index()
    
    fig = px.bar(eficiencia, x='SubProcu', y='TiempoDias',
                 title='Tiempo Promedio de Conclusión por Zona',
                 template='plotly_white',
                 color='TiempoDias',
                 color_continuous_scale='Viridis')
    fig.update_layout(
        xaxis_title="Subprocuraduría",
        yaxis_title="Tiempo Promedio (días)"
    )
    
    return fig

@app.callback(
    Output('grupos-vulnerables', 'figure'),
    [Input('year-slider', 'value'),
     Input('subprocu-dropdown', 'value')]
)
def actualizar_grupos_vulnerables(rango_anios, subprocu):
    df_filtrado = df2[(df2['Año'] >= rango_anios[0]) & (df2['Año'] <= rango_anios[1])]
    
    if subprocu != 'all':
        df_filtrado = df_filtrado[df_filtrado['SubProcu'] == subprocu]
    df_filtrado = df_filtrado[df_filtrado['DireccionMunicipal'] != 'null']
    df_filtrado = df_filtrado[df_filtrado['DireccionMunicipal'] != '']
    df_filtrado = df_filtrado.drop_duplicates(subset=['Expediente','Hecho','Dependencia'])
    grupos = df_filtrado['Dependencia'].value_counts().head(10).reset_index()
    grupos.columns = ['Ciudad', 'Cantidad']
    title = 'Procedencia de los Expedientes'
    
    fig = px.bar(grupos, x='Cantidad', y=grupos.columns[0], orientation='h',
                 title=title,
                 template='plotly_white',
                 color='Cantidad',
                 color_continuous_scale='Blues')
    fig.update_layout(
        xaxis_title="Número de Expedientes",
        yaxis_title=grupos.columns[0]
    )
    
    return fig

@app.callback(
    Output('mapa-calor-tiempos', 'figure'),
    [Input('year-slider', 'value'),
     Input('subprocu-dropdown', 'value')]
)
def actualizar_mapa_calor(rango_anios, subprocu):
    df_filtrado = df[(df['Año'] >= rango_anios[0]) & (df['Año'] <= rango_anios[1])]
    
    if subprocu != 'all':
        df_filtrado = df_filtrado[df_filtrado['SubProcu'] == subprocu]
    
    # VERSIÓN SIMPLIFICADA: Crear matriz manualmente
    años = list(range(rango_anios[0], rango_anios[1] + 1))
    meses = list(range(1, 13))
    
    # Crear matriz vacía
    matriz = np.zeros((len(meses), len(años)))
    
    # Llenar matriz con datos
    for i, año in enumerate(años):
        for j, mes in enumerate(meses):
            conteo = len(df_filtrado[
                (df_filtrado['FechaInicio'].dt.year == año) & 
                (df_filtrado['FechaInicio'].dt.month == mes)
            ])
            matriz[j, i] = conteo
    
    # Nombres de meses
    nombres_meses = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 
                    'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
    
    fig = px.imshow(
        matriz,
        x=años,           # Años en X
        y=nombres_meses,  # Meses en Y
        labels=dict(x="Año", y="Mes", color="Expedientes"),
        title='Expedientes por Mes y Año',
        aspect="auto",
        color_continuous_scale='Viridis'
    )
    
    return fig

@app.callback(
    Output('mapa-geografico', 'figure'),
    [Input('year-slider', 'value'),
     Input('subprocu-dropdown', 'value')]
)
def actualizar_mapa_geografico(rango_anios, subprocu):
    df_filtrado = df[(df['Año'] >= rango_anios[0]) & (df['Año'] <= rango_anios[1])]
    
    if subprocu != 'all':
        df_filtrado = df_filtrado[df_filtrado['SubProcu'] == subprocu]
    
    if 'LugarProcedencia' not in df_filtrado.columns:
        return crear_mapa_vacio("No hay datos de ubicación disponibles")
    
    # COORDENADAS PRECISAS PARA TODOS TUS MUNICIPIOS
    coordenadas_completas = {
        # MUNICIPIOS DE GUANAJUATO (prioridad)
        'León': [21.1250, -101.6860],
        'Celaya': [20.5234, -100.8157],
        'San Miguel de Allende': [20.9144, -100.7450],
        'Salvatierra': [20.2134, -100.8802],
        'Irapuato': [20.6896, -101.3540],
        'Yuriria': [20.2100, -101.1328],
        'Silao': [20.9437, -101.4270],
        'Dolores Hidalgo C.I.N.': [21.1564, -100.9345],
        'Dolores Hidalgo': [21.1564, -100.9345],
        'Villagrán': [20.5153, -100.9972],
        'Tarandacuao': [20.0000, -100.5167],
        'Valle de Santiago': [20.3928, -101.1917],
        'Guanajuato': [21.0190, -101.2574],
        'Pueblo Nuevo': [20.5436, -101.3714],
        'Salamanca': [20.5706, -101.1975],
        'Cortazar': [20.4833, -100.9667],
        'Apaseo el Grande': [20.5458, -100.6861],
        'Acámbaro': [20.0300, -100.7222],
        'Comonfort': [20.7222, -100.7597],
        'San Luis de la Paz': [21.2986, -100.5167],
        'Moroleón': [20.1278, -101.1917],
        'San Felipe': [21.4781, -101.2156],
        'San Francisco del Rincón': [21.0183, -101.8550],
        'San Francisco del Rincón.': [21.0183, -101.8550],
        'San José Iturbide': [21.0014, -100.3842],
        'Apaseo el Alto': [20.4583, -100.6208],
        'Xichú': [21.3000, -100.0583],
        'Coroneo': [20.2000, -100.3667],
        'Pénjamo': [20.4314, -101.7228],
        'Victoria': [21.2111, -100.2139],
        'Tarimoro': [20.2889, -100.7583],
        'Huanímaro': [20.3683, -101.4997],
        'Purísima del Rincón': [21.0344, -101.8700],
        'Tierra Blanca': [21.1000, -100.1583],
        'Jerécuaro': [20.1556, -100.5083],
        'Cuerámaro': [20.6250, -101.6736],
        'Abasolo': [20.4494, -101.5303],
        'Santiago Maravatío': [20.1739, -101.0000],
        'Santa Cruz de Juventino Rosas': [20.6433, -100.9928],
        'Santa Catarina': [21.1411, -100.0694],
        'Atarjea': [21.2667, -99.7167],
        'Ocampo': [21.6472, -101.4792],
        'Uriangato': [20.1400, -101.1717],
        'Jaral del Progreso': [20.3714, -101.0611],
        'San Diego de la Unión': [21.4667, -100.8750],
        'Doctor Mora': [21.1411, -100.3194],
        'Manuel Doblado': [20.7289, -101.9525],
        'Romita': [20.8711, -101.5169],
        'Salamaca': [20.5706, -101.1975],
        'Silao de la Victoria': [20.9437, -101.4270],
        
        # ESTADOS VECINOS (capitales)
        'Querétaro': [20.5881, -100.3881],
        'Michoacán': [19.5665, -101.7068],
        'Jalisco': [20.6595, -103.3494],
        'ESTADO DE MÉXICO': [19.4969, -99.7233],
        'MICHOACÁN': [19.5665, -101.7068],
        'DISTRITO FEDERAL': [19.4326, -99.1332],
        'SINALOA': [25.1721, -107.4795],
        'TAMAULIPAS': [24.2669, -98.8363],
        'GUERRERO': [17.5734, -99.9580],
        'NUEVO LEÓN': [25.5922, -100.2840],
        'COAHUILA': [27.0587, -101.7068],
        'AGUASCALIENTES': [21.8853, -102.2916],
        'ZACATECAS': [22.7709, -102.5832],
        'MORELOS': [18.6813, -99.1013],
        'DURANGO': [24.0277, -104.6532],
        'NAYARIT': [21.7514, -104.8455],
        'SAN LUIS POTOSÍ': [22.1565, -100.9855],
        'VERACRUZ': [19.1738, -96.1342],
        'BAJA CALIFORNIA': [32.6245, -115.4523],
        'HIDALGO': [20.0911, -98.7624],
        'SONORA': [29.2972, -110.3309],
        'CHIHUAHUA': [28.6330, -106.0691],
        'CHIAPAS': [16.7569, -93.1292],
        'Oaxaca': [17.0732, -96.7266],
        'Playas de Rosarito': [32.3333, -117.0333],
        
        # PAÍSES
        'Colombia': [4.5709, -74.2973],
        'REPÚBLICA DE HONDURAS': [14.0818, -87.2068],
        'HONDURAS': [14.0818, -87.2068],
        'ESTADOS UNIDOS': [39.8283, -98.5795],
        'EUA': [39.8283, -98.5795],
        'HONDURAS Y EL SALVADOR': [14.0818, -87.2068],
        'OTRO PAÍS GUATEMALA': [14.6349, -90.5069],
        'OTRO PAÍS (E.U.A)': [39.8283, -98.5795],
        
        # AUTORIDADES
        'AUTORIDADES DE PUEBLA': [19.0414, -98.2063],
        'Autoridades del Estado de México': [19.4969, -99.7233],
        'Autoridades de Querétaro': [20.5881, -100.3881],
        'Autoridades de Ciudad de México': [19.4326, -99.1332],
        'Autoridades de Guerrero': [17.5734, -99.9580],
        'Autoridades de Jalisco': [20.6595, -103.3494],
        'Autoridades de Coahuila': [27.0587, -101.7068],
        'Autoridades de Oaxaca': [17.0732, -96.7266],
        'Autoridades de Michoacán': [19.5665, -101.7068],
        'Autoridades de Chiapas': [16.7569, -93.1292],
        'Autoridades de Veracruz': [19.1738, -96.1342],
        'Autoridades de Hidalgo': [20.0911, -98.7624],
        'Autoridades de Sonora': [29.2972, -110.3309],
        'Autoridades de Nayarit': [21.7514, -104.8455],
        'Autoridades de Durango': [24.0277, -104.6532],
        
        # ENTIDADES
        'ENTIDAD NAYARIT': [21.7514, -104.8455],
        'ENTIDAD QUERÉTARO': [20.5881, -100.3881],
        'E. QUERÉTARO': [20.5881, -100.3881],
        'E. JALISCO': [20.6595, -103.3494],
        'E. VERACRUZ': [19.1738, -96.1342],
        'E. SAN LUIS POTOSÍ': [22.1565, -100.9855],
        'E. TAMAULIPAS': [24.2669, -98.8363],
        'E. MICHOACÁN': [19.5665, -101.7068],
        'E. OAXACA': [17.0732, -96.7266],
        'E. TABASCO': [17.8409, -92.6189],
        'E. Zacatecas': [22.7709, -102.5832],
        'E. Durango': [24.0277, -104.6532],
        'E. Morelos': [18.6813, -99.1013],
        'E. Nayarit': [21.7514, -104.8455],
        'E. Yucatán': [20.9801, -89.6234],
        
        'MÉXICO': [23.6345, -102.5528],
        'CIUDAD DE MÉXICO': [19.4326, -99.1332],
        'CIUDAD DE MEXICO': [19.4326, -99.1332],
        'VERACRUZ (LEÓN)': [21.1250, -101.6860],
        
        # VALORES ESPECIALES
        'OTRO PAÍS': None,
        'OTRO PAIS': None,
        'Indeterminado': None,
        'null': None,
    }
    
    # Procesar datos
    df_filtrado = df_filtrado.copy()
    df_filtrado['LugarLimpio'] = df_filtrado['LugarProcedencia'].fillna('Indeterminado')
    
    # Contar expedientes por lugar
    conteo_lugares = df_filtrado['LugarLimpio'].value_counts().reset_index()
    conteo_lugares.columns = ['Lugar', 'Expedientes']
    
    # CORRECCIÓN: Buscar coordenadas de forma segura
    def obtener_coordenadas(lugar):
        """Obtener coordenadas de forma segura"""
        try:
            coords = coordenadas_completas.get(str(lugar).strip())
            if coords is None:
                return None, None
            return coords[0], coords[1]  # Retornar lat, lon directamente
        except:
            return None, None
    
    # Aplicar la función segura
    coordenadas_result = conteo_lugares['Lugar'].apply(obtener_coordenadas)
    
    # CORRECCIÓN: Separar latitud y longitud directamente
    conteo_lugares['lat'] = coordenadas_result.apply(lambda x: x[0] if x[0] is not None else None)
    conteo_lugares['lon'] = coordenadas_result.apply(lambda x: x[1] if x[1] is not None else None)
    
    # Filtrar lugares con coordenadas válidas
    lugares_con_coordenadas = conteo_lugares[
        (conteo_lugares['lat'].notna()) & 
        (conteo_lugares['lon'].notna())
    ]
    
    if len(lugares_con_coordenadas) == 0:
        return crear_mapa_vacio("No se encontraron ubicaciones en los datos")
    
    print(f"📍 Lugares encontrados: {len(lugares_con_coordenadas)}")
    for _, row in lugares_con_coordenadas.iterrows():
        print(f"   - {row['Lugar']}: {row['Expedientes']} expedientes")
    
    # Separar municipios GTO de otros para colores diferentes
    municipios_gto = [
        'León', 'Celaya', 'San Miguel de Allende', 'Salvatierra', 'Irapuato', 
        'Yuriria', 'Silao', 'Dolores Hidalgo C.I.N.', 'Dolores Hidalgo', 'Villagrán',
        'Tarandacuao', 'Valle de Santiago', 'Guanajuato', 'Pueblo Nuevo', 'Salamanca',
        'Cortazar', 'Apaseo el Grande', 'Acámbaro', 'Comonfort', 'San Luis de la Paz',
        'Moroleón', 'San Felipe', 'San Francisco del Rincón', 'San José Iturbide',
        'Apaseo el Alto', 'Xichú', 'Coroneo', 'Pénjamo', 'Victoria', 'Tarimoro',
        'Huanímaro', 'Purísima del Rincón', 'Tierra Blanca', 'Jerécuaro', 'Cuerámaro',
        'Abasolo', 'Santiago Maravatío', 'Santa Cruz de Juventino Rosas', 'Santa Catarina',
        'Atarjea', 'Ocampo', 'Uriangato', 'Jaral del Progreso', 'San Diego de la Unión',
        'Doctor Mora', 'Manuel Doblado', 'Romita', 'Salamaca', 'Silao de la Victoria'
    ]
    
    lugares_con_coordenadas['Tipo'] = lugares_con_coordenadas['Lugar'].apply(
        lambda x: 'Guanajuato' if x in municipios_gto else 'Otro Estado'
    )
    
    # Crear mapa
    fig = px.scatter_mapbox(
        lugares_con_coordenadas,
        lat='lat',
        lon='lon',
        size='Expedientes',
        color='Tipo',
        hover_name='Lugar',
        hover_data={'Expedientes': True, 'Tipo': False},
        size_max=30,
        zoom=6,
        center={"lat": 21.0, "lon": -101.0},
        height=600,
        title='🗺️ Distribución Geográfica de Expedientes',
        color_discrete_map={'Guanajuato': 'red', 'Otro Estado': 'blue'}
    )
    
    fig.update_layout(
        mapbox_style="open-street-map",
        margin={"r": 0, "t": 40, "l": 0, "b": 0},
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    return fig

def crear_mapa_vacio(mensaje):
    """Crear un mapa vacío con mensaje"""
    fig = go.Figure()
    fig.update_layout(
        title=f'🗺️ {mensaje}',
        annotations=[dict(text=mensaje, x=0.5, y=0.5, showarrow=False, font=dict(size=16))],
        height=400
    )
    return fig

# Para desarrollo local
#if __name__ == '__main__':
#    app.run_server(debug=True, port=8050)

# Para produccion
if __name__ == '__main__':
    import os
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    app.run_server(debug=debug, host='0.0.0.0', port=int(os.environ.get('PORT', 8050)))

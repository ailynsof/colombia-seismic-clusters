import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler
import geopandas as gpd

print("Iniciando la construcción del Dashboard V2...")

# 1. Carga y Preparación de Datos
df = pd.read_csv('data/raw/earthquakes_colombia.csv')
features = ['latitude', 'longitude', 'depth']
X = df[features]

df['year'] = pd.to_datetime(df['time']).dt.year.astype(str)
df = df.sort_values('year')

# K-Means Escala y Sin Escalar
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

kmeans_unscaled = KMeans(n_clusters=5, random_state=42, n_init=10)
df['cluster_unscaled'] = kmeans_unscaled.fit_predict(X).astype(str)

kmeans_scaled = KMeans(n_clusters=5, random_state=42, n_init=10)
df['cluster_scaled'] = kmeans_scaled.fit_predict(X_scaled).astype(str)
df['cluster'] = df['cluster_scaled']

# ================================
# GRÁFICOS EDA
# ================================
print("Generando EDA...")
# 1. Distribución Magnitud
fig_mag = px.histogram(df, x='mag', nbins=30, title='Distribución de Magnitudes', color_discrete_sequence=['#FCD116'])
html_mag = fig_mag.to_html(full_html=False, include_plotlyjs=False)

# 2. Distribución Profundidad
fig_depth = px.histogram(df, x='depth', nbins=30, title='Distribución de Profundidad (km)', color_discrete_sequence=['#CE1126'])
html_depth = fig_depth.to_html(full_html=False, include_plotlyjs=False)

# 3. Correlación
corr_matrix = df[['latitude', 'longitude', 'depth', 'mag']].corr()
fig_corr = px.imshow(corr_matrix, text_auto=True, title='Geografía vs Sismos (Correlación)', color_continuous_scale='viridis')
html_corr = fig_corr.to_html(full_html=False, include_plotlyjs=False)

# ================================
# GRÁFICOS MODELING
# ================================
print("Calculando Silhouette e Inercia...")
inertia = []
silhouette_vals = []
k_range = list(range(2, 11))
for k in k_range:
    km = KMeans(n_clusters=k, random_state=42, n_init=10)
    labels = km.fit_predict(X_scaled)
    inertia.append(km.inertia_)
    silhouette_vals.append(silhouette_score(X_scaled, labels))

fig_elbow = px.line(x=k_range, y=inertia, markers=True, title="Método del Codo (Inercia)", labels={'x':'k', 'y':'Inercia'})
fig_elbow.update_traces(line_color='#003893')
html_elbow = fig_elbow.to_html(full_html=False, include_plotlyjs=False)

fig_sil = px.line(x=k_range, y=silhouette_vals, markers=True, title="Silhouette Score", labels={'x':'k', 'y':'Score'})
fig_sil.update_traces(line_color='#CE1126')
html_sil = fig_sil.to_html(full_html=False, include_plotlyjs=False)

print("Generando Animación Temporal...")
df_melt = pd.melt(df, id_vars=['latitude', 'longitude', 'year', 'mag', 'depth', 'time'],
                  value_vars=['cluster_unscaled', 'cluster_scaled'],
                  var_name='Metodo', value_name='Cluster')
df_melt['Metodo'] = df_melt['Metodo'].replace({
    'cluster_unscaled': '1. Sin Escalar (Erróneo)',
    'cluster_scaled': '2. Con StandardScaler (Correcto)'
})
df_melt = df_melt.sort_values(by='year')

fig_anim = px.scatter(
    df_melt, x='longitude', y='latitude', animation_frame='year',
    color='Cluster', facet_col='Metodo', size='mag',
    hover_name='time', title="Comparación: La Importancia del Scaling",
    color_discrete_sequence=px.colors.qualitative.Plotly, template='plotly_white'
)
url_col_geojson = "https://raw.githubusercontent.com/johan/world.geo.json/master/countries/COL.geo.json"
colombia_gdf_anim = gpd.read_file(url_col_geojson)
for geom in colombia_gdf_anim.geometry:
    polys = [geom] if geom.geom_type == 'Polygon' else list(geom.geoms)
    for p in polys:
        x, y = p.exterior.xy
        fig_anim.add_trace(go.Scatter(x=list(x), y=list(y), mode='lines', line=dict(color='#888', width=1), showlegend=False, hoverinfo='skip'), row="all", col="all")
fig_anim.update_layout(title_font_size=20)
html_anim = fig_anim.to_html(full_html=False, include_plotlyjs=False)

# ================================
# GRÁFICOS CLUSTERS
# ================================
print("Generando Sismos por Tiempo...")
# Time series
events_per_cluster_year = df.groupby(['year', 'cluster_scaled']).size().reset_index(name='count')
fig_time = px.bar(events_per_cluster_year, x='year', y='count', color='cluster_scaled', 
                  title='Actividad Sísmica por Cluster a través del Tiempo', barmode='group',
                  color_discrete_sequence=px.colors.qualitative.Plotly)
html_time = fig_time.to_html(full_html=False, include_plotlyjs=False)

# 3D Map (Para clusters)
print("Reconstruyendo el Mapa 3D...")
fig_3d = px.scatter_3d(
    df, x='longitude', y='latitude', z='depth', color='cluster', size='mag',
    opacity=0.8, title='Mapa 3D Interactivo: Zonas Sísmicas de Colombia',
    color_discrete_sequence=px.colors.qualitative.Plotly
)
vecinos = gpd.GeoDataFrame(pd.concat([gpd.read_file(u) for u in [
    "https://raw.githubusercontent.com/johan/world.geo.json/master/countries/VEN.geo.json",
    "https://raw.githubusercontent.com/johan/world.geo.json/master/countries/ECU.geo.json",
    "https://raw.githubusercontent.com/johan/world.geo.json/master/countries/PER.geo.json",
    "https://raw.githubusercontent.com/johan/world.geo.json/master/countries/BRA.geo.json",
    "https://raw.githubusercontent.com/johan/world.geo.json/master/countries/PAN.geo.json"
]], ignore_index=True))

def add_geo(gdf, color, ancho, opacidad):
    for geom in gdf.geometry:
        polys = [geom] if geom.geom_type == 'Polygon' else list(geom.geoms)
        for p in polys:
            x, y = p.exterior.xy
            fig_3d.add_trace(go.Scatter3d(x=list(x), y=list(y), z=[0]*len(x), mode='lines',
                                          line=dict(color=color, width=ancho), opacity=opacidad, showlegend=False))

add_geo(colombia_gdf_anim, '#1a7a3a', 2.5, 1.0)
add_geo(vecinos, '#888888', 1, 0.5)

fig_3d.update_layout(
    scene=dict(
        xaxis=dict(range=[df['longitude'].min()-0.5, df['longitude'].max()+0.5]),
        yaxis=dict(range=[df['latitude'].min()-0.5, df['latitude'].max()+0.5]),
        zaxis=dict(autorange='reversed')
    ), margin=dict(l=0, r=0, b=0, t=40)
)
# Cargar Mapa 3D Geográfico específico del usuario mediante iframe
path_external_3d = "reports/figures/clusters_3d_geographic.html"
# Usamos un alto mucho mayor para que no se vea cortado ni pequeño
iframe_style = "width:100%; height:950px; border:none; border-radius:12px; box-shadow: 0 4px 12px rgba(0,0,0,0.1);"
html_3d_tab4 = f'<iframe src="{path_external_3d}" style="{iframe_style}"></iframe>'
html_3d_tab5 = f'<iframe src="{path_external_3d}" style="{iframe_style}"></iframe>'
# Nota: Dejamos el fig_3d original por si se necesita para cálculos, pero el HTML usará el iframe.

# Mapa 2D Contexto (Nuevo pedido)
print("Generando Mapa 2D Interactivo de Contexto...")
fig_context = px.scatter_mapbox(df, lat="latitude", lon="longitude", color="cluster", 
                  size="mag", hover_name="time", zoom=4.5,
                  mapbox_style="carto-positron", title="Distribución Sísmica Nacional",
                  center={"lat": 4.5709, "lon": -74.2973})
fig_context.update_layout(margin={"r":0,"t":40,"l":0,"b":0}, height=600)
html_context = fig_context.to_html(full_html=False, include_plotlyjs=False)

# ================================
# GRÁFICOS CONCLUSIÓN (MAPA 2D CLARO)
# ================================
print("Generando Mapa 2D de Alta Claridad para Conclusiones...")
fig_final_2d = px.scatter(df, x='longitude', y='latitude', color='cluster', size='mag',
                          hover_name='time', title="Mapa Definitivo de Clusters en Colombia",
                          labels={'longitude': 'Longitud', 'latitude': 'Latitud'},
                          color_discrete_sequence=px.colors.qualitative.Plotly,
                          template='plotly_white')

# Añadir bordes de Colombia muy claros
for geom in colombia_gdf_anim.geometry:
    polys = [geom] if geom.geom_type == 'Polygon' else list(geom.geoms)
    for p in polys:
        x, y = p.exterior.xy
        fig_final_2d.add_trace(go.Scatter(x=list(x), y=list(y), mode='lines', 
                                          line=dict(color='#333333', width=2), 
                                          showlegend=False, hoverinfo='skip'))

fig_final_2d.update_layout(margin={"r":0,"t":40,"l":0,"b":0}, height=650)
html_final_2d = fig_final_2d.to_html(full_html=False, include_plotlyjs=False)

print("Ensamblando HTML V3...")
html_codigo = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Colombia Sísmica - SGC Dashboard</title>
    <script src="https://cdn.plot.ly/plotly-2.32.0.min.js"></script>
    <style>
        :root {{
            --sgc-green: #104f32;
            --col-yellow: #FCD116;
            --col-blue: #003893;
            --col-red: #CE1126;
            --bg-color: #f4f7f6;
        }}
        body {{ font-family: 'Segoe UI', Arial, sans-serif; background-color: var(--bg-color); color: #333; margin: 0; padding: 0; }}
        .header {{ background: linear-gradient(135deg, var(--sgc-green) 0%, #1a202c 100%); color: white; padding: 40px 20px; text-align: center; border-bottom: 5px solid var(--col-yellow); }}
        .header h1 {{ margin: 0; font-size: 3rem; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); }}
        .header h2 {{ font-weight: 300; font-size: 1.3rem; margin-top: 10px; color: #e2e8f0; }}
        
        .container {{ max-width: 96%; margin: 30px auto; padding: 0 20px; }}
        
        .tab {{ overflow: hidden; background-color: white; border-radius: 8px 8px 0 0; display: flex; box-shadow: 0 2px 4px rgba(0,0,0,0.1); flex-wrap: wrap; }}
        .tab button {{ background-color: inherit; float: left; border: none; outline: none; cursor: pointer; padding: 18px 24px; transition: 0.3s; font-size: 1.1rem; font-weight: bold; flex: 1; color: #4a5568; border-bottom: 4px solid transparent; }}
        .tab button:hover {{ background-color: #f1f5f9; }}
        .tab button.active {{ color: var(--sgc-green); border-bottom: 4px solid var(--col-red); background-color: #f8fafc; }}
        
        .tabcontent {{ display: none; padding: 30px; background-color: white; box-shadow: 0 4px 6px rgba(0,0,0,0.05); border-radius: 0 0 8px 8px; animation: fadeEffect 0.5s; }}
        @keyframes fadeEffect {{ from {{opacity: 0;}} to {{opacity: 1;}} }}

        .intro-box {{ border-left: 6px solid var(--col-blue); padding: 20px; background: #ebf8ff; border-radius: 0 8px 8px 0; font-size: 1.15rem; color: #2c5282; line-height: 1.6; margin-bottom: 30px; }}
        .eda-note {{ background: #fffaf0; border: 1px dashed #ed8936; padding: 15px; border-radius: 8px; margin-top: 10px; font-size: 0.95rem; color: #7b341e; }}

        .cards-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 20px; margin-bottom: 30px; }}
        .kpi-card {{ background: white; border: 1px solid #e2e8f0; padding: 25px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); transition: transform 0.2s; }}
        .kpi-card:hover {{ transform: translateY(-5px); box-shadow: 0 8px 15px rgba(0,0,0,0.1); }}
        .kpi-title {{ font-size: 1.25rem; font-weight: bold; margin-bottom: 10px; padding-bottom: 10px; border-bottom: 2px solid #edf2f7; }}
        
        .graphs-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 30px; }}
        .graph-wrapper {{ border: 1px solid #e2e8f0; border-radius: 8px; padding: 10px; background: #fff; min-height: 450px; }}
        .graph-wrapper.full {{ grid-column: 1 / -1; min-height: 600px; }}
        
        .c-2 {{ border-top: 5px solid #EF553B; }}
        .c-3 {{ border-top: 5px solid #AB63FA; }}
        .c-4 {{ border-top: 5px solid #FFA15A; }}
        .c-0 {{ border-top: 5px solid #00CC96; }}
    </style>
</head>
<body>

    <div class="header">
        <h1>Colombia: Un País Movido</h1>
        <h2>Dinámica Cultural, Social y Furia Geológica (CRISP-DM)</h2>
    </div>

    <div class="container">
        <div class="tab">
            <button class="tablinks active" onclick="openTab(event, 'Contexto')">1. Contexto Geográfico</button>
            <button class="tablinks" onclick="openTab(event, 'EDA')">2. Patrones (EDA)</button>
            <button class="tablinks" onclick="openTab(event, 'Modeling')">3. K-Means (Scaling)</button>
            <button class="tablinks" onclick="openTab(event, 'Clusters')">4. Análisis Social y Clústers</button>
            <button class="tablinks" onclick="openTab(event, 'Conclusiones')">5. Conclusiones Finales</button>
        </div>

        <!-- TAB 1: CONTEXTO -->
        <div id="Contexto" class="tabcontent" style="display: block;">
            <div class="intro-box">
                <p><strong>Colombia es un país en constante movimiento.</strong> No solo por su diversidad cultural y geográfica, sino también por la intensa actividad sísmica que ocurre bajo su territorio.</p>
                <p>Ubicado en una región donde interactúan múltiples placas tectónicas, el país registra miles de sismos cada año, la mayoría imperceptibles, pero algunos con un potencial significativo de impacto sobre la población y la infraestructura.</p>
                <p>Este volumen de actividad plantea un desafío clave: no todos los sismos son iguales, ni todas las regiones del país se comportan de la misma manera. Comprender estas diferencias es fundamental para fortalecer los sistemas de monitoreo y optimizar las estrategias de alerta temprana.</p>
            </div>
            <div class="graph-wrapper full">
                {html_context}
            </div>
        </div>

        <!-- TAB 2: EDA -->
        <div id="EDA" class="tabcontent">
            <h3>Exploración Inicial (Hallazgos Clave)</h3>
            <div class="graphs-grid">
                <div>
                   <div class="graph-wrapper" style="min-height:350px;">{html_mag}</div>
                   <div class="eda-note"><strong>Nota:</strong> Predominan sismos de baja magnitud (2.0-4.0). Las magnitudes altas son inusuales y se concentran en zonas periféricas.</div>
                </div>
                <div>
                   <div class="graph-wrapper" style="min-height:350px;">{html_depth}</div>
                   <div class="eda-note"><strong>Nota:</strong> Existe una bimodalidad clara: Sismos muy superficiales (0-30km) y un pico profundo masivo (>150km, el Nido).</div>
                </div>
                <div class="graph-wrapper full">
                    {html_corr}
                    <div class="eda-note"><strong>Correlación:</strong> Se observa que la Latitud y Longitud tienen correlaciones bajas con la Magnitud, indicando que un terremoto fuerte puede ocurrir en cualquier lugar, pero su PROFUNDIDAD sí tiene patrones geográficos marcados.</div>
                </div>
            </div>
        </div>

        <!-- TAB 3: MODELING & SCALING -->
        <div id="Modeling" class="tabcontent">
            <h3>Optimización de Hiperparámetros y Scaling</h3>
            <div class="graphs-grid">
                <div class="graph-wrapper" style="min-height:500px;">{html_elbow}</div>
                <div class="graph-wrapper" style="min-height:500px;">{html_sil}</div>
                <div class="graph-wrapper full" style="min-height:850px;">
                    {html_anim}
                    <p style="text-align:center;color:#666;font-size:0.9rem; margin-top:20px;">
                        <strong>Análisis Visual:</strong> Observe cómo los gráficos están ahora plenamente expandidos. Sin Scaling, el algoritmo es ciego a la profundidad. Con Scaling, la IA "entiende" la tercera dimensión y separa los clusters geológicamente.
                    </p>
                </div>
            </div>
        </div>

        <!-- TAB 4: CLUSTERS Y SOCIEDAD -->
        <div id="Clusters" class="tabcontent">
            <div class="cards-grid">
                <div class="kpi-card c-2"><div class="kpi-title">🔴 Nido de Bucaramanga</div><p>Santander. Profundidad media: 152km. Gente de temple fuerte.</p></div>
                <div class="kpi-card c-3"><div class="kpi-title">🟣 Costa Pacífica</div><p>Sismos superficiales y fuertes. Alta vulnerabilidad social.</p></div>
                <div class="kpi-card c-4"><div class="kpi-title">🟠 Borde Ecuatoriano</div><p>Frontera sur. Máximas magnitudes registradas.</p></div>
                <div class="kpi-card c-0"><div class="kpi-title">🟢 Cordilleras Andinas</div><p>Eje central. Causantes de nuestro relieve montañoso.</p></div>
                <div class="kpi-card c-1"><div class="kpi-title">🟢 Frontera Caribe / Ven</div><p>Norte de Santander. Dinámica de reacomodación cortical.</p></div>
            </div>
            <div class="graph-wrapper full" style="min-height:950px; margin-bottom:30px; border:none; background:transparent;">{html_3d_tab4}</div>
            <div class="graph-wrapper full">{html_time}</div>
        </div>

        <!-- TAB 5: CONCLUSIONES -->
        <div id="Conclusiones" class="tabcontent">
            <div class="intro-box">
                <h3>Resumen Ejecutivo y Mosaico Sísmico 3D</h3>
                <p>Como conclusión final, presentamos el modelo 3D integral de los clusters. Esta visualización permite apreciar cómo la profundidad y la ubicación espacial definen las zonas de riesgo sísmico en Colombia.</p>
            </div>
            <div class="graph-wrapper full" style="min-height:950px; border:none; background:transparent;">
                {html_3d_tab5}
            </div>
            <div style="margin-top:20px; font-size:1.1rem; line-height:1.6;">
                <p>1. <strong>Identidad Geológica:</strong> Los clusters siguen las fallas reales de Colombia, demostrando que el K-Means con StandardScaler es una herramienta potente para la gestión del riesgo.</p>
                <p>2. <strong>Vulnerabilidad Social:</strong> Las zonas con sismos más destructivos coinciden con territorios históricamente desprotegidos. La ciencia de datos es una herramienta para la justicia social.</p>
            </div>
        </div>

    </div>

    <script>
    function openTab(evt, tabName) {{
        var i, tabcontent, tablinks;
        tabcontent = document.getElementsByClassName("tabcontent");
        for (i = 0; i < tabcontent.length; i++) tabcontent[i].style.display = "none";
        tablinks = document.getElementsByClassName("tablinks");
        for (i = 0; i < tablinks.length; i++) tablinks[i].className = tablinks[i].className.replace(" active", "");
        document.getElementById(tabName).style.display = "block";
        evt.currentTarget.className += " active";
        setTimeout(() => {{ window.dispatchEvent(new Event('resize')); }}, 150);
    }}
    </script>
</body>
</html>
"""


with open("index.html", "w", encoding="utf-8") as file:
    file.write(html_codigo)

print("¡Dashboard Tabulado 'index.html' creado exitosamente!")

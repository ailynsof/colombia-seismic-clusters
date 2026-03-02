import nbformat as nbf
import os
import pandas as pd

# Directorios
os.makedirs('notebooks', exist_ok=True)

nb = nbf.v4.new_notebook()

# 1. TÍTULO Y CONTEXTO
nb['cells'].append(nbf.v4.new_markdown_cell("# Taller 1: Análisis de Clustering de Sismicidad en Colombia\n"
                                          "**Autor:** Ailyn Sofía\n"
                                          "**Metodología:** CRISP-DM\n\n"
                                          "## Introducción\n"
                                          "Colombia es un país en constante movimiento. Ubicado en una zona de alta complejidad tectónica (Placas de Nazca, Suramericana y Caribe), el país registra miles de eventos sísmicos. "
                                          "Este notebook documenta el proceso de identificación de patrones sísmicos mediante **Machine Learning (K-Means Clustering)**."))

# 2. SETUP E IMPORTACIÓN
nb['cells'].append(nbf.v4.new_markdown_cell("## 1. Data Understanding (Entendimiento de Datos)\n"
                                          "Cargamos las librerías necesarias y el dataset oficial del Servicio Geológico Colombiano."))
nb['cells'].append(nbf.v4.new_code_cell("import pandas as pd\n"
                                       "import numpy as np\n"
                                       "import matplotlib.pyplot as plt\n"
                                       "import seaborn as sns\n"
                                       "from sklearn.cluster import KMeans\n"
                                       "from sklearn.preprocessing import StandardScaler\n"
                                       "from sklearn.metrics import silhouette_score\n\n"
                                       "plt.style.use('ggplot')\n"
                                       "sns.set_palette('viridis')\n\n"
                                       "# Cargar datos\n"
                                       "df = pd.read_csv('../data/raw/earthquakes_colombia.csv')\n"
                                       "print(f'Registros cargados: {len(df)}')\n"
                                       "df.head()"))

# 3. EDA BÁSICO
nb['cells'].append(nbf.v4.new_markdown_cell("### Análisis Exploratorio (EDA)\n"
                                          "Buscamos heterogeneidad en la profundidad y magnitud, lo que justifica la segmentación por clusters."))
nb['cells'].append(nbf.v4.new_code_cell("critical_vars = ['latitude', 'longitude', 'depth', 'mag']\n"
                                       "fig, axes = plt.subplots(1, 2, figsize=(15, 5))\n\n"
                                       "sns.histplot(df['depth'], kde=True, ax=axes[0], color='blue')\n"
                                       "axes[0].set_title('Distribución de Profundidad (km)')\n\n"
                                       "sns.histplot(df['mag'], kde=True, ax=axes[1], color='orange')\n"
                                       "axes[1].set_title('Distribución de Magnitud')\n\n"
                                       "plt.show()"))

# 4. DATA PREPARATION
nb['cells'].append(nbf.v4.new_markdown_cell("## 2. Data Preparation (Preparación de Datos)\n"
                                          "Dado que la profundidad se mide en km (0-600) y las coordenadas en grados (-80 a 15), es crítico realizar un **Escalamiento Estándar** para que el algoritmo no ignore la profundidad."))
nb['cells'].append(nbf.v4.new_code_cell("features = ['latitude', 'longitude', 'depth']\n"
                                       "scaler = StandardScaler()\n"
                                       "df_scaled = scaler.fit_transform(df[features])\n\n"
                                       "print('Muestra de datos escalados (Normalizados):')\n"
                                       "print(df_scaled[:5])"))

# 5. MODELING (CODO Y SILHOUETTE)
nb['cells'].append(nbf.v4.new_markdown_cell("## 3. Modeling (Modelado)\n"
                                          "Utilizamos el método del Codo (Inercia) y el Score de Silueta para determinar el número óptimo de clusters (K)."))
nb['cells'].append(nbf.v4.new_code_cell("inertia = []\n"
                                       "silhouette_avg = []\n"
                                       "K_range = range(2, 10)\n\n"
                                       "for k in K_range:\n"
                                       "    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)\n"
                                       "    cluster_labels = kmeans.fit_predict(df_scaled)\n"
                                       "    inertia.append(kmeans.inertia_)\n"
                                       "    silhouette_avg.append(silhouette_score(df_scaled, cluster_labels))\n\n"
                                       "fig, ax1 = plt.subplots(figsize=(10, 5))\n\n"
                                       "ax1.plot(K_range, inertia, 'bx-')\n"
                                       "ax1.set_xlabel('Número de Clusters (k)')\n"
                                       "ax1.set_ylabel('Inercia (Codo)', color='b')\n\n"
                                       "ax2 = ax1.twinx()\n"
                                       "ax2.plot(K_range, silhouette_avg, 'ro-')\n"
                                       "ax2.set_ylabel('Silhouette Score', color='r')\n\n"
                                       "plt.title('Selección de K: Codo vs Silhouette')\n"
                                       "plt.show()"))

# 6. FINAL MODELING
nb['cells'].append(nbf.v4.new_markdown_cell("### Modelo Final: K=5\n"
                                          "Seleccionamos K=5 para capturar la diversidad regional (Norte, Sur, Pacífico, Centro y Nido de Bucaramanga)."))
nb['cells'].append(nbf.v4.new_code_cell("kmeans_final = KMeans(n_clusters=5, random_state=42, n_init=10)\n"
                                       "df['cluster'] = kmeans_final.fit_predict(df_scaled)\n\n"
                                       "print('Distribución de eventos por cluster:')\n"
                                       "print(df['cluster'].value_counts())"))

# 7. VISUALIZACIÓN 2D
nb['cells'].append(nbf.v4.new_markdown_cell("## 4. Evaluation (Evaluación)\n"
                                          "Visualizamos geográficamente los clusters identificados."))
nb['cells'].append(nbf.v4.new_code_cell("plt.figure(figsize=(10, 12))\n"
                                       "sns.scatterplot(data=df, x='longitude', y='latitude', hue='cluster', palette='viridis', alpha=0.6, s=20)\n"
                                       "plt.title('Mapa de Clusters Sísmicos en Colombia (Vista 2D)')\n"
                                       "plt.legend(title='Cluster', bbox_to_anchor=(1.05, 1), loc='upper left')\n"
                                       "plt.show()"))

# 8. ANALISIS SOCIAL Y GEOLOGICO
nb['cells'].append(nbf.v4.new_markdown_cell("## 5. Análisis Geográfico-Social\n"
                                          "De acuerdo a los resultados, identificamos las siguientes zonas críticas:\n\n"
                                          "1. **Nido sísmico de Bucaramanga (Santander):** Zona de alta profundidad, única en el mundo por su concentración.\n"
                                          "2. **Costa Pacífica (Chocó/Nariño):** Sismos superficiales con alto potencial destructivo en zonas socialmente vulnerables.\n"
                                          "3. **Eje Andino:** Concentración poblacional sobre fallas activas.\n"
                                          "4. **Frontera Sur y Caribe:** Zonas de acomodación cortical.\n\n"
                                          "Para una experiencia interactiva completa, visite el Dashboard desplegado:\n"
                                          "**[https://colombia-seismic-clusters.vercel.app](https://colombia-seismic-clusters.vercel.app)**"))

# GUARDAR
with open('notebooks/Taller1_KMeans_Sismicidad_Full.ipynb', 'w') as f:
    nbf.write(nb, f)

print("Notebook 'notebooks/Taller1_KMeans_Sismicidad_Full.ipynb' generado con éxito.")

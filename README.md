# 🌍 Colombia: Un País en Movimiento
## ⚡ Reporte Ejecutivo: Clustering de Actividad Sísmica mediante CRISP-DM

> **Dashboard Interactivo:** [https://colombia-seismic-clusters.vercel.app](https://colombia-seismic-clusters.vercel.app)

---

## 📋 Resumen Ejecutivo
Colombia es un país definido por su dinamismo. No solo por su vibrante cultura y geografía, sino por la intensa actividad bajo sus pies. Ubicado en la convergencia de las placas de **Nazca, Caribe y Sudamericana**, el territorio registra miles de sismos anualmente. 

Este proyecto aplica **Machine Learning (K-Means Clustering)** sobre datos instrumentales para identificar automáticamente zonas sísmicas con comportamientos similares. El objetivo es transformar datos históricos en conocimiento accionable para la **priorización de monitoreo** y el fortalecimiento de los sistemas de alerta temprana del país.

---

## 🛠️ Metodología CRISP-DM

### 1. Comprensión del Negocio (Business Understanding)
**Pregunta Central:** ¿Podemos agrupar automáticamente la sismicidad para optimizar recursos de monitoreo?
- **Objetivo:** Diferenciar zonas superficiales de alto impacto social de zonas profundas geológicamente únicas.
- **Éxito:** Redescubrir mediante procesos de IA estructuras conocidas como el **Nido de Bucaramanga** y segmentar el **Cinturón del Pacífico**.

### 2. Comprensión y Preparación de los Datos (Data Understanding & Prep)
Se utilizó el catálogo sísmico del USGS (2,791 registros) con variables clave: `latitude`, `longitude`, `depth` y `mag`.

> [!IMPORTANT]
> **El Secreto del Éxito: StandardScaler**  
> Sin escalamiento, el algoritmo ignoraba la profundidad (0-600 km) frente a las coordenadas (-80 a 15). Al aplicar **StandardScaler**, logramos que la IA "viera" la tercera dimensión, logrando una separación geológicamente coherente.

### 3. Modelamiento y Selección de K
Evaluamos $k$ entre 2 y 10. La selección final de **k = 5** fue validada mediante:
1.  **Método del Codo (Inercia):** Estabilización clara de la varianza.
2.  **Silhouette Score:** Garantía de que los clusters están bien definidos.
3.  **Juicio Experto:** Correspondencia con las fallas geológicas reales de Colombia.

---

## 📊 Análisis de Clusters: Geología y Sociedad

### 🟥 Cluster 2 — El Nido Sísmico de Bucaramanga (Santander)
- **Profundidad:** ~152 km.
- **Contexto:** Uno de los fenómenos más activos del mundo. El algoritmo aisló perfectamente esta "nube" de sismos de alta profundidad. 
- **Narrativa:** Representa la resiliencia de los santandereanos, quienes han aprendido a convivir con un subsuelo que nunca descansa.

### 🟪 Cluster 3 — La Furia del Pacífico (Chocó / Litoral)
- **Profundidad:** ~30 km (Superficial).
- **Magnitud:** Promedio 4.57 (El más alto del país).
- **Narrativa:** Refleja una zona históricamente marginada socialmente que, además, enfrenta el mayor percance geológico por su baja profundidad y alta magnitud. Es la prioridad #1 para prevención de tsunamis.

### 🟧 Cluster 4 — Borde Ecuatoriano (Cauca / Nariño)
- **Contexto:** Extensión sur del cinturón de fuego.
- **Dato Crítico:** Incluye el evento de magnitud 7.8, el más destructivo registrado en la zona.

### 🟩 Cluster 0 — El Eje de las Cordilleras (Centro / Andino)
- **Interpretación:** Sismicidad que define nuestra orografía. Es el corazón habitado del país donde el riesgo sísmico se cruza con la mayor densidad poblacional e infraestructura.

### light-green Cluster 1 — Frontera Caribe / Ven (Norte de Santander)
- **Contexto:** Dinámica de reacomodación cortical en el nororiente.
- **Narrativa:** Una zona de alto flujo migratorio y social, donde el ajuste de la tierra se suma a los desafíos de integración regional.

---

## 🚀 Impacto y Recomendaciones Técnicas

1.  **Priorización Táctica:** Se recomienda al **Servicio Geológico Colombiano** priorizar la instrumentación del **Cluster 3** debido a su alta peligrosidad superficial.
2.  **Optimización de Alertas:** Utilizar el modelo de clusters para calibrar umbrales de alerta diferenciados por región.
3.  **Justicia Social:** Integrar estos clusters con mapas de pobreza multidimensional para dirigir recursos de prevención a las zonas más vulnerables (específicamente la Costa Pacífica).

---

## 📂 Recursos del Proyecto
- 🌐 **Dashboard Vivo:** [Enlace Vercel](https://colombia-seismic-clusters.vercel.app)
- 📓 **Notebook CRISP-DM:** [Ver Taller1_KMeans_Sismicidad_Full.ipynb](notebooks/Taller1_KMeans_Sismicidad_Full.ipynb)
- 🏗️ **Código Fuente:** [Script del Dashboard](create_dashboard.py)

---
*Este reporte fue generado con orgullo para el Taller 1 de Machine Learning, buscando unir la precisión técnica con la realidad social de Colombia.*

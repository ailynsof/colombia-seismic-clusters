# Reporte Ejecutivo: Clustering de Actividad Sísmica en Colombia

---

## Resumen
Colombia posee una de las sismicidades más complejas del planeta debido a la interacción de las placas tectónicas Nazca, Caribe y Sudamericana. El Servicio Geológico Colombiano (SGC) genera miles de datos instrumentales anuales, lo que plantea un desafío: ¿cómo agrupar automáticamente estos eventos para priorizar recursos de monitoreo?

En este estudio, aplicamos la metodología **CRISP-DM** y el algoritmo **K-Means Clustering** a 2,791 sismos. A diferencia de las clasificaciones geográficas tradicionales "planas", nuestro análisis integra la **profundidad** como dimensión fundamental a través del escalamiento estándar. Los resultados permitieron identificar 5 grandes áreas sísmicas, incluyendo el redescubrimiento autónomo del fenómeno geológico conocido como el **Nido Sísmico de Bucaramanga**, validando la potencia del algoritmo para la gestión del riesgo nacional.

---

## Metodología (CRISP-DM)

### 1. Business Understanding (Comprensión del Negocio)
El problema principal radica en la incapacidad de los analistas humanos para procesar y agrupar miles de sismos en tiempo real basándose en múltiples variables simultáneas. El **clustering no supervisado** es apropiado porque no contamos con etiquetas previas de "zonas sísmicas unificadas"; el algoritmo debe encontrar estructuras ocultas por sí mismo. Los stakeholders (SGC, UNGRD) utilizarán estos resultados para focalizar planes de contingencia y ubicar estaciones de sensoría en los puntos de mayor "atención" por cluster.

### 2. Data Understanding (Comprensión de los Datos)
Exploramos un dataset del USGS con sismos ocurridos entre 2010 y 2026. Hallazgos clave del EDA:
- **Multimodalidad**: La profundidad presenta un pico pronunciado cerca de los 150 km, sugiriendo una estructura geológica masiva bajo tierra.
- **Correlación**: Existe una baja correlación entre magnitud y profundidad, lo que indica que sismos superficiales pueden ser tan fuertes como los profundos.
- **Integridad**: No se detectaron nulos en variables críticas (Latitud, Longitud, Profundidad).

### 3. Data Preparation (Preparación de los Datos)
- **Selección de Features**: Se utilizaron Latitude, Longitude y Depth. No se usó Magnitud para el entrenamiento con el fin de agrupar por "fuente geológica" y no por "impacto", permitiendo luego evaluar el impacto (magnitud) en cada fuente.
- **Scaling**: Se aplicó `StandardScaler`. Sin escalamiento, la profundidad (0-600) abrumaría a las coordenadas (-80 a 13).

### 4. Modeling (Modelamiento)
Entrenamos modelos para k de 2 a 10.
- **Método del Codo**: Mostró una inflexión útil en k=5.
- **Silhouette Score**: Validó k=2 como el más matemáticamente coherente, pero **k=5** como el más **interpretable** para los objetivos de negocio del SGC.

### 5. Evaluation (Evaluación)
Los clusters dividen el país en zonas de subducción costera (superficiales), nidos sísmicos (profundos) e intraplaca (andino).

---

## Resultados (Perfiles de Clusters)

| Cluster | Significado | n (sismos) | Profundidad (Avg ± Std) | Magnitud (Avg) | Hallazgos |
|---------|-------------|------------|-------------------------|----------------|-----------|
| **C2** | **Nido de Bucaramanga** | 765 | 152 ± 15.7 km | 4.41 | **Fenómeno Descubierto**: Aislamiento preciso de una nube profunda al nororiente. |
| **C3** | **Pacífico Norte** | 535 | 30 ± 23.7 km | 4.57 | **Prioridad**: Sismos más fuertes y superficiales (alto riesgo social). |
| **C4** | **Subducción Sur** | 782 | 28 ± 22.1 km | 4.38 | Captura el sismo histórico de magnitud 7.8 (el más destructivo). |
| **C0** | **Sur Profundo** | 330 | 139 ± 32.8 km | 4.54 | Concentración profunda en frontera con Ecuador/Perú. |
| **C1** | **Borde Caribe** | 379 | 18 ± 14.6 km | 4.25 | Sismicidad cortical en la costa norte y frontera con Venezuela. |

---

## Impacto del Scaling
Este fue el paso más crítico del taller:
- **Sin Escalamiento**: K-Means segmentó a Colombia en "rebanadas" verticales (Norte y Sur). Esto ocurre porque las pequeñas variaciones en Longitud pesaban más que los cambios en profundidad.
- **Con Escalamiento**: El algoritmo integró la dimensión Z (Profundidad). Esto permitió que sismos que ocurren en las mismas coordenadas (Bucaramanga superficial vs Bucaramanga profunda) fueran asignados a clusters distintos, revelando la verdadera arquitectura tectónica del país.

---

## Recomendaciones para el SGC
1. **Priorización de Alerta Temprana en Cluster 3**: Debido a su baja profundidad (30 km) y alta magnitud promedio (4.57), es donde los ciudadanos tienen menos tiempo para reaccionar.
2. **Estudio de Estabilidad en Cluster 2**: Monitorear el Nido de Bucaramanga para detectar posibles anomalías en la frecuencia de disparo del acumulado detectado por el algoritmo.
3. **Optimización de Red de Estaciones**: Reforzar la instrumentación en el **Cluster 1**, ya que presenta mayor desviación estándar en profundidad, sugiriendo fallas corticales menos estudiadas.

---

## Conclusiones
K-Means no "descubre la verdad", sino que revela **estructura**.
- **Lo que puede hacer**: Agrupar automáticamente miles de eventos en segundos, reduciendo la carga de trabajo de los geólogos y eliminando sesgos humanos.
- **Lo que NO puede hacer**: Predecir cuándo ocurrirá un sismo o identificar el nombre exacto de una falla geológica subyacente sin el apoyo del experto humano (Domain Knowledge).
En conclusión, el clustering es una herramienta de **soporte a la decisión**, no un sustituto del geólogo.

---

## Referencias
- USGS Earthquake Hazards Program (Datos instrumentales 2010-2026).
- Scikit-learn: Machine Learning en Python (Guía oficial de K-Means).
- Guía metodológica ML1-2026I, Universidad Externado de Colombia.
- Dashboard de visualización interactiva: [Vercel Link](https://colombia-seismic-clusters.vercel.app).

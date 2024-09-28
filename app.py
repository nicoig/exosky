import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from astropy.coordinates import SkyCoord
import astropy.units as u
import matplotlib.pyplot as plt
import os
from PIL import Image

# Configuración de la página
st.set_page_config(page_title="🌌 Exosky! - NASA Space Apps Challenge 2024", page_icon="🌠", layout="wide")

# Crear dos columnas para el encabezado
col1, col2 = st.columns([7, 3])

# Título en la columna izquierda (70% del ancho)
with col1:
    st.title("🌌 Exosky!")
    st.subheader("NASA Space Apps Challenge 2024")

# Logo en la columna derecha (30% del ancho)
with col2:
    nasa_logo = Image.open("img/nasa_white.png")
    st.image(nasa_logo, width=250)

# Descripción debajo del encabezado
st.markdown("""
Bienvenido a **Exosky!**, una aplicación interactiva que te permite explorar cómo se vería el cielo nocturno desde cualquier exoplaneta.
""")

# Ajustar colores para mejor visibilidad
st.markdown("""
<style>
.stApp {
    background-color: #0E1117;
    color: #FAFAFA;
}
</style>
""", unsafe_allow_html=True)

# Cargar Datos
@st.cache_data
def cargar_datos():
    ruta_exoplanetas = os.path.join("Output", "exoplanetas_procesados.csv")
    ruta_estrellas = os.path.join("Output", "estrellas.csv")
    exoplanetas = pd.read_csv(ruta_exoplanetas)
    estrellas = pd.read_csv(ruta_estrellas)
    return exoplanetas, estrellas

exoplanetas, estrellas = cargar_datos()

# Barra Lateral - Selección de Exoplaneta
st.sidebar.header("🔭 Selecciona un Exoplaneta")
nombre_planeta = st.sidebar.selectbox("Elige un exoplaneta:", exoplanetas['pl_name'].sort_values())
exoplaneta = exoplanetas[exoplanetas['pl_name'] == nombre_planeta].iloc[0]

# Mostrar Información del Exoplaneta
st.sidebar.subheader("📌 Información del Exoplaneta")
st.sidebar.write(f"**Nombre:** {exoplaneta['pl_name']}")
st.sidebar.write(f"**Distancia (parsecs):** {exoplaneta['sy_dist']:.2f}")
st.sidebar.write(f"**RA:** {exoplaneta['ra']:.2f}°")
st.sidebar.write(f"**Dec:** {exoplaneta['dec']:.2f}°")

# Filtrar estrellas visibles
def estrellas_visibles(estrellas, ra_planeta, dec_planeta, limite_magnitud=15):
    coords_planeta = SkyCoord(ra=ra_planeta*u.degree, dec=dec_planeta*u.degree)
    estrellas_filtradas = estrellas[estrellas['phot_g_mean_mag'] < limite_magnitud].copy()
    
    coords_estrellas = SkyCoord(ra=estrellas_filtradas['ra'].values*u.degree, 
                                dec=estrellas_filtradas['dec'].values*u.degree)
    
    separaciones = coords_planeta.separation(coords_estrellas)
    estrellas_filtradas['separacion'] = separaciones.degree
    return estrellas_filtradas[estrellas_filtradas['separacion'] < 90]

estrellas_vis = estrellas_visibles(estrellas, exoplaneta['ra'], exoplaneta['dec'])

# Calcular magnitud aparente (ajustado para usar solo la magnitud observada)
def calcular_magnitud_aparente(magnitud_observada):
    return magnitud_observada

estrellas_vis['magnitud_aparente'] = calcular_magnitud_aparente(estrellas_vis['phot_g_mean_mag'])

# Visualización 2D del Cielo Nocturno
st.header("🌟 Cielo Nocturno Interactivo (2D)")

# Función para crear el mapa estelar 2D (mantén tu función existente)
def crear_mapa_estelar_mejorado(exoplaneta, estrellas_vis):
    tamano_estrellas = 20 / (estrellas_vis['magnitud_aparente'] + 5)
    
    fig = px.scatter(
        estrellas_vis,
        x='ra',
        y='dec',
        size=tamano_estrellas,
        color='magnitud_aparente',
        color_continuous_scale='Viridis',
        hover_name='SOURCE_ID',
        hover_data={
            'ra': ':.2f',
            'dec': ':.2f',
            'magnitud_aparente': ':.2f'
        },
        labels={
            'ra': 'Ascensión Recta (grados)',
            'dec': 'Declinación (grados)',
            'magnitud_aparente': 'Magnitud Aparente'
        },
        title=f'Cielo nocturno desde {exoplaneta["pl_name"]}'
    )
    
    fig.update_layout(
        height=800,
        xaxis=dict(autorange='reversed'),
        dragmode='pan',
        hovermode='closest',
        plot_bgcolor='black',
        paper_bgcolor='black',
        font_color='white'
    )
    
    return fig

fig_mapa_estelar = crear_mapa_estelar_mejorado(exoplaneta, estrellas_vis)
st.plotly_chart(fig_mapa_estelar, use_container_width=True)

st.markdown("""
**Explicación del Mapa Estelar 2D:**
- **Ascensión Recta (eje X):** Representa la coordenada angular este-oeste de las estrellas en el cielo. Valores más bajos (hacia la izquierda) indican posiciones más hacia el oeste.
- **Declinación (eje Y):** Representa la coordenada angular norte-sur de las estrellas. Valores más altos indican posiciones más hacia el norte en el cielo.
- **Color de los puntos:** Indica la magnitud aparente de las estrellas. Los colores más brillantes representan estrellas que aparecen más brillantes desde el exoplaneta.
- **Tamaño de los puntos:** También representa la magnitud aparente. Puntos más grandes indican estrellas que aparecen más brillantes.

Este mapa 2D muestra la distribución de las estrellas en el cielo nocturno del exoplaneta, ofreciendo una vista plana similar a un mapa celeste tradicional.
""")

# Visualización 3D del Cielo Nocturno
st.header("🌠 Exploración Tridimensional del Cielo (3D)")

def crear_grafico_3d(estrellas_vis, exoplaneta):
    fig = go.Figure(data=[go.Scatter3d(
        x=estrellas_vis['ra'],
        y=estrellas_vis['dec'],
        z=estrellas_vis['phot_g_mean_mag'],
        mode='markers',
        marker=dict(
            size=5,
            color=estrellas_vis['phot_g_mean_mag'],
            colorscale='Viridis',
            opacity=0.8
        ),
        text=estrellas_vis['SOURCE_ID'],
        hoverinfo='text'
    )])

    fig.update_layout(
        title=f'Distribución 3D de estrellas visibles desde {exoplaneta["pl_name"]}',
        scene=dict(
            xaxis_title='Ascensión Recta',
            yaxis_title='Declinación',
            zaxis_title='Magnitud Aparente'
        ),
        height=700
    )

    st.plotly_chart(fig, use_container_width=True)

crear_grafico_3d(estrellas_vis, exoplaneta)

st.markdown("""
**Explicación del gráfico 3D:**
- **Eje X:** Ascensión Recta - posición este-oeste de la estrella en el cielo.
- **Eje Y:** Declinación - posición norte-sur de la estrella en el cielo.
- **Eje Z:** Magnitud Aparente - brillo percibido de la estrella desde el exoplaneta.
- **Color:** También representa la Magnitud Aparente, facilitando la identificación visual del brillo.

Este gráfico 3D expande la visualización 2D anterior, permitiendo una exploración más inmersiva del cielo nocturno del exoplaneta. Aquí puedes:
1. Ver la distribución espacial de las estrellas en tres dimensiones.
2. Apreciar cómo el brillo de las estrellas varía en diferentes partes del cielo.
3. Interactuar con el gráfico rotándolo y haciendo zoom para explorar desde diferentes ángulos.
4. Comparar fácilmente la densidad de estrellas brillantes y tenues en distintas regiones del cielo.

La transición del mapa 2D a esta representación 3D ofrece una perspectiva más completa y envolvente de cómo sería observar el cielo desde este exoplaneta distante.
""")

# Distribución de Magnitudes Estelares
st.header("📊 Distribución de Magnitudes Estelares")
fig_hist = px.histogram(estrellas_vis, x='magnitud_aparente', nbins=50,
                        title=f"Distribución de Magnitudes Estelares visibles desde {exoplaneta['pl_name']}",
                        labels={'magnitud_aparente': 'Magnitud Aparente', 'count': 'Número de Estrellas'},
                        color_discrete_sequence=['#00CED1'])  # Color turquesa
fig_hist.update_layout(
    height=500,
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    font_color='#FFFFFF'
)
st.plotly_chart(fig_hist, use_container_width=True)
st.markdown("""
**Explicación de la Distribución de Magnitudes Estelares:**
- **Magnitud Aparente (eje X):** Representa el brillo percibido de las estrellas desde el exoplaneta. Valores más bajos indican estrellas más brillantes.
- **Número de Estrellas (eje Y):** Muestra cuántas estrellas hay en cada rango de magnitud.
- **Interpretación:** Este histograma ayuda a entender la composición del cielo nocturno del exoplaneta. Un pico en magnitudes más bajas sugeriría un cielo con muchas estrellas brillantes visibles, mientras que un pico en magnitudes más altas indicaría un cielo dominado por estrellas más tenues.
""")

# Comparación de Brillo
st.header("💫 Comparación de Brillo Real vs Aparente")
fig_brillo = px.scatter(
    estrellas_vis,
    x='phot_g_mean_mag',
    y='magnitud_aparente',
    hover_name='SOURCE_ID',
    labels={
        'phot_g_mean_mag': 'Magnitud Real',
        'magnitud_aparente': 'Magnitud Aparente'
    },
    title='Comparación de Brillo Real vs Aparente',
    color='phot_g_mean_mag',
    color_continuous_scale='Viridis'
)
fig_brillo.update_layout(
    height=600,
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    font_color='#FFFFFF'
)
st.plotly_chart(fig_brillo, use_container_width=True)
st.markdown("""
**Explicación de la Comparación de Brillo Real vs Aparente:**
- **Magnitud Real (eje X):** Representa el brillo intrínseco de las estrellas, independiente de su distancia.
- **Magnitud Aparente (eje Y):** Muestra cómo se percibiría el brillo de estas estrellas desde el exoplaneta.
- **Color:** Indica la magnitud real, con colores más brillantes para estrellas intrínsecamente más luminosas.
- **Interpretación:** Este gráfico permite comparar cómo el brillo de las estrellas cambia desde la perspectiva del exoplaneta. Puntos que se desvían de la diagonal principal representan estrellas cuyo brillo aparente difiere significativamente de su brillo real debido a su distancia relativa al exoplaneta.
""")

# Función para crear constelaciones personalizadas
def crear_constelacion():
    st.subheader("🎨 Crea tu propia constelación")
    nombre_constelacion = st.text_input("Nombre de la constelación:")
    estrellas_seleccionadas = st.multiselect("Selecciona las estrellas:", estrellas_vis['SOURCE_ID'])
    
    if st.button("Guardar constelación"):
        # Aquí guardarías la constelación en una base de datos o archivo
        st.success(f"Constelación '{nombre_constelacion}' guardada con éxito!")
    
    return nombre_constelacion, estrellas_seleccionadas

nombre, estrellas = crear_constelacion()

# Función para exportar la imagen del cielo nocturno
def exportar_imagen():
    st.subheader("📷 Exportar imagen del cielo nocturno")
    if st.button("Generar imagen de alta calidad"):
        fig, ax = plt.subplots(figsize=(20, 10), facecolor='black')
        scatter = ax.scatter(estrellas_vis['ra'], estrellas_vis['dec'], 
                             c=estrellas_vis['magnitud_aparente'], 
                             s=1/estrellas_vis['magnitud_aparente']*10, 
                             cmap='viridis')
        cbar = plt.colorbar(scatter, label='Magnitud aparente')
        cbar.ax.yaxis.set_tick_params(color='white')
        cbar.outline.set_edgecolor('white')
        plt.setp(plt.getp(cbar.ax.axes, 'yticklabels'), color='white')
        cbar.set_label('Magnitud aparente', color='white')
        
        ax.set_facecolor('black')
        ax.set_xlabel('Ascensión Recta', color='white')
        ax.set_ylabel('Declinación', color='white')
        ax.set_title(f"Cielo nocturno desde {exoplaneta['pl_name']}", color='white')
        ax.tick_params(colors='white')
        ax.grid(color='white', linestyle=':', alpha=0.3)
        
        plt.savefig("cielo_nocturno.png", dpi=300, bbox_inches='tight', facecolor='black')
        
        st.image("cielo_nocturno.png", caption="Vista previa de la imagen generada")
        
        with open("cielo_nocturno.png", "rb") as file:
            btn = st.download_button(
                label="Descargar imagen",
                data=file,
                file_name="cielo_nocturno.png",
                mime="image/png"
            )
    
    st.markdown("""
    **Explicación del gráfico:**
    - **Ascensión Recta (eje X):** Representa la coordenada angular este-oeste de una estrella en el cielo. Valores más altos indican posiciones más hacia el este.
    - **Declinación (eje Y):** Representa la coordenada angular norte-sur de una estrella. Valores más altos indican posiciones más hacia el norte.
    - **Color de los puntos:** Indica la magnitud aparente de las estrellas. Colores más brillantes (amarillo/verde) representan estrellas más brillantes, mientras que colores más oscuros (azul/violeta) representan estrellas menos brillantes.
    - **Tamaño de los puntos:** También representa la magnitud aparente. Puntos más grandes indican estrellas más brillantes.

    Este mapa estelar muestra cómo se vería el cielo nocturno desde el exoplaneta seleccionado, permitiendo visualizar la distribución y brillo de las estrellas desde esa perspectiva única.
    """)

exportar_imagen()

# Créditos y Recursos
st.sidebar.markdown("---")
st.sidebar.markdown("""
**Recursos Utilizados:**
- [NASA Exoplanet Archive](https://exoplanetarchive.ipac.caltech.edu/)
- [ESA Gaia DR3 Catalog](https://www.cosmos.esa.int/web/gaia/dr3)

Desarrollado para el NASA International Space Apps Challenge 2024
""")

# Logo de Cordillera al final de la barra lateral
cordillera_logo = Image.open("img/cordillera_white.png")
st.sidebar.image(cordillera_logo, width=250)

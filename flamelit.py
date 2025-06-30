import streamlit as st
import geopandas as gpd
import folium
from streamlit_folium import st_folium

# Carregar shapefiles
cidades = gpd.read_file("cidades-pr.shp").to_crs(epsg=4326)
queimadas = gpd.read_file("queimadas-pr.shp").to_crs(epsg=4326)

# Criar coluna de contagem de queimadas por cidade
cidades['qtd_queimadas'] = cidades.geometry.apply(
    lambda geom: queimadas[queimadas.within(geom)].shape[0]
)

# Criar coluna de popup em HTML
cidades['popup_html'] = cidades.apply(
    lambda row: f"<strong>{row['NM_MUN']}</strong><br>Queimadas: {row['qtd_queimadas']}", axis=1
)

# Criar mapa
m = folium.Map(location=[-24.5, -51.5], zoom_start=7)

# Adicionar GeoJson com popup
folium.GeoJson(
    cidades,
    name="Cidades",
    style_function=lambda x: {
        'fillColor': 'blue',
        'color': 'black',
        'weight': 1,
        'fillOpacity': 0.3,
    },
    tooltip=folium.GeoJsonTooltip(fields=['NM_MUN'], aliases=['Cidade:']),
    popup=folium.GeoJsonPopup(fields=['popup_html'], labels=False, max_width=300)
).add_to(m)

# Mostrar no Streamlit
st.title("Mapa Interativo de Queimadas no Paraná")
st_folium(m, width=800, height=600)

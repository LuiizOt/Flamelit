import streamlit as st
import geopandas as gpd
import folium
from streamlit_folium import st_folium

# Carregar os shapefiles
cidades = gpd.read_file("cidades-pr.shp").to_crs(epsg=4326)
queimadas = gpd.read_file("queimadas-pr.shp").to_crs(epsg=4326)

st.title("Mapa Interativo de Queimadas no Paraná")

# Criar o mapa centralizado no PR
m = folium.Map(location=[-24.5, -51.5], zoom_start=7)

# Função para contar queimadas e gerar popup
def gerar_popup(feature):
    codigo = feature['properties']['CD_MUN']
    nome = feature['properties']['NM_MUN']
    geom = cidades[cidades['CD_MUN'] == codigo].geometry.iloc[0]
    qtd = queimadas[queimadas.within(geom)].shape[0]
    return f"<strong>{nome}</strong><br>Queimadas: {qtd}"

# Adicionar GeoJson dos municípios com popup
folium.GeoJson(
    cidades,
    name="Cidades",
    style_function=lambda x: {
        'fillColor': 'blue',
        'color': 'black',
        'weight': 1,
        'fillOpacity': 0.2,
    },
    tooltip=folium.GeoJsonTooltip(fields=['NM_MUN'], aliases=['Cidade:']),
    popup=folium.GeoJsonPopup(fields=[], labels=False, parse_html=False,
        script=True, max_width=300,
        html=lambda feat: gerar_popup(fe_

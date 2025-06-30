import streamlit as st
import geopandas as gpd
import folium
from streamlit_folium import st_folium

# Carregar shapefiles
cidades = gpd.read_file("cidades-pr.shp").to_crs(epsg=4326)
queimadas = gpd.read_file("queimadas-pr.shp").to_crs(epsg=4326)

# Contar queimadas por cidade
cidades['qtd_queimadas'] = cidades.geometry.apply(
    lambda geom: queimadas[queimadas.within(geom)].shape[0]
)

# Criar popup HTML
cidades['popup_html'] = cidades.apply(
    lambda row: f"<strong>{row['NM_MUN']}</strong><br>Queimadas: {row['qtd_queimadas']}", axis=1
)

# Função para definir cor com base na quantidade
def get_cor(qtd):
    if qtd == 0:
        return 'white'
    elif qtd <= 3:
        return 'yellow'
    else:
        return 'red'

# Criar mapa
m = folium.Map(location=[-24.5, -51.5], zoom_start=7)

# Adicionar GeoJson com estilo baseado na contagem
folium.GeoJson(
    cidades,
    name="Cidades",
    style_function=lambda feature: {
        'fillColor': get_cor(feature['properties']['qtd_queimadas']),
        'color': 'black',
        'weight': 1,
        'fillOpacity': 0.6,
    },
    tooltip=folium.GeoJsonTooltip(fields=['NM_MUN'], aliases=['Cidade:']),
    popup=folium.GeoJsonPopup(fields=['popup_html'], labels=False, max_width=300)
).add_to(m)

# Exibir no Streamlit
st.title("Mapa de Queimadas no Paraná")
st_folium(m, width=800, height=600)

import streamlit as st
import geopandas as gpd
import folium
from streamlit_folium import st_folium

# Carregar arquivos (coloque o caminho correto localmente ou no servidor do Streamlit)
cidades = gpd.read_file("cidades-pr.shp").to_crs(epsg=4326)
queimadas = gpd.read_file("queimadas-pr.shp").to_crs(epsg=4326)

# Sidebar para seleção do bairro
st.sidebar.title('Selecione a Cidade')
cidades = cidades.sort_values('NM_MUN')
cidade = st.sidebar.selectbox(
    "Cidade:",
    cidades['NM_MUN']
)

# Encontrar o código do bairro selecionado
codigo = cidades[cidades['NM_MUN'] == cidade]['CD_MUN'].values[0]

# Filtrar o bairro selecionado
selecionado = cidades[cidades['CD_MUN'] == codigo]

# Centroide para centralizar o mapa
centro = selecionado.geometry.iloc[0].centroid
lat, lon = centro.y, centro.x

# Escolas dentro do bairro
q_selec = queimadas[queimadas.within(selecionado.geometry.iloc[0])]

# Criar o mapa
m = folium.Map(location=[lat, lon], zoom_start=12)

# Adicionar camada do bairro
folium.GeoJson(
    selecionado.__geo_interface__,
    name="Cidade",
    style_function=lambda feature: {
        'fillColor': 'blue',
        'color': 'black',
        'fillOpacity': 0.5,
        'weight': 2,
    }
).add_to(m)

# Adicionar marcadores de escolas
for _, queimada in q_selec.iterrows():
    coords = queimada.geometry
    folium.Marker(
        location=[coords.y, coords.x],
        icon=folium.Icon(color='red', icon='info-sign')
    ).add_to(m)

# Exibir o mapa
st_data = st_folium(m, width=700, height=500)

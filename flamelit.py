import streamlit as st
import geopandas as gpd
import folium
from streamlit_folium import st_folium
import pandas as pd

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

# Criar abas
aba_mapa, aba_ranking = st.tabs(["🗺️ Mapa Interativo", "📊 Ranking de Queimadas"])

# ----- Aba 1: Mapa Interativo -----
with aba_mapa:
    st.title("Mapa de Queimadas no Paraná")

    m = folium.Map(location=[-24.5, -51.5], zoom_start=7)

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

    st_folium(m, width=800, height=600)

# ----- Aba 2: Ranking -----
with aba_ranking:
    st.title("Ranking de Cidades com Mais Queimadas")

    ranking = cidades[['NM_MUN', 'qtd_queimadas']].sort_values(by='qtd_queimadas', ascending=False)
    ranking = ranking[ranking['qtd_queimadas'] > 0].reset_index(drop=True)
    ranking.index += 1  # Começar do 1

    st.dataframe(ranking, use_container_width=True)

    # Se quiser um gráfico de barras:
    st.subheader("Visualização Gráfica")
    st.bar_chart(ranking.set_index('NM_MUN')['qtd_queimadas'])

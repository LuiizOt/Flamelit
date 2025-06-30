import streamlit as st
import geopandas as gpd
import folium
from streamlit_folium import st_folium
import pandas as pd
import matplotlib
import matplotlib.cm as cm
import matplotlib.colors as colors

# ----- Dados -----
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

# Escala de cores (gradiente)
cmap = cm.get_cmap('Reds', 20)
norm = colors.Normalize(vmin=0, vmax=cidades['qtd_queimadas'].max())
def get_cor_gradiente(qtd):
    rgba = cmap(norm(qtd))
    return matplotlib.colors.to_hex(rgba)

# ----- Layout -----
st.set_page_config(layout="wide")  # Isso deixa a página mais larga

# Sidebar como menu
opcao = st.sidebar.radio("Navegação", ["🗺️ Mapa Interativo", "📊 Ranking de Queimadas"])

# ----- Mapa Interativo -----
if opcao == "🗺️ Mapa Interativo":
    st.title("Mapa de Queimadas no Paraná")

    m = folium.Map(
        location=[-24.5, -51.5],
        zoom_start=7,
        tiles=None  # sem tiles padrão
    )

    # Base map sem rótulo
    folium.TileLayer(
        tiles='https://{s}.basemaps.cartocdn.com/light_nolabels/{z}/{x}/{y}{r}.png',
        attr='CartoDB Positron No Labels',
        name='CartoDB Light',
        control=False
    ).add_to(m)

    # Cidades com estilo e popup
    folium.GeoJson(
        cidades,
        name="Cidades",
        style_function=lambda feature: {
            'fillColor': get_cor_gradiente(feature['properties']['qtd_queimadas']),
            'color': 'black',
            'weight': 0.5,
            'fillOpacity': 0.8,
        },
        tooltip=folium.GeoJsonTooltip(fields=['NM_MUN'], aliases=['Cidade:']),
        popup=folium.GeoJsonPopup(fields=['popup_html'], labels=False, max_width=300)
    ).add_to(m)

    # Mostrar o mapa com tamanho proporcional
    st_folium(m, width="100%", height=600)  # ou height="70vh"

# ----- Ranking -----
else:
    st.title("Ranking de Cidades com Mais Queimadas")

    ranking = cidades[['NM_MUN', 'qtd_queimadas']].sort_values(by='qtd_queimadas', ascending=False)
    ranking = ranking[ranking['qtd_queimadas'] > 0].reset_index(drop=True)
    ranking.index += 1

    if not ranking.empty:
        ranking.rename(columns={
            'NM_MUN': 'Cidade',
            'qtd_queimadas': 'Número de Queimadas'
        }, inplace=True)

        # Mostrar pódio com as 3 primeiras
st.subheader("🏆 Pódio de Queimadas")

top3 = ranking.head(3)
col1, col2, col3 = st.columns(3)

with col2:  # 🥇 1º lugar no centro
    cidade = top3.iloc[0]['Cidade']
    valor = top3.iloc[0]['Número de Queimadas']
    st.markdown(f"## 🥇 {cidade} 🔥\n### {valor} queimadas")

with col1:  # 🥈 2º lugar à esquerda
    cidade = top3.iloc[1]['Cidade']
    valor = top3.iloc[1]['Número de Queimadas']
    st.markdown(f"### 🥈 {cidade} 🔥\n{valor} queimadas")

with col3:  # 🥉 3º lugar à direita
    cidade = top3.iloc[2]['Cidade']
    valor = top3.iloc[2]['Número de Queimadas']
    st.markdown(f"### 🥉 {cidade} 🔥\n{valor} queimadas")

import streamlit as st
import geopandas as gpd
import folium
from streamlit_folium import st_folium
import pandas as pd
import matplotlib
import matplotlib.cm as cm
import matplotlib.colors as colors

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

# Escala de 20 tons de rosa até vermelho
cmap = cm.get_cmap('Reds', 30)  # Matplotlib Reds colormap
norm = colors.Normalize(vmin=0, vmax=cidades['qtd_queimadas'].max())

def get_cor_gradiente(qtd):
    rgba = cmap(norm(qtd))  # rgba com alpha
    return matplotlib.colors.to_hex(rgba)  # converte pra HEX

# Criar abas
aba_mapa, aba_ranking = st.tabs(["🗺️ Mapa Interativo", "📊 Ranking de Queimadas"])

# ----- Aba do mapa -----
with aba_mapa:
    st.title("Mapa com Gradiente de Queimadas")

    m = folium.Map(location=[-24.5, -51.5], zoom_start=7)

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

    st_folium(m, width=800, height=600)

# ----- Aba do ranking -----
with aba_ranking:
    st.title("Ranking de Cidades com Mais Queimadas")

    ranking = cidades[['NM_MUN', 'qtd_queimadas']].sort_values(by='qtd_queimadas', ascending=False)
    ranking = ranking[ranking['qtd_queimadas'] > 0].reset_index(drop=True)
    ranking.index += 1

    st.dataframe(ranking, use_container_width=True)

    st.subheader("Visualização Gráfica")
    st.bar_chart(ranking.set_index('NM_MUN')['qtd_queimadas'])

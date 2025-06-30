import streamlit as st
import geopandas as gpd
import folium
from streamlit_folium import st_folium
import pandas as pd
import matplotlib
import matplotlib.cm as cm
import matplotlib.colors as colors
import numpy as np

# Configuração
st.set_page_config(layout="wide")

# Carregar dados
cidades = gpd.read_file("cidades-pr.shp").to_crs(epsg=4326)
queimadas = gpd.read_file("queimadas-pr.shp").to_crs(epsg=4326)

# Contagem de queimadas
cidades['qtd_queimadas'] = cidades.geometry.apply(
    lambda geom: queimadas[queimadas.within(geom)].shape[0]
)
cidades['popup_html'] = cidades.apply(
    lambda row: f"<strong>{row['NM_MUN']}</strong><br>Queimadas: {row['qtd_queimadas']}", axis=1
)

# Gradiente de cor: vermelho escuro → claro, branco se 0
original = cm.get_cmap('Reds', 256)
cmap = colors.LinearSegmentedColormap.from_list(
    "custom_reds", original(np.linspace(0.4, 1.0, 20))
)
norm = colors.Normalize(vmin=1, vmax=cidades['qtd_queimadas'].max())
def get_cor_gradiente(qtd):
    if qtd == 0:
        return '#ffffff'  # branco total
    rgba = cmap(norm(qtd))
    return matplotlib.colors.to_hex(rgba)

# Navegação lateral
pagina = st.sidebar.radio("Menu", ["Página Inicial", "Mapa de Queimadas", "Ranking", "Tabela Completa"])

# Página Inicial
if pagina == "Página Inicial":
    st.title("🌱 Queimadas no Paraná")
    st.markdown("""
        As queimadas são um dos principais problemas ambientais no Brasil. Elas afetam diretamente a saúde da população,
        a biodiversidade, os recursos naturais e contribuem significativamente para as mudanças climáticas.

        No estado do Paraná, o monitoramento das queimadas é fundamental para entender sua distribuição e impacto.
        Este aplicativo visa visualizar os focos de queimadas registrados por município e conscientizar sobre seus danos.

        **Impactos das queimadas:**
        - Problemas respiratórios em crianças e idosos;
        - Perda de vegetação nativa e fauna;
        - Empobrecimento do solo e desertificação;
        - Emissão de gases de efeito estufa;
        - Aumento do risco de acidentes em rodovias e áreas urbanas.

        Use as abas laterais para navegar pelo mapa interativo, visualizar o ranking das cidades mais afetadas
        e acessar os dados completos.

        🔗 [Acesse o repositório no GitHub](https://github.com/LuiizOt/Flamelit)
    """)

# Mapa
elif pagina == "Mapa de Queimadas":
    st.title("Mapa Interativo de Queimadas no Paraná")

    m = folium.Map(
        location=[-24.5, -51.5],
        zoom_start=7,
        tiles=None
    )
    folium.TileLayer(
        tiles='https://{s}.basemaps.cartocdn.com/light_nolabels/{z}/{x}/{y}{r}.png',
        attr='CartoDB Positron No Labels',
        control=False
    ).add_to(m)

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

    st_folium(m, width="100%", height=600)

# Ranking (apenas top 3)
elif pagina == "Ranking":
    st.title("Cidades com Maior Número de Queimadas")

    ranking = cidades[['NM_MUN', 'qtd_queimadas']].sort_values(by='qtd_queimadas', ascending=False)
    ranking = ranking[ranking['qtd_queimadas'] > 0].reset_index(drop=True)
    ranking.rename(columns={'NM_MUN': 'Cidade', 'qtd_queimadas': 'Número de Queimadas'}, inplace=True)

    if ranking.empty:
        st.warning("Nenhuma queimada registrada nas cidades carregadas.")
    else:
        top3 = ranking.head(3)
        col1, col2, col3 = st.columns(3)

        with col2:
            st.markdown(f"## 1º {top3.iloc[0]['Cidade']}")
            st.write(f"{top3.iloc[0]['Número de Queimadas']} queimadas registradas")

        with col1:
            st.markdown(f"### 2º {top3.iloc[1]['Cidade']}")
            st.write(f"{top3.iloc[1]['Número de Queimadas']} queimadas")

        with col3:
            st.markdown(f"### 3º {top3.iloc[2]['Cidade']}")
            st.write(f"{top3.iloc[2]['Número de Queimadas']} queimadas")

# Tabela completa
elif pagina == "Tabela Completa":
    st.title("Dados Completos por Cidade")

    tabela = cidades[['NM_MUN', 'qtd_queimadas']].sort_values(by='qtd_queimadas', ascending=False)
    tabela.rename(columns={'NM_MUN': 'Cidade', 'qtd_queimadas': 'Número de Queimadas'}, inplace=True)

    st.dataframe(tabela, use_container_width=True)

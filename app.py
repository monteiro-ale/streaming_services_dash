import json
import streamlit as st
import pandas as pd
import plotly.express as px

with open("generos_map.json", "r", encoding="utf-8") as f:
    genre_map = json.load(f)

# ========== Carregar Dados ==========
@st.cache_data
def load_data():
    netflix = pd.read_csv("netflix_titles.csv")
    disney = pd.read_csv("disney_plus_titles.csv")
    amazon = pd.read_csv("amazon_prime_titles.csv")

    # Adiciona coluna 'platform' em cada um
    netflix["platform"] = "Netflix"
    disney["platform"] = "Disney+"
    amazon["platform"] = "Amazon Prime"

    df = pd.concat([netflix, disney, amazon], ignore_index=True)
    df["type"] = df["type"].replace({
        "Movie": "Filmes",
        "TV Show": "Séries"
    })
    return df

df = load_data()

# Chama o CSS
def inject_css():
    with open("style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

inject_css()

# De-para
def traduzir_generos(listed_in):
    if pd.isna(listed_in):
        return []
    generos = [g.strip() for g in listed_in.split(",")]
    generos_traduzidos = [genre_map.get(g, g) for g in generos]
    return generos_traduzidos

df["genres"] = df["listed_in"].apply(traduzir_generos)

st.title("Análise de Catálogos de Streaming")
st.markdown("<p style='color: #aaa;'>Explorando dados e padrões nos catálogos de streaming</p>", unsafe_allow_html=True)
st.markdown(
    """<br><hr style='border: 1px solid rgba(255, 255, 255, 0.1); margin-top: -10px;'><br>""",
    unsafe_allow_html=True
)



# ========== Filtros ==========
st.sidebar.header("🔧 Filtros")

platforms = df["platform"].unique().tolist()
types = df["type"].unique().tolist()

selected_platforms = st.sidebar.multiselect(
    "Plataforma",
    options=platforms,
    default=platforms
)

selected_types = st.sidebar.multiselect(
    "Tipo",
    options=types,
    default=types
)

filtered_df = df[
    (df["platform"].isin(selected_platforms)) &
    (df["type"].isin(selected_types))
]

# ========== Filmes vs Séries ==========
st.subheader("🎥 Quantidade de Filmes e Séries por Plataforma")

type_counts = filtered_df.groupby(["platform", "type"]).size().reset_index(name="count")

fig = px.bar(
    type_counts,
    x="platform",
    y="count",
    color="type",
    barmode="group",
    labels={"platform": "Plataforma", "count": "Quantidade", "type": "Tipo"},
    color_discrete_sequence=px.colors.qualitative.Set1
)
st.plotly_chart(fig, use_container_width=True)

# ========== Evolução de Lançamentos por Ano ==========
st.subheader("📅 Evolução de Lançamentos por Ano")

year_counts = filtered_df.groupby(["release_year", "platform"]).size().reset_index(name="count")
year_counts = year_counts[year_counts["release_year"] >= 1980]

fig2 = px.line(
    year_counts,
    x="release_year",
    y="count",
    color="platform",
    labels={
        "release_year": "Ano de Lançamento",
        "count": "Quantidade de Títulos",
        "platform": "Plataforma"
    },
    markers=True,
    color_discrete_sequence=px.colors.qualitative.Set1
)

fig2.update_layout(
    xaxis=dict(dtick=2),
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    font_color="white"
)
st.plotly_chart(fig2, use_container_width=True)

# ========== Análise de Gêneros ==========
st.subheader("🎭 Gêneros Mais Comuns")

generos_excluir = [
    "Internacional",
    "Filmes Internacionais",
    "Séries Internacionais",
    "Séries"
]

genre_series = filtered_df["genres"].explode()
genre_series = genre_series[~genre_series.isin(generos_excluir)]

top_genres = genre_series.value_counts().nlargest(15).reset_index()
top_genres.columns = ["Gênero", "Quantidade"]

fig4 = px.bar(
    top_genres,
    x="Gênero",
    y="Quantidade",
    labels={"Quantidade": "Quantidade de Títulos"},
    text="Quantidade",
    color="Quantidade",
    color_continuous_scale="Inferno"
)

fig4.update_layout(
    xaxis_tickangle=-45,
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    font_color="white",
    showlegend=False
)
st.plotly_chart(fig4, use_container_width=True)

# ========== Mapa de Títulos por País ==========
st.subheader("🌍 Quantidade de Títulos por País")

# Remove nulos e explode países
df_country = filtered_df[~filtered_df['country'].isna()].copy()
df_country['country'] = df_country['country'].str.split(",")
df_country = df_country.explode('country')
df_country['country'] = df_country['country'].str.strip()

country_counts = df_country.groupby('country').size().reset_index(name='count')

fig5 = px.choropleth(
    country_counts,
    locations="country",
    locationmode="country names",
    color="count",
    color_continuous_scale="Plasma",
    title="Quantidade de Títulos por País"
)

fig5.update_layout(
    geo=dict(showframe=False, showcoastlines=True),
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    font_color="white"
)

st.plotly_chart(fig5, use_container_width=True)

# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns

# Configuración de página de Streamlit
st.set_page_config(page_title="Top 500 Películas - Letterboxd", layout="wide")

st.title("🎬 Página Interactiva de las 500 Mejores Películas según Letterboxd")
st.markdown("---")

# 1. CARGA DE DATOS OPTIMIZADA CON CACHÉ
@st.cache_data
def load_data():
    # Se corrige la ruta fija de Colab a una ruta relativa compatible con GitHub y Streamlit Cloud
    df = pd.read_csv("top500.csv")
    return df

df_top500 = load_data()

# 2. SECCIÓN DE ESTADÍSTICAS Y GRÁFICOS (Dashboard Inicial)
st.header("📊 Dashboard Estadístico del Top 500")

col1, col2 = st.columns(2)

with col1:
    # Mapa Coroplético de Películas por País
    country_count = df_top500["country"].value_counts().reset_index()
    country_count.columns = ["country", "Cantidad de películas"]

    fig_map = px.choropleth(
        country_count,
        locations="country",
        locationmode="country names",
        color="Cantidad de películas",
        hover_name="country",
        hover_data=["Cantidad de películas"],
        color_continuous_scale="Greens",
        title="Cantidad de películas del Top 500 por país"
    )
    fig_map.update_layout(width=600, height=400)
    st.plotly_chart(fig_map, use_container_width=True)

with col2:
    # Gráfico de líneas interactivo por Año de Estreno
    year_counts = df_top500['year'].value_counts().sort_index().reset_index()
    year_counts.columns = ['Año', 'Cantidad de Películas']

    fig_year = px.line(
        year_counts,
        x='Año',
        y='Cantidad de Películas',
        title='Cantidad de Películas del Top 500 por Año de Estreno',
        markers=True,
        labels={'Año': 'Año de Estreno', 'Cantidad de Películas': 'Cantidad de Películas'},
        hover_name='Año'
    )
    fig_year.update_xaxes(tickangle=45)
    fig_year.update_layout(width=600, height=400)
    st.plotly_chart(fig_year, use_container_width=True)

col3, col4 = st.columns(2)

with col3:
    # Directores más comunes
    director_cols = [col for col in df_top500.columns if 'director/' in col]
    all_directors = df_top500[director_cols].stack().dropna().tolist()
    director_counts = pd.Series(all_directors).value_counts().reset_index()
    director_counts.columns = ['Director', 'Cantidad de Películas']

    fig_dir, ax_dir = plt.subplots(figsize=(10, 5))
    sns.barplot(x='Cantidad de Películas', y='Director', data=director_counts.head(10), palette='viridis', ax=ax_dir)
    ax_dir.set_title('Top 10 Directores con Más Películas en el Top 500')
    plt.tight_layout()
    st.pyplot(fig_dir)

with col4:
    # Géneros más comunes
    if 'genres_combined' not in df_top500.columns:
        genre_cols = [col for col in df_top500.columns if 'genres/' in col]
        df_top500['genres_combined'] = df_top500[genre_cols].apply(lambda row: ', '.join(row.dropna().astype(str)), axis=1)

    all_genres = df_top500['genres_combined'].str.split(', ').explode().str.strip().tolist()
    all_genres = [genre for genre in all_genres if genre]
    genre_counts = pd.Series(all_genres).value_counts().reset_index()
    genre_counts.columns = ['Género', 'Cantidad de Películas']

    fig_gen, ax_gen = plt.subplots(figsize=(10, 5))
    sns.barplot(x='Cantidad de Películas', y='Género', data=genre_counts.head(10), palette='magma', ax=ax_gen)
    ax_gen.set_title('Top 10 Géneros Más Comunes en el Top 500')
    plt.tight_layout()
    st.pyplot(fig_gen)

st.markdown("---")

# 3. CREACIÓN DE PESTAÑAS PARA LOS BUSCADORES MANUALES Y EL QUIZ
tab1, tab2, tab3 = st.tabs(["🔍 Buscar por País", "🎭 Buscar por Género", "🎯 Quiz de Recomendación Inteligente"])

with tab1:
    st.header("Explorador por País")
    # Selector dinámico extraído de la base de datos
    paises_disponibles = sorted(df_top500["country"].dropna().unique())
    country = st.selectbox("Selecciona el nombre del país para ver sus películas:", paises_disponibles)

    if country:
        resultado = df_top500[df_top500["country"] == country]
        if resultado.empty:
            st.warning(f"No se encontraron películas para {country} en el Top 500.")
        else:
            st.success(f"Se encontraron {len(resultado)} películas de {country}:")
            for index, row in resultado.sort_values(by='averageRating', ascending=False).iterrows():
                title = row["title"]
                year = row["year"]
                director = row["director/0"] if "director/0" in row and pd.notna(row["director/0"]) else "N/A"
                avg_rating = row["averageRating"]
                poster_url = row["posterUrl"] if "posterUrl" in row and pd.notna(row["posterUrl"]) else ""

                movie_info_html = ""
                if poster_url:
                    movie_info_html += f"<div style='display:flex; align-items:center; margin-bottom: 20px;'>"
                    movie_info_html += f"<img src='{poster_url}' style='width:100px; height:auto; margin-right:15px;'>"
                    movie_info_html += f"<div>"
                else:
                    movie_info_html += f"<div>"

                movie_info_html += f"  <strong>Título:</strong> {title}<br>"
                movie_info_html += f"  <strong>Año:</strong> {year}<br>"
                movie_info_html += f"  <strong>Director:</strong> {director}<br>"
                movie_info_html += f"  <strong>Calificación Promedio (Ranking):</strong> {avg_rating}<br>"
                movie_info_html += f"</div></div>"

                st.markdown(movie_info_html, unsafe_allow_html=True)

with tab2:
    st.header("Explorador por Género")
    st.info("Géneros populares recomendados: Adventure, Drama, Fantasy, Music, Romance, Thriller, War, Western")
    
    genre_input = st.text_input("Escribe el nombre del género para ver sus películas:", "Drama")

    if genre_input:
        resultado_genero = df_top500[df_top500['genres_combined'].str.contains(genre_input, case=False, na=False)]
        if resultado_genero.empty:
            st.warning(f"No se encontraron películas para el género '{genre_input}' en el Top 500.")
        else:
            st.success(f"Top 10 películas del género '{genre_input}':")
            for index, row in resultado_genero.sort_values(by='averageRating', ascending=False).head(10).iterrows():
                title = row["title"]
                year = row["year"]
                director = row["director/0"] if "director/0" in row and pd.notna(row["director/0"]) else "N/A"
                avg_rating = row["averageRating"]
                poster_url = row["posterUrl"] if "posterUrl" in row and pd.notna(row["posterUrl"]) else ""

                movie_info_html = ""
                if poster_url:
                    movie_info_html += f"<div style='display:flex; align-items:center; margin-bottom: 20px;'>"
                    movie_info_html += f"<img src='{poster_url}' style='width:100px; height:auto; margin-right:15px;'>"
                    movie_info_html += f"<div>"
                else:
                    movie_info_html += f"<div>"

                movie_info_html += f"  <strong>Título:</strong> {title}<br>"
                movie_info_html += f"  <strong>Año:</strong> {year}<br>"
                movie_info_html += f"  <strong>Director:</strong> {director}<br>"
                movie_info_html += f"  <strong>Calificación Promedio (Ranking):</strong> {avg_rating}<br>"
                movie_info_html += f"</div></div>"

                st.markdown(movie_info_html, unsafe_allow_html=True)


with tab3:
    st.header("🎯 Quiz Interactivo de Recomendación de Películas")
    st.markdown("Responde a las siguientes preguntas para generar un listado a tu medida de manera algorítmica:")

    # Lógica de Limpieza integrada para el Quiz
    def cargar_y_limpiar_datos(df_source):
        df = df_source.copy()
        df = df.rename(columns={
            'title': 'título',
            'year': 'año',
            'country': 'país o región',
            'averageRating': 'rating de Letterboxd'
        })
        director_cols_map = {f'director/{i}': f'director{i}' for i in range(3) if f'director/{i}' in df.columns}
        df = df.rename(columns=director_cols_map)
        genre_cols_map = {f'genres/{i}': f'género{i}' for i in range(8) if f'genres/{i}' in df.columns}
        df = df.rename(columns=genre_cols_map)

        if 'sinopsis' not in df.columns: df['sinopsis'] = ''
        if 'duración (minutos)' not in df.columns: df['duración (minutos)'] = 120
        if 'idioma' not in df.columns: df['idioma'] = 'inglés'

        columnas_str = ['título', 'sinopsis', 'idioma', 'país o región'] + list(director_cols_map.values())
        for col in columnas_str:
            if col in df.columns: df[col] = df[col].astype(str).str.strip()

        for i in range(8):
            col_gen = f'género{i}'
            if col_gen in df.columns:
                df[col_gen] = df[col_gen].astype(str).str.strip().str.capitalize()
        return df

    df_peliculas = cargar_y_limpiar_datos(df_top500)

    # RE-DISEÑO DEL FORMULARIO DEL QUIZ EN STREAMLIT
    with st.form("quiz_form"):
        col_q1, col_q2 = st.columns(2)
        
        with col_q1:
            gen_pref = st.selectbox("1. ¿Qué género te gustaría ver hoy?", 
                                    ["Drama", "Comedia", "Acción", "Thriller", "Terror", "Romance", "Ciencia ficción", "Animación", "Documental", "Fantasía", "Crimen", "Aventura", "Musical", "Guerra", "Western", "Ninguno"])
            
            dur_opt = st.selectbox("2. ¿Qué duración prefieres?", 
                                    [("1", "Menos de 90 minutos"), ("2", "90–120 minutos"), ("3", "120–150 minutos"), ("4", "Más de 150 minutos"), ("5", "Me da igual")], 
                                    format_func=lambda x: x[1])[0]
            
            ep_opt = st.selectbox("3. ¿De qué época prefieres la película?", 
                                   [("1", "Antes de 1970"), ("2", "1970–1989"), ("3", "1990–2009"), ("4", "2010+"), ("5", "No importa")],
                                   format_func=lambda x: x[1])[0]
            
            rat_opt = st.selectbox("4. ¿Qué calificación mínima en Letterboxd buscas?", 
                                    [("1", "3.5+"), ("2", "4.0+"), ("3", "4.3+"), ("4", "Top rated (4.5+)"), ("5", "Me da igual")],
                                    format_func=lambda x: x[1])[0]
            
            region_opt = st.selectbox("5. ¿De qué región te gustaría ver una película?", 
                                       ["Cualquiera", "USA/Canadá", "Europa", "Asia", "Latinoamérica", "África", "Oceanía"]).lower()

        with col_q2:
            id_opt = st.selectbox("6. ¿Qué prefieres respecto al idioma?", 
                                   [("1", "Solo Español"), ("2", "Español/Inglés"), ("3", "Cualquier idioma"), ("4", "Descubrir otros (No inglés/español)")],
                                   format_func=lambda x: x[1])[0]
            
            exp_opt = st.selectbox("7. ¿Qué tipo de experiencia buscas?", 
                                    ["Indiferente", "Emocionarme", "Reflexionar", "Suspenso", "Reír", "Sorprenderme"]).lower()
            
            evitar_opt = st.text_input("8. ¿Quieres evitar algún género? (Separa por comas o escribe 'ninguno')", "ninguno").strip().lower()
            
            dir_opt = st.text_input("9. ¿Hay algún director que te guste especialmente? (Opcional)", "").strip().lower()
            
            n_recom = st.slider("10. ¿Cuántas recomendaciones deseas?", min_value=1, max_value=5, value=3, step=2)

        submit_quiz = st.form_submit_button("✨ ¡Calcular Mis Recomendaciones!")

    # Funciones de Filtrado, Puntuación y Despliegue de Resultados adaptados
    def filtrar_y_puntuar(df, respuestas):
        df_filtrado = df.copy()

        if respuestas['evitar'] != 'ninguno' and respuestas['evitar'] != '':
            generos_evitar = [g.strip().capitalize() for g in respuestas['evitar'].split(',')]
            for g_evitar in generos_evitar:
                for i in range(8):
                    if f'género{i}' in df_filtrado.columns:
                        df_filtrado = df_filtrado[df_filtrado[f'género{i}'] != g_evitar]

        df_filtrado['score'] = 0.0

        if respuestas['genero'] != 'Ninguno' and respuestas['genero'] != '':
            gen_mask = pd.Series(False, index=df_filtrado.index)
            for i in range(8):
                if f'género{i}' in df_filtrado.columns:
                    gen_mask = gen_mask | (df_filtrado[f'género{i}'] == respuestas['genero'])
            df_filtrado.loc[gen_mask, 'score'] += 3.0

        dic_palabras_clave = {
            'emocionarme': ['llorar', 'amor', 'drama', 'emoción', 'conmovedor', 'familia', 'triste', 'vida'],
            'reflexionar': ['filosofía', 'mente', 'pensar', 'existencial', 'sociedad', 'realidad', 'humano', 'moral'],
            'suspenso': ['misterio', 'crimen', 'asesinato', 'tensión', 'peligro', 'secreto', 'investigación', 'terror'],
            'reír': ['comedia', 'divertido', 'humor', 'chiste', 'risa', 'sátira', 'parodia'],
            'sorprenderme': ['giro', 'inesperado', 'secreto', 'magia', 'ciencia ficción', 'fantasía', 'viaje', 'descubrir']
        }

        exp = respuestas['experiencia']
        if exp in dic_palabras_clave:
            keywords = dic_palabras_clave[exp]
            regex_pattern = '|'.join(keywords)
            if 'sinopsis' in df_filtrado.columns:
                sinopsis_match = df_filtrado['sinopsis'].str.contains(regex_pattern, case=False, na=False)
                df_filtrado.loc[sinopsis_match, 'score'] += 2.0

        if 'rating de Letterboxd' in df_filtrado.columns:
            df_filtrado['score'] += (df_filtrado['rating de Letterboxd'].fillna(0) / 5.0) * 2.0

        dur = respuestas['duracion']
        if 'duración (minutos)' in df_filtrado.columns:
            if dur == '1': df_filtrado.loc[df_filtrado['duración (minutos)'] < 90, 'score'] += 1.0
            elif dur == '2': df_filtrado.loc[(df_filtrado['duración (minutos)'] >= 90) & (df_filtrado['duración (minutos)'] <= 120), 'score'] += 1.0
            elif dur == '3': df_filtrado.loc[(df_filtrado['duración (minutos)'] > 120) & (df_filtrado['duración (minutos)'] <= 150), 'score'] += 1.0
            elif dur == '4': df_filtrado.loc[df_filtrado['duración (minutos)'] > 150, 'score'] += 1.0

        ep = respuestas['epoca']
        if 'año' in df_filtrado.columns:
            if ep == '1': df_filtrado.loc[df_filtrado['año'] < 1970, 'score'] += 1.0
            elif ep == '2': df_filtrado.loc[(df_filtrado['año'] >= 1970) & (df_filtrado['año'] <= 1989), 'score'] += 1.0
            elif ep == '3': df_filtrado.loc[(df_filtrado['año'] >= 1990) & (df_filtrado['año'] <= 2009), 'score'] += 1.0
            elif ep == '4': df_filtrado.loc[df_filtrado['año'] >= 2010, 'score'] += 1.0

        rat = respuestas['rating']
        if 'rating de Letterboxd' in df_filtrado.columns:
            if rat == '1': df_filtrado = df_filtrado[df_filtrado['rating de Letterboxd'] >= 3.5]
            elif rat == '2': df_filtrado = df_filtrado[df_filtrado['rating de Letterboxd'] >= 4.0]
            elif rat == '3': df_filtrado = df_filtrado[df_filtrado['rating de Letterboxd'] >= 4.3]
            elif rat == '4': df_filtrado = df_filtrado[df_filtrado['rating de Letterboxd'] >= 4.5]

        reg = respuestas['region']
        if reg != 'cualquiera' and reg != '':
            mapa_regiones = {
                'usa/canadá': ['estados unidos', 'canadá', 'usa', 'united states', 'canada', 'estados unidos o canadá'],
                'europa': ['europa', 'francia', 'españa', 'reino unido', 'italia', 'alemania'],
                'asia': ['asia', 'japón', 'corea', 'china', 'india'],
                'latinoamérica': ['latinoamérica', 'argentina', 'méxico', 'brasil', 'chile', 'colombia'],
                'áfrica': ['áfrica', 'sudáfrica', 'egipto', 'nigeria'],
                'oceanía': ['oceanía', 'australia', 'nueva zelanda']
            }
            if reg in mapa_regiones and 'país o región' in df_filtrado.columns:
                reg_mask = df_filtrado['país o región'].str.lower().isin(mapa_regiones[reg])
                df_filtrado.loc[reg_mask, 'score'] += 1.0

        idioma_opt = respuestas['idioma']
        if 'idioma' in df_filtrado.columns:
            if idioma_opt == '1': df_filtrado = df_filtrado[df_filtrado['idioma'].str.lower() == 'español']
            elif idioma_opt == '2': df_filtrado = df_filtrado[df_filtrado['idioma'].str.lower().isin(['español', 'inglés', 'english'])]
            elif idioma_opt == '4': df_filtrado = df_filtrado[~df_filtrado['idioma'].str.lower().isin(['español', 'inglés', 'english'])]

        if respuestas['director'] != '':
            dir_mask = pd.Series(False, index=df_filtrado.index)
            for i in range(3):
                col_dir = f'director{i}'
                if col_dir in df_filtrado.columns:
                    dir_mask = dir_mask | (df_filtrado[col_dir].str.lower() == respuestas['director'])
            df_filtrado.loc[dir_mask, 'score'] += 1.5

        if 'rating de Letterboxd' in df_filtrado.columns:
            df_filtrado = df_filtrado.sort_values(by=['score', 'rating de Letterboxd'], ascending=[False, False])
        else:
            df_filtrado = df_filtrado.sort_values(by='score', ascending=False)

        return df_filtrado

    if submit_quiz:
        respuestas_usuario = {
            'genero': gen_pref, 'duracion': dur_opt, 'epoca': ep_opt, 'rating': rat_opt,
            'region': region_opt, 'idioma': id_opt, 'experiencia': exp_opt, 'evitar': evitar_opt,
            'director': dir_opt, 'cantidad': n_recom
        }
        
        resultados = filtrar_y_puntuar(df_peliculas, respuestas_usuario)
        n_mostrar = min(len(resultados), respuestas_usuario['cantidad'])

        if n_mostrar == 0:
            st.warning("No se encontraron películas que coincidan exactamente con tus criterios de filtrado. Prueba ampliando las restricciones.")
        else:
            st.success(f"Basado en tus respuestas, estas son tus {n_mostrar} mejores recomendaciones cinematográficas:")
            
            for idx in range(n_mostrar):
                peli = resultados.iloc[idx]

                generos = []
                for i in range(8):
                    gen_col = f'género{i}'
                    if gen_col in peli.index:
                        gen = peli[gen_col]
                        if pd.notna(gen) and str(gen).strip() != '' and str(gen).lower() != 'nan':
                            generos.append(str(gen))
                generos_str = ", ".join(generos)

                directores = []
                for i in range(3):
                    col_dir = f'director{i}'
                    if col_dir in peli.index and pd.notna(peli[col_dir]) and str(peli[col_dir]).strip() != '' and str(peli[col_dir]).lower() != 'nan':
                        directores.append(str(peli[col_dir]))
                directores_str = ", ".join(directores)

                motivos = []
                if respuestas_usuario['genero'] != 'Ninguno' and respuestas_usuario['genero'] in generos:
                    motivos.append(f"coincide perfectamente con tu deseo de ver un film de {respuestas_usuario['genero']}")
                if respuestas_usuario['experiencia'] != 'indiferente':
                    motivos.append(f"su trama está especialmente alineada a tu búsqueda de {respuestas_usuario['experiencia']}")
                if 'rating de Letterboxd' in peli.index and float(peli['rating de Letterboxd']) >= 4.0:
                    motivos.append(f"cuenta con un excelente respaldo crítico de {peli['rating de Letterboxd']} en la comunidad cinéfila")

                por_que = "Esta obra maestra te la sugiero porque " + " y ".join(motivos[:2]) + "." if motivos else "Es una de las obras con mayor afinidad y calidad dentro de tus filtros elegidos."

                poster_url = peli["posterUrl"] if "posterUrl" in peli.index and pd.notna(peli["posterUrl"]) else ""

                movie_info_html = ""
                if poster_url:
                    movie_info_html += f"<div style='display:flex; align-items:center; margin-bottom: 20px;'>"
                    movie_info_html += f"<img src='{poster_url}' style='width:100px; height:auto; margin-right:15px;'>"
                    movie_info_html += f"<div>"
                else:
                    movie_info_html += f"<div>"

                movie_info_html += f"  <strong>Título:</strong> {peli['título']}<br>"
                movie_info_html += f"  <strong>Año:</strong> {int(peli['año'])}<br>"
                movie_info_html += f"  <strong>Director:</strong> {directores_str}<br>"
                movie_info_html += f"  <strong>Calificación Promedio (Ranking):</strong> {peli['rating de Letterboxd']}<br>"
                movie_info_html += f"  <strong>Duración:</strong> {int(peli['duración (minutos)'])} minutos<br>"
                movie_info_html += f"  <strong>País:</strong> {peli['país o región']}<br>"
                movie_info_html += f"  <strong>Géneros:</strong> {generos_str}<br>"
                movie_info_html += f"  <strong>Por qué te lo recomiendo:</strong> {por_que}<br>"
                movie_info_html += f"</div></div>"

                st.markdown(movie_info_html, unsafe_allow_html=True)
                st.markdown("---")
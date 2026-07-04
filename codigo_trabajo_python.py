# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns

# Configuración de la página de Streamlit
st.set_page_config(
    page_title="Top 500 Películas - Dashboard & Recomendador",
    page_icon="🎬",
    layout="wide"
)

# Título Principal
st.title("Sistema de Recomendación y Análisis del Top 500 de Películas")
st.markdown("---")

# 1. Carga de Datos optimizada con Cache
@st.cache_data
def load_data():
    try:
        # Lee el archivo 'top500.csv' verbatim desde la raíz del proyecto
        df = pd.read_csv("top500.csv")
        return df
    except FileNotFoundError:
        st.error("No se encontró el archivo 'top500.csv' en la raíz del proyecto. Por favor asegúrate de subirlo junto a este script.")
        return None

df_top500 = load_data()

if df_top500 is not None:
    # Crear pestañas para organizar el contenido limpiamente
    tab_dashboard, tab_busqueda, tab_quiz = st.tabs([
        "Dashboard Estadístico", 
        "Explorador (País/Género)", 
        "Recomendador de Películas"
    ])

    # =========================================================================
    # PESTAÑA 1: DASHBOARD ESTADÍSTICO
    # =========================================================================
    with tab_dashboard:
        st.header("Estadísticas Globales del Top 500")
        
        # Mapa Coroplético (Plotly)
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
        fig_map.update_layout(width=1000, height=500)
        st.plotly_chart(fig_map, use_container_width=True)

        # Gráficos de Directores y Géneros (Dos columnas para aprovechar el espacio)
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Top 10 Directores")
            director_cols = [col for col in df_top500.columns if 'director/' in col]
            all_directors = df_top500[director_cols].stack().dropna().tolist()
            director_counts = pd.Series(all_directors).value_counts().reset_index()
            director_counts.columns = ['Director', 'Cantidad de Películas']

            fig_dir, ax_dir = plt.subplots(figsize=(8, 4.5))
            sns.barplot(x='Cantidad de Películas', y='Director', data=director_counts.head(10), palette='viridis', ax=ax_dir)
            ax_dir.set_title('Top 10 Directores con Más Películas')
            plt.tight_layout()
            st.pyplot(fig_dir)

        with col2:
            st.subheader("Top 10 Géneros")
            genre_cols = [col for col in df_top500.columns if 'genres/' in col]
            df_top500['genres_combined'] = df_top500[genre_cols].apply(lambda row: ', '.join(row.dropna().astype(str)), axis=1)
            all_genres = df_top500['genres_combined'].str.split(', ').explode().str.strip().tolist()
            all_genres = [genre for genre in all_genres if genre]
            genre_counts = pd.Series(all_genres).value_counts().reset_index()
            genre_counts.columns = ['Género', 'Cantidad de Películas']

            fig_gen, ax_gen = plt.subplots(figsize=(8, 4.5))
            sns.barplot(x='Cantidad de Películas', y='Género', data=genre_counts.head(10), palette='magma', ax=ax_gen)
            ax_gen.set_title('Top 10 Géneros Más Comunes')
            plt.tight_layout()
            st.pyplot(fig_gen)

        # Gráfico de Línea por Año (Plotly)
        st.subheader("Evolución Temporal")
        year_counts = df_top500['year'].value_counts().sort_index()
        year_counts_df = year_counts.reset_index()
        year_counts_df.columns = ['Año', 'Cantidad de Películas']

        fig_year = px.line(
            year_counts_df,
            x='Año',
            y='Cantidad de Películas',
            title='Cantidad de Películas del Top 500 por Año de Estreno',
            markers=True,
            labels={'Año': 'Año de Estreno', 'Cantidad de Películas': 'Cantidad de Películas'},
            hover_name='Año',
            hover_data={'Cantidad de Películas': True}
        )
        fig_year.update_xaxes(tickangle=45)
        st.plotly_chart(fig_year, use_container_width=True)

    # =========================================================================
    # PESTAÑA 2: EXPLORADOR POR PAÍS Y GÉNERO
    # =========================================================================
    with tab_busqueda:
        st.header("Buscador Manual")
        
        subtab_pais, subtab_genero = st.tabs(["Por País", "Por Género"])
        
        with subtab_pais:
            paises_disponibles = sorted(df_top500["country"].dropna().unique().tolist())
            country_input = st.selectbox("Selecciona el nombre del país para ver sus películas:", paises_disponibles)
            
            if country_input:
                resultado = df_top500[df_top500["country"] == country_input]
                if resultado.empty:
                    st.warning(f"No se encontraron películas para {country_input} en el Top 500.")
                else:
                    st.success(f"Películas de {country_input} (Top 500):")
                    for index, row in resultado.sort_values(by='averageRating', ascending=False).iterrows():
                        title = row["title"]
                        year = row["year"]
                        director = row["director/0"] if "director/0" in row and pd.notna(row["director/0"]) else "N/A"
                        avg_rating = row["averageRating"]
                        poster_url = row["posterUrl"] if "posterUrl" in row and pd.notna(row["posterUrl"]) else ""

                        movie_info_html = f"<div style='display:flex; align-items:center; margin-bottom: 20px; border-bottom: 1px solid #ddd; padding-bottom: 10px;'>"
                        if poster_url:
                            movie_info_html += f"<img src='{poster_url}' style='width:90px; height:auto; margin-right:20px; border-radius:5px;'>"
                        movie_info_html += f"<div>"
                        movie_info_html += f"  <h4 style='margin:0;'>{title} ({int(year)})</h4>"
                        movie_info_html += f"  <p style='margin: 5px 0;'><strong>Director:</strong> {director}</p>"
                        movie_info_html += f"  <p style='margin: 5px 0;'><strong>Calificación Promedio:</strong> ⭐ {avg_rating}</p>"
                        movie_info_html += f"</div></div>"
                        st.markdown(movie_info_html, unsafe_allow_html=True)

        with subtab_genero:
            st.info("Géneros recomendados: Adventure, Drama, Fantasy, Music, Romance, Thriller, War, Western")
            genre_input = st.text_input("Escribe el nombre del género para ver sus películas (Ej. Drama):", "Drama")
            
            if genre_input:
                genre_cols = [col for col in df_top500.columns if 'genres/' in col]
                df_top500['genres_combined'] = df_top500[genre_cols].apply(lambda row: ', '.join(row.dropna().astype(str)), axis=1)
                
                resultado_genero = df_top500[df_top500['genres_combined'].str.contains(genre_input, case=False, na=False)]
                
                if resultado_genero.empty:
                    st.warning(f"No se encontraron películas para el género '{genre_input}' en el Top 500.")
                else:
                    st.success(f"Top 10 películas del género '{genre_input}' (Top 500):")
                    for index, row in resultado_genero.sort_values(by='averageRating', ascending=False).head(10).iterrows():
                        title = row["title"]
                        year = row["year"]
                        director = row["director/0"] if "director/0" in row and pd.notna(row["director/0"]) else "N/A"
                        avg_rating = row["averageRating"]
                        poster_url = row["posterUrl"] if "posterUrl" in row and pd.notna(row["posterUrl"]) else ""

                        movie_info_html = f"<div style='display:flex; align-items:center; margin-bottom: 20px; border-bottom: 1px solid #ddd; padding-bottom: 10px;'>"
                        if poster_url:
                            movie_info_html += f"<img src='{poster_url}' style='width:90px; height:auto; margin-right:20px; border-radius:5px;'>"
                        movie_info_html += f"<div>"
                        movie_info_html += f"  <h4 style='margin:0;'>{title} ({int(year)})</h4>"
                        movie_info_html += f"  <p style='margin: 5px 0;'><strong>Director:</strong> {director}</p>"
                        movie_info_html += f"  <p style='margin: 5px 0;'><strong>Calificación Promedio:</strong> ⭐ {avg_rating}</p>"
                        movie_info_html += f"</div></div>"
                        st.markdown(movie_info_html, unsafe_allow_html=True)

    # =========================================================================
    # PESTAÑA 3: QUIZ INTERACTIVO DE RECOMENDACIÓN
    # =========================================================================
    with tab_quiz:
        st.header("Cuestionario de Recomendación Personalizada")
        st.markdown("Responde a las siguientes preguntas para descubrir tus películas ideales basadas en nuestro algoritmo predictivo:")

        def cargar_y_limpiar_datos(df_source):
            df = df_source.copy()
            df = df.rename(columns={
                'title': 'título',
                'year': 'año',
                'country': 'país o región',
                'averageRating': 'rating de Letterboxd'
            })
            director_cols_map = {f'director/{i}': f'director{i}' for i in range(3) if f'director/{i}' in df.columns}
            df = df.rename(columns={**director_cols_map, **{f'genres/{i}': f'género{i}' for i in range(8) if f'genres/{i}' in df.columns}})

            if 'sinopsis' not in df.columns: df['sinopsis'] = ''
            if 'duración (minutos)' not in df.columns: df['duración (minutos)'] = 120
            if 'idioma' not in df.columns: df['idioma'] = 'inglés'

            columnas_str = ['título', 'sinopsis', 'idioma', 'país o región'] + list(director_cols_map.values())
            for col in columnas_str:
                if col in df.columns: df[col] = df[col].astype(str).str.strip()

            for i in range(8):
                col_gen = f'género{i}'
                if col_gen in df.columns: df[col_gen] = df[col_gen].astype(str).str.strip().str.capitalize()
            return df

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
                    'usa/canadá': ['estados unidos', 'canadá', 'usa', 'united states', 'canada'],
                    'europa': ['europa', 'francia', 'españa', 'reino unido', 'italia', 'alemania'],
                    'asia': ['asia', 'japón', 'corea', 'china', 'india'],
                    'latinoamérica': ['latinoamérica', 'argentina', 'méxico', 'brasil', 'chile'],
                    'áfrica': ['áfrica', 'sudáfrica', 'egipto'],
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

        df_peliculas = cargar_y_limpiar_datos(df_top500)

        # Obtener géneros únicos para el selector web
        all_cleaned_genres = set()
        for i in range(8):
            col_gen = f'género{i}'
            if col_gen in df_peliculas.columns:
                all_cleaned_genres.update(df_peliculas[col_gen].dropna().unique())
        lista_opciones_genero = sorted([g for g in all_cleaned_genres if g and g.lower() != 'nan'])
        lista_opciones_genero.insert(0, "Ninguno")

        # Formulario de Entrada Web de Streamlit
        with st.form("quiz_form"):
            col_q1, col_q2 = st.columns(2)
            
            with col_q1:
                gen_pref = st.selectbox("1. ¿Qué género te gustaría ver hoy?", lista_opciones_genero)
                dur_opt_label = st.radio("2. ¿Qué duración prefieres?", [
                    "Menos de 90 minutos", "90–120 minutos", "120–150 minutos", "Más de 150 minutos", "Me da igual"
                ], index=4)
                ep_opt_label = st.radio("3. ¿De qué época prefieres la película?", [
                    "Antes de 1970", "1970–1989", "1990–2009", "2010+", "No importa"
                ], index=4)
                rat_opt_label = st.radio("4. ¿Qué calificación mínima en Letterboxd buscas?", [
                    "3.5+", "4.0+", "4.3+", "Top rated (4.5+)", "Me da igual"
                ], index=4)
                region_opt = st.selectbox("5. ¿De qué región te gustaría ver una película?", [
                    "Cualquiera", "USA/Canadá", "Europa", "Asia", "Latinoamérica", "África", "Oceanía"
                ])
                
            with col_q2:
                id_opt_label = st.radio("6. ¿Qué prefieres respecto al idioma?", [
                    "Solo Español", "Español/Inglés", "Cualquier idioma", "Descubrir otros (No inglés/español)"
                ], index=2)
                exp_opt = st.selectbox("7. ¿Qué tipo de experiencia buscas?", [
                    "Indiferente", "Emocionarme", "Reflexionar", "Suspenso", "Reír", "Sorprenderme"
                ])
                evitar_opt = st.text_input("8. ¿Quieres evitar algún género? (Separados por comas o 'ninguno')", "ninguno")
                dir_opt = st.text_input("9. ¿Hay algún director que te guste especialmente? (Opcional)", "")
                n_recom = st.slider("10. ¿Cuántas recomendaciones deseas?", min_value=1, max_value=5, value=3, step=2)

            submit_btn = st.form_submit_button("Generar Recomendaciones")

        # Mapeos de etiquetas a códigos originales
        map_dur = {"Menos de 90 minutos": "1", "90–120 minutos": "2", "120–150 minutos": "3", "Más de 150 minutos": "4", "Me da igual": "5"}
        map_ep = {"Antes de 1970": "1", "1970–1989": "2", "1990–2009": "3", "2010+": "4", "No importa": "5"}
        map_rat = {"3.5+": "1", "4.0+": "2", "4.3+": "3", "Top rated (4.5+)": "4", "Me da igual": "5"}
        map_id = {"Solo Español": "1", "Español/Inglés": "2", "Cualquier idioma": "3", "Descubrir otros (No inglés/español)": "4"}

        if submit_btn:
            respuestas_usuario = {
                'genero': gen_pref,
                'duracion': map_dur[dur_opt_label],
                'epoca': map_ep[ep_opt_label],
                'rating': map_rat[rat_opt_label],
                'region': region_opt.lower(),
                'idioma': map_id[id_opt_label],
                'experiencia': exp_opt.lower(),
                'evitar': evitar_opt.lower(),
                'director': dir_opt.strip().lower(),
                'cantidad': n_recom
            }

            resultados = filtrar_y_puntuar(df_peliculas, respuestas_usuario)
            n_mostrar = min(len(resultados), respuestas_usuario['cantidad'])

            if n_mostrar == 0:
                st.warning("No se encontraron películas que coincidan exactamente con tus criterios de filtrado. ¡Prueba reduciendo las restricciones!")
            else:
                st.balloons()
                st.success(f"Basado en tus respuestas, estas son tus {n_mostrar} mejores recomendaciones:")
                
                for idx in range(n_mostrar):
                    peli = resultados.iloc[idx]

                    generos = []
                    for i in range(8):
                        gen_col = f'género{i}'
                        if gen_col in peli.index and pd.notna(peli[gen_col]) and str(peli[gen_col]).strip() != '' and str(peli[gen_col]).lower() != 'nan':
                            generos.append(str(peli[gen_col]))
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

                    movie_info_html = f"<div style='display:flex; align-items:flex-start; margin-bottom: 25px; background-color:#f9f9f9; padding:15px; border-radius:10px; border-left: 5px solid #2e7d32;'>"
                    if poster_url:
                        movie_info_html += f"<img src='{poster_url}' style='width:110px; height:auto; margin-right:20px; border-radius:5px; box-shadow: 2px 2px 5px rgba(0,0,0,0.1);'>"
                    movie_info_html += f"<div>"
                    movie_info_html += f"  <h3 style='margin:0; color:#1e1e1e;'>{peli['título']} ({int(peli['año'])})</h3>"
                    movie_info_html += f"  <p style='margin: 6px 0; color:#444;'><strong>Director(es):</strong> {directores_str}</p>"
                    movie_info_html += f"  <p style='margin: 6px 0; color:#444;'><strong>Calificación Promedio:</strong> {peli['rating de Letterboxd']}</p>"
                    movie_info_html += f"  <p style='margin: 6px 0; color:#444;'><strong>Duración:</strong> {int(peli['duración (minutos)'])} minutos</p>"
                    movie_info_html += f"  <p style='margin: 6px 0; color:#444;'><strong>País:</strong> {peli['país o región']}</p>"
                    movie_info_html += f"  <p style='margin: 6px 0; color:#444;'><strong>Géneros:</strong> {generos_str}</p>"
                    movie_info_html += f"  <p style='margin: 10px 0 0 0; padding:8px; background-color:#e8f5e9; border-radius:5px; color:#1b5e20;'><strong> Por qué te lo recomiendo:</strong> {por_que}</p>"
                    movie_info_html += f"</div></div>"
                    st.markdown(movie_info_html, unsafe_allow_html=True)

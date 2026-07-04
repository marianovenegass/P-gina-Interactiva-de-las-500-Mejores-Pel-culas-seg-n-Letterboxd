# Sistema de Recomendación y Análisis del Top 500 de Películas (Streamlit)

Este repositorio contiene una aplicación interactiva desarrollada en **Streamlit** para explorar, visualizar y obtener recomendaciones personalizadas del **Top 500 de películas** basándose en el archivo `top500.csv`. 

El código original de Google Colab ha sido adaptado para funcionar de forma nativa en la web, sustituyendo los inputs de consola (`input()`) por componentes interactivos de Streamlit (`st.selectbox`, `st.text_input`, etc.) y renderizando los gráficos interactivos de Plotly, Seaborn y las imágenes de los posters correctamente.

---

## 🚀 Estructura Recomendada del Proyecto

Para desplegar este proyecto en Streamlit de forma exitosa, organiza tus archivos de la siguiente manera:

```text
├── top500.csv              # Base de datos de las películas (Verbatim)
├── app.py                  # Código principal de la aplicación Streamlit
├── requirements.txt        # Dependencias del proyecto
└── README.md               # Este archivo de instrucciones
```

---

## 🛠️ Requisitos e Instalación

Para ejecutar la aplicación localmente o en **Streamlit Community Cloud**, necesitas crear un archivo `requirements.txt` con las siguientes dependencias:

```text
streamlit
pandas
numpy
plotly
matplotlib
seaborn
openpyxl
```

### Instalación Local:

1. **Clona este repositorio** o descarga los archivos en una carpeta local.
2. **Instala las dependencias** ejecutando en tu terminal:
   ```bash
   pip install -r requirements.txt
   ```
3. **Ejecuta la aplicación**:
   ```bash
   streamlit run app.py
   ```

---

## 💻 Guía de Migración de Código (De Colab a Streamlit)

A continuación se detalla cómo adaptar las funciones clave del Jupyter Notebook a la estructura orientada a eventos de Streamlit dentro de tu archivo `app.py`:

### 1. Carga de Datos y Caché
En lugar de usar la ruta fija de Colab (`/content/top500.csv`), lee el archivo directamente de la raíz del proyecto y optimiza el rendimiento usando `@st.cache_data`.

```python
import streamlit as st
import pandas as pd

@st.cache_data
def load_data():
    # Lee el archivo 'top500.csv' verbatim
    return pd.read_csv("top500.csv")

df_top500 = load_data()
```

### 2. Sustitución de `input()` y `display(HTML())`
Streamlit no soporta `input()` de consola ni `IPython.display`. En su lugar, usa componentes nativos de interfaz de usuario y `st.markdown` con soporte HTML (`unsafe_allow_html=True`):

* **Buscar por País:**
  ```python
  country = st.selectbox("Selecciona un país:", df_top500["country"].unique())
  # Filtrado y lógica...
  st.markdown(movie_info_html, unsafe_allow_html=True)
  ```

* **Mostrar Gráficos de Plotly:**
  Sustituye `fig.show()` por:
  ```python
  st.plotly_chart(fig, use_container_width=True)
  ```

* **Mostrar Gráficos de Matplotlib/Seaborn:**
  Sustituye `plt.show()` por:
  ```python
  st.pyplot(fig)
  ```

### 3. Quiz Interactivo en la Barra Lateral o Tabs
El quiz interactivo (`ejecutar_quiz()`) puede transformarse en un formulario en la barra lateral (`st.sidebar.form`) o en una pestaña principal para que el usuario envíe todas sus respuestas a la vez:

```python
with st.form("quiz_form"):
    st.subheader("🎯 Quiz de Recomendación")
    gen_pref = st.selectbox("¿Qué género te gustaría ver hoy?", opciones_generos)
    dur_opt = st.radio("¿Qué duración prefieres?", ["Menos de 90 min", "90–120 min", "120–150 min", "Más de 150 min", "Me da igual"])
    # ... resto de preguntas
    submit_button = st.form_submit_button("Obtener Recomendaciones")

if submit_button:
    # Llamar a las funciones filtrar_y_puntuación() y mostrar resultados
```

---

## 📊 Características de la Aplicación

1. **Dashboard Estadístico:** Visualización del Top 500 mediante mapas coropléticos interactivos (Plotly), evolución histórica por año de estreno, y gráficos de barras (Seaborn) que muestran los directores y géneros más predominantes.
2. **Explorador por País y Género:** Buscador interactivo dinámico con despliegue de las fichas de las películas incluyendo su póster oficial de Letterboxd.
3. **Sistema de Scoring Adaptativo (Quiz):** Algoritmo inteligente que evalúa las preferencias del usuario (duración, época, rating mínimo, región, director y experiencia emocional deseada) para puntuar y ordenar las mejores recomendaciones cinematográficas en tiempo real.

---

## 🌐 Despliegue en Streamlit Cloud

1. Sube tus archivos (`app.py`, `top500.csv`, `requirements.txt`) a un repositorio público de **GitHub**.
2. Entra en [share.streamlit.io](https://share.streamlit.io) e inicia sesión con tu cuenta de GitHub.
3. Haz clic en **"New app"**, selecciona tu repositorio, la rama (`main`) y el archivo principal (`app.py`).
4. ¡Haz clic en **"Deploy!"** y tu aplicación estará online para todo el mundo!

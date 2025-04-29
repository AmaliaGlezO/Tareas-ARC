import os
import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt
import pdfplumber
from transformers import pipeline

# Función para extraer texto de un PDF
def extraer_texto_de_pdf(ruta_pdf):
    texto = ""
    with pdfplumber.open(ruta_pdf) as pdf:
        for pagina in pdf.pages:
            texto += pagina.extract_text()
    return texto

# Cargar un modelo de pregunta-respuesta (QA)
qa_pipeline = pipeline("question-answering", model="mrm8488/bert-spanish-cased-finetuned-squad")

# Extraer información usando QA
def extraer_informacion_con_qa(texto, pregunta):
    try:
        resultado = qa_pipeline(question=pregunta, context=texto)
        if resultado["score"] > 0.5:  # Filtrar respuestas con baja confianza
            return resultado["answer"]
        else:
            return None
    except:
        return None

# Extraer autores y manejar diferentes formatos
def extraer_autores(texto):
    respuesta = extraer_informacion_con_qa(texto, "Lista los autores del artículo")
    if not respuesta:
        return []
    # Manejar diferentes formatos de separación
    for separador in [", ", "; ", " y "]:
        if separador in respuesta:
            return respuesta.split(separador)
    return [respuesta]

# Función para crear el grafo
def crear_grafo(datos):
    G = nx.Graph()
    for doc in datos:
        titulo = doc["titulo"]
        autores = doc["autores"]
        G.add_node(titulo, type="titulo")
        for autor in autores:
            G.add_node(autor, type="autor")
            G.add_edge(autor, titulo)
    return G

# Interfaz de Streamlit
st.title("Visualización de Red de Autores y Artículos")

# Cargar archivos PDF
carpeta_pdfs = st.text_input("Ingresa la ruta de la carpeta con los PDFs:", "articles")

if os.path.exists(carpeta_pdfs):
    archivos_pdf = [archivo for archivo in os.listdir(carpeta_pdfs) if archivo.endswith(".pdf")]
    if archivos_pdf:
        st.write(f"Se encontraron {len(archivos_pdf)} archivos PDF en la carpeta.")
        
        # Extraer texto y procesar
        textos = []
        for archivo in archivos_pdf:
            ruta_completa = os.path.join(carpeta_pdfs, archivo)
            texto = extraer_texto_de_pdf(ruta_completa)
            textos.append(texto)

        # Procesar todos los textos
        datos = []
        for texto in textos:
            titulo = extraer_informacion_con_qa(texto, "¿Cuál es el título del artículo?")
            autores = extraer_autores(texto)
            if titulo and autores:  # Solo añadir si se encontraron título y autores
                datos.append({"titulo": titulo, "autores": autores})

        if datos:
            st.write("### Datos extraídos:")
            st.json(datos)  # Mostrar los datos extraídos en formato JSON

            # Crear el grafo
            G = crear_grafo(datos)

            # Visualizar el grafo
            st.write("### Grafo de Autores y Artículos")
            pos = nx.spring_layout(G)
            plt.figure(figsize=(10, 8))
            nx.draw(G, pos, with_labels=True, node_color="lightblue", node_size=2000, font_size=10, font_weight="bold")
            st.pyplot(plt)
        else:
            st.warning("No se pudieron extraer títulos y autores de los PDFs.")
    else:
        st.error("No se encontraron archivos PDF en la carpeta.")
else:
    st.error("La carpeta no existe. Por favor, ingresa una ruta válida.")
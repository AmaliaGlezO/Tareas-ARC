import os
import requests
import feedparser
import csv

# Configuración
query = "data science"  # Puedes cambiar esto por el tema que te interese
max_results = 100
output_folder = "articles"

# Crear carpeta si no existe
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# URL base de arXiv API
base_url = "http://export.arxiv.org/api/query?"
search_query = f"search_query=all:{query}"
start = 0
max_results_param = f"max_results={max_results}"
sort_by = "sortBy=submittedDate"
sort_order = "sortOrder=descending"

url = f"{base_url}{search_query}&{sort_by}&{sort_order}&{max_results_param}&start={start}"

# Realizar la consulta
response = requests.get(url)
feed = feedparser.parse(response.content)

# Lista para almacenar los resultados
articles_data = []

# Procesar cada entrada
for entry in feed.entries:
    try:
        article = {
            'title': entry.title,
            'authors': [author.name for author in entry.authors],
            'link': entry.link,
            'published': entry.published
        }
        articles_data.append(article)
        print(f"Título: {article['title']}")
        print(f"Autores: {', '.join(article['authors'])}")
        print("-" * 80)
        
    except Exception as e:
        print(f"Error al procesar una entrada: {str(e)}")

# Agregamos el código para guardar los datos en un archivo CSV
output_file = "articles_data.csv"
with open(output_file, 'w', newline='', encoding='utf-8') as file:
    # Definimos las columnas del CSV
    writer = csv.DictWriter(file, fieldnames=['title', 'authors', 'link', 'published'])
    # Escribimos el encabezado
    writer.writeheader()
    # Escribimos los datos de cada artículo
    for article in articles_data:
        # Convertimos la lista de autores a una cadena de texto
        article_row = article.copy()
        article_row['authors'] = ', '.join(article['authors'])
        writer.writerow(article_row)

print(f"Datos guardados en {output_file}")

print("Proceso completado.")
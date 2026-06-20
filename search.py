from elasticsearch import Elasticsearch
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
import os

# ── 1. Cargar configuración ────────────────────────────────────────────────
load_dotenv()
URL   = os.getenv("ELASTICSEARCH_URL", "http://localhost:9200")
# Actualizamos el índice por defecto al de soporte
INDEX = os.getenv("INDEX_SOPORTE", "documentos_soporte")

# ── 2. Conectar a Elasticsearch y cargar modelo ───────────────────────────
es = Elasticsearch(URL)

if not es.ping():
    print(" No se pudo conectar a Elasticsearch. Verifica que Docker esté corriendo.")
    exit()

print("Conexión exitosa a Elasticsearch")
print("⏳ Cargando modelo de embeddings multilingüe...")
# Asegúrate de usar este mismo modelo en tu archivo de ingesta
modelo = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
print("Modelo listo\n")

# ── 3. Función de búsqueda VECTORIAL (kNN con HNSW) ───────────────────────
def busqueda_vectorial(consulta, top=5):
    vector_consulta = modelo.encode(consulta).tolist()

    respuesta = es.search(
        index=INDEX,
        body={
            "knn": {
                "field": "vector",
                "query_vector": vector_consulta,
                "k": top,
                "num_candidates": 20
            },
            "_source": ["texto"]
        }
    )
    return respuesta["hits"]["hits"]

# ── 4. Función de búsqueda TRADICIONAL (keyword / BM25) ───────────────────
def busqueda_keyword(consulta, top=5):
    respuesta = es.search(
        index=INDEX,
        body={
            "query": {
                "match": {
                    "texto": consulta
                }
            },
            "size": top,
            "_source": ["texto"]
        }
    )
    return respuesta["hits"]["hits"]

# ── 5. Función de búsqueda HÍBRIDA (RRF calculado en Python) ──────────────
def busqueda_hibrida(resp_vectorial, resp_keyword, top=5):
    rrf_scores = {}
    textos_docs = {}

    # Asignar puntajes según posición en búsqueda Vectorial
    for rank, hit in enumerate(resp_vectorial):
        doc_id = hit["_id"]
        textos_docs[doc_id] = hit["_source"]["texto"]
        # Fórmula RRF
        rrf_scores[doc_id] = rrf_scores.get(doc_id, 0.0) + (1.0 / (60 + rank + 1))

    # Asignar puntajes según posición en búsqueda Keyword
    for rank, hit in enumerate(resp_keyword):
        doc_id = hit["_id"]
        textos_docs[doc_id] = hit["_source"]["texto"]
        rrf_scores[doc_id] = rrf_scores.get(doc_id, 0.0) + (1.0 / (60 + rank + 1))

    # Ordenar por el mejor puntaje RRF
    hits_h_ordenados = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)[:top]

    # Reconstruir el formato para que sea compatible con mostrar_resultados()
    resultados_formateados = []
    for doc_id, score in hits_h_ordenados:
        resultados_formateados.append({
            "_score": score,
            "_source": {"texto": textos_docs[doc_id]}
        })
        
    return resultados_formateados

# ── 6. Función para mostrar resultados ────────────────────────────────────
def mostrar_resultados(resultados, tipo):
    print(f"\n{'='*60}")
    print(f"  RESULTADOS — {tipo}")
    print(f"{'='*60}")

    if not resultados:
        print("Sin resultados encontrados")
        return

    for i, hit in enumerate(resultados):
        score = hit["_score"]
        texto = hit["_source"]["texto"]
        print(f"\n  [{i+1}] Score: {score:.4f}")
        print(f"       {texto}")

# ── 7. Demo interactiva en Consola ────────────────────────────────────────
print("╔══════════════════════════════════════════════════════════╗")
print("║     DEMO — Base de Conocimiento de Soporte Técnico       ║")
print("║     Grupo 7 · IF0007 · UCR Sede del Caribe               ║")
print("╚══════════════════════════════════════════════════════════╝")
print()
print("Escribe el problema del cliente o la consulta de soporte.")
print("La misma consulta se evaluará de TRES formas distintas:")
print("  1️⃣  Búsqueda VECTORIAL  — Entiende el contexto del problema (kNN)")
print("  2️⃣  Búsqueda KEYWORD    — Busca errores o palabras exactas (BM25)")
print("  3️⃣  Búsqueda HÍBRIDA    — Combina precisión y contexto (RRF)")
print()
print("Escribe 'salir' para terminar.\n")

while True:
    consulta = input("🔍 Problema del cliente: ").strip()

    if consulta.lower() == "salir":
        print("\n Sistema de soporte finalizado.")
        break

    if not consulta:
        print("Escribe el caso a buscar.\n")
        continue

    print(f"\nAnalizando caso: '{consulta}'")

    # Ejecutar las búsquedas base
    resultados_vectorial = busqueda_vectorial(consulta)
    resultados_keyword   = busqueda_keyword(consulta)
    
    # Ejecutar la búsqueda híbrida uniendo las dos anteriores
    resultados_hibrida   = busqueda_hibrida(resultados_vectorial, resultados_keyword)

    # Mostrar comparativa de las TRES columnas
    mostrar_resultados(resultados_vectorial, "VECTORIAL (por contexto)")
    mostrar_resultados(resultados_keyword,   "KEYWORD   (por términos exactos)")
    mostrar_resultados(resultados_hibrida,   "HÍBRIDA   (Algoritmo RRF)")

    # ── Explicación del detrás de escena ──────────────────────────────
    print(f"\n{'─'*60}")
    print("  🔬 DETRÁS DE ESCENA")
    print(f"{'─'*60}")
    vector_consulta = modelo.encode(consulta).tolist()
    print(f"  El caso del cliente convertido a vector (primeros 8 de 384):")
    print(f"  {vector_consulta[:8]}")
    print(f"  Elasticsearch comparó este vector contra la base de datos")
    print(f"  de soporte usando el algoritmo HNSW y similitud de coseno.")
    print(f"{'─'*60}\n")
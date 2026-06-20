from elasticsearch import Elasticsearch
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
import json
import os



# ---------------- CONFIG ----------------

load_dotenv()


URL = os.getenv(
    "ELASTICSEARCH_URL",
    "http://localhost:9200"
)


INDEX = os.getenv(
    "INDEX_SOPORTE",
    "soporte_tecnico"
)



# ---------------- CONEXION ----------------


es = Elasticsearch(URL)


if not es.ping():

    print("No hay conexión con Elasticsearch")
    exit()


print("Elasticsearch conectado")



# ---------------- MODELO ----------------


print("Cargando modelo...")


modelo = SentenceTransformer(
    "paraphrase-multilingual-MiniLM-L12-v2"
)


print("Modelo listo")



# ---------------- DATASET ----------------


with open(
    "dataset_soporte.json",
    "r",
    encoding="utf-8"
) as archivo:

    documentos = json.load(archivo)



print(
    f"{len(documentos)} documentos encontrados"
)



# ---------------- CREAR INDICE ----------------


if es.indices.exists(index=INDEX):

    es.indices.delete(
        index=INDEX
    )

    print("Índice eliminado")



mapping = {


"mappings":{

"properties":{


"titulo":{

"type":"text"

},


"categoria":{

"type":"keyword"

},


"problema":{

"type":"text"

},


"solucion":{

"type":"text"

},


"texto":{

"type":"text"

},


"vector":{

"type":"dense_vector",

"dims":384,

"index":True,

"similarity":"cosine"

}


}

}

}



es.indices.create(

index=INDEX,

body=mapping

)


print(
"Índice creado"
)



# ---------------- INGESTA ----------------


for i, doc in enumerate(documentos):


# Unificamos todo el contexto rico del documento
    texto_completo = f"{doc['titulo']} {doc['categoria']} {doc['problema']} {doc['solucion']}"

    # Vectorizamos el contexto completo
    vector = modelo.encode(
        texto_completo
    ).tolist()
    
    # Recuerda actualizar el diccionario final para que BM25 también use todo el texto
    documento_final = {
        "titulo": doc["titulo"],
        "categoria": doc["categoria"],
        "problema": doc["problema"],
        "solucion": doc["solucion"],
        "texto": texto_completo, # Usamos la nueva variable aquí
        "vector": vector
    }
    es.index(
        index=INDEX,
        id=i+1,
        document=documento_final
    )

    print(
        f"[{i+1}] {doc['titulo']}"
    )

es.indices.refresh(
    index=INDEX
)

total = es.count(
    index=INDEX
)["count"]

print(
    f"\nIngesta terminada: {total} documentos"
)
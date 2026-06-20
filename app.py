# app.py
# Demo búsqueda semántica soporte técnico empresarial
# Grupo 7 - IF0007 Bases de Datos I - UCR

import streamlit as st
from elasticsearch import Elasticsearch
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
import os


# ---------------- CONFIG ----------------

st.set_page_config(
    page_title="Soporte TI Inteligente",
    page_icon="💻",
    layout="wide"
)


load_dotenv()

URL = os.getenv(
    "ELASTICSEARCH_URL",
    "http://localhost:9200"
)

INDEX = os.getenv(
    "INDEX_NAME",
    "soporte_tecnico"
)



# ---------------- RECURSOS ----------------

@st.cache_resource
def cargar_recursos():

    es = Elasticsearch(URL)

    modelo = SentenceTransformer(
        "paraphrase-multilingual-MiniLM-L12-v2"
    )

    return es, modelo


es, modelo = cargar_recursos()



# ---------------- HEADER ----------------

st.title("💻 Sistema Inteligente de Soporte Técnico")

st.subheader(
    "Búsqueda semántica usando Elasticsearch Vector Search"
)

st.markdown("---")



# ---------------- ESTADO ----------------


col1, col2, col3 = st.columns(3)


with col1:
    conectado = es.ping()
    if conectado:
        st.success("✅ Elasticsearch conectado")
    else:
        st.error("❌ Sin conexión")

with col2:
    if conectado:
        total = es.count(index=INDEX)["count"]
        st.info(f"📄 {total} casos indexados")
    else:
        st.info("📄 -- casos indexados")

with col3:

    st.info(
        "🧠 Modelo: MiniLM multilingüe\n384 dimensiones"
    )



st.markdown("---")



# ---------------- BUSQUEDA ----------------


st.markdown(
    "### Describe tu problema"
)


consulta = st.text_input(
    "",
    placeholder=
    "Ej: mi computadora se queda pegada cuando uso muchos programas"
)



buscar = st.button(
    "🔍 Buscar solución",
    type="primary"
)



# ---------------- LOGICA ----------------


if buscar and consulta:


    vector = modelo.encode(
        consulta
    ).tolist()



    # VECTORIAL

    vectorial = es.search(

        index=INDEX,

        body={

            "knn":{

                "field":"vector",

                "query_vector":vector,

                "k":5,

                "num_candidates":50
            },

            "_source":[

                "titulo",
                "categoria",
                "problema",
                "solucion"

            ]

        }

    )



    # BM25

    keyword = es.search(

        index=INDEX,

        body={

            "query":{

                "match":{

                    "texto":consulta

                }

            },


            "size":5,


            "_source":[

                "titulo",
                "categoria",
                "problema",
                "solucion"

            ]

        }

    )



    # ---------------- RRF ----------------


    rrf={}

    documentos={}


    for rank,hit in enumerate(
        vectorial["hits"]["hits"]
    ):

        id = hit["_id"]

        documentos[id]=hit["_source"]

        rrf[id]=rrf.get(id,0)+(
            1/(60+rank+1)
        )



    for rank,hit in enumerate(
        keyword["hits"]["hits"]
    ):

        id = hit["_id"]

        documentos[id]=hit["_source"]

        rrf[id]=rrf.get(id,0)+(
            1/(60+rank+1)
        )



    resultados = sorted(

        rrf.items(),

        key=lambda x:x[1],

        reverse=True

    )[:5]




# ---------------- RESULTADO PRINCIPAL ----------------
    st.markdown("---")
    st.markdown("## ⚡ Comparativa de Motores de Búsqueda")
    
    col_v, col_k, col_h = st.columns(3)

    # 1. Columna Vectorial
    with col_v:
        st.subheader("🧠 Vectorial (kNN)")
        for hit in vectorial["hits"]["hits"]:
            doc = hit["_source"]
            score = hit["_score"]
            with st.container(border=True):
                st.caption(f"Score: {score:.3f}")
                st.markdown(f"**{doc['titulo']}**")
                st.markdown(f"🏷️ *{doc['categoria']}*")
                st.markdown(f"{doc['problema'][:120]}...")

    # 2. Columna Léxica (BM25)
    with col_k:
        st.subheader("🔤 Léxica (BM25)")
        for hit in keyword["hits"]["hits"]:
            doc = hit["_source"]
            score = hit["_score"]
            with st.container(border=True):
                st.caption(f"Score: {score:.3f}")
                st.markdown(f"**{doc['titulo']}**")
                st.markdown(f"🏷️ *{doc['categoria']}*")
                st.markdown(f"{doc['problema'][:120]}...")

    # 3. Columna Híbrida (RRF)
    with col_h:
        st.subheader("⚡ Híbrida (RRF)")
        for id, score in resultados:
            doc = documentos[id]
            with st.container(border=True):
                st.caption(f"Score RRF: {score:.4f}")
                st.markdown(f"**{doc['titulo']}**")
                st.markdown(f"🏷️ *{doc['categoria']}*")
                st.markdown(f"{doc['problema'][:120]}...")
    # ---------------- EXPLICACION ----------------


    with st.expander(
        "🔬 Ver cómo funciona internamente"
    ):


        st.write(
            "Consulta original:"
        )


        st.code(
            consulta
        )


        st.write(
            "Primeros valores del embedding:"
        )


        st.code(
            vector[:10]
        )


        st.write(

            """
            La consulta fue transformada en un vector
            numérico de 384 dimensiones.

            Elasticsearch compara este vector mediante
            similitud de coseno utilizando búsqueda kNN
            con índice HNSW.

            También combina resultados tradicionales
            BM25 mediante RRF.
            """

        )



elif buscar:

    st.warning(
        "Escribe un problema primero"
    )



st.markdown("---")


st.caption(

    "Universidad de Costa Rica · IF0007 Bases de Datos I · Grupo 7"

)
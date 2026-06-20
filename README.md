
# Manual Técnico: 

**Universidad de Costa Rica · Sede del Caribe**
**Curso:** IF0007 - Bases de Datos I
**Desarrollado por:** Grupo 7
**Base de datos vectorial:** ElasticSearch

> [!NOTE]
>  Resumen del Proyecto
> Este proyecto implementa un motor de búsqueda avanzado utilizando **Elasticsearch** (v8.13) en un entorno contenedorizado con Docker. Emplea el modelo de Inteligencia Artificial `paraphrase-multilingual-MiniLM-L12-v2` (vía Hugging Face) para transformar texto en vectores de 384 dimensiones. El sistema destaca por una arquitectura que calcula el algoritmo **Reciprocal Rank Fusion (RRF)** en la capa de la aplicación (Python), logrando una **Búsqueda Híbrida** de nivel empresarial a costo cero.

---

## 📂 Estructura del Proyecto

El sistema utiliza una arquitectura plana (*Flat Architecture*) para facilitar su ejecución. Todos los archivos deben estar en la misma carpeta principal:

```text
📁 Proyecto_Vectorial/
├── 📄 .env                  # Variables de entorno y configuración
├── 📄 app.py                # Interfaz gráfica principal (Streamlit)
├── 📄 docker-compose.yml    # Configuración de contenedores (Elasticsearch + Dejavu)
├── 📄 ingest_soporte.py      # Script de vectorización para dataset de soporte
├── 📄 requirements.txt      # Dependencias de Python
└── 📄 search.py             # Interfaz de búsqueda por consola (Debug)
````

##  1. Prerrequisitos de Instalación

Antes de iniciar el sistema, asegúrese de contar con las siguientes herramientas y recursos en su entorno local:

1. **Hardware Mínimo:** Al menos 4GB de memoria RAM libre (Elasticsearch reserva 2GB para su máquina virtual Java).
    
2. **Docker Desktop:** Instalado y ejecutándose (estado _Running_).
    
3. **Python 3.x:** Instalado y agregado al PATH del sistema.
    
4. **Git (Opcional):** Para clonar el repositorio si aplica.
    

## 2. Descargar el Proyecto (Clonación)

Para obtener el código fuente manteniendo intacta la arquitectura plana del proyecto, abra su terminal en la ubicación donde desea guardar la carpeta y ejecute el siguiente comando:

```bash
git clone https://github.com/Angely-Guido/elasticsearch.git
```

Una vez descargado, ingrese a la carpeta del proyecto para ejecutar los siguientes pasos:

```Bash
cd la_ubicacion_de_la_carpeta_clonada
```
##  3. Configuración del Entorno

### Paso 3.1: Archivo de Variables de Entorno (`.env`)

El sistema utiliza un archivo de configuración centralizado para proteger credenciales y facilitar la portabilidad. Cree un archivo llamado exactamente `.env` en la raíz del proyecto y pegue el siguiente contenido:

```Fragmento de código
ELASTICSEARCH_URL=http://localhost:9200
INDEX_SOPORTE=soporte_tecnico
```

### Paso 3.2: Instalación de Dependencias

Abra su terminal (PowerShell o CMD) en la carpeta del proyecto e instale las librerías de Python necesarias para la IA y la interfaz gráfica:
### Paso 3.2: Instalación de Dependencias

Abra su terminal (PowerShell o CMD) en la carpeta del proyecto e instale las librerías de Python necesarias para la IA y la interfaz gráfica:

```bash
py -m pip install -r requirements.txt
```

> [!tip]
> Consejo de Buenas Prácticas
> Se recomienda realizar esta instalación dentro de un entorno virtual (`venv`) para no crear conflictos con otros proyectos de la computadora.

> [!tip]
> Alternativa si `py` no es reconocido
> Si el comando anterior no funciona, intente con `pip install -r requirements.txt`. Si tampoco funciona, consulte la sección de Troubleshooting sobre el error de `pip` no reconocido como comando.

> [!tip]
> Consejo de Buenas Prácticas Se recomienda realizar esta instalación dentro de un entorno virtual (`venv`) para no crear conflictos con otros proyectos de la computadora.

##  4. Levantamiento de la Base de Datos

Antes de iniciar, confirme que Docker Desktop está activo: 

```bash 
docker --version 
``` 

Si responde con un número de versión, proceda a encender el clúster de Elasticsearch y la interfaz visual Dejavu: 

```bash 
docker compose up -d 
```

> [!warning]
> La importancia del comando `-d` (Detached) Es vital incluir el `-d` al final. Esto obliga a la base de datos a correr silenciosamente en segundo plano, dejándole la terminal libre para ejecutar los siguientes scripts de Python. Si no lo pone, la terminal quedará bloqueada mostrando bitácoras.

> [!NOTE]
> Auditoría de Arranque
> Para confirmar que ambos servicios están vivos, verifique los dos por separado:
> 
> **Elasticsearch:** abra su navegador e ingrese a `http://localhost:9200`. Debería ver un archivo JSON de respuesta con el mensaje *"You Know, for Search"*.
> 
> **Dejavu:** abra su navegador e ingrese a `http://localhost:1358`. Debería ver la interfaz de Dejavu solicitando la URL de conexión al clúster.
> 
> Si alguno de los dos no responde, ejecute `docker ps` en la terminal y confirme que ambos contenedores (`elasticsearch-demo` y `dejavu-ui`) aparecen con estado `Up`.

##  5. Ingesta de Datos (Vectorización)

Al iniciar por primera vez, la base de datos está vacía. Es necesario ejecutar los scripts que descargan el modelo de IA, transforman los textos en matemáticas puras y los inyectan en Elasticsearch.

Ejecute los siguientes comandos en orden:

**1. Inyectar el dataset de soporte:**

```Bash
python ingest_soporte.py
```


> [!TIP]
> Tiempo de espera La primera vez que ejecute estos scripts, el sistema tardará unos segundos extra porque descargará automáticamente el modelo pre-entrenado de Hugging Face (~90MB).

##  6. Ejecución y Uso del Sistema

El proyecto cuenta con dos métodos de interacción preparados para la demostración técnica:

### Interfaz Gráfica Web (Modo Presentación)

Lanza la aplicación interactiva construida con Streamlit, ideal para visualizar las diferencias entre las búsquedas Vectorial, Keyword e Híbrida.

```Bash
streamlit run app.py
```

_(Esto abrirá automáticamente una pestaña en `http://localhost:8501`)_

### Interfaz de Consola (Modo Debug)

Lanza un script interactivo en la terminal para analizar los vectores crudos y el cálculo matemático detrás de escena.

```Bash
python search.py
```

_(Para detener este modo en la terminal, simplemente escriba la palabra `salir` y presione Enter)._

##  7. Auditoría Visual con Dejavu

El sistema incluye una interfaz gráfica para auditar los registros directamente en la base de datos, similar a phpMyAdmin.

1. Ingrese a `http://localhost:1358`
    
2. En el campo URL conecte su clúster: `http://localhost:9200` (o `http://127.0.0.1:9200`)
    
3. En el campo Índice escriba el nombre de la colección: `soporte_tecnico`
    
4. Haga clic en **Conectar**.
    

> [!warning]
> Cuidado al Exportar Datos Si desea utilizar la función de "Exportar" en Dejavu, asegúrese de conectarse indicando el nombre exacto del índice (ej. `soporte_tecnico`). Si utiliza el comodín asterisco (`*`), la herramienta de exportación colapsará y mostrará una pantalla en blanco debido a restricciones internas.

##  8. Apagado Limpio y Mantenimiento

Una vez finalizada la demostración, **NO** basta con cerrar la terminal. El motor de Java seguirá consumiendo memoria RAM en segundo plano. Para apagar la infraestructura correctamente:

```Bash
docker compose down
```

> [!WARNING]
> Persistencia de Datos ¡No se preocupe por la pérdida de vectores! Gracias a la configuración del volumen (`esdata`) en el archivo Docker Compose, toda la información de la base de datos queda guardada permanentemente en su disco duro para la próxima sesión.


### 9. Reinicio de Fábrica (Opcional)

Si se necesita borrar por completo la base de datos y comenzar desde cero (eliminando todos los índices, vectores y configuraciones guardadas), ejecute el siguiente comando.

> [!WARNING]
> Precaución: Pérdida total de datos El modificador `-v` (volumes) le indica a Docker que destruya el disco duro virtual donde Elasticsearch guarda la información. Después de ejecutar esto, la base de datos quedará completamente en blanco y deberá volver a correr los scripts de ingesta.

```Bash
docker compose down -v
```

##  10. Solución de Problemas Frecuentes 

> [!WARNING]
> - Error: `No se pudo conectar a Elasticsearch` al abrir la web o la consola **Causa:** El contenedor de Docker no está activo. **Solución:** Abra la terminal y asegúrese de ejecutar `docker compose up -d` antes de iniciar los scripts de Python.

> [!WARNING]
> - Error: `pip` no reconocido como comando interno o externo
> **Causa:** El instalador de Python no agregó la carpeta `Scripts` al PATH de Windows.
> **Solución:** Ejecute `python -m pip install --force-reinstall pip`, luego agregue manualmente la ruta de la carpeta `Scripts` a las Variables de Entorno del sistema y reinicie la terminal.

> [!WARNING]
> - Error de conflicto de versiones de `numpy` al instalar Streamlit
> **Causa:** Streamlit requiere una versión de `numpy` distinta a la que usan otras librerías como `opencv`.
> **Solución:** Verifique que las librerías del proyecto sigan funcionando con:
> ```bash
> python -c "from elasticsearch import Elasticsearch; from sentence_transformers import SentenceTransformer; print('Todo listo')"
> ```
> Si responde correctamente, el conflicto no afecta al proyecto y puede ignorarse.

> [!WARNING]
> - La columna de búsqueda Híbrida no aparece en Streamlit
> **Causa:** Error de indentación en Python — el bloque `with col_h:` quedó anidado dentro de `with col_k:`.
> **Solución:** Verifique que los tres bloques `with col_v:`, `with col_k:` y `with col_h:` tengan exactamente el mismo nivel de indentación dentro de la función.

> [!WARNING]
> - Dejavu muestra "No se puede conectar" al intentar conectar con Elasticsearch
> **Causa:** Configuración de CORS incompleta, o uso de `allow-origin=*` junto con `allow-credentials=true`, combinación que Elasticsearch rechaza por seguridad.
> **Solución:** En el `docker-compose.yml`, especifique el origen exacto en lugar del comodín:
> ```yaml
> http.cors.allow-origin=http://localhost:1358,http://127.0.0.1:1358
> ```

> [!WARNING]
> - Las búsquedas devuelven resultados aunque no tengan relación con la consulta
> **Causa:** La búsqueda vectorial siempre devuelve los documentos matemáticamente más cercanos, incluso si la similitud real es baja.
> **Solución:** Esto no es un error del sistema. Preste atención al *score* de similitud: valores cercanos a 0.9 indican alta confianza; valores cercanos a 0.6–0.7 indican que probablemente no existe contenido relevante en el dataset seleccionado.

> [!WARNING]
> - Error: `Failed to connect to the docker API` en la terminal **Causa:** El motor central de Docker Desktop está apagado. **Solución:** Busque "Docker Desktop" en el menú de Windows, ábralo y espere a que el estado cambie a verde (_Engine running_) antes de lanzar cualquier comando en PowerShell.

> [!WARNING]
> - Streamlit falla indicando que "no reconoce la librería" o "module not found" **Causa:** No se instalaron las dependencias del archivo o se está corriendo fuera del entorno virtual. **Solución:** Ejecute nuevamente el comando de instalación: `pip install -r requirements.txt`.

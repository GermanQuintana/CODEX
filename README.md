 (cd "$(git rev-parse --show-toplevel)" && git apply --3way <<'EOF' 
diff --git a//dev/null b/14-veterinary-assistant-web-app/README.md
index 0000000..b391102 100644
--- a//dev/null
+++ b/14-veterinary-assistant-web-app/README.md
@@ -0,0 +1,31 @@
+# Aplicación web: Asistente Veterinario
+
+Este ejemplo muestra cómo montar una aplicación web sencilla que permita elegir distintos asistentes basados en GPT, conversar con ellos, subir archivos y contabilizar los tokens consumidos por usuario.
+
+## Requisitos previos
+
+- Python 3.11 o superior
+- Una clave de OpenAI. Colócala en un archivo `.env` con el nombre `OPENAI_API_KEY`.
+- Dependencias: `fastapi`, `uvicorn`, `openai`, `tiktoken`, `python-multipart`, `python-dotenv`.
+
+Instala las dependencias con:
+
+```bash
+pip install fastapi uvicorn openai tiktoken python-multipart python-dotenv
+```
+
+## Ejecución
+
+1. Crea un archivo `.env` junto a `app.py`:
+   ```env
+   OPENAI_API_KEY=tu_api_key_aqui
+   ```
+2. Inicia la aplicación:
+   ```bash
+   uvicorn app:app --reload
+   ```
+3. Abre `http://localhost:8000/docs` para probar la API.
+
+## Código de ejemplo
+
+`app.py` contiene un esqueleto básico. Sustituye los valores marcados como `TODO` por tus propios datos (por ejemplo, nombres de asistentes o modelos).
 
EOF
)

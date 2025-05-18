 (cd "$(git rev-parse --show-toplevel)" && git apply --3way <<'EOF' 
diff --git a//dev/null b/14-veterinary-assistant-web-app/app.py
index 0000000..d717cd6 100644
--- a//dev/null
+++ b/14-veterinary-assistant-web-app/app.py
@@ -0,0 +1,51 @@
+import os
+from typing import Dict
+
+import dotenv
+import openai
+import tiktoken
+from fastapi import FastAPI, UploadFile, File, Form
+from fastapi.middleware.cors import CORSMiddleware
+
+dotenv.load_dotenv()
+
+# TODO: reemplaza con tu clave real en .env
+openai.api_key = os.getenv("OPENAI_API_KEY")
+
+# Diccionario de asistentes y modelos
+MODELOS: Dict[str, str] = {
+    "general": "gpt-3.5-turbo",
+    "exoticas": "gpt-4"
+}
+
+app = FastAPI()
+app.add_middleware(CORSMiddleware, allow_origins=["*"])
+
+# Almacena los tokens consumidos por usuario en memoria
+usuarios_tokens: Dict[str, int] = {}
+
+def contar_tokens(texto: str, modelo: str) -> int:
+    codificador = tiktoken.encoding_for_model(modelo)
+    return len(codificador.encode(texto))
+
+@app.post("/chat")
+async def chat(usuario: str = Form(...), asistente: str = Form(...), mensaje: str = Form(...)):
+    modelo = MODELOS.get(asistente, "gpt-3.5-turbo")
+    respuesta = openai.ChatCompletion.create(
+        model=modelo,
+        messages=[{"role": "user", "content": mensaje}]
+    )
+    contenido = respuesta.choices[0].message["content"]
+    tokens = respuesta.usage.total_tokens
+    usuarios_tokens[usuario] = usuarios_tokens.get(usuario, 0) + tokens
+    return {
+        "respuesta": contenido,
+        "tokens_usados": tokens,
+        "tokens_totales_usuario": usuarios_tokens[usuario]
+    }
+
+@app.post("/upload")
+async def subir_archivo(asistente: str = Form(...), archivo: UploadFile = File(...)):
+    datos = await archivo.read()
+    # TODO: procesa el archivo según tus necesidades
+    return {"archivo": archivo.filename, "tamano": len(datos)}
 
EOF
)

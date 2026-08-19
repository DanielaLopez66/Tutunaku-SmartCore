# Se sirve `socket_app` (FastAPI + Socket.IO combinados) bajo el nombre `app`
# para que el dashboard en tiempo real (Etapa 14) funcione también al correr
# `python main.py`.
from app.main import socket_app as app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

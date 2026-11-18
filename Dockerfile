FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app
COPY requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt \
    && useradd --system --uid 10001 cana

COPY app ./app
COPY templates ./templates
COPY main.py ./main.py
COPY gerar_qrcode.py ./gerar_qrcode.py
COPY listar_modelos.py ./listar_modelos.py

USER cana
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

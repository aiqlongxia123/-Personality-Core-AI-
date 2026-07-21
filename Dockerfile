FROM python:3.11-slim

WORKDIR /app

# 安装依赖
COPY pyproject.toml .
RUN pip install --no-cache-dir \
    sentence-transformers>=3.0 \
    scikit-learn>=1.4 \
    numpy>=1.26 \
    fastapi>=0.110 \
    uvicorn[standard]>=0.29 \
    pydantic>=2.0 \
    jieba>=0.42 \
    umap-learn>=0.5

# 复制源码
COPY src/ src/
COPY data/ data/
COPY api/ api/
COPY models/ models/

ENV PYTHONPATH=/app/src

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "api.server:app", "--host", "0.0.0.0", "--port", "8000"]

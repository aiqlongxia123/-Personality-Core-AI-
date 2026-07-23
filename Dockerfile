FROM python:3.11-slim

WORKDIR /app

# 创建非 root 用户
RUN groupadd -r appuser && useradd -r -g appuser -d /app -s /sbin/nologin appuser

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

COPY src/ src/
COPY data/ data/
COPY api/ api/
COPY models/ models/

ENV PYTHONPATH=/app/src
ENV PERSONALITY_API_KEY=CHANGE_ME_IN_PRODUCTION

EXPOSE 8000

# 设置所有者
RUN chown -R appuser:appuser /app /tmp/model_cache
USER appuser

CMD ["python", "-m", "uvicorn", "api.server:app", "--host", "0.0.0.0", "--port", "8000"]

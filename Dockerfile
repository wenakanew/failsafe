FROM python:3.13-slim
WORKDIR /app
COPY pyproject.toml .python-version ./
# Install uv and dependencies
RUN pip install uv && uv sync
COPY . .
EXPOSE 5000
CMD ["uv", "run", "gunicorn", "--bind", "0.0.0.0:5000", "run:app"]

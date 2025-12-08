# Usar una imagen base de Python oficial
FROM python:3.10-slim

# Configuraciones de entorno
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema (necesarias para algunas librerías)
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Instalar dependencias de Python
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código fuente
COPY . /app/

# Puerto expuesto
EXPOSE 8000

# Comando de inicio del servidor
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
# Usar una imagen oficial de Python
FROM python:3.10-slim

# Configurar el directorio de trabajo
WORKDIR /app

# Copiar los archivos de requerimientos e instalarlos
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar todo el contenido del backend al contenedor
COPY . .

# Exponer el puerto en el que Render escuchará la aplicación
EXPOSE 10000

# Comando para ejecutar la aplicación con Gunicorn apuntando a tu instancia de Flask
CMD ["gunicorn", "--bind", "0.0.0.0:10000", "cuentas:instancia_servidor"]
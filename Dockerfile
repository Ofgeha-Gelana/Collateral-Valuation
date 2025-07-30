# Use official Python image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all source code
COPY . .

# Expose the port Streamlit uses
EXPOSE 9000

# Run the Streamlit app
# CMD ["streamlit", "run", "ui/streamlit_app.py", "--server.port=9000", "--server.enableCORS=false"]

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "9000"]


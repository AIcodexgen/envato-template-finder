FROM mcr.microsoft.com/playwright/python:v1.40.0-jammy

# Set environment variables to suppress pip warnings
ENV PIP_ROOT_USER_ACTION=ignore \
    PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Playwright browsers are pre-installed in this image.
# We run install chromium just to ensure it matches the package version if needed.
RUN playwright install chromium

# Copy application code
COPY . .

# Use the built-in pwuser provided by the Playwright image
RUN chown -R pwuser:pwuser /app
USER pwuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000')" || exit 1

# Run the application
CMD ["python", "main.py"]

# Multi-stage lightweight Python container
FROM python:3.12-slim

WORKDIR /app

# Ensure non-root user for security
RUN groupadd -r schoolapp && useradd -r -g schoolapp schoolapp

# Copy application source
COPY . /app

# Setup data directory permissions
RUN mkdir -p /app/data && chown -R schoolapp:schoolapp /app

USER schoolapp

ENV PYTHONPATH=/app/src
ENV PYTHONUNBUFFERED=1

# Expose server port
EXPOSE 8000

# Start fee management dashboard
CMD ["python", "-m", "school_fee_system", "serve", "--host", "0.0.0.0", "--port", "8000"]

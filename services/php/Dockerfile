FROM php:8.4-cli-alpine
WORKDIR /app
COPY index.php .
EXPOSE 8000
CMD ["php", "-S", "0.0.0.0:8000", "-t", "/app"]

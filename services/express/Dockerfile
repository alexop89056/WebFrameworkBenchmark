FROM node:22-alpine
WORKDIR /app
COPY package.json .
RUN npm install --omit=dev --no-audit --no-fund
COPY index.js .
EXPOSE 8000
CMD ["node", "index.js"]

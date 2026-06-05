FROM node:20-slim

WORKDIR /app
COPY services/automation-node/package.json package.json
RUN npm install
COPY services/automation-node/src src

CMD ["node", "src/server.js"]

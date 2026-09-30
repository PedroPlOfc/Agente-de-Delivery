FROM evoapicloud/evolution-api:v1.8.2

ENV PORT=8080
EXPOSE 8080

CMD ["node", "dist/src/main.js"]
FROM maven:3.9.9-eclipse-temurin-21 AS build
WORKDIR /workspace
COPY pom.xml .
RUN mvn -q -DskipTests dependency:go-offline
COPY src ./src
RUN mvn -q package

FROM eclipse-temurin:21-jre
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/* && useradd --system --uid 10001 cana
COPY --from=build /workspace/target/cana-backend.jar /app/app.jar
USER cana
EXPOSE 8081
HEALTHCHECK --interval=10s --timeout=5s --retries=20 --start-period=45s CMD curl -fsS http://127.0.0.1:8081/api/health || exit 1
ENTRYPOINT ["java", "-XX:MaxRAMPercentage=75.0", "-jar", "/app/app.jar"]

FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build
WORKDIR /src
COPY csharp.csproj .
RUN dotnet restore
COPY Program.cs .
RUN dotnet publish -c Release -o /out --no-restore

FROM mcr.microsoft.com/dotnet/aspnet:8.0
WORKDIR /app
ENV ASPNETCORE_URLS=http://0.0.0.0:8000
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*
COPY --from=build /out .
EXPOSE 8000
ENTRYPOINT ["dotnet", "csharp.dll"]

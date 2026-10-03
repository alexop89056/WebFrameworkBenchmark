using Microsoft.AspNetCore.Builder;
using Microsoft.AspNetCore.Http;

var builder = WebApplication.CreateBuilder(args);
var app = builder.Build();

app.MapGet("/", () => Results.Json(new
{
    message = "hello",
    framework = "csharp-aspnet-minimal"
}));

app.Run();

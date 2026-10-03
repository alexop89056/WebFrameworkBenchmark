from django_bolt import BoltAPI

api = BoltAPI()


@api.get("/")
async def hello():
    return {"message": "hello", "framework": "django-bolt"}

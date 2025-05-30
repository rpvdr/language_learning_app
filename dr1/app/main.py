import logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from fastapi.middleware.cors import CORSMiddleware
from .routers import phrases, parts_of_speech, auth, search, studyset, training, semantic_groups, notes, profile, categories, words, labels, components

app = FastAPI(
    title="German Language Learning API",
    description="API for managing German words, phrases, components, examples, and semantic groups.",
    version="1.0.0"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Optional: Custom OpenAPI schema function (uncomment to use)
# def custom_openapi():
#     if app.openapi_schema:
#         return app.openapi_schema
#     openapi_schema = get_openapi(
#         title=app.title,
#         version=app.version,
#         description=app.description,
#         routes=app.routes,
#     )
#     # You can modify openapi_schema here if needed
#     app.openapi_schema = openapi_schema
#     return app.openapi_schema
# app.openapi = custom_openapi


app.include_router(phrases.router, prefix="/api", tags=["phrases"])


app.include_router(words.router, prefix="/api", tags=["words"])


app.include_router(parts_of_speech.router, prefix="/api", tags=["parts_of_speech"])


app.include_router(auth.router, prefix="/api", tags=["auth"])


app.include_router(profile.router, prefix="/api", tags=["profile"])


app.include_router(categories.router, prefix="/api", tags=["categories"])


app.include_router(studyset.router, prefix="/api", tags=["studyset"])


app.include_router(training.router, prefix="/api", tags=["training"])


app.include_router(semantic_groups.router, prefix="/api", tags=["semantic_groups"])


app.include_router(notes.router, prefix="/api", tags=["notes"])


app.include_router(labels.router, prefix="/api", tags=["labels"])


app.include_router(components.router, prefix="/api", tags=["components"])


app.include_router(search.router, prefix="/api", tags=["search"])

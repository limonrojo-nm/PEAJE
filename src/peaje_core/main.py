from fastapi import FastAPI

app = FastAPI(title="peaje-core")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}

from app import app


def main():
    import os
    import uvicorn

    uvicorn.run("server.app:app", host="0.0.0.0", port=int(os.getenv("PORT", "8000")))


if __name__ == "__main__":
    main()
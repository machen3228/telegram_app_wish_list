import uvicorn

from application import app

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=80)  # noqa: S104

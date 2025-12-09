import application  # noqa: F401
import uvicorn

if __name__ == '__main__':
    uvicorn.run('application:app', host='0.0.0.0', port=80)  # noqa: S104

import uvicorn

import application  # noqa: F401

if __name__ == '__main__':
    uvicorn.run('application:app', host='0.0.0.0', port=80, reload=True)  # noqa: S104

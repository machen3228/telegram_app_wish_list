from flask import Flask, render_template
from flask.typing import ResponseReturnValue

app = Flask(__name__)


@app.route('/')  # type: ignore[misc]
def web() -> ResponseReturnValue:
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port='80')  # noqa: S201 S104

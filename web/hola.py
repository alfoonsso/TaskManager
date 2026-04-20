from flask import Flask

app = Flask(__name__)

@app.route('/')
def index():
    return '<h1>Hola desde Flask</h1><p>TaskManager está en construcción.</p>'

if __name__ == '__main__':
    app.run(debug=True)

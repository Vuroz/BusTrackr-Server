from bustrackr_server import app

@app.route('/')
def index():
    '''Handler for index the index (`/`) route'''

    return '<p>Hello, World!</p>'
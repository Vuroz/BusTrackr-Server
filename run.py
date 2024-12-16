from bustrackr_server import app, fix_database
from flask.cli import with_appcontext

@app.cli.command('initdb')
@with_appcontext
def init_db_command():
    '''Load all relevant static data into the database'''
    fix_database()

if __name__ == '__main__':
    app.run(host='localhost', port=5000, debug=False) # Start the application :)
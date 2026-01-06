#!/usr/bin/env python
import os
os.environ['FLASK_ENV'] = 'production'
from wsgi import app

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)

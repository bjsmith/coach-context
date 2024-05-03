import os
from web_app import *
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    wapp.run(host='0.0.0.0', port=port)

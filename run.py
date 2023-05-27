from app import create_app
from config import Config, config
import os

current_config: Config = None

if os.getenv('FLASK_ENV') == 'production':
    current_config = config['production']()
else:
    current_config = config['development']()

app = create_app(current_config)

if __name__ == '__main__':
    app.run()

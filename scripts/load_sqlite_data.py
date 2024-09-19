import sys
from irisiceberg import main, app

if __name__ == '__main__':
    config_path = sys.argv[1] 
    config = app.load_config(config_path)
    ice = main.Iceberg(config)
    

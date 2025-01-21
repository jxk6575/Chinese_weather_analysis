import os
import sys
from pathlib import Path

def run_web_server():
    project_root = Path(__file__).parent.absolute()
    web_dir = project_root / 'web'
    
    if str(web_dir) not in sys.path:
        sys.path.insert(0, str(web_dir))
    
    os.chdir(web_dir)
    
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "weather_web.settings")
    
    try:
        import django
        django.setup()
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    
    execute_from_command_line([sys.argv[0], 'runserver'])

if __name__ == "__main__":
    run_web_server() 
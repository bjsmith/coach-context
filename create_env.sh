conda env export | grep -v "^prefix: " > environment.yml
pip list --format=freeze > requirements.txt
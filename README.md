# Taskmanagement-KIP
Des wird super

## Getting Started

1. Run `pip install -e .` in the root directory of the project to install the package in editable mode. (Maybe create a virtual environment first)
2. Create a ".env" file in the root dirctory of the project with the following content (add the api key):
   ```
    GEMINI_API_KEY=""
   ``` 
3. Run the following command to start the backend:
`python .\src\backend\api.py`

4. For the Frontend:
 - Either open the html file from the frontend folder in a browser
 - Or cd into the frontend folder and run `python -m http.server 8001` to start a local server and open `http://localhost:8001` in your browser. 
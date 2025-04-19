# Taskmanagement-KIP
Des wird super

## Getting Started

1. Create a virtual environment containing Python==3.11.3 using `venv` or `conda` (optional but highly recommended).
2. Clone the repository using `git clone` and navigate to the project directory.
3. Run `pip install -e .` in the root directory of the project to install the package in editable mode. You may also choose to additionally install the development tools with `pip install -e .[dev]`.
4. Create a `.env` file in the root directory of the project and add the api keys:
   ```
    GEMINI_API_KEY="<your_api_key>"
    OPENAI_API_KEY="<your_api_key>"
   ```
5. Start the backend server by running `python backend/src/app.py`.
6. View the frontend by opening the HTML file in the `frontend` folder in a web browser or by running `python -m http.server 8001` in the `frontend` folder and navigating to `http://localhost:8001`.

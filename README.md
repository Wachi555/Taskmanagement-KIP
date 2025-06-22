# Taskmanagement-KIP
Des wird super

## Getting Started

1. Create a virtual environment containing Python==3.11.3 using `venv` or `conda`
   (optional but highly recommended).
2. Clone the repository using `git clone` and navigate to the project directory.
3. Using the terminal, run `pip install -e .` in the root directory of the project to
   install the package in editable mode. You may also choose to additionally install the
   development tools with `pip install -e .[dev]`.
4. Create a `.env` file in the root directory of the project and add the api keys:
   ```
    GEMINI_API_KEY="<your_api_key>"
    OPENAI_API_KEY="<your_api_key>"
   ```
5. Using the terminal, navigate to the frontend/src directory using `cd ./frontend/src`,
   and run `npm install` to install the frontend dependencies.

## Starting the Application
1. Ensure you have finished the setup steps above.
2. Using the terminal, navigate to the frontend/src directory using `cd ./frontend/src`.
   Run `node server.js` to start the frontend development server.
3. Open a second terminal and run `python.exe ./backend/src/app.py` in the root
   directory to start the backend server.
4. Open your web browser and navigate to `http://localhost:4000` to access the
   application.

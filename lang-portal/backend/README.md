 # Language Learning Portal Backend

## Running the Application

To start the development server:
```bash
poetry run poe start
```

To run tests with coverage:
```bash
poetry run poe test
```

This will:
- Run all tests
- Show a coverage report in the terminal with missing lines highlighted
- Generate an HTML coverage report in the `htmlcov` directory

To view the HTML coverage report in your browser:
```bash
poetry run poe coverage-report
```

Then open http://localhost:8888 in your browser to view the interactive HTML coverage report.

Alternatively, you can run the app directly with:
```bash
poetry run python app/app.py
```
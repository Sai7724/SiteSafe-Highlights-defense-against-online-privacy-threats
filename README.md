# Site Safe: Web Privacy Advisor

Site Safe is a web-based tool that analyzes any given website for potential privacy risks. It provides a detailed report and a final privacy score to help users understand how a site handles their data.

## Features

- **HTTPS Security Check:** Verifies if the website uses a secure HTTPS connection.
- **Tracker Detection:** Scans the site for known third-party trackers that might be collecting user data.
- **Privacy Policy Analysis:**
    - Automatically finds and fetches the privacy policy.
    - Uses Natural Language Processing (NLP) to summarize the policy.
    - Employs an AI model to classify the privacy policy's risk level (Low, Moderate, or High).
- **Domain Information:** Retrieves the website's age and domain registrar to assess its legitimacy.
- **Privacy Score:** Calculates a final privacy score and assigns a grade (A, B, or C) based on the collected data.

## How to Run

### Prerequisites

- Python 3.7+

### Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd site_safe
    ```

2.  **Create and activate a virtual environment:**
    - On Windows:
      ```bash
      python -m venv venv
      .\venv\Scripts\activate
      ```
    - On macOS/Linux:
      ```bash
      python3 -m venv venv
      source venv/bin/activate
      ```

3.  **Install the required dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Download the NLP model:**
    The application uses the `en_core_web_sm` model from spaCy for text processing. Download it by running:
    ```bash
    python -m spacy download en_core_web_sm
    ```

### Running the Application

Once the installation is complete, you can start the Flask web server:

```bash
python app.py
```

The application will be accessible at `http://127.0.0.1:5000`.

## Usage

1.  Open your web browser and navigate to `http://127.0.0.1:5000`.
2.  Enter the full URL of the website you want to analyze (e.g., `https://example.com`).
3.  Click the "Analyze" button.
4.  The tool will process the URL and display a detailed privacy report.

## Project Structure

```
site_safe/
├── app.py                  # Main Flask application file
├── privacy_checker.py      # Core logic for URL analysis
├── nlp_analyzer.py         # NLP functions for privacy policy analysis
├── requirements.txt        # Project dependencies
├── static/
│   └── style.css           # CSS for styling the report page
└── templates/
    ├── index.html          # Main page with the URL input form
    └── result.html         # Page to display the analysis report
```

## Dependencies

The project relies on the following major libraries:

- **Flask:** For the web framework.
- **Requests:** For making HTTP requests.
- **BeautifulSoup4:** For parsing HTML.
- **tldextract & whois:** For domain information.
- **spaCy & Transformers:** For NLP tasks (summarization and classification).
- **torch:** As a dependency for the Transformers library.

For a full list of dependencies, see the `requirements.txt` file.

## License

This project is licensed under the terms of the LICENSE file.

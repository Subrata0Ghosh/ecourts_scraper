# 🏛️ eCourts Daily Cause List Scraper and PDF Generator

This Streamlit application uses **Selenium** to interact with the eCourts website for a specific District Court, scrape the daily cause lists for a selected date and court, and generate structured **PDF reports** using **ReportLab**.

⚠️ **DISCLAIMER:** This tool is intended for personal, educational, or legal transparency purposes only. Users are solely responsible for ensuring their usage complies with the specific **Terms of Service** and **Acceptable Use Policy** of the target website (`newdelhi.dcourts.gov.in`). Excessive, automated scraping or activities that may disrupt the website's service are strictly prohibited. **Always check the site's `robots.txt` and legal guidelines.**

---

## 🚀 Features

* **Date Selection:** Easily select the desired cause list date.
* **Court Selection:** Select the Court Complex and specific Court Number.
* **CAPTCHA Handling:** Captures the on-screen CAPTCHA for manual user entry within the Streamlit interface.
* **Data Scraper:** Uses Selenium to navigate, input details, submit the form, and extract tabular data.
* **PDF Generation:** Generates print-ready, landscape A4 PDF reports for each scraped court list using ReportLab, ensuring text wrapping and proper column sizing.

---

## 🛠️ Installation and Setup

### 1. Prerequisites

You need **Python 3.x** installed.

### 2. Project Setup

```bash
# Clone the repository (if applicable)
# git clone <your-repo-link>
# cd <your-project-folder>

# Create and activate a virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
````

### 3\. Dependencies

Install the required Python packages:

```bash
pip install streamlit selenium pandas reportlab
```

### 4\. Browser Driver Setup

This application uses **Google Chrome** and **Chromedriver**.

1.  **Download Chromedriver:** Download the appropriate `chromedriver` binary for your version of Google Chrome from the [Chromedriver website](https://googlechromelabs.github.io/chrome-for-testing/).
2.  **Path Configuration:**
      * The provided code expects `chromedriver` to be located at `/usr/local/bin/chromedriver`.
      * **If you are on Windows or your driver is in a different location**, you must change the line:
        ```python
        driver_path = Service("/usr/local/bin/chromedriver")
        ```
        to the correct path for your system, e.g., `Service("C:/Users/User/Downloads/chromedriver.exe")`.

-----

## ⚙️ How to Run

1.  Save the provided Python code as a file (e.g., `main.py`).
2.  Run the application from your terminal:

<!-- end list -->

```bash
streamlit run main.py
```

The app will automatically open in your web browser.

-----

## 💻 Usage

1.  **Select Date:** Choose the desired date for the cause list using the date picker.
2.  **Fetch Cause List:** Click the **"Fetch Cause List"** button.
      * A Chrome browser instance will launch.
      * The script will navigate to the site, select the Court Complex and Court Number, and input the date.
      * It will then capture the security CAPTCHA image.
3.  **Enter CAPTCHA:** An image of the CAPTCHA will be displayed in the Streamlit app.
      * Enter the characters shown in the image into the input box.
4.  **Submit Captcha:** Click **"Submit Captcha"**.
      * The script submits the form on the website.
      * Upon successful verification, the results are scraped.
5.  **View and Save Results:**
      * The scraped data will be displayed in a table format within the Streamlit app.
      * A PDF report for each section is automatically generated and saved in a new folder structure: `CauseLists/DD-MM-YYYY/`.

-----

-----

## 📄 Output Structure

The generated files are saved into a dated directory structure:

```
ECORTS_SCRAPER/
├── main.py                          # The Streamlit application code
├── captcha/
│   └── ecourts_captcha.png          # Temporary file for the current CAPTCHA image
└── CauseLists/
    └── 18-10-2025/                  # Folder created dynamically based on the selected date (DD-MM-YYYY)
        ├── Arguments.pdf            # PDF report for 'Arguments' section
        ├── Misc.__Appearance.pdf    # PDF report for 'Misc. / Appearance' section
        └── Misc.__Arguments.pdf     # PDF report for 'Misc. / Arguments' section
```

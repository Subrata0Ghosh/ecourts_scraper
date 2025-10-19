import streamlit as st
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
import time
import os
import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import landscape
from reportlab.lib.styles import ParagraphStyle
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

def get_driver():
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=Options)

st.title("eCourts Cause List Scraper")

# --- Date picker ---
# Yesterday's date
yesterday = datetime.today() - timedelta(days=1)
selected_date = st.date_input("Select Cause List Date", yesterday)
date_str = selected_date.strftime("%m/%d/%Y")  # MM/DD/YYYY format
st.write("Selected date:", date_str)

# --- Fetch Cause List Button ---
if st.button("Fetch Cause List"):
    st.write("Launching browser...")

    # --- Selenium Setup ---
    # driver_path = Service("/usr/local/bin/chromedriver")
    # driver = webdriver.Chrome(service=driver_path)
    
    # Auto-install ChromeDriver
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    # chrome_options.add_argument("--headless")  # Optional: remove for visible browser

    # Path to chromium and chromedriver installed by packages.txt
    driver = get_driver()    
    
    driver.get("https://newdelhi.dcourts.gov.in/cause-list-%e2%81%84-daily-board/")
    time.sleep(3)  # wait for page to load

    # --- Select Court Complex ---
    court_complex_dropdown = Select(driver.find_element(By.ID, "est_code"))
    court_complex_dropdown.select_by_index(1)
    time.sleep(2)

    # --- Select Court Number ---
    court_number_dropdown = Select(driver.find_element(By.ID, "court"))
    court_number_dropdown.select_by_index(1)
    time.sleep(2)

    # --- Enter Cause List Date ---
    date_input = driver.find_element(By.ID, "date")
    driver.execute_script(
        "arguments[0].removeAttribute('readonly')", date_input)
    date_input.clear()
    date_input.send_keys(date_str)

    # --- Captcha Handling ---
    CAPTCHA_SAVE = "captcha/ecourts_captcha.png"
    os.makedirs(os.path.dirname(CAPTCHA_SAVE), exist_ok=True)

    captcha_el = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "siwp_captcha_image_0"))
    )
    captcha_el.screenshot(CAPTCHA_SAVE)

    st.image(CAPTCHA_SAVE, caption="CAPTCHA")
    st.session_state['captcha_driver'] = driver
    st.success("Captcha captured. Please enter it below.")

# --- Captcha Input ---
if 'captcha_driver' in st.session_state:
    driver = st.session_state['captcha_driver']
    captcha_input = st.text_input(
        "Enter CAPTCHA code shown above:", key="captcha_input")

    if st.button("Submit Captcha"):
        with st.spinner("Processing cause lists and generating PDFs. Please wait..."):
            try:
                # Wait for captcha input to appear
                captcha_field = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.ID, "siwp_captcha_value_0"))
                )
                captcha_field.clear()
                captcha_field.send_keys(captcha_input)
                st.success("CAPTCHA entered on website.")

                # Click submit button
                submit_button = driver.find_element(
                    By.CSS_SELECTOR, "input[type='submit']")
                submit_button.click()

                # --- WAIT FOR RESULTS TO LOAD ---
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located(
                        (By.CLASS_NAME, "distTableContent"))
                )

                # Grab all result sections
                sections = driver.find_elements(By.CLASS_NAME, "distTableContent")

                if not sections:
                    st.warning("No results found for this date/court.")
                else:
                    for sec in sections:
                        # Table caption
                        caption = sec.find_element(By.TAG_NAME, "caption").text

                        # All rows in tbody
                        rows = sec.find_elements(By.XPATH, ".//tbody/tr")
                        data = []

                        for row in rows:
                            cols = row.find_elements(By.TAG_NAME, "td")
                            row_data = [col.text for col in cols]
                            data.append(row_data)


                        # --- Folder to save PDFs ---
                        SAVE_DIR = f"CauseLists/{selected_date.strftime('%d-%m-%Y')}"
                        os.makedirs(SAVE_DIR, exist_ok=True)

                        if data:
                            st.write(f"### {caption}")
                            df = pd.DataFrame(
                                data,
                                columns=[
                                    "Serial Number", "Case Type/Case Number/Case Year", "Party Name", "Advocate"]
                            )
                            df.index = df.index + 1
                            df.index.name = "No."
                            st.dataframe(df)

                            # --- Save table as PDF ---
                            pdf_filename = os.path.join(SAVE_DIR, f"{caption.replace('/', '_').replace(' ', '_')}.pdf")
                            doc = SimpleDocTemplate(pdf_filename, pagesize=landscape(A4))
                            styles = getSampleStyleSheet()
                            elements = []

                            # Add title
                            elements.append(Paragraph(f"Cause List: {caption}", styles["Title"]))
                            elements.append(Spacer(1, 12))
                            
                            # --- Create paragraph style for wrapped text ---
                            wrap_style = ParagraphStyle(name="Wrap", fontSize=8, leading=10)

                            # Prepare table data (header + rows)
                            table_data = [df.columns.tolist()] 
                            for row in df.values.tolist():
                                wrapped_row = [Paragraph(str(cell), wrap_style) for cell in row]
                                table_data.append(wrapped_row)
                            table = Table(table_data, repeatRows=1)
                            
                            # --- ✅ Auto-fit columns to A4 width ---
                            page_width = landscape(A4)[0] - 40  # total width minus margins
                            num_cols = len(df.columns)
                            col_width = page_width / num_cols
                            table._argW = [col_width] * num_cols


                            table.setStyle(TableStyle([
                                ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
                                ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                                ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
                                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                                ('FONTSIZE', (0, 0), (-1, -1), 8),
                                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                            ]))

                            elements.append(table)
                            doc.build(elements)

                            st.success(f"Saved PDF: {pdf_filename}")
                            
            except Exception as e:
                st.error(f"Captcha input not found: {e}")
                
    driver.quit()

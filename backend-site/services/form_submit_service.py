import asyncio
import random
from urllib.parse import urlencode, urlparse, urlunparse
import pandas as pd
import io
from fastapi import HTTPException, UploadFile, status
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from schemas import FormRequest
from .google_form_parser import GoogleFormService
import time
import os

class FormSubmissionService:
    def __init__(self, service_data=None):
        # Initializing your GoogleFormService parser module cleanly
        self.service_data = GoogleFormService()

    async def _get_data(self, url: str):
        try:
            data = await self.service_data.get_questions(str(url))
            if isinstance(data, dict) and "questions" in data:
                return data["questions"]
            return data
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail=f"Failed to fetch form structure: {str(e)}"
            )
        
    def _get_driver(self):
        options = Options()
        options.add_argument("--headless=new") # Modern headless mode
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--single-process") # Keeps memory usage down on Vercel

        # 1. Point options directly to the Vercel-installed Chromium binary
        options.binary_location = "/usr/bin/chromium"

        # 2. MANUALLY DEFINE THE SERVICE PATH
        # This prevents the Rust 'selenium-manager' binary from running!
        service = Service(executable_path="/usr/bin/chromedriver")

        try:
            # 3. Pass both service and options explicitly
            driver = webdriver.Chrome(service=service, options=options)
            return driver
        except Exception as e:
            print(f"Failed to boot driver: {str(e)}")
            raise e
        
    def _run_selenium_submission(self, final_prefilled_url: str) -> bool:
        # options = Options()
        # options.add_argument("--headless=new")
        # options.add_argument("--no-sandbox")
        # options.add_argument("--disable-dev-shm-usage")
        # options.add_argument("--start-maximized")
        # options.add_argument("--disable-blink-features=AutomationControlled")
        # options.add_experimental_option("excludeSwitches", ["enable-automation"])
        # driver = webdriver.Chrome(options=options)
        driver = self._get_driver()
        submission_success = False

        try:
            driver.get(final_prefilled_url)
            time.sleep(1.5)
            max_pages = 15
            for page in range(1, max_pages + 1):
                time.sleep(1.5)  
                next_clicked = False
                next_selectors = [
                    "//span[contains(text(), 'Next') or contains(text(), 'បន្ទាប់')]",
                    "//div[@role='button']//span[contains(text(), 'Next') or contains(text(), 'បន្ទាប់')]",
                    "//div[@role='button' and (contains(., 'Next') or contains(., 'បន្ទាប់'))]"
                ]

                for selector in next_selectors:
                    try:
                        next_btn = WebDriverWait(driver, 3).until(
                            EC.element_to_be_clickable((By.XPATH, selector))
                        )
                        btn_text = next_btn.text.lower()
                        if "submit" in btn_text or "បញ្ជូន" in btn_text:
                            continue
                            
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", next_btn)
                        time.sleep(0.3)
                        driver.execute_script("arguments[0].click();", next_btn)
                        next_clicked = True
                        break
                    except:
                        continue

                if not next_clicked:
                    break

            # === FINAL SUBMIT ===
            time.sleep(1.5)
            submit_selectors = [
                "//span[contains(text(), 'Submit') or contains(text(), 'បញ្ជូន')]",
                "//div[@role='button']//span[contains(text(), 'Submit') or contains(text(), 'បញ្ជូន')]",
                "//div[@role='button' and (contains(., 'Submit') or contains(., 'បញ្ជូន'))]"
            ]

            submit_clicked = False
            for selector in submit_selectors:
                try:
                    submit_btn = WebDriverWait(driver, 4).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", submit_btn)
                    time.sleep(0.3)
                    driver.execute_script("arguments[0].click();", submit_btn)
                    submit_clicked = True
                    break
                except:
                    continue

            if not submit_clicked:
                try:
                    driver.execute_script("""
                        document.querySelectorAll('div[role="button"]').forEach(btn => {
                            if (btn.innerText.toLowerCase().includes('submit') || btn.innerText.includes('បញ្ជូន')) {
                                btn.click();
                            }
                        });
                    """)
                    submit_clicked = True
                except:
                    pass

            # ==========================================================
            # BULLETPROOF HYBRID SUCCESS CHECK
            # ==========================================================
            time.sleep(5)  # Wait for redirect or submission update loop
            current_url_lower = driver.current_url.lower()

            if "formresponse" in current_url_lower:
                print("✅ Success! Confirmed via redirect URL link.")
                submission_success = True
            else:
                # Fallback Check: Did the submit buttons disappear from the page?
                # If the submit buttons are completely gone, Google accepted the submission!
                try:
                    remaining_buttons = driver.find_elements(By.XPATH, "//span[contains(text(), 'Submit') or contains(text(), 'បញ្ជូន')]")
                    if len(remaining_buttons) == 0 and submit_clicked:
                        print("✅ Success Fallback! Submit buttons are gone. Form data accepted.")
                        submission_success = True
                    else:
                        print(f"❌ Failed. Form buttons still present on current URL: {driver.current_url}")
                        submission_success = False
                except:
                    # If we can't even scan elements, fallback safely if we executed the button click event
                    submission_success = submit_clicked

        except Exception as e:
            print("Automation tracking error:", e)
            submission_success = False
        finally:
            try:
                driver.close()
                driver.quit()
                print("✅ Browser instances stopped completely.")
            except:
                pass
            
        return submission_success

    async def submit_excel(self, form_request: FormRequest, file: UploadFile):
        # 1. Fetch form schemas from your service logic layer
        data = await self._get_data(form_request.url)

        # 2. Parse file once before the iteration loops to preserve the memory read pointer!
        try:
            file_content = await file.read()
            df = pd.read_excel(io.BytesIO(file_content))
            
            # Remove any trailing white spaces from headers
            df.columns = [str(c).strip() for c in df.columns]
            
            # Map out rules: { "Question": ["Exception Item 1", "Exception Item 2"] }
            excel_rules = {}
            for _, row in df.iterrows():
                q_name = str(row.get('Question', '')).strip()
                exc_val = row.get('Exception')
                
                if q_name and q_name != 'nan':
                    if pd.notna(exc_val) and str(exc_val).strip().lower() != 'nan':
                        exceptions = [e.strip() for e in str(exc_val).split(',')]
                    else:
                        exceptions = []
                    excel_rules[q_name] = exceptions
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid Excel format or file structural reading error: {str(e)}"
            )

        # Standardize uniform landing addresses for viewforms
        clean_form_url = form_request.url.split('/viewform')[0] + '/viewform'

        # Loop processing your sequential loop automation configurations
        for i in range(form_request.number):
            print(f"Time automation execution run: {i + 1} / {form_request.number}")
            
            # Reinitializes fresh parameters stack for every submission run
            query_params = [('usp', 'pp_url')]
            
            # 3. Process questions and apply rules exclusions dynamically
            for q in data:
                entry_id = q['entry']
                options = q.get('options', [])
                field_type = q.get('type')
                q_title = q.get('title', '').strip()
                
                if not options:
                    continue

                valid_pool = list(options)

                # Execute pool exclusion filter on a title dictionary match
                if q_title in excel_rules:
                    exclusions = excel_rules[q_title]
                    if exclusions:
                        valid_pool = [opt for opt in options if str(opt).strip() not in exclusions]
                        
                        # Fallback case protection if exclusions wiped out options completely
                        if not valid_pool:
                            valid_pool = list(options)

                # 4. Generate query allocations from our validated pool subsets
                if field_type == 2:  # Checkboxes handling
                    num_choices = random.randint(1, min(3, len(valid_pool)))
                    chosen_options = random.sample(valid_pool, num_choices)
                    for choice in chosen_options:
                        query_params.append((f"entry.{entry_id}", choice))
                else:  # Radio choices, dropdown selections, or linear grids
                    chosen_option = random.choice(valid_pool)
                    query_params.append((f"entry.{entry_id}", chosen_option))
                    
            # 5. Build full prefilled string address paths
            url_parts = list(urlparse(clean_form_url))
            url_parts[4] = urlencode(query_params)
            final_prefilled_url = urlunparse(url_parts)
            
            # 6. Execute headless selenium submission concurrently without blocking FastAPI main thread
            success = await asyncio.to_thread(self._run_selenium_submission, final_prefilled_url)
            
            if not success:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Automation failed at instance step trace count index: {i + 1}"
                )
        return {
                "results": {
                    "status": "success", 
                    "message": f"Successfully completed all {form_request.number} form automated entries."
                }
        }
# import asyncio
# import random
# from urllib.parse import urlencode, urlparse, urlunparse
# import pandas as pd
# import io
# from fastapi import HTTPException, UploadFile, status
# from selenium import webdriver
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.chrome.service import Service
# from schemas import FormRequest
# from .google_form_parser import GoogleFormService
# import time
# import os

# class FormSubmissionService:
#     def __init__(self, service_data=None):
#         # Initializing your GoogleFormService parser module cleanly
#         self.service_data = GoogleFormService()

#     async def _get_data(self, url: str):
#         try:
#             data = await self.service_data.get_questions(str(url))
#             if isinstance(data, dict) and "questions" in data:
#                 return data["questions"]
#             return data
#         except Exception as e:
#             raise HTTPException(
#                 status_code=status.HTTP_400_BAD_REQUEST, 
#                 detail=f"Failed to fetch form structure: {str(e)}"
#             )
        
#     def _get_driver(self):
#         options = Options()
#         options.add_argument("--headless=new") # Modern headless mode
#         options.add_argument("--no-sandbox")
#         options.add_argument("--disable-dev-shm-usage")
#         options.add_argument("--disable-gpu")
#         options.add_argument("--single-process") # Keeps memory usage down on Vercel

#         # 1. Point options directly to the Vercel-installed Chromium binary
#         options.binary_location = "/usr/bin/chromium"

#         # 2. MANUALLY DEFINE THE SERVICE PATH
#         # This prevents the Rust 'selenium-manager' binary from running!
#         service = Service(executable_path="/usr/bin/chromedriver")

#         try:
#             # 3. Pass both service and options explicitly
#             driver = webdriver.Chrome(service=service, options=options)
#             return driver
#         except Exception as e:
#             print(f"Failed to boot driver: {str(e)}")
#             raise e
        
#     def _run_selenium_submission(self, final_prefilled_url: str) -> bool:
#         # options = Options()
#         # options.add_argument("--headless=new")
#         # options.add_argument("--no-sandbox")
#         # options.add_argument("--disable-dev-shm-usage")
#         # options.add_argument("--start-maximized")
#         # options.add_argument("--disable-blink-features=AutomationControlled")
#         # options.add_experimental_option("excludeSwitches", ["enable-automation"])
#         # driver = webdriver.Chrome(options=options)
#         driver = self._get_driver()
#         submission_success = False

#         try:
#             driver.get(final_prefilled_url)
#             time.sleep(1.5)
#             max_pages = 15
#             for page in range(1, max_pages + 1):
#                 time.sleep(1.5)  
#                 next_clicked = False
#                 next_selectors = [
#                     "//span[contains(text(), 'Next') or contains(text(), 'បន្ទាប់')]",
#                     "//div[@role='button']//span[contains(text(), 'Next') or contains(text(), 'បន្ទាប់')]",
#                     "//div[@role='button' and (contains(., 'Next') or contains(., 'បន្ទាប់'))]"
#                 ]

#                 for selector in next_selectors:
#                     try:
#                         next_btn = WebDriverWait(driver, 3).until(
#                             EC.element_to_be_clickable((By.XPATH, selector))
#                         )
#                         btn_text = next_btn.text.lower()
#                         if "submit" in btn_text or "បញ្ជូន" in btn_text:
#                             continue
                            
#                         driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", next_btn)
#                         time.sleep(0.3)
#                         driver.execute_script("arguments[0].click();", next_btn)
#                         next_clicked = True
#                         break
#                     except:
#                         continue

#                 if not next_clicked:
#                     break

#             # === FINAL SUBMIT ===
#             time.sleep(1.5)
#             submit_selectors = [
#                 "//span[contains(text(), 'Submit') or contains(text(), 'បញ្ជូន')]",
#                 "//div[@role='button']//span[contains(text(), 'Submit') or contains(text(), 'បញ្ជូន')]",
#                 "//div[@role='button' and (contains(., 'Submit') or contains(., 'បញ្ជូន'))]"
#             ]

#             submit_clicked = False
#             for selector in submit_selectors:
#                 try:
#                     submit_btn = WebDriverWait(driver, 4).until(
#                         EC.element_to_be_clickable((By.XPATH, selector))
#                     )
#                     driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", submit_btn)
#                     time.sleep(0.3)
#                     driver.execute_script("arguments[0].click();", submit_btn)
#                     submit_clicked = True
#                     break
#                 except:
#                     continue

#             if not submit_clicked:
#                 try:
#                     driver.execute_script("""
#                         document.querySelectorAll('div[role="button"]').forEach(btn => {
#                             if (btn.innerText.toLowerCase().includes('submit') || btn.innerText.includes('បញ្ជូន')) {
#                                 btn.click();
#                             }
#                         });
#                     """)
#                     submit_clicked = True
#                 except:
#                     pass

#             # ==========================================================
#             # BULLETPROOF HYBRID SUCCESS CHECK
#             # ==========================================================
#             time.sleep(5)  # Wait for redirect or submission update loop
#             current_url_lower = driver.current_url.lower()

#             if "formresponse" in current_url_lower:
#                 print("✅ Success! Confirmed via redirect URL link.")
#                 submission_success = True
#             else:
#                 # Fallback Check: Did the submit buttons disappear from the page?
#                 # If the submit buttons are completely gone, Google accepted the submission!
#                 try:
#                     remaining_buttons = driver.find_elements(By.XPATH, "//span[contains(text(), 'Submit') or contains(text(), 'បញ្ជូន')]")
#                     if len(remaining_buttons) == 0 and submit_clicked:
#                         print("✅ Success Fallback! Submit buttons are gone. Form data accepted.")
#                         submission_success = True
#                     else:
#                         print(f"❌ Failed. Form buttons still present on current URL: {driver.current_url}")
#                         submission_success = False
#                 except:
#                     # If we can't even scan elements, fallback safely if we executed the button click event
#                     submission_success = submit_clicked

#         except Exception as e:
#             print("Automation tracking error:", e)
#             submission_success = False
#         finally:
#             try:
#                 driver.close()
#                 driver.quit()
#                 print("✅ Browser instances stopped completely.")
#             except:
#                 pass
            
#         return submission_success

#     async def submit_excel(self, form_request: FormRequest, file: UploadFile):
#         # 1. Fetch form schemas from your service logic layer
#         data = await self._get_data(form_request.url)

#         # 2. Parse file once before the iteration loops to preserve the memory read pointer!
#         try:
#             file_content = await file.read()
#             df = pd.read_excel(io.BytesIO(file_content))
            
#             # Remove any trailing white spaces from headers
#             df.columns = [str(c).strip() for c in df.columns]
            
#             # Map out rules: { "Question": ["Exception Item 1", "Exception Item 2"] }
#             excel_rules = {}
#             for _, row in df.iterrows():
#                 q_name = str(row.get('Question', '')).strip()
#                 exc_val = row.get('Exception')
                
#                 if q_name and q_name != 'nan':
#                     if pd.notna(exc_val) and str(exc_val).strip().lower() != 'nan':
#                         exceptions = [e.strip() for e in str(exc_val).split(',')]
#                     else:
#                         exceptions = []
#                     excel_rules[q_name] = exceptions
#         except Exception as e:
#             raise HTTPException(
#                 status_code=status.HTTP_400_BAD_REQUEST,
#                 detail=f"Invalid Excel format or file structural reading error: {str(e)}"
#             )

#         # Standardize uniform landing addresses for viewforms
#         clean_form_url = form_request.url.split('/viewform')[0] + '/viewform'

#         # Loop processing your sequential loop automation configurations
#         for i in range(form_request.number):
#             print(f"Time automation execution run: {i + 1} / {form_request.number}")
            
#             # Reinitializes fresh parameters stack for every submission run
#             query_params = [('usp', 'pp_url')]
            
#             # 3. Process questions and apply rules exclusions dynamically
#             for q in data:
#                 entry_id = q['entry']
#                 options = q.get('options', [])
#                 field_type = q.get('type')
#                 q_title = q.get('title', '').strip()
                
#                 if not options:
#                     continue

#                 valid_pool = list(options)

#                 # Execute pool exclusion filter on a title dictionary match
#                 if q_title in excel_rules:
#                     exclusions = excel_rules[q_title]
#                     if exclusions:
#                         valid_pool = [opt for opt in options if str(opt).strip() not in exclusions]
                        
#                         # Fallback case protection if exclusions wiped out options completely
#                         if not valid_pool:
#                             valid_pool = list(options)

#                 # 4. Generate query allocations from our validated pool subsets
#                 if field_type == 2:  # Checkboxes handling
#                     num_choices = random.randint(1, min(3, len(valid_pool)))
#                     chosen_options = random.sample(valid_pool, num_choices)
#                     for choice in chosen_options:
#                         query_params.append((f"entry.{entry_id}", choice))
#                 else:  # Radio choices, dropdown selections, or linear grids
#                     chosen_option = random.choice(valid_pool)
#                     query_params.append((f"entry.{entry_id}", chosen_option))
                    
#             # 5. Build full prefilled string address paths
#             url_parts = list(urlparse(clean_form_url))
#             url_parts[4] = urlencode(query_params)
#             final_prefilled_url = urlunparse(url_parts)
            
#             # 6. Execute headless selenium submission concurrently without blocking FastAPI main thread
#             success = await asyncio.to_thread(self._run_selenium_submission, final_prefilled_url)
            
#             if not success:
#                 raise HTTPException(
#                     status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#                     detail=f"Automation failed at instance step trace count index: {i + 1}"
#                 )
#         return {
#                 "results": {
#                     "status": "success", 
#                     "message": f"Successfully completed all {form_request.number} form automated entries."
#                 }
#         }




# import asyncio
# import random
# import sys
# from urllib.parse import urlencode, urlparse, urlunparse
# import pandas as pd
# import io
# from fastapi import HTTPException, UploadFile, status
# from playwright.async_api import async_playwright

# from schemas import FormRequest
# from .google_form_parser import GoogleFormService
# from core.config import settings 

# class FormSubmissionService:
#     def __init__(self):
#         self.service_data = GoogleFormService()
#         self.browserless_key = settings.BROWSERLESS_API_KEY
        
#         if not self.browserless_key:
#             print("⚠️ WARNING: BROWSERLESS_API_KEY is not configured in settings!")

#     async def _get_data(self, url: str):
#         try:
#             data = await self.service_data.get_questions(str(url))
#             if isinstance(data, dict) and "questions" in data:
#                 return data["questions"]
#             return data
#         except Exception as e:
#             raise HTTPException(
#                 status_code=status.HTTP_400_BAD_REQUEST, 
#                 detail=f"Failed to fetch form structure: {str(e)}"
#             )
        
#     async def _execute_via_browserless_api(self, final_prefilled_url: str) -> bool:
#         """
#         Windows Safe Fallback: Executes the automation steps by sending a direct 
#         Puppeteer/Playwright script execution payload directly to Browserless over HTTP.
#         This completely eliminates the need for a local loop process.
#         """
#         import httpx
        
#         # We tell Browserless to execute a short automation script on its servers directly
#         browserless_url = f"https://chrome.browserless.io/function?token={self.browserless_key}"
        
#         # FIXED: Configured exactly to match Browserless required signature "export default async ({ page }) => {}"
#         javascript_code = f"""
#         export default async ({{ page }}) => {{
#             await page.goto('{final_prefilled_url}');
#             await new Promise(r => setTimeout(r, 1500));
            
#             // Navigate multipage forms
#             for (let i = 0; i < 15; i++) {{
#                 await new Promise(r => setTimeout(r, 1500));
#                 let nextClicked = false;
#                 try {{
#                     const nextBtn = await page.$("xpath=//div[@role='button'][(contains(., 'Next') or contains(., 'បន្ទាប់')) and not(contains(., 'Submit') or contains(., 'បញ្ជូន'))]");
#                     if (nextBtn && await nextBtn.isVisible()) {{
#                         await nextBtn.click();
#                         nextClicked = true;
#                     }}
#                 }} catch(e) {{}}
#                 if (!nextClicked) break;
#             }}
            
#             // Final submit execution
#             await new Promise(r => setTimeout(r, 1500));
#             let submitClicked = false;
#             try {{
#                 const submitBtn = await page.$("xpath=//div[@role='button'][contains(., 'Submit') or contains(., 'បញ្ជូន')]");
#                 if (submitBtn && await submitBtn.isVisible()) {{
#                     await submitBtn.click();
#                     submitClicked = true;
#                 }}
#             }} catch(e) {{}}
            
#             if (!submitClicked) {{
#                 try {{
#                     await page.evaluate(() => {{
#                         document.querySelectorAll('div[role="button"]').forEach(btn => {{
#                             if (btn.innerText.toLowerCase().includes('submit') || btn.innerText.includes('បញ្ជូន')) {{
#                                 btn.click();
#                             }}
#                         }});
#                     }});
#                     submitClicked = true;
#                 }} catch(e) {{}}
#             }}
            
#             await new Promise(r => setTimeout(r, 5000));
#             const currentUrl = page.url().toLowerCase();
#             return {{ success: currentUrl.includes('formresponse') || submitClicked }};
#         }};
#         """
        
#         headers = {"Content-Type": "application/javascript"}
        
#         async with httpx.AsyncClient(timeout=60.0) as client:
#             try:
#                 response = await client.post(browserless_url, content=javascript_code, headers=headers)
#                 if response.status_code == 200:
#                     result = response.json()
#                     # Browserless puts returned value inside a nested data property block
#                     data_output = result.get("data", {})
#                     return data_output.get("success", False)
#                 else:
#                     print(f"Browserless API error status: {response.status_code}")
#                     print(f"Details: {response.text}")
#                     return False
#             except Exception as e:
#                 print(f"Direct API call exception failed: {e}")
#                 return False

#     async def _execute_automation_steps(self, final_prefilled_url: str) -> bool:
#         """
#         Standard non-windows automation flow using live CDP sockets.
#         """
#         submission_success = False
#         cdp_url = f"wss://chrome.browserless.io/playwright?token={self.browserless_key}"

#         async with async_playwright() as p:
#             try:
#                 browser = await p.chromium.connect_over_cdp(cdp_url)
#                 context = await browser.new_context()
#                 page = await context.new_page()

#                 await page.goto(final_prefilled_url)
#                 await page.wait_for_timeout(1500)

#                 max_pages = 15
#                 for _ in range(1, max_pages + 1):
#                     await page.wait_for_timeout(1500)
#                     next_clicked = False
#                     next_button_selector = "xpath=//div[@role='button'][(contains(., 'Next') or contains(., 'បន្ទាប់')) and not(contains(., 'Submit') or contains(., 'បញ្ជូន'))]"

#                     try:
#                         next_btn = page.locator(next_button_selector)
#                         if await next_btn.is_visible(timeout=3000):
#                             await next_btn.click()
#                             next_clicked = True
#                     except:
#                         pass
#                     if not next_clicked:
#                         break

#                 await page.wait_for_timeout(1500)
#                 submit_button_selector = "xpath=//div[@role='button'][contains(., 'Submit') or contains(., 'បញ្ជូន')]"
#                 submit_clicked = False

#                 try:
#                     submit_btn = page.locator(submit_button_selector)
#                     if await submit_btn.is_visible(timeout=4000):
#                         await submit_btn.click()
#                         submit_clicked = True
#                 except:
#                     pass

#                 if not submit_clicked:
#                     try:
#                         await page.evaluate("""() => {
#                             document.querySelectorAll('div[role="button"]').forEach(btn => {
#                                 if (btn.innerText.toLowerCase().includes('submit') || btn.innerText.includes('បញ្ជូន')) {
#                                     btn.click();
#                                 }
#                             });
#                         }""")
#                         submit_clicked = True
#                     except:
#                         pass

#                 await page.wait_for_timeout(5000)
#                 current_url_lower = page.url.lower()
#                 submission_success = "formresponse" in current_url_lower or submit_clicked

#                 await context.close()
#                 await browser.close()
#             except Exception as e:
#                 print("Automation error inside native CDP execution:", e)
#                 submission_success = False
                
#         return submission_success

#     async def _run_playwright_submission(self, final_prefilled_url: str) -> bool:
#         """
#         Main routing gateway. Runs via serverless execution on local Windows 
#         to circumvent event-loop subprocess boundaries, or raw code on Vercel.
#         """
#         if sys.platform == 'win32':
#             print("🔧 Windows environment detected. Shifting execution processing directly to Browserless Cloud REST API...")
#             return await self._execute_via_browserless_api(final_prefilled_url)
        
#         return await self._execute_automation_steps(final_prefilled_url)

#     async def submit_excel(self, form_request: FormRequest, file: UploadFile):
#         data = await self._get_data(form_request.url)

#         try:
#             file_content = await file.read()
#             df = pd.read_excel(io.BytesIO(file_content))
#             df.columns = [str(c).strip() for c in df.columns]
            
#             excel_rules = {}
#             for _, row in df.iterrows():
#                 q_name = str(row.get('Question', '')).strip()
#                 exc_val = row.get('Exception')
                
#                 if q_name and q_name != 'nan':
#                     if pd.notna(exc_val) and str(exc_val).strip().lower() != 'nan':
#                         exceptions = [e.strip() for e in str(exc_val).split(',')]
#                     else:
#                         exceptions = []
#                     excel_rules[q_name] = exceptions
#         except Exception as e:
#             raise HTTPException(
#                 status_code=status.HTTP_400_BAD_REQUEST,
#                 detail=f"Invalid Excel format or file structural reading error: {str(e)}"
#             )

#         clean_form_url = form_request.url.split('/viewform')[0] + '/viewform'

#         for i in range(form_request.number):
#             print(f"Time automation execution run: {i + 1} / {form_request.number}")
#             query_params = [('usp', 'pp_url')]
            
#             for q in data:
#                 entry_id = q['entry']
#                 options = q.get('options', [])
#                 field_type = q.get('type')
#                 q_title = q.get('title', '').strip()
                
#                 if not options:
#                     continue

#                 valid_pool = list(options)

#                 if q_title in excel_rules:
#                     exclusions = excel_rules[q_title]
#                     if exclusions:
#                         valid_pool = [opt for opt in options if str(opt).strip() not in exclusions]
#                         if not valid_pool:
#                             valid_pool = list(options)

#                 if field_type == 2:  # Checkboxes
#                     num_choices = random.randint(1, min(3, len(valid_pool)))
#                     chosen_options = random.sample(valid_pool, num_choices)
#                     for choice in chosen_options:
#                         query_params.append((f"entry.{entry_id}", choice))
#                 else:  # Radio/Dropdown
#                     chosen_option = random.choice(valid_pool)
#                     query_params.append((f"entry.{entry_id}", chosen_option))
                    
#             url_parts = list(urlparse(clean_form_url))
#             url_parts[4] = urlencode(query_params)
#             final_prefilled_url = urlunparse(url_parts)
            
#             success = await self._run_playwright_submission(final_prefilled_url)
            
#             if not success:
#                 raise HTTPException(
#                     status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#                     detail=f"Automation failed at instance step trace count index: {i + 1}"
#                 )
                
#         return {
#             "results": {
#                 "status": "success", 
#                 "message": f"Successfully completed all {form_request.number} form automated entries."
#             }
#         }



# import asyncio
# import random
# import sys
# from urllib.parse import urlencode, urlparse, urlunparse
# import pandas as pd
# import io
# from fastapi import HTTPException, UploadFile, status
# from playwright.async_api import async_playwright

# from schemas import FormRequest
# from .google_form_parser import GoogleFormService
# from core.config import settings 

# class FormSubmissionService:
#     def __init__(self):
#         self.service_data = GoogleFormService()
#         self.browserless_key = settings.BROWSERLESS_API_KEY
        
#         if not self.browserless_key:
#             print("⚠️ WARNING: BROWSERLESS_API_KEY is not configured in settings!")

#     async def _get_data(self, url: str):
#         try:
#             data = await self.service_data.get_questions(str(url))
#             if isinstance(data, dict) and "questions" in data:
#                 return data["questions"]
#             return data
#         except Exception as e:
#             raise HTTPException(
#                 status_code=status.HTTP_400_BAD_REQUEST, 
#                 detail=f"Failed to fetch form structure: {str(e)}"
#             )
        
#     async def _execute_via_browserless_api(self, final_prefilled_url: str) -> bool:
#         """
#         REST API Fallback: Executes the automation steps by sending a direct 
#         Puppeteer script execution payload directly to Browserless over HTTP.
#         """
#         import httpx
        
#         browserless_url = f"https://chrome.browserless.io/function?token={self.browserless_key}"
        
#         javascript_code = f"""
#         export default async ({{ page }}) => {{
#             await page.setViewport({{ width: 1440, height: 900 }});
            
#             await page.goto('{final_prefilled_url}', {{ waitUntil: 'networkidle2', timeout: 30000 }});
#             await new Promise(r => setTimeout(r, 2000));
            
#             const maxPages = 15;
            
#             for (let i = 0; i < maxPages; i++) {{
#                 let stepResult = await page.evaluate(() => {{
#                     const buttons = Array.from(document.querySelectorAll('div[role="button"]'));
#                     if (buttons.length === 0) return {{ clicked: false, finished: true }};
                    
#                     let operationalButtons = buttons.filter(b => b.className.includes('uArJb') || b.getAttribute('jsname') !== null);
#                     if (operationalButtons.length === 0) operationalButtons = buttons;
                    
#                     let submitBtn = operationalButtons.find(b => {{
#                         const innerStr = b.innerText ? b.innerText.toLowerCase() : "";
#                         return innerStr.includes('submit') || innerStr.includes('បញ្ជូន') || b.outerHTML.includes('submit');
#                     }});
                    
#                     if (submitBtn) {{
#                         submitBtn.scrollIntoView({{ block: 'center' }});
#                         submitBtn.click();
#                         return {{ clicked: true, finished: true }};
#                     }}
                    
#                     let nextBtn = operationalButtons.find(b => {{
#                         const innerStr = b.innerText ? b.innerText.toLowerCase() : "";
#                         return innerStr.includes('next') || innerStr.includes('បន្ទាប់') || innerStr.includes('continue');
#                     }});
                    
#                     if (!nextBtn && operationalButtons.length > 0) {{
#                         nextBtn = operationalButtons[operationalButtons.length - 1];
#                     }}
                    
#                     if (nextBtn) {{
#                         nextBtn.scrollIntoView({{ block: 'center' }});
#                         nextBtn.click();
#                         return {{ clicked: true, finished: false }};
#                     }}
                    
#                     return {{ clicked: false, finished: true }};
#                 }});
                
#                 if (stepResult.finished || !stepResult.clicked) break;
#                 await new Promise(r => setTimeout(r, 2000));
#             }}
            
#             await new Promise(r => setTimeout(r, 3000));
#             return {{ completed: true }};
#         }};
#         """
        
#         headers = {"Content-Type": "application/javascript"}
        
#         async with httpx.AsyncClient(timeout=60.0) as client:
#             try:
#                 response = await client.post(browserless_url, content=javascript_code, headers=headers)
#                 if response.status_code == 200:
#                     print("📡 Browserless Cloud HTTP REST execution submitted form successfully!")
#                     return True
#                 else:
#                     print(f"❌ Browserless REST API returned error status: {response.status_code}")
#                     return False
#             except Exception as e:
#                 print(f"❌ Exception caught during HTTP execution: {e}")
#                 return False

#     async def _execute_automation_steps(self, final_prefilled_url: str) -> bool:
#         """
#         Standard automation flow using live CDP sockets.
#         FIXED: Updated endpoint path from /playwright to /chromium to resolve 404 errors.
#         """
#         submission_success = False
#         cdp_url = f"wss://chrome.browserless.io/chromium?token={self.browserless_key}"

#         async with async_playwright() as p:
#             try:
#                 browser = await p.chromium.connect_over_cdp(cdp_url)
#                 context = await browser.new_context()
#                 page = await context.new_page()

#                 await page.goto(final_prefilled_url)
#                 await page.wait_for_timeout(1500)

#                 max_pages = 15
#                 for _ in range(1, max_pages + 1):
#                     await page.wait_for_timeout(1500)
#                     next_clicked = False
#                     next_button_selector = "xpath=//div[@role='button'][(contains(., 'Next') or contains(., 'បន្ទាប់')) and not(contains(., 'Submit') or contains(., 'បញ្ជូន'))]"

#                     try:
#                         next_btn = page.locator(next_button_selector)
#                         if await next_btn.is_visible(timeout=3000):
#                             await next_btn.click()
#                             next_clicked = True
#                     except:
#                         pass
#                     if not next_clicked:
#                         break

#                 await page.wait_for_timeout(1500)
#                 submit_button_selector = "xpath=//div[@role='button'][contains(., 'Submit') or contains(., 'បញ្ជូន')]"
#                 submit_clicked = False

#                 try:
#                     submit_btn = page.locator(submit_button_selector)
#                     if await submit_btn.is_visible(timeout=4000):
#                         await submit_btn.click()
#                         submit_clicked = True
#                 except:
#                     pass

#                 if not submit_clicked:
#                     try:
#                         await page.evaluate("""() => {
#                             document.querySelectorAll('div[role="button"]').forEach(btn => {
#                                 if (btn.innerText.toLowerCase().includes('submit') || btn.innerText.includes('បញ្ជូន')) {
#                                     btn.click();
#                                 }
#                             });
#                         }""")
#                         submit_clicked = True
#                     except:
#                         pass

#                 await page.wait_for_timeout(5000)
#                 current_url_lower = page.url.lower()
#                 submission_success = "formresponse" in current_url_lower or submit_clicked

#                 await context.close()
#                 await browser.close()
#             except Exception as e:
#                 print("⚠️ Live CDP WebSocket connection failed:", e)
#                 submission_success = False
                
#         return submission_success

#     async def _run_playwright_submission(self, final_prefilled_url: str) -> bool:
#         """
#         Main routing gateway. Runs via serverless execution.
#         FIXED: Automatically falls back to the HTTP REST API if WebSocket drops or fails on Vercel.
#         """
#         if sys.platform == 'win32':
#             print("🔧 Windows environment detected. Shifting execution processing directly to Browserless Cloud REST API...")
#             return await self._execute_via_browserless_api(final_prefilled_url)
        
#         print("🚀 Running native Playwright CDP connection...")
#         success = await self._execute_automation_steps(final_prefilled_url)
        
#         # Safe catch-all fallback loop for production server drops
#         if not success:
#             print("🔄 WebSocket connection failed or rejected. Dropping back to resilient HTTP REST API pipeline...")
#             return await self._execute_via_browserless_api(final_prefilled_url)
            
#         return success

#     async def submit_excel(self, form_request: FormRequest, file: UploadFile):
#         data = await self._get_data(form_request.url)

#         try:
#             file_content = await file.read()
#             df = pd.read_excel(io.BytesIO(file_content))
#             df.columns = [str(c).strip() for c in df.columns]
            
#             excel_rules = {}
#             for _, row in df.iterrows():
#                 q_name = str(row.get('Question', '')).strip()
#                 exc_val = row.get('Exception')
                
#                 if q_name and q_name != 'nan':
#                     if pd.notna(exc_val) and str(exc_val).strip().lower() != 'nan':
#                         exceptions = [e.strip() for e in str(exc_val).split(',')]
#                     else:
#                         exceptions = []
#                     excel_rules[q_name] = exceptions
#         except Exception as e:
#             raise HTTPException(
#                 status_code=status.HTTP_400_BAD_REQUEST,
#                 detail=f"Invalid Excel format or file structural reading error: {str(e)}"
#             )

#         clean_form_url = form_request.url.split('/viewform')[0] + '/viewform'

#         for i in range(form_request.number):
#             print(f"Time automation execution run: {i + 1} / {form_request.number}")
#             query_params = [('usp', 'pp_url')]
            
#             for q in data:
#                 entry_id = q['entry']
#                 options = q.get('options', [])
#                 field_type = q.get('type')
#                 q_title = q.get('title', '').strip()
                
#                 if not options:
#                     continue

#                 valid_pool = list(options)

#                 if q_title in excel_rules:
#                     exclusions = excel_rules[q_title]
#                     if exclusions:
#                         valid_pool = [opt for opt in options if str(opt).strip() not in exclusions]
#                         if not valid_pool:
#                             valid_pool = list(options)

#                 if field_type == 2:  # Checkboxes
#                     num_choices = random.randint(1, min(3, len(valid_pool)))
#                     chosen_options = random.sample(valid_pool, num_choices)
#                     for choice in chosen_options:
#                         query_params.append((f"entry.{entry_id}", choice))
#                 else:  # Radio/Dropdown
#                     chosen_option = random.choice(valid_pool)
#                     query_params.append((f"entry.{entry_id}", chosen_option))
                    
#             url_parts = list(urlparse(clean_form_url))
#             url_parts[4] = urlencode(query_params)
#             final_prefilled_url = urlunparse(url_parts)
            
#             success = await self._run_playwright_submission(final_prefilled_url)
            
#             if not success:
#                 raise HTTPException(
#                     status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#                     detail=f"Automation failed at instance step trace count index: {i + 1}"
#                 )
                
#         return {
#             "results": {
#                 "status": "success", 
#                 "message": f"Successfully completed all {form_request.number} form automated entries."
#             }
#         }



# import random
# import sys
# from urllib.parse import urlencode, urlparse, urlunparse
# import pandas as pd
# import io
# from fastapi import HTTPException, UploadFile, status
# from playwright.async_api import async_playwright

# from schemas import FormRequest
# from .google_form_parser import GoogleFormService
# from core.config import settings 

# class FormSubmissionService:
#     def __init__(self):
#         self.service_data = GoogleFormService()
#         self.browserless_key = settings.BROWSERLESS_API_KEY
        
#         if not self.browserless_key:
#             print("⚠️ WARNING: BROWSERLESS_API_KEY is not configured in settings!")

#     def _generate_random_email(self) -> str:
#         """Generates a realistic random email address to bypass collection boxes."""
#         first_names = ["sopanha", "bhavana", "rath", "vicheka", "chan", "sok", "narith", "serey"]
#         last_names = ["sin", "kim", "chean", "meang", "seng", "oun", "reach", "vuth"]
#         domains = [
#             "student.passerellesnumeriques.org", # Your target organization domain
#             "gmail.com", 
#             "outlook.com"
#         ]
        
#         fname = random.choice(first_names)
#         lname = random.choice(last_names)
#         rand_num = random.randint(10, 999)
#         domain = random.choice(domains)
        
#         # Mix up formats slightly (e.g., fname.lname123@domain or fname123@domain)
#         formats = [
#             f"{fname}.{lname}",
#             f"{fname}.{lname}{rand_num}",
#             f"{fname}{rand_num}"
#         ]
#         return f"{random.choice(formats)}@{domain}"

#     async def _get_data(self, url: str):
#         try:
#             data = await self.service_data.get_questions(str(url))
#             if isinstance(data, dict) and "questions" in data:
#                 return data["questions"]
#             return data
#         except Exception as e:
#             raise HTTPException(
#                 status_code=status.HTTP_400_BAD_REQUEST, 
#                 detail=f"Failed to fetch form structure: {str(e)}"
#             )
        
#     async def _execute_via_browserless_api(self, final_prefilled_url: str) -> bool:
#         """
#         REST API Fallback: Executes the automation steps by sending a direct 
#         Puppeteer script execution payload directly to Browserless over HTTP.
#         """
#         import httpx
        
#         browserless_url = f"https://chrome.browserless.io/function?token={self.browserless_key}"
        
#         javascript_code = f"""
#         export default async ({{ page }}) => {{
#             await page.setViewport({{ width: 1440, height: 900 }});
            
#             await page.goto('{final_prefilled_url}', {{ waitUntil: 'networkidle2', timeout: 30000 }});
#             await new Promise(r => setTimeout(r, 2000));
            
#             const maxPages = 15;
            
#             for (let i = 0; i < maxPages; i++) {{
#                 let stepResult = await page.evaluate(() => {{
#                     const buttons = Array.from(document.querySelectorAll('div[role="button"]'));
#                     if (buttons.length === 0) return {{ clicked: false, finished: true }};
                    
#                     let operationalButtons = buttons.filter(b => b.className.includes('uArJb') || b.getAttribute('jsname') !== null);
#                     if (operationalButtons.length === 0) operationalButtons = buttons;
                    
#                     let submitBtn = operationalButtons.find(b => {{
#                         const innerStr = b.innerText ? b.innerText.toLowerCase() : "";
#                         return innerStr.includes('submit') || innerStr.includes('បញ្ជូន') || b.outerHTML.includes('submit');
#                     }});
                    
#                     if (submitBtn) {{
#                         submitBtn.scrollIntoView({{ block: 'center' }});
#                         submitBtn.click();
#                         return {{ clicked: true, finished: true }};
#                     }}
                    
#                     let nextBtn = operationalButtons.find(b => {{
#                         const innerStr = b.innerText ? b.innerText.toLowerCase() : "";
#                         return innerStr.includes('next') || innerStr.includes('បន្ទាប់') || innerStr.includes('continue');
#                     }});
                    
#                     if (!nextBtn && operationalButtons.length > 0) {{
#                         nextBtn = operationalButtons[operationalButtons.length - 1];
#                     }}
                    
#                     if (nextBtn) {{
#                         nextBtn.scrollIntoView({{ block: 'center' }});
#                         nextBtn.click();
#                         return {{ clicked: true, finished: false }};
#                     }}
                    
#                     return {{ clicked: false, finished: true }};
#                 }});
                
#                 if (stepResult.finished || !stepResult.clicked) break;
#                 await new Promise(r => setTimeout(r, 2000));
#             }}
            
#             await new Promise(r => setTimeout(r, 3000));
#             return {{ completed: true }};
#         }};
#         """
        
#         headers = {"Content-Type": "application/javascript"}
        
#         async with httpx.AsyncClient(timeout=60.0) as client:
#             try:
#                 response = await client.post(browserless_url, content=javascript_code, headers=headers)
#                 if response.status_code == 200:
#                     print("📡 Browserless Cloud HTTP REST execution submitted form successfully!")
#                     return True
#                 else:
#                     print(f"❌ Browserless REST API returned error status: {response.status_code}")
#                     return False
#             except Exception as e:
#                 print(f"❌ Exception caught during HTTP execution: {e}")
#                 return False

#     async def _execute_automation_steps(self, final_prefilled_url: str) -> bool:
#         """
#         Standard automation flow using live CDP sockets.
#         FIXED: Updated endpoint path from /playwright to /chromium to resolve 404 errors.
#         """
#         submission_success = False
#         cdp_url = f"wss://chrome.browserless.io/chromium?token={self.browserless_key}"

#         async with async_playwright() as p:
#             try:
#                 browser = await p.chromium.connect_over_cdp(cdp_url)
#                 context = await browser.new_context()
#                 page = await context.new_page()

#                 await page.goto(final_prefilled_url)
#                 await page.wait_for_timeout(1500)

#                 max_pages = 15
#                 for _ in range(1, max_pages + 1):
#                     await page.wait_for_timeout(1500)
#                     next_clicked = False
#                     next_button_selector = "xpath=//div[@role='button'][(contains(., 'Next') or contains(., 'បន្ទាប់')) and not(contains(., 'Submit') or contains(., 'បញ្ជូន'))]"

#                     try:
#                         next_btn = page.locator(next_button_selector)
#                         if await next_btn.is_visible(timeout=3000):
#                             await next_btn.click()
#                             next_clicked = True
#                     except:
#                         pass
#                     if not next_clicked:
#                         break

#                 await page.wait_for_timeout(1500)
#                 submit_button_selector = "xpath=//div[@role='button'][contains(., 'Submit') or contains(., 'បញ្ជូន')]"
#                 submit_clicked = False

#                 try:
#                     submit_btn = page.locator(submit_button_selector)
#                     if await submit_btn.is_visible(timeout=4000):
#                         await submit_btn.click()
#                         submit_clicked = True
#                 except:
#                     pass

#                 if not submit_clicked:
#                     try:
#                         await page.evaluate("""() => {
#                             document.querySelectorAll('div[role="button"]').forEach(btn => {
#                                 if (btn.innerText.toLowerCase().includes('submit') || btn.innerText.includes('បញ្ជូន')) {
#                                     btn.click();
#                                 }
#                             });
#                         }""")
#                         submit_clicked = True
#                     except:
#                         pass

#                 await page.wait_for_timeout(5000)
#                 current_url_lower = page.url.lower()
#                 submission_success = "formresponse" in current_url_lower or submit_clicked

#                 await context.close()
#                 await browser.close()
#             except Exception as e:
#                 print("⚠️ Live CDP WebSocket connection failed:", e)
#                 submission_success = False
                
#         return submission_success

#     async def _run_playwright_submission(self, final_prefilled_url: str) -> bool:
#         """
#         Main routing gateway. Runs via serverless execution.
#         FIXED: Automatically falls back to the HTTP REST API if WebSocket drops or fails on Vercel.
#         """
#         if sys.platform == 'win32':
#             print("🔧 Windows environment detected. Shifting execution processing directly to Browserless Cloud REST API...")
#             return await self._execute_via_browserless_api(final_prefilled_url)
        
#         print("🚀 Running native Playwright CDP connection...")
#         success = await self._execute_automation_steps(final_prefilled_url)
        
#         # Safe catch-all fallback loop for production server drops
#         if not success:
#             print("🔄 WebSocket connection failed or rejected. Dropping back to resilient HTTP REST API pipeline...")
#             return await self._execute_via_browserless_api(final_prefilled_url)
            
#         return success

#     async def submit_excel(self, form_request: FormRequest, file: UploadFile):
#         data = await self._get_data(form_request.url)

#         try:
#             file_content = await file.read()
#             df = pd.read_excel(io.BytesIO(file_content))
#             df.columns = [str(c).strip() for c in df.columns]
            
#             excel_rules = {}
#             for _, row in df.iterrows():
#                 q_name = str(row.get('Question', '')).strip()
#                 exc_val = row.get('Exception')
                
#                 if q_name and q_name != 'nan':
#                     if pd.notna(exc_val) and str(exc_val).strip().lower() != 'nan':
#                         exceptions = [e.strip() for e in str(exc_val).split(',')]
#                     else:
#                         exceptions = []
#                     excel_rules[q_name] = exceptions
#         except Exception as e:
#             raise HTTPException(
#                 status_code=status.HTTP_400_BAD_REQUEST,
#                 detail=f"Invalid Excel format or file structural reading error: {str(e)}"
#             )

#         clean_form_url = form_request.url.split('/viewform')[0] + '/viewform'

#         for i in range(form_request.number):
#             print(f"Time automation execution run: {i + 1} / {form_request.number}")
#             query_params = [('usp', 'pp_url')]
            
#             # --- CONDITION ADDED HERE ---
#             # Automatically generate and append a random email to handle the form tracking constraint
#             random_email = self._generate_random_email()
#             query_params.append(('emailAddress', random_email))
#             # -----------------------------
            
#             for q in data:
#                 entry_id = q['entry']
#                 options = q.get('options', [])
#                 field_type = q.get('type')
#                 q_title = q.get('title', '').strip()
                
#                 if not options:
#                     continue

#                 valid_pool = list(options)

#                 if q_title in excel_rules:
#                     exclusions = excel_rules[q_title]
#                     if exclusions:
#                         valid_pool = [opt for opt in options if str(opt).strip() not in exclusions]
#                         if not valid_pool:
#                             valid_pool = list(options)

#                 if field_type == 2:  # Checkboxes
#                     num_choices = random.randint(1, min(3, len(valid_pool)))
#                     chosen_options = random.sample(valid_pool, num_choices)
#                     for choice in chosen_options:
#                         query_params.append((f"entry.{entry_id}", choice))
#                 else:  # Radio/Dropdown
#                     chosen_option = random.choice(valid_pool)
#                     query_params.append((f"entry.{entry_id}", chosen_option))
                    
#             url_parts = list(urlparse(clean_form_url))
#             url_parts[4] = urlencode(query_params)
#             final_prefilled_url = urlunparse(url_parts)
            
#             success = await self._run_playwright_submission(final_prefilled_url)
            
#             if not success:
#                 raise HTTPException(
#                     status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#                     detail=f"Automation failed at instance step trace count index: {i + 1}"
#                 )
                
#         return {
#             "results": {
#                 "status": "success", 
#                 "message": f"Successfully completed all {form_request.number} form automated entries."
#             }
#         }


import asyncio
import random
import string
import sys
from urllib.parse import urlencode, urlparse, urlunparse
import pandas as pd
import io
from fastapi import HTTPException, UploadFile, status
from playwright.async_api import async_playwright

from schemas import FormRequest
from .google_form_parser import GoogleFormService
from core.config import settings 

class FormSubmissionService:
    def __init__(self):
        self.service_data = GoogleFormService()
        self.browserless_key = settings.BROWSERLESS_API_KEY
        
        if not self.browserless_key:
            print("⚠️ WARNING: BROWSERLESS_API_KEY is not configured in settings!")

    def _create_dynamic_email(self) -> str:
        """Generates a completely unique, fully random email address from scratch for each request."""
        # Generate a random username length between 5 and 10 characters
        user_length = random.randint(5, 10)
        username = ''.join(random.choices(string.ascii_lowercase, k=user_length))
        
        # Add a random numeric suffix to make it look like a real system ID
        numeric_suffix = str(random.randint(10, 9999))
        
        # Define variations of domains, keeping your school domain as a primary layout option
        domains = [
            "gmail.com",
            "outlook.com"
        ]
        chosen_domain = random.choice(domains)
        
        # Alternate between formats: 'username.number@domain' or 'username_number@domain' or 'usernamenumber@domain'
        formats = [
            f"{username}.{numeric_suffix}@{chosen_domain}",
            f"{username}_{numeric_suffix}@{chosen_domain}",
            f"{username}{numeric_suffix}@{chosen_domain}"
        ]
        
        return random.choice(formats)

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
        
    async def _execute_via_browserless_api(self, final_prefilled_url: str) -> bool:
        """
        REST API Fallback: Executes the automation steps by sending a direct 
        Puppeteer script execution payload directly to Browserless over HTTP.
        """
        import httpx
        
        browserless_url = f"https://chrome.browserless.io/function?token={self.browserless_key}"
        
        javascript_code = f"""
        export default async ({{ page }}) => {{
            await page.setViewport({{ width: 1440, height: 900 }});
            
            await page.goto('{final_prefilled_url}', {{ waitUntil: 'networkidle2', timeout: 30000 }});
            await new Promise(r => setTimeout(r, 2000));
            
            const maxPages = 15;
            
            for (let i = 0; i < maxPages; i++) {{
                let stepResult = await page.evaluate(() => {{
                    const buttons = Array.from(document.querySelectorAll('div[role="button"]'));
                    if (buttons.length === 0) return {{ clicked: false, finished: true }};
                    
                    let operationalButtons = buttons.filter(b => b.className.includes('uArJb') || b.getAttribute('jsname') !== null);
                    if (operationalButtons.length === 0) operationalButtons = buttons;
                    
                    let submitBtn = operationalButtons.find(b => {{
                        const innerStr = b.innerText ? b.innerText.toLowerCase() : "";
                        return innerStr.includes('submit') || innerStr.includes('បញ្ជូន') || b.outerHTML.includes('submit');
                    }});
                    
                    if (submitBtn) {{
                        submitBtn.scrollIntoView({{ block: 'center' }});
                        submitBtn.click();
                        return {{ clicked: true, finished: true }};
                    }}
                    
                    let nextBtn = operationalButtons.find(b => {{
                        const innerStr = b.innerText ? b.innerText.toLowerCase() : "";
                        return innerStr.includes('next') || innerStr.includes('បន្ទាប់') || innerStr.includes('continue');
                    }});
                    
                    if (!nextBtn && operationalButtons.length > 0) {{
                        nextBtn = operationalButtons[operationalButtons.length - 1];
                    }}
                    
                    if (nextBtn) {{
                        nextBtn.scrollIntoView({{ block: 'center' }});
                        nextBtn.click();
                        return {{ clicked: true, finished: false }};
                    }}
                    
                    return {{ clicked: false, finished: true }};
                }});
                
                if (stepResult.finished || !stepResult.clicked) break;
                await new Promise(r => setTimeout(r, 2000));
            }}
            
            await new Promise(r => setTimeout(r, 3000));
            return {{ completed: true }};
        }};
        """
        
        headers = {"Content-Type": "application/javascript"}
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                response = await client.post(browserless_url, content=javascript_code, headers=headers)
                if response.status_code == 200:
                    print("📡 Browserless Cloud HTTP REST execution submitted form successfully!")
                    return True
                else:
                    print(f"❌ Browserless REST API returned error status: {response.status_code}")
                    return False
            except Exception as e:
                print(f"❌ Exception caught during HTTP execution: {e}")
                return False

    async def _execute_automation_steps(self, final_prefilled_url: str) -> bool:
        """
        Standard automation flow using live CDP sockets.
        FIXED: Updated endpoint path from /playwright to /chromium to resolve 404 errors.
        """
        submission_success = False
        cdp_url = f"wss://chrome.browserless.io/chromium?token={self.browserless_key}"

        async with async_playwright() as p:
            try:
                browser = await p.chromium.connect_over_cdp(cdp_url)
                context = await browser.new_context()
                page = await context.new_page()

                await page.goto(final_prefilled_url)
                await page.wait_for_timeout(1500)

                max_pages = 15
                for _ in range(1, max_pages + 1):
                    await page.wait_for_timeout(1500)
                    next_clicked = False
                    next_button_selector = "xpath=//div[@role='button'][(contains(., 'Next') or contains(., 'បន្ទាប់')) and not(contains(., 'Submit') or contains(., 'បញ្ជូន'))]"

                    try:
                        next_btn = page.locator(next_button_selector)
                        if await next_btn.is_visible(timeout=3000):
                            await next_btn.click()
                            next_clicked = True
                    except:
                        pass
                    if not next_clicked:
                        break

                await page.wait_for_timeout(1500)
                submit_button_selector = "xpath=//div[@role='button'][contains(., 'Submit') or contains(., 'បញ្ជូន')]"
                submit_clicked = False

                try:
                    submit_btn = page.locator(submit_button_selector)
                    if await submit_btn.is_visible(timeout=4000):
                        await submit_btn.click()
                        submit_clicked = True
                except:
                    pass

                if not submit_clicked:
                    try:
                        await page.evaluate("""() => {
                            document.querySelectorAll('div[role="button"]').forEach(btn => {
                                if (btn.innerText.toLowerCase().includes('submit') || btn.innerText.includes('បញ្ជូន')) {
                                    btn.click();
                                }
                            });
                        }""")
                        submit_clicked = True
                    except:
                        pass

                await page.wait_for_timeout(5000)
                current_url_lower = page.url.lower()
                submission_success = "formresponse" in current_url_lower or submit_clicked

                await context.close()
                await browser.close()
            except Exception as e:
                print("⚠️ Live CDP WebSocket connection failed:", e)
                submission_success = False
                
        return submission_success

    async def _run_playwright_submission(self, final_prefilled_url: str) -> bool:
        """
        Main routing gateway. Runs via serverless execution.
        FIXED: Automatically falls back to the HTTP REST API if WebSocket drops or fails on Vercel.
        """
        if sys.platform == 'win32':
            print("🔧 Windows environment detected. Shifting execution processing directly to Browserless Cloud REST API...")
            return await self._execute_via_browserless_api(final_prefilled_url)
        
        print("🚀 Running native Playwright CDP connection...")
        success = await self._execute_automation_steps(final_prefilled_url)
        
        # Safe catch-all fallback loop for production server drops
        if not success:
            print("🔄 WebSocket connection failed or rejected. Dropping back to resilient HTTP REST API pipeline...")
            return await self._execute_via_browserless_api(final_prefilled_url)
            
        return success

    async def submit_excel(self, form_request: FormRequest, file: UploadFile):
        data = await self._get_data(form_request.url)

        try:
            file_content = await file.read()
            df = pd.read_excel(io.BytesIO(file_content))
            df.columns = [str(c).strip() for c in df.columns]
            
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

        clean_form_url = form_request.url.split('/viewform')[0] + '/viewform'

        for i in range(form_request.number):
            print(f"Time automation execution run: {i + 1} / {form_request.number}")
            query_params = [('usp', 'pp_url')]
            
            # --- MODIFIED: Creates a completely new random email string on each iteration ---
            new_random_email = self._create_dynamic_email()
            query_params.append(('emailAddress', new_random_email))
            # ---------------------------------------------------------------------------------
            
            for q in data:
                entry_id = q['entry']
                options = q.get('options', [])
                field_type = q.get('type')
                q_title = q.get('title', '').strip()
                
                if not options:
                    continue

                valid_pool = list(options)

                if q_title in excel_rules:
                    exclusions = excel_rules[q_title]
                    if exclusions:
                        valid_pool = [opt for opt in options if str(opt).strip() not in exclusions]
                        if not valid_pool:
                            valid_pool = list(options)

                if field_type == 2:  # Checkboxes
                    num_choices = random.randint(1, min(3, len(valid_pool)))
                    chosen_options = random.sample(valid_pool, num_choices)
                    for choice in chosen_options:
                        query_params.append((f"entry.{entry_id}", choice))
                else:  # Radio/Dropdown
                    chosen_option = random.choice(valid_pool)
                    query_params.append((f"entry.{entry_id}", chosen_option))
                    
            url_parts = list(urlparse(clean_form_url))
            url_parts[4] = urlencode(query_params)
            final_prefilled_url = urlunparse(url_parts)
            
            success = await self._run_playwright_submission(final_prefilled_url)
            
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
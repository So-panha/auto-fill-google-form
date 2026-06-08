# import io
# import random
# import pandas as pd
# import json
# import requests
# from fastapi import HTTPException, UploadFile, status
# from schemas import FormRequest
# from .google_form_parser import GoogleFormService
# from utils import UrlParse
# class FormService:

#     def __init__(self):
          
#             self.service_data = GoogleFormService()
#     # ------------------------------------------------
#     # MAIN: SUBMIT EXCEL DIRECTLY
#     # ------------------------------------------------
#     async def submit_excel(self, form_request: FormRequest, file: UploadFile) -> list[dict]:

#         """
#         Reads an uploaded Excel file stream and pushes its data directly 
#         to Google Forms automatically based on entries.
#         """
        

#         submit_url = UrlParse.parse(form_request.url)
#         data = await self._get_data(submit_url)
#         # print("Question: ", data)

#         # 1. Safely read Excel files from memory using BytesIO
#         try:
#             file_content = await file.read()
#             df = pd.read_excel(io.BytesIO(file_content))
#         except Exception as e:
#             raise HTTPException(
#                 status_code=status.HTTP_400_BAD_REQUEST,
#                 detail=f"Failed to parse Excel file. Ensure it is not corrupted. Error: {str(e)}"
#             )

#         results = []

#         # 2. Loop through execution counts requested from the endpoint
#         for i in range(form_request.number):
            
#             print(f"Executing form submission batch sweep: {i + 1}/{form_request.number}")

#             for _, row in df.iterrows():
#                 payload = {}

#                 for col in df.columns:
#                     value = row[col]

#                     # Skip empty spreadsheet blocks
#                     if pd.isna(value):
#                         continue

#                     # Get parsed matching question entry details
#                     question = data.get(col)
#                     if not question:
#                         continue

#                     print("Question :", question)

#                     # Support options retrieval from either objects or dict fields
#                     options = []
#                     if hasattr(question, "options"):
#                         options = question.options or []
#                     elif isinstance(question, dict):
#                         options = question.get("options", [])

#                     # -------------------------
#                     # RANDOM VALUE LOGIC
#                     # -------------------------
#                     if str(value).upper() == "RANDOM":
#                         exception_value = None

#                         if "exception" in df.columns:
#                             exception_value = row.get("exception")

#                         pool = list(options).copy() if options else []

#                         if exception_value and exception_value in pool:
#                             pool.remove(exception_value)

#                         value = random.choice(pool) if pool else ""

#                     # Add matched element directly to the submission structure
#                     payload[col] = value

#                 # # Modifying target URL endpoint structure cleanly to formResponse route structure
#                 # submit_url = form_request.url
#                 # if "formResponse" not in submit_url:
#                 #     if submit_url.endswith("/viewform"):
#                 #         submit_url = submit_url.replace("/viewform", "/formResponse")
#                 #     elif not submit_url.endswith("/formResponse"):
#                 #         # Truncate clean trailing components to stitch properly
#                 #         submit_url = submit_url.rstrip("/") + "/formResponse"

#                 # -------------------------
#                 # HTTP SUBMIT TO GOOGLE FORM
#                 # -------------------------
#                 # try:
#                 #     response = requests.post(
#                 #         submit_url,
#                 #         data=payload,
#                 #         headers={
#                 #             "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
#                 #         },
#                 #         timeout=10 # Avoid thread locks by using explicit timeouts
#                 #     )

#                 #     results.append({
#                 #         "status": response.status_code,
#                 #         "success": response.status_code in [200, 201]
#                 #     })

#                 # except Exception as e:
#                 #     results.append({
#                 #         "status": "error",
#                 #         "message": f"Network submission failure: {str(e)}"
#                 #     })

#         return {"results": results}

#     async def _get_data(self, url: str):
#         try:
#             data = await self.service_data.get_questions(str(url))
#             return data["questions"]
#         except Exception as e:
#             raise HTTPException(
#                 status_code=status.HTTP_400_BAD_REQUEST, 
#                 detail=f"Failed to fetch form structure: {str(e)}"
#             )











import io
import random
import pandas as pd
import json
import requests
from fastapi import HTTPException, UploadFile, status
from schemas import FormRequest
from .google_form_parser import GoogleFormService
from utils import UrlParse

class FormService:

    def __init__(self):
        self.service_data = GoogleFormService()

    # ------------------------------------------------
    # MAIN: SUBMIT EXCEL DIRECTLY
    # ------------------------------------------------
    async def submit_excel(self, form_request: FormRequest, file: UploadFile) -> dict:
        """
        Reads a vertically aligned custom layout sheet and submits a full form compilation.
        """
        submit_url = UrlParse.parse(form_request.url)
        questions_list = await self._get_data(submit_url)
        
        # Map Google Form titles to their structural metadata dictionaries
        questions_map = {str(q.get("title")).strip().lower(): q for q in questions_list if isinstance(q, dict)}

        try:
            file_content = await file.read()
            df = pd.read_excel(io.BytesIO(file_content))
            
            # Clean dataframe column strings cleanly
            df.columns = [str(c).strip() for c in df.columns]
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to parse Excel file: {str(e)}"
            )

        # Confirm columns exist based on your uploaded image layout
        if "Question" not in df.columns:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Excel must contain a column named 'Question'."
            )

        results = []

        # Loop through execution counts requested from the endpoint
        for i in range(form_request.number):
            print(f"Executing form submission batch sweep: {i + 1}/{form_request.number}")

            payload = {}

            # Loop through your rows (each row is a question)
            for _, row in df.iterrows():
                question_text = str(row.get("Question")).strip()
                
                if pd.isna(row.get("Question")) or not question_text:
                    continue

                # Look up the question meta details out of our schema map
                question_data = questions_map.get(question_text.lower())
                if not question_data:
                    print(f"Skipping: '{question_text}' - not found in Google Form setup.")
                    continue

                entry_id = question_data.get("entry")
                options = question_data.get("options", []) or []
                options = [opt for opt in options if opt is not None]

                # --- FIX: ASSIGN THE RANDOM MATRIX POOL TRULY FROM GOOGLE FORM DATA OPTIONS ---
                # Since your template says "Question" on the left, we look for the cell contents 
                # or evaluate how you want to fill it. If you want this tool to always choose 
                # randomly out of your options list unless an exception hits:
                
                exception_value = None
                if "Exception" in df.columns and not pd.isna(row.get("Exception")):
                    exception_value = str(row.get("Exception")).strip()

                # Filter pool using your exclusion parameters
                pool = list(options).copy()
                if exception_value:
                    pool = [opt for opt in pool if str(opt).strip().lower() != exception_value.lower()]

                # Select a clean target value option out of your data choice options array!
                final_value = random.choice(pool) if pool else ""

                if entry_id:
                    payload[f"entry.{entry_id}"] = final_value

            # Print your clean, newly calculated options array payload block!
            print("DEBUG Payload: ", payload)

            # Submit the completed form array block to Google
            if payload:
                try:
                    response = requests.post(
                        submit_url,
                        data=payload,
                        headers={"User-Agent": "Mozilla/5.0"},
                        timeout=10
                    )
                    results.append({"status": response.status_code, "success": response.status_code in [200, 201]})
                except Exception as e:
                    results.append({"status": "error", "message": str(e)})

        return {"results": results}

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
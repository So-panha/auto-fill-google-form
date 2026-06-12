import re
import json
import httpx
class GoogleFormService:

    async def get_questions(self, url: str):
            """Extract questions, entry IDs, and types from Google Form"""
            async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
                response = await client.get(url)
                response.raise_for_status()
                html = response.text

            match = re.search(r'FB_PUBLIC_LOAD_DATA_\s*=\s*(\[.+?\]);', html, re.DOTALL)
            if not match:
                raise Exception("Could not find form data in HTML. Make sure URL is correct.")

            try:
                data = json.loads(match.group(1))
            except json.JSONDecodeError:
                raise Exception("Failed to parse Google Form data")

            form_items = None
            if len(data) > 1 and isinstance(data[1], list):
                form_items = data[1][1] if len(data[1]) > 1 else data[1]
            elif len(data) > 0:
                form_items = data[0][1] if isinstance(data[0], list) else []

            if not form_items:
                raise Exception("Could not find questions in form structure")

            questions = []

            for item in form_items:
                try:
                    if not isinstance(item, list) or len(item) < 4:
                        continue

                    title = item[1]  # Question title
                    item_type = item[3]  # <--- CRITICAL CHHANGE: Extracting Google's Type ID

                    # Find question info
                    question_info = None
                    if len(item) > 4 and isinstance(item[4], list) and item[4]:
                        question_info = item[4][0]
                    elif len(item) > 3 and isinstance(item[3], list) and item[3]:
                        question_info = item[3][0]

                    if not question_info or not isinstance(question_info, list):
                        continue

                    entry_id = question_info[0]

                    # Extract options
                    options = []
                    if len(question_info) > 1 and isinstance(question_info[1], list):
                        for choice in question_info[1]:
                            if isinstance(choice, list) and choice:
                                opt_text = choice[0]
                                if opt_text is not None and opt_text !=  "":
                                    options.append(str(opt_text).strip())

                    questions.append({
                        "title": str(title).strip(),
                        "entry": str(entry_id),
                        "type": item_type,  # <--- Dynamic field type added to your schema
                        "options": options
                    })

                except Exception:
                    continue 

            return {
                "questions": questions,
                "size": len(questions)
            }

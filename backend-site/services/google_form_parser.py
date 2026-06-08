import re
import json
import httpx
class GoogleFormService:

    async def get_questions(self, url: str):

        async with httpx.AsyncClient(
            timeout=30,
            follow_redirects=True
        ) as client:

            response = await client.get(url)
            response.raise_for_status()

        html = response.text

        match = re.search(
            r'FB_PUBLIC_LOAD_DATA_\s*=\s*(\[.*?\]);',
            html,
            re.DOTALL
        )

        if not match:
            raise Exception("FB_PUBLIC_LOAD_DATA_ not found")

        data = json.loads(match.group(1))

        try:
            form_items = data[1][1]
        except Exception:
            raise Exception("Google form structure differs")

        # ✔ FIX 1: create list
        questions = []

        for item in form_items:

            try:
                title = item[1].split(".")[1].strip()
                question_info = item[4][0]
                entry_id = question_info[0]

                options = []

                if len(question_info) > 1 and question_info[1]:
                    for choice in question_info[1]:
                        if isinstance(choice, list) and choice:
                            options.append(choice[0])

                # ✔ FIX 2: append OBJECT, not class
                questions.append(
                    {
                        "title": title,
                        "entry":entry_id,
                        "options":options
                    }                )

            except Exception:
                continue

        return {
            "questions": questions,
            "size" : len(questions)
        }
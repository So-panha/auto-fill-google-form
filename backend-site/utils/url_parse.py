import urllib.parse
class UrlParse():

    def parse(url : str):
        # Inside form_service.py -> submit_excel()

        incoming_url = url

        # 1. Parse the URL components accurately
        parsed_url = urllib.parse.urlparse(incoming_url)

        # 2. Extract the path component (e.g., /forms/d/e/.../viewform)
        path = parsed_url.path

        # 3. Forcefully replace path variants to target formResponse
        if path.endswith("/viewform"):
            path = path.replace("/viewform", "/formResponse")
        elif path.endswith("/edit"):
            path = path.replace("/edit", "/formResponse")
        elif path.endswith("/prefill"):
            path = path.replace("/prefill", "/formResponse")
        elif not path.endswith("/formResponse"):
            path = path.rstrip("/") + "/formResponse"

        # 4. Reconstruct the clean URL without trailing parameters
        submit_url = f"{parsed_url.scheme}://{parsed_url.netloc}{path}"

        # Check your console terminal to ensure this says /formResponse!
        print(f"DEBUG FINAL TARGET URL -> {submit_url}")

        return submit_url
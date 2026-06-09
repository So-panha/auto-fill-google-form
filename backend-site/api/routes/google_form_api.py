from fastapi import APIRouter, Form, Form, status
from schemas import FormRequest, FormResponse
from services import FormSubmissionService, GoogleFormService
from fastapi import File, UploadFile
from fastapi import APIRouter, HTTPException
from schemas import FormRequest, QuestionReq



router = APIRouter()
@router.post("/auto_fill", response_model=FormResponse, status_code=status.HTTP_200_OK)
async def auto_fill ( url: str = Form(...), number: str = Form(...), file: UploadFile = File(...)):
    
    form_in = FormRequest(url=url, number=number)
    service_submit = FormSubmissionService()
    return await service_submit.submit_excel(form_in, file)      



@router.post("/data_extract", response_model=dict, status_code=status.HTTP_200_OK)
async def get_google_form(request: QuestionReq):

    service = GoogleFormService()
    try:
        return await service.get_questions(str(request.url))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
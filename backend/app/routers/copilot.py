# from fastapi import APIRouter, UploadFile, File, Form, HTTPException
# from typing import Optional

# from app.agents.langgraph_agent import run_extraction, run_correction
# from app.services.pdf_service import extract_text_from_upload
# from app.schemas.complaint import (
#     CopilotParseResponse, CopilotChatRequest, CopilotChatResponse,
#     ExtractedFields, RiskAssessment, BonusInsights,
# )

# router = APIRouter(prefix="/api/copilot", tags=["copilot"])


# @router.post("/parse", response_model=CopilotParseResponse)
# async def parse_complaint(
#     text: Optional[str] = Form(None),
#     file: Optional[UploadFile] = File(None),
# ):
#     """
#     Accepts EITHER pasted text/email OR an uploaded PDF/email/txt file
#     (matches the two intake modes in the reference UI: "paste text" and
#     "drop complaint files"). Runs the LangGraph extraction workflow and
#     returns form fields + AI risk assessment + bonus insights.
#     """
#     if not text and not file:
#         raise HTTPException(400, "Provide either 'text' or a 'file'.")

#     if file:
#         raw_bytes = await file.read()
#         raw_text = extract_text_from_upload(file.filename, raw_bytes)
#     else:
#         raw_text = text

#     if not raw_text or not raw_text.strip():
#         raise HTTPException(422, "Could not read any text from the input.")

#     result = run_extraction(raw_text)
#     return CopilotParseResponse(
#         reply=result["reply"],
#         fields=ExtractedFields(**result["fields"]),
#         risk=RiskAssessment(**result["risk"]),
#         bonus=BonusInsights(**result["bonus"]),
#     )


# @router.post("/chat", response_model=CopilotChatResponse)
# async def chat_correction(payload: CopilotChatRequest):
#     """
#     Conversational corrections after the initial parse, e.g.
#     "ah sorry the batch number is BMX240602 and affected quantity is 48 capsules"
#     -> only the mentioned fields are updated, matching the demo video flow.
#     """
#     result = run_correction(payload.message, payload.current_fields)
#     return CopilotChatResponse(
#         reply=result["reply"],
#         updated_fields=ExtractedFields(**result["updated_fields"]),
#         changed_keys=result["changed_keys"],
#     )





# from typing import Optional

# from fastapi import APIRouter, UploadFile, File, Form, HTTPException

# from app.agents.langgraph_agent import run_extraction, run_correction
# from app.services.pdf_service import extract_text_from_upload
# from app.schemas.complaint import (
#     CopilotParseResponse,
#     CopilotChatRequest,
#     CopilotChatResponse,
#     ExtractedFields,
#     RiskAssessment,
#     BonusInsights,
# )

# router = APIRouter(
#     prefix="/api/copilot",
#     tags=["copilot"],
# )


# @router.post("/parse", response_model=CopilotParseResponse)
# async def parse_complaint(
#     text: Optional[str] = Form(None),
#     file: Optional[UploadFile] = File(None),
# ):

#     if text is None and file is None:
#         raise HTTPException(
#             status_code=400,
#             detail="Provide either text or file."
#         )

#     if file:
#         raw_bytes = await file.read()
#         raw_text = extract_text_from_upload(file.filename, raw_bytes)
#     else:
#         raw_text = text

#     if not raw_text or not raw_text.strip():
#         raise HTTPException(
#             status_code=422,
#             detail="Could not extract any text."
#         )

#     result = run_extraction(raw_text)

#     return CopilotParseResponse(
#         reply=result["reply"],
#         fields=ExtractedFields(**result["fields"]),
#         risk=RiskAssessment(**result["risk"]),
#         bonus=BonusInsights(**result["bonus"]),
#     )


# @router.post("/chat", response_model=CopilotChatResponse)
# async def chat(payload: CopilotChatRequest):

#     result = run_correction(
#         payload.message,
#         payload.current_fields,
#     )

#     return CopilotChatResponse(



from typing import Optional

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.agents.langgraph_agent import run_correction, run_extraction
from app.schemas.complaint import (
    BonusInsights,
    CopilotChatRequest,
    CopilotChatResponse,
    CopilotParseResponse,
    ExtractedFields,
    RiskAssessment,
)
from app.services.pdf_service import extract_text_from_upload


router = APIRouter(
    prefix="/api/copilot",
    tags=["copilot"],
)


@router.post("/parse", response_model=CopilotParseResponse)
async def parse_complaint(
    text: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
):
    """
    Accept pasted complaint text or an uploaded complaint file.

    The complaint is processed by the LangGraph extraction workflow,
    which returns extracted fields, risk assessment, and bonus insights.
    """

    if not text and not file:
        raise HTTPException(
            status_code=400,
            detail="Provide either 'text' or a 'file'.",
        )

    if file:
        raw_bytes = await file.read()

        if not raw_bytes:
            raise HTTPException(
                status_code=422,
                detail="The uploaded file is empty.",
            )

        raw_text = extract_text_from_upload(
            file.filename or "",
            raw_bytes,
        )
    else:
        raw_text = text

    if not raw_text or not raw_text.strip():
        raise HTTPException(
            status_code=422,
            detail="Could not read any text from the input.",
        )

    result = run_extraction(raw_text)

    return CopilotParseResponse(
        reply=result["reply"],
        fields=ExtractedFields(**result["fields"]),
        risk=RiskAssessment(**result["risk"]),
        bonus=BonusInsights(**result["bonus"]),
    )


@router.post("/chat", response_model=CopilotChatResponse)
async def chat_correction(payload: CopilotChatRequest):
    """
    Processes conversational corrections after the initial complaint parse.

    Example:
        "The batch number is BMX240602 and affected quantity is 48 capsules."

    Only the fields identified by the correction workflow are updated.
    """

    result = run_correction(
        payload.message,
        payload.current_fields,
    )

    return CopilotChatResponse(
        reply=result["reply"],
        updated_fields=ExtractedFields(**result["updated_fields"]),
        changed_keys=result["changed_keys"],
    )

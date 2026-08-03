
# from typing import Optional

# from fastapi import APIRouter, File, Form, HTTPException, UploadFile

# from app.agents.langgraph_agent import run_correction, run_extraction
# from app.schemas.complaint import (
#     BonusInsights,
#     CopilotChatRequest,
#     CopilotChatResponse,
#     CopilotParseResponse,
#     ExtractedFields,
#     RiskAssessment,
# )
# from app.services.pdf_service import extract_text_from_upload


# router = APIRouter(
#     prefix="/api/copilot",
#     tags=["copilot"],
# )


# @router.post("/parse", response_model=CopilotParseResponse)
# async def parse_complaint(
#     text: Optional[str] = Form(None),
#     file: Optional[UploadFile] = File(None),
# ):
#     """
#     Accept pasted complaint text or an uploaded complaint file.

#     The complaint is processed by the LangGraph extraction workflow,
#     which returns extracted fields, risk assessment, and bonus insights.
#     """

#     if not text and not file:
#         raise HTTPException(
#             status_code=400,
#             detail="Provide either 'text' or a 'file'.",
#         )

#     if file:
#         raw_bytes = await file.read()

#         if not raw_bytes:
#             raise HTTPException(
#                 status_code=422,
#                 detail="The uploaded file is empty.",
#             )

#         raw_text = extract_text_from_upload(
#             file.filename or "",
#             raw_bytes,
#         )
#     else:
#         raw_text = text

#     if not raw_text or not raw_text.strip():
#         raise HTTPException(
#             status_code=422,
#             detail="Could not read any text from the input.",
#         )

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
#     Processes conversational corrections after the initial complaint parse.

#     Example:
#         "The batch number is BMX240602 and affected quantity is 48 capsules."

#     Only the fields identified by the correction workflow are updated.
#     """

#     result = run_correction(
#         payload.message,
#         payload.current_fields,
#     )

#     return CopilotChatResponse(
#         reply=result["reply"],
#         updated_fields=ExtractedFields(**result["updated_fields"]),
#         changed_keys=result["changed_keys"],
#     )



from typing import Optional

from fastapi import (
    APIRouter,
    File,
    Form,
    HTTPException,
    UploadFile,
)

from app.agents.langgraph_agent import (
    run_correction,
    run_extraction,
)
from app.schemas.complaint import (
    BonusInsights,
    CopilotChatRequest,
    CopilotChatResponse,
    CopilotParseResponse,
    ExtractedFields,
    RiskAssessment,
)
from app.services.pdf_service import (
    extract_text_from_upload,
)


router = APIRouter(
    prefix="/api/copilot",
    tags=["copilot"],
)


@router.post(
    "/parse",
    response_model=CopilotParseResponse,
)
async def parse_complaint(
    text: Optional[str] = Form(default=None),
    file: Optional[UploadFile] = File(default=None),
):
    """
    Parse a new customer complaint.

    Input can be either:
    - pasted complaint text, or
    - an uploaded complaint file.

    The extracted complaint is processed through the
    LangGraph extraction workflow.
    """

    # Require either text or file.
    if not text and not file:
        raise HTTPException(
            status_code=400,
            detail="Provide either 'text' or a 'file'.",
        )

    # Extract text from uploaded file.
    if file is not None:
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

    # Use pasted text.
    else:
        raw_text = text

    # Validate extracted text.
    if not raw_text or not raw_text.strip():
        raise HTTPException(
            status_code=422,
            detail="Could not read any text from the input.",
        )

    # Run AI extraction.
    try:
        result = run_extraction(
            raw_text.strip()
        )
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Complaint extraction failed: {str(exc)}",
        ) from exc

    # Validate AI result.
    if not isinstance(result, dict):
        raise HTTPException(
            status_code=500,
            detail="Invalid response from the extraction workflow.",
        )

    try:
        return CopilotParseResponse(
            reply=result.get("reply", ""),
            fields=ExtractedFields(
                **result.get("fields", {})
            ),
            risk=RiskAssessment(
                **result.get("risk", {})
            ),
            bonus=BonusInsights(
                **result.get("bonus", {})
            ),
        )
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Could not format extraction result: {str(exc)}",
        ) from exc


@router.post(
    "/chat",
    response_model=CopilotChatResponse,
)
async def chat_correction(
    payload: CopilotChatRequest,
):
    """
    Process a conversational correction to the
    previously extracted complaint fields.
    """

    if not payload.message or not payload.message.strip():
        raise HTTPException(
            status_code=400,
            detail="Correction message cannot be empty.",
        )

    try:
        result = run_correction(
            payload.message.strip(),
            payload.current_fields,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Complaint correction failed: {str(exc)}",
        ) from exc

    if not isinstance(result, dict):
        raise HTTPException(
            status_code=500,
            detail="Invalid response from the correction workflow.",
        )

    try:
        return CopilotChatResponse(
            reply=result.get("reply", ""),
            updated_fields=ExtractedFields(
                **result.get("updated_fields", {})
            ),
            changed_keys=result.get("changed_keys", []),
        )
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Could not format correction result: {str(exc)}",
        ) from exc

import base64
import os
from io import StringIO
from typing import Optional

import pandas as pd
from fastapi import APIRouter, Depends, Form
from starlette.responses import HTMLResponse, RedirectResponse

from common.schemas.models.message import SuccessMessage
from points.database.database import get_db, PointsDatabase
from points.schemas.crud.csv_document import CSVDocumentCreate
from points.schemas.models import CSVDocument

from points.routers.document._point import router as points_router
from points.settings import DOCUMENTS_FOLDER

router = APIRouter(
    prefix="/documents",
    tags=["document"]
)


@router.post("", response_model=CSVDocument, status_code=201, summary="Create a new document",
             description="Create a new document", response_description="The created document")
async def create_document(new_document: CSVDocumentCreate, db: PointsDatabase = Depends(get_db)):

    base64_decoded_file = StringIO(new_document.csv_file)
    contents = base64_decoded_file.read()

    # decode file_content_base64
    decoded_file_content = base64.b64decode(contents).decode('utf-8')

    # Specify the folder to save the file
    upload_folder = DOCUMENTS_FOLDER
    os.makedirs(upload_folder, exist_ok=True)

    # Construct the file path
    file_name = new_document.name + ".csv"
    file_path = os.path.join(upload_folder, file_name)

    # Write the file contents to the specified path
    with open(file_path, "wb") as f:
        print("saving document " + file_name)
        f.write(decoded_file_content.encode('utf-8'))

    document = CSVDocument(name=new_document.name, file_name=file_name)
    result = await db.document.create(document)
    return result


@router.post("/real/time", response_class=RedirectResponse, status_code=201, summary="Create a new document",
             description="Create a new document from real time data")
async def create_document_real_time(first_skeleton_id: int = Form(...), last_skeleton_id: int = Form(...),
                                    new_document_name: str = Form(...), db: PointsDatabase = Depends(get_db)):
    # Get all skeletons
    skeletons = await db.skeleton.filter()
    skeletons = [skeleton for skeleton in skeletons if first_skeleton_id <= skeleton.id <= last_skeleton_id]
    if not skeletons:
        return SuccessMessage(success=False, message="No skeletons found in the specified range", data={})

    # Get all body parts
    new_data = []
    count = 0
    for skeleton in skeletons:
        body_parts = await db.body_parts.filter(skeleton_id=skeleton.id)
        for part in body_parts:
            new_data.append([count, skeleton.id, skeleton.datetime, part.part_type, part.x, part.y])
            count += 1

    columns = ["count", "id", "datetime", "part_type", "x", "y"]
    pd.DataFrame(data=new_data, columns=columns).to_csv(
        os.path.join(DOCUMENTS_FOLDER, new_document_name + ".csv"), index=False
    )

    document = CSVDocument(name=new_document_name, file_name=new_document_name + ".csv")
    result = await db.document.create(document)

    # redirect to the analysis page of the document
    return RedirectResponse("/documents/" + str(result.id) + "/points/analysis", status_code=303)


@router.get("", response_model=list[CSVDocument], summary="Read all documents",
            description="Read all documents", response_description="List of all documents")
async def read_documents(db: PointsDatabase = Depends(get_db)):
    result = await db.document.filter()
    return result


@router.get("/html", response_class=HTMLResponse, summary="Read all documents html",
            description="Read all documents html", response_description="List of all documents html")
async def get_documents_html(document_id: Optional[int] = None, db: PointsDatabase = Depends(get_db)):
    result = await db.document.filter()
    options_documents = ""
    if not document_id:
        options_documents = "<option selected readonly disabled value=''>-- Select a document --</option>"
    for result_document in result:
        selected = "selected" if document_id and document_id == result_document.id else ""
        options_documents += f"<option value='{result_document.id}' {selected}>{result_document.name}</option>"
    return HTMLResponse(content=options_documents, status_code=200)


@router.get("/{document_id}", response_model=CSVDocument, summary="Read a document",
            description="Read a document", response_description="The requested document")
async def read_document(document_id: int, db: PointsDatabase = Depends(get_db)):
    result = await db.document.get(document_id)
    return result


@router.delete("/{document_id}", response_model=SuccessMessage, summary="Delete a document",
               description="Delete a document", response_description="True if the document was deleted")
async def delete_document(document_id: int, db: PointsDatabase = Depends(get_db)):
    result = await db.document.delete(document_id)
    return SuccessMessage(success=result, message="CSVDocument deleted", data={"document_id": document_id})


router.include_router(points_router, tags=["points"], prefix="/{document_id}")

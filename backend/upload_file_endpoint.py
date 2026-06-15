@app.post("/upload-file")
async def upload_file(
    file: UploadFile = File(...),
    use_ai_tagging: bool = Form(False),
    ai_provider: str = Form("openai"),
    ollama_model: str = Form("llama3.1")
):
    """
    Upload a file (PDF, DOCX, TXT) and process it
    """
    try:
        logger.info(f"Uploading file: {file.filename}")
        
        # Read file content
        content = await file.read()
        
        # Extract text based on file type
        if file.filename.endswith('.pdf'):
            import PyPDF2
            import io
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(content))
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
        elif file.filename.endswith('.docx'):
            import docx
            import io
            doc = docx.Document(io.BytesIO(content))
            text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        elif file.filename.endswith('.txt'):
            text = content.decode('utf-8')
        else:
            raise HTTPException(status_code=400, detail="Unsupported file type. Use PDF, DOCX, or TXT")
        
        # Use the existing upload logic
        upload_request = UploadRequest(
            title=file.filename,
            source=file.filename,
            text=text,
            use_ai_tagging=use_ai_tagging,
            ai_provider=ai_provider,
            ollama_model=ollama_model
        )
        
        return await upload_document(upload_request)
        
    except Exception as e:
        logger.error(f"File upload failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

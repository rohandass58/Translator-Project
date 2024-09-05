import os
from django.shortcuts import render
from django.conf import settings
from django.http import HttpResponse
from .forms import UploadFileForm
from PyPDF2 import PdfReader
from googletrans import Translator
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from io import BytesIO


def handle_uploaded_file(f, filename):
    """Save the uploaded file to the media folder."""
    save_path = os.path.join(settings.MEDIA_ROOT, filename)
    with open(save_path, "wb+") as destination:
        for chunk in f.chunks():
            destination.write(chunk)
    return save_path


def read_file_content(file_path):
    """Read the content of the file based on its type."""
    file_extension = os.path.splitext(file_path)[1].lower()
    try:
        if file_extension in [".txt", ".md", ".csv"]:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()
        elif file_extension == ".pdf":
            reader = PdfReader(file_path)
            content = ""
            for page in reader.pages:
                content += page.extract_text()
            return content
        else:
            raise ValueError(f"Unsupported file format: {file_extension}")
    except Exception as e:
        raise ValueError(f"Error reading file: {str(e)}")


def create_pdf(content, filename):
    """Create a PDF file with the given content."""
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    y = height - 40
    for line in content.split("\n"):
        if y < 40:
            p.showPage()
            y = height - 40
        p.drawString(40, y, line)
        y -= 15
    p.showPage()
    p.save()
    buffer.seek(0)
    return buffer


def translate_text(content, target_language):
    """Use googletrans to translate the content into the target language."""
    translator = Translator()
    try:
        translation = translator.translate(content, dest=target_language)
        return translation.text
    except Exception as e:
        raise ValueError(f"Translation error: {str(e)}")


def upload_and_translate(request):
    if request.method == "POST":
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES["file"]
            target_language = form.cleaned_data["target_language"]
            try:
                file_path = handle_uploaded_file(file, file.name)
                content = read_file_content(file_path)
                translated_content = translate_text(content, target_language)

                # Create PDF
                pdf_buffer = create_pdf(translated_content, file.name)

                # Prepare response
                response = HttpResponse(
                    pdf_buffer.getvalue(), content_type="application/pdf"
                )
                response["Content-Disposition"] = (
                    f'attachment; filename="{file.name}_translated.pdf"'
                )
                return response
            except Exception as e:
                return render(
                    request,
                    "upload.html",
                    {"form": form, "error_message": f"An error occurred: {str(e)}"},
                )
    else:
        form = UploadFileForm()
    return render(request, "upload.html", {"form": form})

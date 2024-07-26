FROM public.ecr.aws/lambda/python:latest

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY extract_pdf.py .
COPY transform_pdf.py .
COPY load_pdf.py .
COPY pdf_report.py .
COPY styles.css .

CMD [ "pdf_report.main" ]
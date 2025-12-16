FROM python:3.11-slim
WORKDIR /main
COPY . /main
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 8000
CMD [ "uvicorn", "main.main:app", "--reload", "--port", "8000" ]

FROM python:3.10-slim

WORKDIR /home/app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
RUN mkdir -p /home/app
RUN mkdir -p /home/frontend
COPY . /home/app
COPY ../frontend/* /home
CMD ["uvicorn", "main:app"]


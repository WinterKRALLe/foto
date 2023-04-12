FROM python:3.8-slim-buster
ENV LD_LIBRARY_PATH=/usr/lib

WORKDIR /app

COPY . .

RUN apt-get update \
    && apt-get install -y pkg-config libglib2.0-0 libgl1-mesa-glx \
    && rm -rf /var/lib/apt/lists/*

ENV LD_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu/

RUN apt-get update \
    && apt-get install -y tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install pytesseract pdf2img PyPDF3 opencv-python

CMD [ "python3", "new_script.py" ]

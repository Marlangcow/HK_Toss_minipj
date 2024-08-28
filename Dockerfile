FROM python:3.10.14-slim

# Working Directory
WORKDIR /usr/src/app

# COPY
COPY requirements.txt .

# Install Dependencies
RUN pip install -r requirements.txt

# COPY
COPY . .

# Entry
EXPOSE 8501
ENTRYPOINT streamlit run demo.py
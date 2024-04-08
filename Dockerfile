#Using python
FROM python:3.9.7
# Using Layered approach for the installation of requirements
COPY requirements.txt ./requirements.txt
RUN pip install -r requirements.txt
#Copy files to your container
COPY . ./
#Running your APP and doing some PORT Forwarding
EXPOSE 8080

CMD python app.py
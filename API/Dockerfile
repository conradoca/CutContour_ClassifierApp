FROM python:3.9.17-slim

# Copy the local package directories to the container
COPY . .

# Install any needed packages specified in requirements.txt
RUN pip install --trusted-host pypi.python.org -r requirements.txt

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Run app.py when the container launches
CMD ["uvicorn", "ClassifierAPI:app", "--host", "0.0.0.0", "--port", "8000"]
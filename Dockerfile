# Используем официальный Python-образ
FROM python:3.12-alpine

# Set the working directory
WORKDIR /app

# Copy the poetry.lock and pyproject.toml files
COPY poetry.lock pyproject.toml ./

# Install Poetry
RUN pip install poetry

# Install dependencies
RUN poetry install

# Copy the rest of the application code
COPY . .

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application
CMD ["poetry", "run", "python", "manage.py", "runserver", "0.0.0.0:8000"]
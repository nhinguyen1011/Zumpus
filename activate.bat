@echo off
REM Activate the virtual environment
if exist venv\Srcipts\activate (
    call venv\Scripts\activate
    echo Virtual environment activated.
) else (
    echo Virtual environment not found. Please ensure that venv is created.
)

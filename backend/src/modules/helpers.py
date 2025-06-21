from datetime import datetime

def calculate_age(birth_year: str) -> int:
    try:
        birth_date = datetime.strptime(birth_year, "%Y-%d-%m")
        today = datetime.now()
        age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
        return age
    except ValueError:
        print(f"Invalid date format for birth year: {birth_year}. Expected format is 'dd.mm.yyyy'.")
        return -1
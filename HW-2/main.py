import os
if not os.path.exists("appeals"):
    os.makedirs("appeals")

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr, validator, Field
from enum import Enum
import json
from datetime import date, datetime
from typing import List
import re

app = FastAPI(title="Customer Appeal Service", version="1.0.0")

class AppealReason(str, Enum):
    no_network = "нет доступа к сети"
    phone_not_working = "не работает телефон"
    no_emails = "не приходят письма"

class CustomerAppeal(BaseModel):
    surname: str = Field(..., min_length=1, max_length=50, description="Surname with uppercase first letter, Cyrillic only", example="Иванов")
    name: str = Field(..., min_length=1, max_length=50, description="Name with uppercase first letter, Cyrillic only", example="Иван")
    birth_date: date = Field(..., description="Birth date in YYYY-MM-DD format", example="1990-01-01")
    phone: str = Field(..., min_length=10, max_length=20, description="Valid phone number", example="+7 (999) 123-45-67")
    email: EmailStr = Field(..., description="Valid email address", example="ivan@example.com")
    reason: AppealReason = Field(..., description="Причина обращения", example="нет доступа к сети")
    problem_detected_at: datetime = Field(..., description="Дата и время обнаружения проблемы (YYYY-MM-DDTHH:MM:SS)", example="2025-07-05T14:27:50.890Z")

    @validator('surname')
    def validate_surname(cls, v):
        if not v or not v[0].isupper():
            raise ValueError('Фамилия должна начинаться с заглавной буквы')
        if not re.match(r'^[А-Яа-яЁё\s-]+$', v):
            raise ValueError('Фамилия должна содержать только кириллические символы')
        return v

    @validator('name')
    def validate_name(cls, v):
        if not v or not v[0].isupper():
            raise ValueError('Имя должно начинаться с заглавной буквы')
        if not re.match(r'^[А-Яа-яЁё\s-]+$', v):
            raise ValueError('Имя должно содержать только кириллические символы')
        return v

    @validator('phone')
    def validate_phone(cls, v):
        if not re.match(r'^\+?[0-9\s\-\(\)]+$', v):
            raise ValueError('Телефон должен содержать только цифры, пробелы, дефисы, скобки и опционально +')
        digits_only = re.sub(r'[^\d]', '', v)
        if len(digits_only) < 10 or len(digits_only) > 15:
            raise ValueError('Телефон должен содержать от 10 до 15 цифр')
        return v

@app.post("/appeals/", response_model=CustomerAppeal)
async def create_appeal(appeal: CustomerAppeal):
    try:
        appeal_data = appeal.dict()
        appeal_data['birth_date'] = appeal_data['birth_date'].isoformat()
        appeal_data['problem_detected_at'] = appeal_data['problem_detected_at'].isoformat()
        
        filename = f"appeals/appeal_{len(os.listdir('appeals')) + 1}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(appeal_data, f, ensure_ascii=False, indent=2)
        
        return appeal
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving appeal: {str(e)}")

@app.get("/appeals/", response_model=List[CustomerAppeal])
async def get_all_appeals():
    appeals = []
    appeals_dir = "appeals"
    
    if not os.path.exists(appeals_dir):
        return appeals
    
    for filename in os.listdir(appeals_dir):
        if filename.endswith('.json'):
            filepath = os.path.join(appeals_dir, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    data['birth_date'] = date.fromisoformat(data['birth_date'])
                    appeals.append(CustomerAppeal(**data))
            except Exception as e:
                print(f"Error reading {filename}: {e}")
    
    return appeals

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 
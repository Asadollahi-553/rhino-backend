# main.py

# 1. ایمپورت کردن کلاس‌های مورد نیاز
# FastAPI: کلاس اصلی برای ایجاد برنامه وب API.
# uvicorn: یک سرور ASGI (Asynchronous Server Gateway Interface) است که FastAPI از آن برای اجرا استفاده می‌کند.
# os: برای کار با متغیرهای محیطی سیستم عامل.
# google.generativeai as genai: کتابخانه رسمی گوگل برای کار با Gemini API.
# dotenv: برای خواندن متغیرهای محیطی از یک فایل .env.
# pydantic.BaseModel: برای تعریف مدل داده‌ای ورودی درخواست، که به FastAPI کمک می‌کند اعتبارسنجی را انجام دهد.
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
import uvicorn
import os
import google.generativeai as genai
from dotenv import load_dotenv
from pydantic import BaseModel

# 2. بارگذاری متغیرهای محیطی از فایل .env
# این تابع، محتوای فایل .env را در کنار این فایل، به عنوان متغیرهای محیطی بارگذاری می‌کند.
# این کار به ما اجازه می‌دهد که کلید API را به صورت امن از کد جدا کنیم.
load_dotenv()

# 3. ایجاد یک نمونه از برنامه FastAPI
app = FastAPI()

# 4. تعریف یک مدل داده‌ای برای بدنه درخواست POST
# این مدل مشخص می‌کند که بدنه درخواست POST باید یک فیلد به نام 'prompt' از نوع رشته داشته باشد.
# این کار از دریافت درخواست‌های نامعتبر جلوگیری می‌کند و کد را خواناتر می‌کند.
class PromptRequest(BaseModel):
    prompt: str

# 5. بررسی و پیکربندی Gemini API
# ابتدا تلاش می‌کنیم کلید API را از متغیر محیطی GEMINI_API_KEY دریافت کنیم.
api_key = os.environ.get("GEMINI_API_KEY")
#api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    # اگر کلید API در متغیرهای محیطی پیدا نشد، یک خطا ایجاد می‌کنیم.
    # این کار از اجرای برنامه بدون کلید جلوگیری کرده و یک پیام واضح برای توسعه‌دهنده فراهم می‌کند.
    print("Error: GEMINI_API_KEY environment variable not set.")
    raise ValueError("GEMINI_API_KEY environment variable not set. Please create a .env file and add your key.")
else:
    # اگر کلید پیدا شد، مدل جمینای را با آن کلید پیکربندی می‌کنیم.
    genai.configure(api_key=api_key)
    print("Gemini API is configured successfully.")


# 6. تعریف یک مسیر (Endpoint) برای روت اصلی ('/')
@app.get("/")
async def read_root():
    """
    این تابع یک درخواست HTTP GET به مسیر اصلی '/' را مدیریت می‌کند و یک پیام خوشامدگویی برمی‌گرداند.
    """
    return {"message": "Hello from FastAPI Backend! Gemini is ready."}

# 7. تعریف یک مسیر جدید برای ارتباط با Gemini API
@app.post("/generate")
async def generate_content_endpoint(request_body: PromptRequest):
    """
    این تابع درخواست‌های POST را برای تولید محتوا با Gemini API مدیریت می‌کند.
    :param request_body: بدنه درخواست که توسط Pydantic اعتبارسنجی شده و شامل فیلد 'prompt' است.
    """
    try:
        # دریافت متن پرامپت از بدنه درخواست
        prompt = request_body.prompt
        
        # انتخاب مدل Gemini (در اینجا از 'gemini-2.5-flash' استفاده می‌شود)
        # این خط یک مدل جدید برای هر درخواست ایجاد می‌کند.
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        # ارسال پرامپت به API جمینای
        response = model.generate_content(prompt)
        
        # استخراج متن تولید شده از پاسخ
        generated_text = response.text
        
        # بازگرداندن پاسخ به صورت JSON
        return JSONResponse(content={"text": generated_text})

    except Exception as e:
        # مدیریت خطاهای احتمالی و بازگرداندن پاسخ خطا
        # برای حفظ امنیت، تنها پیام خطا را به عنوان یک رشته برمی‌گردانیم و جزئیات فنی را فاش نمی‌کنیم.
        return JSONResponse(content={"error": str(e)}, status_code=500)

# 8. تعریف یک مسیر دیگر با پارامتر مسیر (Path Parameter) و پارامتر کوئری (Query Parameter)
# این همان مسیر قبلی شماست که بدون تغییر حفظ شده است.
@app.get("/items/{item_id}")
async def read_item(item_id: int, query_param: str = None):
    """
    این تابع یک درخواست HTTP GET به مسیر '/items/{item_id}' را مدیریت می‌کند.
    """
    item_data = {"item_id": item_id, "description": f"This is item number {item_id}"}
    if query_param:
        item_data["query_param"] = query_param
    return item_data

# 9. کد برای اجرای سرور توسعه (فقط برای تست لوکال)
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)

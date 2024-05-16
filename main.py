from dotenv import load_dotenv
from fastapi import FastAPI, File, UploadFile,HTTPException
from PIL import Image
import google.generativeai as genai
import os
from typing import List


load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-pro')

app = FastAPI()


prompt = """
You need to extract the information from the invoice document given as text format and fill up the JSON as below output format.
output format -

<{
    "vendor_name": "",
    "invoice_number": "",
    "vendor_address": "",
    "tax_id": "",
    "invoice_date": "",
    "bill_to_name": "",
    "bill_to_address": "",
    "invoice_amount": "",
    "invoice_currency": "",
    "invoice_items": [
        {
            "description": "",
            "item_no": "",
            "unit_price": "",
            "quantity": "",
            "net_price": ""
        }
    ]
}>
"""
def LLM(files):
    result = []

    for file in files:
        image = Image.open(file.file)
        model = genai.GenerativeModel("gemini-pro-vision")
        response = model.generate_content([prompt, image], stream=True)
        response.resolve()
        result.append(response.text)

    return process_images(result)


def LLM_folder(file_paths):
    result = []
    try:
        # Check if the folder exists
        if not os.path.exists(file_paths):
            raise HTTPException(status_code=404, detail=f"Folder not found: {file_paths}")

        # Get the list of files in the given folder
        file_paths = [os.path.join(file_paths, file) for file in os.listdir(file_paths) if
                      file.lower().endswith(('.png', '.jpg', '.jpeg'))]

        for file_path in file_paths:
            image = Image.open(file_path)
            model = genai.GenerativeModel("gemini-pro-vision")
            response = model.generate_content([prompt, image], stream=True)
            response.resolve()
            result.append(response.text)
        return process_images(result)
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))


@app.post("/process_folder/")
async def folder_image(file_name:str):
    return LLM_folder(file_name)


@app.post("/process_image/")
async def process_image(files: List[UploadFile] = File(...)):
    return LLM(files)

def process_images(processed_texts):
    try:
        if len(processed_texts) < 2:
            raise HTTPException(status_code=400, detail="At least two processed texts are required for comparison.")

        prompt = """
        Generate a similarity score of these two invoices. These invoices might be duplicates. Hence, generate a similarity score in percentage.
        Compare the below information of Vendor Invoices and generate the difference between those two invoices.

        Consider these invoice comparison attributes - `Invoice Number`, `Invoice Amount`, `Invoice Quantity`, `Vendor Name`, `Invoice Date`, `Invoice Items`, `Bill To`

        Output Format -

        {
            "similarity_score": "", # in percentage [comparing invoice comparison attributes]
            "similarity_reason": "", # [comparing invoice comparison attributes]
            "difference": "" # text [invoice comparison attributes]
        }

        vendor_invoice json data is parsed by <>.
        """

        for i, text in enumerate(processed_texts, start=1):
            prompt += f"\nvendor_invoice_{i}: \n<{text}>"

        # print(prompt)

        text_model = genai.GenerativeModel("gemini-pro")
        response_compared = text_model.generate_content(prompt)
        response_compared.resolve()
        return response_compared.text
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))


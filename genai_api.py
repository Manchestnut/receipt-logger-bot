from google import genai
from google.genai import types
from typing import Literal, Optional
from pydantic import BaseModel, Field

class ReceiptData(BaseModel):

    is_receipt: bool = Field(description="True if the image is a financial receipt, invoice, or bill, or money transfer. False otherwise.")

    merchant: Optional[str] = Field(description="The name of the store or business")
    total_amount: Optional[float] = Field(description="The total cost on the scripts")
    transaction_date: Optional[str] = Field(description="The date of the transaction in YYYY-MM-DD format")
    category: Literal["Groceries", "Dining", "Fuel", "Utilities", "Entertainment", "Others"] = Field(
        default=None,
        description="The expense category selected from the allowed list")

async def analyze_receipt_with_ai(image_path: str):
    client = genai.Client().aio

    with open(image_path, "rb") as f:
        image_bytes = f.read()

    response = await client.models.generate_content(
        model='gemini-2.5-flash-lite',
        contents=[
            types.Part.from_bytes(
                data=image_bytes,
                mime_type='image/jpeg'
            ),
            "Extract the merchant, total_amount, transaction_date, and category from this receipt"
        ],
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=ReceiptData,
        ),
    )
    return response.text
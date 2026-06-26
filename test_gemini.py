from openai import OpenAI
import os
client = OpenAI(api_key=os.getenv('GEMINI_API_KEY'), base_url='https://generativelanguage.googleapis.com/v1beta/openai/')
try:
  models = client.models.list()
  for m in models.data: print(m.id)
except Exception as e: print(e)

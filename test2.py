from google import genai
from google.genai import types

ai_client = genai.Client(api_key='AIzaSyCLsKYp-STratMiisGemdyL-R1sFV_6zQg')



response = ai_client.models.generate_content(
    model='gemini-2.0-flash',
    contents='Tell me a story in 300 words.'
)
print(response.text)

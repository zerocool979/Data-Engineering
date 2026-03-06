from google import genai

client = genai.Client(
    api_key="YOUR_GOOGLE_API_KEY"
)

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="Jawab dengan singkat: tips untuk public speaking dengan profesional dan friendly"
)

print(response.text)





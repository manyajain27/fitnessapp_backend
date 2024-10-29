from django.http import HttpResponse
import google.generativeai as genai
from django.conf import settings

genai.configure(api_key=settings.GEMINI_API_KEY)

def chatbot_view(request):
    default_prompt = "create a 7 day meal plan for vegetarian diet to gain muscle and weight. dont give any extra informaion,titles.just the meal plan."

    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content([default_prompt])

    print(response.text)


    return HttpResponse("Check the console for the Gemini API response.")

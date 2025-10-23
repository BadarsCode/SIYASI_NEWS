from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, JsonResponse
from .models import NewsArticle
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from django.shortcuts import redirect
from rest_framework import generics
from .serializers import NewsArticleSerializer
from django.views.decorators.csrf import csrf_exempt
import json
import google.generativeai as genai

genai.configure(api_key=settings.GEN_API_KEY)  # Use the API key from settings

@csrf_exempt
def chatbot_api(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user_msg = data.get("message", "").strip()
            
            if not user_msg:
                return JsonResponse({"reply": "Please type a message."}, status=400)
            
            # Try using Gemini API first
            try:
                model = genai.GenerativeModel('gemini-2.5-flash')
                response = model.generate_content(user_msg)
                bot_reply = response.text
            except Exception as gemini_error:
                print(f"Gemini API Error: {gemini_error}")
                # Fallback to rule-based responses
                bot_reply = get_rule_based_response(user_msg)
            
            return JsonResponse({"reply": bot_reply})
            
        except json.JSONDecodeError:
            return JsonResponse({"reply": "Invalid request format."}, status=400)
        except Exception as e:
            print(f"Error in chatbot_api: {e}")
            return JsonResponse({
                "reply": "Sorry, I'm experiencing technical difficulties. Please try again later."
            }, status=500)
    
    return JsonResponse({"reply": "Invalid request method."}, status=405)


def get_rule_based_response(message):
    '''Fallback rule-based responses'''
    message_lower = message.lower()
    
    # Greetings
    if any(word in message_lower for word in ['hello', 'hi', 'hey', 'greetings']):
        return "Hello! 👋 I'm your news assistant. How can I help you today?"
    
    # News related
    elif any(word in message_lower for word in ['news', 'article', 'latest', 'recent']):
        return "You can explore the latest news in various categories on our homepage. Browse through Politics, Sports, Technology, Entertainment, and more! 📰"
    
    # About
    elif 'about' in message_lower:
        return "We're a news platform dedicated to bringing you the latest updates from around the world. Check out our About page for more information! ℹ️"
    
    # Contact
    elif 'contact' in message_lower:
        return "You can reach us through our Contact page. We'd love to hear from you! 📧"
    
    # Categories
    elif 'category' in message_lower or 'categories' in message_lower:
        return "We cover multiple categories including Politics, Sports, Technology, Entertainment, Business, and more. Use the menu to explore! 📑"
    
    # Help
    elif 'help' in message_lower:
        return "I can help you navigate the site, find news articles, or answer questions about our platform. What would you like to know? 🤔"
    
    # Thank you
    elif any(word in message_lower for word in ['thanks', 'thank you', 'appreciate']):
        return "You're welcome! Feel free to ask if you need anything else. 😊"
    
    # Goodbye
    elif any(word in message_lower for word in ['bye', 'goodbye', 'see you']):
        return "Goodbye! Have a great day! 👋"
    
    # Default
    else:
        return "I'm here to help! You can ask me about news categories, how to navigate the site, or any other questions. What would you like to know? 🤖"


class NewsArticleListAPI(generics.ListCreateAPIView):
    queryset = NewsArticle.objects.all().order_by('-published_at')
    serializer_class = NewsArticleSerializer

class NewsArticleDetailAPI(generics.RetrieveUpdateDestroyAPIView):
    queryset = NewsArticle.objects.all()
    serializer_class = NewsArticleSerializer


def Home(request):
    articles = NewsArticle.objects.order_by('-published_at')[:5]  # slider
    top_articles = NewsArticle.objects.order_by('-published_at')[:5]
    breaking_news= NewsArticle.objects.order_by('-published_at')[:5]  # sidebar top  # sidebar top
    all_articles = NewsArticle.objects.all().order_by('-published_at')
    categories = [cat[0] for cat in NewsArticle.categories]
    return render(request, 'news/home.html', {
        'articles': articles,
        'top_articles': top_articles,
        'all_articles': all_articles,
        'categories': categories,
        'breaking_news': breaking_news
    })

def gallery(request):
    articles = NewsArticle.objects.exclude(images="").order_by('-published_at')
    return render(request, 'news/gallery.html', {'articles': articles})

# Static policy/info pages
def privacy_view(request): return render(request, 'news/privacy.html')
def terms_view(request): return render(request, 'news/terms.html')
def about_view(request): return render(request, 'news/about.html')
def contact_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')
        full_message = f"From: {name} < {email} >\n\n{message}"
        try:
            send_mail(
                subject="Contact Form Submission",
                message=full_message,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[settings.EMAIL_HOST_USER],
                fail_silently=False,

            )
            messages.success(request, "your message has been sent successfully!")
        except Exception as e:
            messages.error(request, f"An error occurred: {e}")
        return redirect('contact')
    return render(request, 'news/contact.html')


from django.shortcuts import render, get_object_or_404
from .models import NewsArticle

def article_detail(request, pk):
    article = get_object_or_404(NewsArticle, pk=pk)
    articles = NewsArticle.objects.exclude(pk=pk).order_by('-published_at')[:10]  # show 10 related
    return render(request, 'news/article_detail.html', {
        'article': article,
        'articles': articles
    })


def CategoryView(request, category_name):
    articles = NewsArticle.objects.filter(category=category_name).order_by('-published_at')
    for i in articles:
        print(i)
    return render(request, 'news/category.html',  {'article': articles, 'category': category_name})
def category_view(request, category):
    article = NewsArticle.objects.filter(category=category).order_by('-published_at')
    return render(request, 'news/category.html', {'article': article, 'category': category})


@csrf_exempt
def chatbot_view(request):
    if request.method == "POST":
        data = json.loads(request.body)
        user_msg = data.get("message", "")

        # Simple rule-based bot
        if "hello" in user_msg.lower():
            reply = "Hello! 👋 How can I help you today?"
        elif "news" in user_msg.lower():
            reply = "You can explore the latest news in the categories above 📢."
        else:
            reply = "Sorry, I don’t understand that yet. 😅"

        return JsonResponse({"reply": reply})

# login view
def login_view(request):
    return render(request, 'news/login.html')

def signup_view(request):
    return render(request, 'news/signup.html')
def logout_view(request):
    return HttpResponse("You have been logged out.")

def category(request):
    categories = NewsArticle.objects.all()
    return render(request, "home.html", {'categories':categories})
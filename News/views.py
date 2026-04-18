import re
import json
import google.generativeai as genai

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.db import models
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import generics

from .models import NewsArticle, SavedArticle, UserProfile
from .serializers import NewsArticleSerializer

GEN_API_KEY = getattr(settings, "GEN_API_KEY", None)
if GEN_API_KEY:
    genai.configure(api_key=GEN_API_KEY)

MAX_HEADLINES = 5
MAX_CHAT_HISTORY = 12
CHAT_HISTORY_SESSION_KEY = "chat_history"
CHAT_STATE_SESSION_KEY = "chat_state"
CATEGORY_ALIASES = {
    "politics": "Politics",
    "sports": "Sports",
    "tech": "Technology",
    "technology": "Technology",
    "health": "Health",
    "entertainment": "Entertainment",
    "business": "Business",
    "world": "World",
    "science": "Science",
    "travel": "Travel",
    "lifestyle": "Lifestyle",
    "education": "Education",
    "environment": "Environment",
    "opinion": "Opinion",
    "culture": "Culture",
    "food": "Food",
    "fashion": "Fashion",
    "history": "History",
    "music": "Music",
    "art": "Art",
    "religion": "Religion",
}


def _normalize_message(message):
    return re.sub(r"\s+", " ", message or "").strip()


def _match_category(message_lower):
    for alias, canonical in CATEGORY_ALIASES.items():
        if re.search(rf"\b{re.escape(alias)}\b", message_lower):
            return canonical
    return None


def _build_article_links(articles):
    links = []
    for article in articles:
        links.append({
            "title": article.title,
            "url": reverse("article_detail", args=[article.pk]),
            "category": article.category,
            "published": article.published_at.strftime("%b %d, %Y"),
        })
    return links


def _format_articles(articles, heading):
    if not articles:
        return f"{heading} There are no articles yet.", []

    lines = [heading, "Tap a headline below to open the story."]
    return "\n".join(lines), _build_article_links(articles)


def _format_search_results(results, query):
    if not results:
        return f'I could not find any results for "{query}".', []

    lines = [f'Results for "{query}":', "Tap a result below to read it."]
    return "\n".join(lines), _build_article_links(results)


def _get_saved_ids(user):
    if user.is_authenticated:
        return set(SavedArticle.objects.filter(user=user).values_list("article_id", flat=True))
    return set()


def _get_chat_history(request):
    history = request.session.get(CHAT_HISTORY_SESSION_KEY, [])
    return history if isinstance(history, list) else []


def _save_chat_history(request, history):
    request.session[CHAT_HISTORY_SESSION_KEY] = history[-MAX_CHAT_HISTORY:]


def _get_chat_state(request):
    state = request.session.get(CHAT_STATE_SESSION_KEY, {})
    return state if isinstance(state, dict) else {}


def _save_chat_state(request, state):
    request.session[CHAT_STATE_SESSION_KEY] = state or {}


def _render_history(history):
    if not history:
        return ""
    lines = []
    for item in history[-8:]:
        role = "User" if item.get("role") == "user" else "Assistant"
        content = _normalize_message(item.get("content", ""))
        if content:
            lines.append(f"{role}: {content}")
    return "\n".join(lines)


def _is_follow_up(message_lower):
    return any(word in message_lower for word in ["more", "another", "next", "again", "continue"])


def generate_bot_reply(user_msg, history=None, state=None):
    message = _normalize_message(user_msg)
    if not message:
        return "Please type a message so I can help.", [], state or {}

    history = history or []
    state = state or {}
    message_lower = message.lower()

    if _is_follow_up(message_lower):
        last_intent = state.get("last_intent")
        if last_intent == "category" and state.get("last_category"):
            matched_category = state["last_category"]
            category_articles = NewsArticle.objects.filter(category__iexact=matched_category).order_by("-published_at")[
                :MAX_HEADLINES
            ]
            heading = f"More {matched_category} headlines:"
            reply, links = _format_articles(category_articles, heading)
            state["last_intent"] = "category"
            return reply, links, state

        if last_intent == "search" and state.get("last_query"):
            query = state["last_query"]
            results = NewsArticle.objects.filter(
                models.Q(title__icontains=query) | models.Q(content__icontains=query)
            ).order_by("-published_at")[:MAX_HEADLINES]
            reply, links = _format_search_results(results, query)
            state["last_intent"] = "search"
            return reply, links, state

        if last_intent == "latest":
            latest_articles = NewsArticle.objects.order_by("-published_at")[:MAX_HEADLINES]
            reply, links = _format_articles(latest_articles, "Here are more headlines:")
            state["last_intent"] = "latest"
            return reply, links, state

    if any(word in message_lower for word in ["hello", "hi", "hey", "greetings"]):
        return "Hello! I am your news assistant. What would you like to explore today?", [], state

    if "help" in message_lower:
        return (
            "I can share the latest headlines, show a category, or help you search. "
            'Try: "latest headlines", "technology news", or "search: economy".',
            [],
            state,
        )

    if "contact" in message_lower:
        return "You can reach us through the Contact page. We would love to hear from you.", [], state

    if "about" in message_lower:
        return (
            "Siyasi News brings you updates across politics, world, technology, business, "
            "sports, and more. Ask for a category or the latest headlines.",
            [],
            state,
        )

    if "category" in message_lower or "categories" in message_lower:
        categories = ", ".join([cat[0] for cat in NewsArticle.categories])
        return f"We cover: {categories}. Ask for any category to see recent stories.", [], state

    if message_lower.startswith("search:") or message_lower.startswith("find "):
        query = message.split(":", 1)[-1].strip() if ":" in message else message[5:].strip()
        if query:
            results = NewsArticle.objects.filter(
                models.Q(title__icontains=query) | models.Q(content__icontains=query)
            ).order_by("-published_at")[:MAX_HEADLINES]
            reply, links = _format_search_results(results, query)
            state["last_intent"] = "search"
            state["last_query"] = query
            return reply, links, state

    if any(word in message_lower for word in ["latest", "headlines", "breaking", "top", "recent"]):
        latest_articles = NewsArticle.objects.order_by("-published_at")[:MAX_HEADLINES]
        reply, links = _format_articles(latest_articles, "Here are the latest headlines:")
        state["last_intent"] = "latest"
        return reply, links, state

    matched_category = _match_category(message_lower)
    if matched_category:
        category_articles = NewsArticle.objects.filter(category__iexact=matched_category).order_by("-published_at")[
            :MAX_HEADLINES
        ]
        heading = f"Latest {matched_category} headlines:"
        reply, links = _format_articles(category_articles, heading)
        state["last_intent"] = "category"
        state["last_category"] = matched_category
        return reply, links, state

    if GEN_API_KEY:
        try:
            latest_articles = NewsArticle.objects.order_by("-published_at")[:MAX_HEADLINES]
            context_lines = [
                f"- {article.title} ({article.category})"
                for article in latest_articles
            ]
            context_block = "\n".join(context_lines) if context_lines else "No recent headlines available."
            history_block = _render_history(history)
            history_prompt = f"Recent conversation:\n{history_block}\n" if history_block else ""
            prompt = (
                "You are the Siyasi News assistant. Answer concisely, in plain text, and be friendly. "
                "Do not include HTML. When a user asks about news, use these headlines as context:\n"
                f"{context_block}\n"
                f"{history_prompt}"
                f"User: {message}\nAssistant:"
            )
            model = genai.GenerativeModel("gemini-2.5-flash")
            response = model.generate_content(prompt)
            if response and response.text:
                return response.text.strip(), [], state
        except Exception as gemini_error:
            print(f"Gemini API Error: {gemini_error}")

    return get_rule_based_response(message), [], state


@csrf_exempt
def chatbot_api(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user_msg = data.get("message", "")
            history = _get_chat_history(request)
            state = _get_chat_state(request)
            reply_text, links, state = generate_bot_reply(user_msg, history=history, state=state)

            history.extend([
                {"role": "user", "content": _normalize_message(user_msg)},
                {"role": "assistant", "content": reply_text},
            ])
            _save_chat_history(request, history)
            _save_chat_state(request, state)

            return JsonResponse({"reply": reply_text, "links": links})
        except json.JSONDecodeError:
            return JsonResponse({"reply": "Invalid request format."}, status=400)
        except Exception as exc:
            print(f"Error in chatbot_api: {exc}")
            return JsonResponse(
                {"reply": "Sorry, I am experiencing technical difficulties. Please try again later."},
                status=500,
            )

    return JsonResponse({"reply": "Invalid request method."}, status=405)


def chat_page(request):
    history = _get_chat_history(request)
    return render(request, "news/chat.html", {"chat_history": history})

def get_rule_based_response(message):
    message_lower = message.lower()

    if any(word in message_lower for word in ["hello", "hi", "hey", "greetings"]):
        return "Hello! I am your news assistant. How can I help you today?"

    if any(word in message_lower for word in ["news", "article", "latest", "recent"]):
        return (
            "You can explore the latest news in various categories on our homepage. "
            "Browse Politics, Sports, Technology, Entertainment, and more."
        )

    if "about" in message_lower:
        return (
            "We are a news platform dedicated to bringing you the latest updates from around the world. "
            "Check out our About page for more information."
        )

    if "contact" in message_lower:
        return "You can reach us through our Contact page. We would love to hear from you."

    if "category" in message_lower or "categories" in message_lower:
        return (
            "We cover multiple categories including Politics, Sports, Technology, Entertainment, Business, "
            "and more. Use the menu to explore."
        )

    if "help" in message_lower:
        return (
            "I can help you navigate the site, find news articles, or answer questions about our platform. "
            "What would you like to know?"
        )

    if any(word in message_lower for word in ["thanks", "thank you", "appreciate"]):
        return "You are welcome! Feel free to ask if you need anything else."

    if any(word in message_lower for word in ["bye", "goodbye", "see you"]):
        return "Goodbye! Have a great day!"

    return (
        "I am here to help. You can ask me about news categories, how to navigate the site, "
        "or any other questions. What would you like to know?"
    )


class NewsArticleListAPI(generics.ListCreateAPIView):
    queryset = NewsArticle.objects.all().order_by("-published_at")
    serializer_class = NewsArticleSerializer


class NewsArticleDetailAPI(generics.RetrieveUpdateDestroyAPIView):
    queryset = NewsArticle.objects.all()
    serializer_class = NewsArticleSerializer


def Home(request):
    latest_five = list(NewsArticle.objects.order_by("-published_at")[:5])
    all_articles = NewsArticle.objects.order_by("-published_at")[:20]
    categories = [cat[0] for cat in NewsArticle.categories]
    saved_ids = _get_saved_ids(request.user)
    return render(request, "news/home.html", {
        "articles": latest_five,
        "top_articles": latest_five,
        "all_articles": all_articles,
        "categories": categories,
        "breaking_news": latest_five,
        "saved_ids": saved_ids,
    })


def gallery(request):
    articles = NewsArticle.objects.exclude(images="").exclude(images__isnull=True).order_by("-published_at")[:50]
    return render(request, "news/gallery.html", {"articles": articles})


def privacy_view(request):
    return render(request, "news/privacy.html")


def terms_view(request):
    return render(request, "news/terms.html")


def about_view(request):
    return render(request, "news/about.html")


def contact_view(request):
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        email = request.POST.get("email", "").strip()
        message = request.POST.get("message", "").strip()
        
        if not name or not email or not message:
            messages.error(request, "All fields are required.")
            return redirect("contact")
            
        full_message = f"From: {name} < {email} >\n\n{message}"
        try:
            send_mail(
                subject="Contact Form Submission",
                message=full_message,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[settings.EMAIL_HOST_USER],
                fail_silently=False,
            )
            messages.success(request, "Your message has been sent successfully!")
        except Exception as exc:
            messages.error(request, "We couldn't deliver the message. Please check server email configurations.")
        return redirect("contact")
    return render(request, "news/contact.html")


def article_detail(request, pk):
    article = get_object_or_404(NewsArticle, pk=pk)
    related_articles = NewsArticle.objects.filter(category__iexact=article.category).exclude(pk=pk).order_by("-published_at")[:6]
    is_saved = False
    if request.user.is_authenticated:
        is_saved = SavedArticle.objects.filter(user=request.user, article=article).exists()
    return render(request, "news/article_detail.html", {
        "article": article,
        "related_articles": related_articles,
        "is_saved": is_saved,
    })


def category_view(request, category):
    articles = NewsArticle.objects.filter(category__iexact=category).order_by("-published_at")
    saved_ids = _get_saved_ids(request.user)
    return render(request, "news/category.html", {"articles": articles, "category": category, "saved_ids": saved_ids})


@csrf_exempt
def chatbot_view(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"reply": "Invalid request format."}, status=400)

        user_msg = data.get("message", "")
        history = _get_chat_history(request)
        state = _get_chat_state(request)
        reply_text, links, state = generate_bot_reply(user_msg, history=history, state=state)

        history.extend([
            {"role": "user", "content": _normalize_message(user_msg)},
            {"role": "assistant", "content": reply_text},
        ])
        _save_chat_history(request, history)
        _save_chat_state(request, state)

        return JsonResponse({"reply": reply_text, "links": links})

    return JsonResponse({"reply": "Invalid request method."}, status=405)


def chat_page(request):
    history = _get_chat_history(request)
    return render(request, "news/chat.html", {"chat_history": history})

def login_view(request):
    if request.method == "POST":
        username = _normalize_message(request.POST.get("username", ""))
        password = request.POST.get("password", "")

        if not username or not password:
            messages.error(request, "Please enter both username and password.")
            return render(request, "news/login.html")

        user = authenticate(request, username=username, password=password)
        if user:
            auth_login(request, user)
            messages.success(request, "Welcome back!")
            return redirect("home")

        messages.error(request, "Invalid username or password.")

    return render(request, "news/login.html")


def signup_view(request):
    if request.method == "POST":
        username = _normalize_message(request.POST.get("username", ""))
        email = request.POST.get("email", "").strip()
        password1 = request.POST.get("password1", "")
        password2 = request.POST.get("password2", "")

        if not username or not email or not password1 or not password2:
            messages.error(request, "All fields are required.")
            return render(request, "news/signup.html")

        if password1 != password2:
            messages.error(request, "Passwords do not match.")
            return render(request, "news/signup.html")

        if User.objects.filter(username=username).exists():
            messages.error(request, "This username is already taken.")
            return render(request, "news/signup.html")

        if User.objects.filter(email=email).exists():
            messages.error(request, "This email is already registered.")
            return render(request, "news/signup.html")

        try:
            validate_password(password1)
        except ValidationError as exc:
            messages.error(request, " ".join(exc.messages))
            return render(request, "news/signup.html")

        user = User.objects.create_user(username=username, email=email, password=password1)
        auth_login(request, user)
        messages.success(request, "Account created successfully.")
        return redirect("home")

    return render(request, "news/signup.html")


@login_required(login_url="login")
def profile_view(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        request.user.first_name = _normalize_message(request.POST.get("first_name", ""))
        request.user.last_name = _normalize_message(request.POST.get("last_name", ""))
        email = request.POST.get("email", "").strip()
        if email:
            request.user.email = email
        profile.location = _normalize_message(request.POST.get("location", ""))
        profile.bio = request.POST.get("bio", "").strip()
        if request.FILES.get("avatar"):
            profile.avatar = request.FILES["avatar"]

        request.user.save()
        profile.save()
        messages.success(request, "Profile updated.")
        return redirect("profile")

    saved_articles = SavedArticle.objects.filter(user=request.user).select_related("article")
    return render(request, "news/profile.html", {"saved_articles": saved_articles, "profile": profile})


@login_required(login_url="login")
def toggle_save_article(request, pk):
    article = get_object_or_404(NewsArticle, pk=pk)
    saved_item = SavedArticle.objects.filter(user=request.user, article=article).first()

    if saved_item:
        saved_item.delete()
        messages.info(request, "Removed from your saved list.")
    else:
        SavedArticle.objects.create(user=request.user, article=article)
        messages.success(request, "Saved to your reading list.")

    next_url = request.POST.get("next") or request.META.get("HTTP_REFERER")
    if next_url:
        return redirect(next_url)
    return redirect("article_detail", pk=pk)


def logout_view(request):
    auth_logout(request)
    messages.success(request, "You have been logged out.")
    return redirect("home")


def search(request):
    query = _normalize_message(request.GET.get("q", ""))
    if query:
        results = NewsArticle.objects.filter(
            models.Q(title__icontains=query) | models.Q(content__icontains=query)
        ).order_by("-published_at")[:50]
    else:
        results = NewsArticle.objects.none()
    saved_ids = _get_saved_ids(request.user)
    return render(request, "news/search.html", {"results": results, "query": query, "saved_ids": saved_ids})






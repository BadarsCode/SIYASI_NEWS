from .models import NewsArticle

def categories_processor(request):
    categories = [cat[0] for cat in NewsArticle.categories]
    return {'categories':categories}

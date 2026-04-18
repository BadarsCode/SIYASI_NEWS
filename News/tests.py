import io
import tempfile

from PIL import Image

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings

from News.models import NewsArticle


@override_settings(ALLOWED_HOSTS=["testserver", "localhost", "127.0.0.1"])
class NewsArticleAdminTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="password123",
        )
        self.client.force_login(self.user)
        self.temp_media = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_media.cleanup)
        self.media_override = override_settings(MEDIA_ROOT=self.temp_media.name)
        self.media_override.enable()
        self.addCleanup(self.media_override.disable)

    def _make_test_image(self):
        image = Image.new("RGB", (20, 20), "red")
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        return SimpleUploadedFile("article.png", buffer.getvalue(), content_type="image/png")

    def test_admin_can_create_article_with_image(self):
        response = self.client.post(
            "/control-panel/News/newsarticle/add/",
            {
                "title": "Admin upload test",
                "content": "Article body",
                "category": "Politics",
                "images": self._make_test_image(),
            },
        )

        self.assertEqual(response.status_code, 302)
        article = NewsArticle.objects.get(title="Admin upload test")
        self.assertTrue(article.images.name.startswith("news_images/"))

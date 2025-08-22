document.addEventListener('DOMContentLoaded', function () {
  // Console check
  console.log('Siyasi News loaded');

  // Cookie banner logic (simple)
  const banner = document.getElementById('cookie-banner');
  const accepted = localStorage.getItem('cookieConsent');
  if (banner && !accepted) {
    banner.hidden = false;
    document.getElementById('cookie-accept').onclick = () => {
      localStorage.setItem('cookieConsent', 'accepted');
      banner.hidden = true;
    };
    document.getElementById('cookie-decline').onclick = () => {
      localStorage.setItem('cookieConsent', 'declined');
      banner.hidden = true;
    };
  }

  // AJAX load on left list click
  const list = document.getElementById('news-list');
  if (list) {
    list.querySelectorAll('li').forEach(li => {
      li.addEventListener('click', () => {
        const id = li.getAttribute('data-id');
        list.querySelectorAll('li').forEach(x => x.classList.remove('active'));
        li.classList.add('active');

        fetch(`/article/ajax/${id}/`)
          .then(res => res.json())
          .then(data => {
            document.getElementById('article-content').innerHTML = data.html;
            window.scrollTo({ top: 0, behavior: 'smooth' });
          });
      });
    });
  }

  // Simple client-side search
  const search = document.getElementById('news-search');
  if (search) {
    search.addEventListener('input', function () {
      const q = this.value.toLowerCase().trim();
      list.querySelectorAll('li').forEach(li => {
        const txt = li.innerText.toLowerCase();
        li.style.display = txt.includes(q) ? '' : 'none';
      });
    });
  }
});

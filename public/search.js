const searchInput = document.getElementById('tool-search');
const cards = Array.from(document.querySelectorAll('.tool-card'));
const emptyState = document.getElementById('no-results');

function normalize(text) {
  return String(text || '').trim().toLowerCase();
}

function filterTools(query) {
  const normalizedQuery = normalize(query);
  let visibleCount = 0;

  cards.forEach(card => {
    const title = normalize(card.dataset.title);
    const description = normalize(card.dataset.description);
    const match = normalizedQuery === '' || title.includes(normalizedQuery) || description.includes(normalizedQuery);
    card.style.display = match ? '' : 'none';
    if (match) visibleCount += 1;
  });

  emptyState.style.display = visibleCount === 0 ? 'block' : 'none';
}

function updateQueryString(query) {
  const url = new URL(window.location.href);
  if (query) {
    url.searchParams.set('q', query);
  } else {
    url.searchParams.delete('q');
  }
  history.replaceState(null, '', url.toString());
}

searchInput.addEventListener('input', event => {
  const query = event.target.value;
  filterTools(query);
  updateQueryString(query);
});

window.addEventListener('DOMContentLoaded', () => {
  const params = new URLSearchParams(window.location.search);
  const query = params.get('q') || '';
  if (query) {
    searchInput.value = query;
    filterTools(query);
  }
});

function getStore(key) {
  try {
    return JSON.parse(localStorage.getItem(key) || "[]");
  } catch (error) {
    return [];
  }
}

function setStore(key, value) {
  localStorage.setItem(key, JSON.stringify(value));
}

function normalizeStoreItems(rawItems) {
  if (!Array.isArray(rawItems)) return [];

  const normalized = rawItems
    .map((item) => {
      if (!item || typeof item !== "object") return null;
      const slug = String(item.slug || item.url || "").trim();
      if (!slug) return null;
      const name = String(item.name || slug).trim() || slug;
      return { slug, name };
    })
    .filter(Boolean);

  const seen = new Set();
  return normalized.filter((item) => {
    if (seen.has(item.slug)) return false;
    seen.add(item.slug);
    return true;
  });
}

window.catalogUi = function catalogUi() {
  const initialFavorites = normalizeStoreItems(getStore("algos:favorites")).slice(0, 30);
  const initialRecents = normalizeStoreItems(getStore("algos:recent")).slice(0, 20);
  setStore("algos:favorites", initialFavorites);
  setStore("algos:recent", initialRecents);

  return {
    viewMode: localStorage.getItem("view-algos") || "grid",
    favorites: initialFavorites,
    recents: initialRecents,

    setView(mode) {
      this.viewMode = mode;
      localStorage.setItem("view-algos", mode);
    },

    isFavorite(slug) {
      if (!slug) return false;
      return this.favorites.some((item) => item.slug === slug);
    },

    toggleFavorite(slug, name) {
      if (!slug) return;
      const exists = this.isFavorite(slug);
      if (exists) {
        this.favorites = this.favorites.filter((item) => item.slug !== slug);
      } else {
        this.favorites.unshift({ slug: slug, name: name || slug });
      }
      this.favorites = this.favorites.slice(0, 30);
      setStore("algos:favorites", this.favorites);
    },

    addRecent(slug, name) {
      if (!slug) return;
      this.recents = this.recents.filter((item) => item.slug !== slug);
      this.recents.unshift({ slug: slug, name: name || slug });
      this.recents = this.recents.slice(0, 20);
      setStore("algos:recent", this.recents);
    },

    renderFavorites() {
      if (!this.favorites.length) return "<p class='text-slate-400'>No favorites yet.</p>";
      return this.favorites
        .filter((item) => item && item.slug)
        .map((item) => `<a href='/algo/${item.slug}' class='block rounded-lg border border-slate-200 px-3 py-2'>${item.name}</a>`)
        .join("");
    },

    renderRecents() {
      if (!this.recents.length) return "<p class='text-slate-400'>No recent calculators.</p>";
      return this.recents
        .filter((item) => item && item.slug)
        .map((item) => `<a href='/algo/${item.slug}' class='block rounded-lg border border-slate-200 px-3 py-2'>${item.name}</a>`)
        .join("");
    },
  };
};

window.applyVariableMetadata = function applyVariableMetadata(payload) {
  if (!Array.isArray(payload)) return;
  payload.forEach((entry) => {
    const key = (entry.variable_name || entry.variable_notation || "").toString().toLowerCase();
    if (!key) return;

    const input = document.querySelector(`#input-${key}`) || document.querySelector(`input[name='${key}']`);
    if (!input) return;

    if (entry.variable_name) {
      const label = input.closest("label");
      if (label) {
        label.childNodes[0].textContent = `${entry.variable_name} `;
      }
    }

    if (entry.placeholder) {
      input.placeholder = entry.placeholder;
    }

    const hintNode = document.querySelector(`.meta-hint[data-key='${key}']`);
    if (hintNode) {
      const bits = [entry.type, entry.constraint].filter(Boolean);
      hintNode.textContent = bits.join(" | ");
    }
  });
};

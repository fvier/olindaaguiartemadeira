(() => {
  const search = document.getElementById('blogSearchInput');
  if (!search) return;
  const items = [...document.querySelectorAll('.blog-article-item')];
  const buttons = [...document.querySelectorAll('[data-category].blog-nav-tab')];
  const normalize = value => value.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLocaleLowerCase('pt-BR');
  let category = 'all';
  function apply(save = true) {
    const term = normalize(search.value.trim());
    let count = 0;
    items.forEach(item => {
      const visible = (category === 'all' || item.dataset.category === category) && normalize(`${item.dataset.title} ${item.dataset.category} ${item.dataset.search}`).includes(term);
      item.classList.toggle('d-none', !visible);
      if (visible) count++;
    });
    buttons.forEach(button => {
      const active = button.dataset.category === category;
      button.classList.toggle('active', active);
      button.setAttribute('aria-pressed', String(active));
    });
    document.querySelector('main').classList.toggle('blog-filtered', Boolean(term || category !== 'all'));
    document.getElementById('blogResultCount').textContent = `${count} ${count === 1 ? 'artigo encontrado' : 'artigos encontrados'}`;
    document.getElementById('blogEmptyMessage').classList.toggle('d-none', count > 0);
    if (save) {
      const url = new URL(location.href);
      for (const [key, value] of [['q', search.value.trim()], ['categoria', category === 'all' ? '' : category]]) {
        value ? url.searchParams.set(key, value) : url.searchParams.delete(key);
      }
      history.replaceState(null, '', url);
    }
  }
  function restore() {
    const params = new URLSearchParams(location.search);
    search.value = params.get('q') || '';
    category = buttons.some(b => b.dataset.category === params.get('categoria')) ? params.get('categoria') : 'all';
    apply(false);
  }
  buttons.forEach(button => button.addEventListener('click', () => { category = button.dataset.category; apply(); }));
  search.addEventListener('input', () => apply());
  document.getElementById('clearBlogFilters').addEventListener('click', () => { search.value = ''; category = 'all'; apply(); search.focus(); });
  window.addEventListener('popstate', restore);
  restore();
})();

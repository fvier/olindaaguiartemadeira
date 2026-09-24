/**
 * Catálogo Interativo — Olinda Arte em Madeira
 * Baseado na estrutura da loja de referência com adaptações para madeira de demolição
 */

(() => {
  const grid = document.getElementById('storeProductGrid');
  if (!grid) return;

  const cards = [...grid.querySelectorAll('.store-product-card')];
  const search = document.getElementById('storeSearch');
  const sort = document.getElementById('storeSort');
  const count = document.getElementById('visibleProductCount');
  const activeLabel = document.getElementById('activeStoreFilter');
  const empty = document.getElementById('storeEmpty');
  const interestCount = document.getElementById('interestCount');
  const storageKey = 'olinda-woodwork-store-interest';
  
  let interests = new Set();
  try {
    const saved = JSON.parse(localStorage.getItem(storageKey) || '[]');
    if (Array.isArray(saved)) interests = new Set(saved);
  } catch (_) { /* Fallback */ }

  const productFor = card => JSON.parse(card.dataset.json);
  const money = value => `R$ ${Number(value).toFixed(2).replace('.', ',')}`;

  // -------------------------------------------------------------
  // 1. FILTRAGEM & ORDENAÇÃO
  // -------------------------------------------------------------
  function selectedValue(name) {
    return document.querySelector(`input[name="${name}"]:checked`)?.value || 'all';
  }

  function matchesPrice(price, range) {
    if (range === 'all') return true;
    const [min, max] = range.split('-').map(Number);
    return price >= min && price < max;
  }

  function applyFilters() {
    const wood = selectedValue('wood');
    const price = selectedValue('price');
    const term = search ? search.value.trim().toLocaleLowerCase('pt-BR') : '';
    const categories = new Set([...document.querySelectorAll('.category-filter:checked')].map(input => input.value));

    const visible = cards.filter(card => {
      const searchable = `${card.dataset.name} ${card.dataset.category} ${card.dataset.wood}`.toLocaleLowerCase('pt-BR');
      const show = (wood === 'all' || card.dataset.wood === wood)
        && (!categories.size || categories.has(card.dataset.category))
        && matchesPrice(Number(card.dataset.price), price)
        && (!term || searchable.includes(term));
      card.classList.toggle('hidden', !show);
      return show;
    });

    const comparator = {
      name: (a, b) => a.dataset.name.localeCompare(b.dataset.name, 'pt-BR'),
      'price-asc': (a, b) => Number(a.dataset.price) - Number(b.dataset.price),
      'price-desc': (a, b) => Number(b.dataset.price) - Number(a.dataset.price),
      featured: (a, b) => cards.indexOf(a) - cards.indexOf(b)
    }[sort ? sort.value : 'featured'];

    visible.sort(comparator).forEach(card => grid.appendChild(card));

    if (count) count.textContent = visible.length;
    if (empty) empty.classList.toggle('hidden', visible.length !== 0);

    const labels = [];
    const woodNames = {
      'peroba-rosa': 'Peroba Rosa Centenária',
      'jacaranda': 'Jacarandá da Bahia',
      'cumaru': 'Cumaru de Demolição',
      'brauna': 'Braúna Centenária',
      'canela-preta': 'Canela Preta'
    };
    if (wood !== 'all') labels.push(woodNames[wood] || wood);
    if (categories.size) labels.push([...categories].join(', '));
    if (price !== 'all') labels.push('faixa de investimento');
    if (term) labels.push(`busca: “${search.value.trim()}”`);
    if (activeLabel) activeLabel.textContent = labels.length ? labels.join(' • ') : 'Todas as madeiras e categorias';
  }

  function updateInterestButtons() {
    document.querySelectorAll('[data-interest]').forEach(button => {
      const active = interests.has(button.dataset.interest);
      button.classList.toggle('active', active);
      button.setAttribute('aria-pressed', String(active));
    });
    if (interestCount) interestCount.textContent = interests.size;
    try { localStorage.setItem(storageKey, JSON.stringify([...interests])); } catch (_) { /* Fallback */ }
  }

  // -------------------------------------------------------------
  // 2. SELEÇÃO DE ACABAMENTO / TONALIDADE DO CARD
  // -------------------------------------------------------------
  function activateColor(card, colorId) {
    const product = productFor(card);
    const color = product.colors?.find(item => item.id === colorId) || product.colors?.[0];
    const variant = color || product;

    card.dataset.selectedColor = color?.id || '';
    card.dataset.price = variant.price ?? product.price;

    card.querySelectorAll('.store-swatch-dot').forEach(swatch => {
      const active = swatch.dataset.colorId === color?.id;
      swatch.classList.toggle('active', active);
      swatch.setAttribute('aria-pressed', String(active));
    });

    const priceEl = card.querySelector('.card-price');
    const oldPriceEl = card.querySelector('.card-old-price');
    if (priceEl) priceEl.textContent = money(variant.price ?? product.price);
    const oldPrice = variant.old_price ?? product.old_price;
    if (oldPriceEl) oldPriceEl.textContent = oldPrice ? money(oldPrice) : '';

    const badge = card.querySelector('.card-badge-element');
    if (badge) badge.textContent = variant.badge ?? product.badge ?? '';

    return color;
  }

  cards.forEach(card => {
    activateColor(card, card.querySelector('.store-swatch-dot.active')?.dataset.colorId);
    card.querySelectorAll('.store-swatch-dot').forEach(swatch => {
      swatch.addEventListener('click', event => {
        event.stopPropagation();
        activateColor(card, swatch.dataset.colorId);
        applyFilters();
      });
    });
  });

  // -------------------------------------------------------------
  // 3. MODAL DE VISUALIZAÇÃO RÁPIDA (QUICK-VIEW)
  // -------------------------------------------------------------
  const modal = document.getElementById('storeProductModal');
  const closeModalBtn = document.getElementById('closeProductModal');
  const modalTitle = document.getElementById('modalTitle');
  const modalWoodTag = document.getElementById('modalWoodTag');
  const modalCategoryTag = document.getElementById('modalCategoryTag');
  const modalMainImg = document.getElementById('modalMainImg');
  const modalBadge = document.getElementById('modalProductBadge');
  const modalPrice = document.getElementById('modalPrice');
  const modalOldPrice = document.getElementById('modalOldPrice');
  const modalDescription = document.getElementById('modalDescription');
  const modalColorBlock = document.getElementById('modalColorBlock');
  const modalColorPills = document.getElementById('modalColorPills');
  const modalSelectedColorText = document.getElementById('modalSelectedColorText');
  const modalSizeBlock = document.getElementById('modalSizeBlock');
  const modalSizePills = document.getElementById('modalSizePills');
  const modalSelectedSizeText = document.getElementById('modalSelectedSizeText');
  const modalZapLink = document.getElementById('modalZapLink');
  const modalInterestBtn = document.getElementById('modalInterestBtn');
  const modalInterestLabel = document.getElementById('modalInterestLabel');

  let currentProduct = null;
  let selectedColor = null;
  let selectedSize = null;
  let currentCard = null;
  let bodyOverflow = '';

  function updateZapLink() {
    if (!currentProduct || !modalZapLink) return;
    const phone = '5581994522504'; // WhatsApp oficial Olinda Aguiar
    const finishStr = selectedColor ? ` (Acabamento: ${selectedColor.name})` : '';
    const sizeStr = selectedSize ? ` (Dimensões: ${selectedSize})` : '';
    const text = encodeURIComponent(`Olá Olinda! Gostaria de consultar detalhes da peça *${currentProduct.name}* [Código: ${currentProduct.id}]${finishStr}${sizeStr} vista na Loja Virtual.`);
    modalZapLink.href = `https://api.whatsapp.com/send?phone=${phone}&text=${text}`;
  }

  function openModalForProduct(card) {
    if (!card.dataset.json || !modal) return;
    try {
      currentProduct = JSON.parse(card.dataset.json);
    } catch (e) {
      return;
    }
    currentCard = card;

    const woodNames = {
      'peroba-rosa': 'Peroba Rosa Centenária',
      'jacaranda': 'Jacarandá da Bahia',
      'cumaru': 'Cumaru de Demolição',
      'brauna': 'Braúna Centenária',
      'canela-preta': 'Canela Preta'
    };

    if (modalWoodTag) modalWoodTag.textContent = woodNames[currentProduct.wood_type] || currentProduct.wood_type;
    if (modalCategoryTag) modalCategoryTag.textContent = currentProduct.category || '';
    if (modalTitle) modalTitle.textContent = currentProduct.name || '';
    if (modalDescription) modalDescription.textContent = currentProduct.description || '';
    if (modalBadge) modalBadge.textContent = currentProduct.badge || 'Peça Única';

    if (modalPrice) modalPrice.textContent = money(currentProduct.price);
    if (modalOldPrice) {
      modalOldPrice.textContent = currentProduct.old_price ? money(currentProduct.old_price) : '';
    }

    // Imagem ou ícone
    if (modalMainImg) {
      if (currentProduct.image) {
        modalMainImg.src = `/static/images/${currentProduct.image}`;
        modalMainImg.alt = currentProduct.name;
        modalMainImg.style.display = 'block';
      } else {
        modalMainImg.style.display = 'none';
      }
    }

    // Pílulas de Acabamento
    if (modalColorPills && modalColorBlock) {
      modalColorPills.innerHTML = '';
      if (currentProduct.colors && currentProduct.colors.length > 0) {
        modalColorBlock.classList.remove('hidden');
        selectedColor = currentProduct.colors.find(col => col.id === card.dataset.selectedColor) || currentProduct.colors[0];
        if (modalSelectedColorText) modalSelectedColorText.textContent = selectedColor.name;

        currentProduct.colors.forEach(col => {
          const pill = document.createElement('button');
          pill.type = 'button';
          pill.className = `modal-pill-btn ${col.id === selectedColor.id ? 'active' : ''}`;
          pill.dataset.colorId = col.id;

          const dot = document.createElement('span');
          dot.className = 'modal-pill-color-dot';
          dot.style.backgroundColor = col.hex;

          pill.append(dot, document.createTextNode(` ${col.name}`));
          pill.addEventListener('click', () => {
            modalColorPills.querySelectorAll('.modal-pill-btn').forEach(p => p.classList.remove('active'));
            pill.classList.add('active');
            selectedColor = col;
            activateColor(card, col.id);
            if (modalSelectedColorText) modalSelectedColorText.textContent = col.name;
            if (modalPrice) modalPrice.textContent = money(col.price ?? currentProduct.price);
            if (modalOldPrice) {
              modalOldPrice.textContent = (col.old_price ?? currentProduct.old_price) ? money(col.old_price ?? currentProduct.old_price) : '';
            }
            updateZapLink();
          });
          modalColorPills.appendChild(pill);
        });
      } else {
        modalColorBlock.classList.add('hidden');
        selectedColor = null;
      }
    }

    // Pílulas de Dimensões
    if (modalSizePills && modalSizeBlock) {
      modalSizePills.innerHTML = '';
      if (currentProduct.sizes && currentProduct.sizes.length > 0) {
        modalSizeBlock.classList.remove('hidden');
        selectedSize = currentProduct.sizes[0];
        if (modalSelectedSizeText) modalSelectedSizeText.textContent = selectedSize;

        currentProduct.sizes.forEach((sz, idx) => {
          const szPill = document.createElement('button');
          szPill.type = 'button';
          szPill.className = `modal-pill-btn ${idx === 0 ? 'active' : ''}`;
          szPill.textContent = sz;
          szPill.addEventListener('click', () => {
            modalSizePills.querySelectorAll('.modal-pill-btn').forEach(p => p.classList.remove('active'));
            szPill.classList.add('active');
            selectedSize = sz;
            if (modalSelectedSizeText) modalSelectedSizeText.textContent = sz;
            updateZapLink();
          });
          modalSizePills.appendChild(szPill);
        });
      } else {
        modalSizeBlock.classList.add('hidden');
        selectedSize = null;
      }
    }

    // Atualiza estado do botão de interesse
    if (modalInterestBtn) {
      modalInterestBtn.dataset.interest = currentProduct.id;
      const isInterested = interests.has(currentProduct.id);
      if (modalInterestLabel) modalInterestLabel.textContent = isInterested ? 'Salvo na Lista' : 'Salvar no Interesse';
      modalInterestBtn.classList.toggle('active', isInterested);
    }

    updateZapLink();
    updateInterestButtons();
    modal.classList.remove('hidden');
    bodyOverflow = document.body.style.overflow;
    document.body.style.overflow = 'hidden';
    modal.scrollTop = 0;
  }

  function closeModal() {
    if (!modal) return;
    modal.classList.add('hidden');
    document.body.style.overflow = bodyOverflow;
    applyFilters();
  }

  // Delegação de cliques para abrir modal
  document.addEventListener('click', e => {
    if (e.target.closest('[data-interest], [data-share-product]')) return;
    const trigger = e.target.closest('[data-open-modal]');
    if (trigger) {
      const card = trigger.closest('.store-product-card');
      if (card) openModalForProduct(card);
    }
  });

  if (closeModalBtn) closeModalBtn.addEventListener('click', closeModal);
  if (modal) {
    modal.addEventListener('click', e => {
      if (e.target === modal) closeModal();
    });
    document.addEventListener('keydown', e => {
      if (e.key === 'Escape' && !modal.classList.contains('hidden')) closeModal();
    });
  }

  if (modalInterestBtn) {
    modalInterestBtn.addEventListener('click', () => {
      if (!currentProduct) return;
      const id = currentProduct.id;
      interests.has(id) ? interests.delete(id) : interests.add(id);
      updateInterestButtons();
      const isInterested = interests.has(id);
      if (modalInterestLabel) modalInterestLabel.textContent = isInterested ? 'Salvo na Lista' : 'Salvar no Interesse';
      modalInterestBtn.classList.toggle('active', isInterested);
    });
  }

  // -------------------------------------------------------------
  // 4. EVENTOS DE FILTROS & AÇÕES
  // -------------------------------------------------------------
  document.querySelectorAll('input[name="wood"], input[name="price"], .category-filter').forEach(input => {
    input.addEventListener('change', applyFilters);
  });
  if (search) search.addEventListener('input', applyFilters);
  if (sort) sort.addEventListener('change', applyFilters);

  document.querySelectorAll('[data-quick-filter]').forEach(button => {
    button.addEventListener('click', () => {
      const val = button.dataset.quickFilter;
      const input = document.querySelector(`input[name="wood"][value="${val}"]`);
      if (input) {
        input.checked = true;
        document.querySelector('.store-layout')?.scrollIntoView({behavior: 'smooth'});
        applyFilters();
      }
    });
  });

  grid.querySelectorAll('[data-interest]').forEach(button => {
    button.addEventListener('click', e => {
      e.stopPropagation();
      const id = button.dataset.interest;
      interests.has(id) ? interests.delete(id) : interests.add(id);
      updateInterestButtons();
    });
  });

  const clearBtn = document.getElementById('clearStoreFilters');
  if (clearBtn) {
    clearBtn.addEventListener('click', () => {
      const woodAll = document.querySelector('input[name="wood"][value="all"]');
      const priceAll = document.querySelector('input[name="price"][value="all"]');
      if (woodAll) woodAll.checked = true;
      if (priceAll) priceAll.checked = true;
      document.querySelectorAll('.category-filter').forEach(input => { input.checked = false; });
      if (search) search.value = '';
      if (sort) sort.value = 'featured';
      applyFilters();
    });
  }

  const filterPanel = document.querySelector('.store-filter-panel');
  const mobileFilterToggle = document.getElementById('storeMobileFilterToggle');
  if (filterPanel && mobileFilterToggle) {
    if (window.matchMedia('(max-width: 800px)').matches) filterPanel.classList.add('filters-collapsed');
    mobileFilterToggle.addEventListener('click', () => {
      const collapsed = filterPanel.classList.toggle('filters-collapsed');
      mobileFilterToggle.textContent = collapsed ? 'Abrir' : 'Fechar';
    });
  }

  // -------------------------------------------------------------
  // 5. COMPARTILHAMENTO DE PRODUTO (URL & NATIVE SHARE)
  // -------------------------------------------------------------
  async function shareProduct(card, button) {
    if (!card) return;
    const product = productFor(card);
    const color = product.colors?.find(item => item.id === card.dataset.selectedColor);
    const url = new URL('/loja', window.location.origin);
    url.searchParams.set('produto', product.id);
    if (color) url.searchParams.set('acabamento', color.id);

    const area = button.closest('.store-share-area');
    const status = area ? area.querySelector('.store-share-status') : null;
    const manual = area ? area.querySelector('.store-share-copy') : null;

    if (navigator.share) {
      try {
        await navigator.share({
          title: `${product.name} — Olinda Arte em Madeira`,
          text: `Confira esta peça única em madeira de demolição: ${product.name}`,
          url: url.href
        });
        return;
      } catch (err) {
        if (err.name === 'AbortError') return;
      }
    }

    // Fallback: Clipboard
    try {
      await navigator.clipboard.writeText(url.href);
      if (status) status.textContent = 'Link copiado! Cole para compartilhar.';
    } catch (_) {
      if (manual) {
        manual.classList.remove('hidden');
        const input = manual.querySelector('input');
        if (input) {
          input.value = url.href;
          input.focus();
          input.select();
        }
      }
    }
  }

  grid.querySelectorAll('[data-share-product]').forEach(button => {
    button.addEventListener('click', () => shareProduct(button.closest('.store-product-card'), button));
  });
  document.getElementById('modalShareBtn')?.addEventListener('click', event => {
    shareProduct(currentCard, event.currentTarget);
  });

  // Deep linking: abre produto solicitado na URL
  const requested = new URLSearchParams(window.location.search);
  const requestedId = requested.get('produto');
  if (requestedId) {
    const linkedCard = cards.find(card => card.dataset.id === requestedId);
    if (linkedCard) {
      activateColor(linkedCard, requested.get('acabamento'));
      linkedCard.scrollIntoView({block: 'center'});
      openModalForProduct(linkedCard);
    }
  }

  // -------------------------------------------------------------
  // 6. MODAL DA LISTA DE DESEJOS / INTERESSES
  // -------------------------------------------------------------
  const wishlistModal = document.getElementById('storeWishlistModal');
  const openWishlistBtn = document.getElementById('openWishlistBtn');
  const closeWishlistBtn = document.getElementById('closeWishlistBtn');
  const wishlistContainer = document.getElementById('wishlistContainer');
  const sendWishlistZapBtn = document.getElementById('sendWishlistZapBtn');

  function openWishlist() {
    if (!wishlistModal || !wishlistContainer) return;
    wishlistContainer.innerHTML = '';

    if (interests.size === 0) {
      wishlistContainer.innerHTML = `
        <div class="text-center py-4 text-muted">
          <i class="ri-heart-line fs-32 text-secondary d-block mb-2"></i>
          <p>Sua lista de interesses está vazia no momento.<br>Clique no coração das peças que você mais gostar!</p>
        </div>
      `;
      if (sendWishlistZapBtn) sendWishlistZapBtn.style.display = 'none';
    } else {
      let messageLines = ['Olá Olinda! Tenho interesse nas seguintes peças do ateliê:'];
      interests.forEach(id => {
        const card = cards.find(c => c.dataset.id === id);
        if (card) {
          const prod = productFor(card);
          messageLines.push(`- *${prod.name}* [${prod.id}] - ${money(prod.price)}`);
          const item = document.createElement('div');
          item.className = 'wishlist-item';
          item.innerHTML = `
            ${prod.image ? `<img src="/static/images/${prod.image}" alt="${prod.name}">` : `<div class="wishlist-item-icon">${prod.icon || '🪵'}</div>`}
            <div class="flex-grow-1">
              <strong class="d-block text-dark">${prod.name}</strong>
              <small class="text-secondary">${prod.category} • ${money(prod.price)}</small>
            </div>
            <button type="button" class="btn btn-sm btn-outline-danger rounded-circle p-1" data-remove-wishlist="${prod.id}" title="Remover">
              <i class="ri-delete-bin-line"></i>
            </button>
          `;
          wishlistContainer.appendChild(item);
        }
      });

      if (sendWishlistZapBtn) {
        sendWishlistZapBtn.style.display = 'inline-flex';
        const zapText = encodeURIComponent(messageLines.join('\n'));
        sendWishlistZapBtn.href = `https://api.whatsapp.com/send?phone=5581994522504&text=${zapText}`;
      }

      wishlistContainer.querySelectorAll('[data-remove-wishlist]').forEach(btn => {
        btn.addEventListener('click', () => {
          const id = btn.dataset.removeWishlist;
          interests.delete(id);
          updateInterestButtons();
          openWishlist();
        });
      });
    }

    wishlistModal.classList.remove('hidden');
    document.body.style.overflow = 'hidden';
  }

  function closeWishlist() {
    if (!wishlistModal) return;
    wishlistModal.classList.add('hidden');
    document.body.style.overflow = '';
  }

  if (openWishlistBtn) openWishlistBtn.addEventListener('click', openWishlist);
  if (interestCount) interestCount.closest('div')?.addEventListener('click', openWishlist);
  if (closeWishlistBtn) closeWishlistBtn.addEventListener('click', closeWishlist);
  if (wishlistModal) {
    wishlistModal.addEventListener('click', e => {
      if (e.target === wishlistModal) closeWishlist();
    });
  }

  updateInterestButtons();
  applyFilters();
})();

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

  // Elementos do Slider de Preço (Slace de Preço)
  const priceSlider = document.getElementById('storePriceSlider');
  const priceSliderDisplay = document.getElementById('priceSliderDisplay');
  const priceSliderBadge = document.getElementById('priceSliderBadge');
  const priceChips = [...document.querySelectorAll('.store-chip-btn')];
  const maxPriceCeiling = 10000;

  // Elementos do Mar de Tags
  const tagPills = [...document.querySelectorAll('.store-tag-pill')];
  const tagGroupBtns = [...document.querySelectorAll('.store-tag-group-btn')];
  const clearTagBtn = document.getElementById('clearTagSelectionBtn');
  const activeTagIndicator = document.getElementById('activeTagPillIndicator');
  let activeTag = null;
  
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

  function matchesPrice(price) {
    if (!priceSlider) return true;
    const maxVal = Number(priceSlider.value);
    if (isNaN(maxVal) || maxVal >= maxPriceCeiling) return true;
    return price <= maxVal;
  }

  function applyFilters() {
    const wood = selectedValue('wood');
    const term = search ? search.value.trim().toLocaleLowerCase('pt-BR') : '';
    const categories = new Set([...document.querySelectorAll('.category-filter:checked')].map(input => input.value));

    const visible = cards.filter(card => {
      const cardTags = (card.dataset.tags || '').split(',').map(t => t.trim().toLowerCase()).filter(Boolean);
      const searchable = `${card.dataset.name} ${card.dataset.category} ${card.dataset.wood} ${(card.dataset.tags || '').replace(/,/g, ' ')}`.toLocaleLowerCase('pt-BR');
      const matchesTag = !activeTag || cardTags.includes(activeTag.toLowerCase());
      const show = (wood === 'all' || card.dataset.wood === wood)
        && (!categories.size || categories.has(card.dataset.category))
        && matchesPrice(Number(card.dataset.price))
        && matchesTag
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

    // Atualiza estado visual das pílulas no Mar de Tags
    tagPills.forEach(pill => {
      const isActive = Boolean(activeTag && pill.dataset.tagSlug?.toLowerCase() === activeTag.toLowerCase());
      pill.classList.toggle('is-active', isActive);
      pill.setAttribute('aria-pressed', String(isActive));
    });

    if (activeTagIndicator) {
      if (activeTag) {
        const found = tagPills.find(p => p.dataset.tagSlug?.toLowerCase() === activeTag.toLowerCase());
        const tagName = found ? found.dataset.tagName : activeTag.replace(/-/g, ' ');
        activeTagIndicator.innerHTML = `<span>Tag: #${tagName}</span>`;
        activeTagIndicator.style.display = 'inline-flex';
      } else {
        activeTagIndicator.style.display = 'none';
      }
    }

    if (clearTagBtn) {
      clearTagBtn.style.display = activeTag ? 'inline-flex' : 'none';
    }

    const labels = [];
    const woodNames = {
      'peroba-rosa': 'Peroba Rosa Centenária',
      'jacaranda': 'Jacarandá da Bahia',
      'cumaru': 'Cumaru de Demolição',
      'brauna': 'Braúna Centenária',
      'canela-preta': 'Canela Preta',
      'jatoba': 'Jatobá de Demolição'
    };
    if (wood !== 'all') labels.push(woodNames[wood] || wood);
    if (categories.size) labels.push([...categories].join(', '));
    if (priceSlider && Number(priceSlider.value) < maxPriceCeiling) {
      labels.push(`investimento: até ${money(priceSlider.value)}`);
    }
    if (activeTag) {
      const found = tagPills.find(p => p.dataset.tagSlug?.toLowerCase() === activeTag.toLowerCase());
      const tagName = found ? found.dataset.tagName : activeTag.replace(/-/g, ' ');
      labels.push(`tag: #${tagName}`);
    }
    if (term) labels.push(`busca: “${search.value.trim()}”`);
    if (activeLabel) activeLabel.textContent = labels.length ? labels.join(' • ') : 'Todas as madeiras e categorias';
  }

  function setActiveTag(slug, shouldScroll = false) {
    if (activeTag && slug && activeTag.toLowerCase() === slug.toLowerCase()) {
      activeTag = null;
    } else {
      activeTag = slug || null;
    }
    applyFilters();
    if (shouldScroll && activeTag) {
      const target = document.querySelector('.store-layout') || grid;
      target?.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
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
  // 2. SELEÇÃO DE ACABAMENTO & CARROSSEL DO CARD
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

    // Carrossel de fotos no card
    const prod = productFor(card);
    const prodImages = prod.images && prod.images.length > 0 ? prod.images : (prod.image ? [prod.image] : []);
    if (prodImages.length > 1) {
      let cardImgIdx = 0;
      const cardImgEl = card.querySelector('.card-img-element');
      const dots = card.querySelectorAll('.store-carousel-dot');

      const setCardImage = (idx) => {
        cardImgIdx = (idx + prodImages.length) % prodImages.length;
        if (cardImgEl) cardImgEl.src = `/static/images/${prodImages[cardImgIdx]}`;
        dots.forEach((dot, i) => {
          dot.classList.toggle('active', i === cardImgIdx);
        });
      };

      const prevBtn = card.querySelector('.store-carousel-btn.prev');
      const nextBtn = card.querySelector('.store-carousel-btn.next');
      if (prevBtn) {
        prevBtn.addEventListener('click', (e) => {
          e.stopPropagation();
          setCardImage(cardImgIdx - 1);
        });
      }
      if (nextBtn) {
        nextBtn.addEventListener('click', (e) => {
          e.stopPropagation();
          setCardImage(cardImgIdx + 1);
        });
      }
      dots.forEach((dot, i) => {
        dot.addEventListener('click', (e) => {
          e.stopPropagation();
          setCardImage(i);
        });
      });
    }
  });

  // -------------------------------------------------------------
  // 3. MODAL DE VISUALIZAÇÃO RÁPIDA (QUICK-VIEW COM CARROSSEL)
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
  const modalCarouselNav = document.getElementById('modalCarouselNav');
  const modalThumbsRow = document.getElementById('modalThumbsRow');
  const modalPrevImgBtn = document.getElementById('modalPrevImgBtn');
  const modalNextImgBtn = document.getElementById('modalNextImgBtn');
  const modalTagsBlock = document.getElementById('modalTagsBlock');
  const modalTagsRow = document.getElementById('modalTagsRow');

  let currentProduct = null;
  let selectedColor = null;
  let selectedSize = null;
  let currentCard = null;
  let bodyOverflow = '';
  let modalImgIdx = 0;

  function updateZapLink() {
    if (!currentProduct || !modalZapLink) return;
    const phone = '5581994522504'; // WhatsApp oficial Olinda Aguiar
    const finishStr = selectedColor ? ` (Acabamento: ${selectedColor.name})` : '';
    const sizeStr = selectedSize ? ` (Dimensões: ${selectedSize})` : '';
    const text = encodeURIComponent(`Olá Olinda! Gostaria de consultar detalhes da peça *${currentProduct.name}* [Código: ${currentProduct.id}]${finishStr}${sizeStr} vista na Loja Virtual.`);
    modalZapLink.href = `https://api.whatsapp.com/send?phone=${phone}&text=${text}`;
  }

  function setModalImage(idx, modalImages) {
    if (!modalImages || !modalImages.length) return;
    modalImgIdx = (idx + modalImages.length) % modalImages.length;
    if (modalMainImg) {
      modalMainImg.src = `/static/images/${modalImages[modalImgIdx]}`;
      modalMainImg.alt = `${currentProduct.name} - Foto ${modalImgIdx + 1}`;
    }
    if (modalThumbsRow) {
      modalThumbsRow.querySelectorAll('.modal-thumb-btn').forEach((btn, i) => {
        btn.classList.toggle('active', i === modalImgIdx);
      });
    }
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
      'canela-preta': 'Canela Preta',
      'jatoba': 'Jatobá de Demolição'
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

    // Carrossel e Galeria do Modal
    const modalImages = currentProduct.images && currentProduct.images.length > 0 
      ? currentProduct.images 
      : (currentProduct.image ? [currentProduct.image] : []);

    modalImgIdx = 0;
    if (modalImages.length > 0) {
      setModalImage(0, modalImages);
      if (modalMainImg) modalMainImg.style.display = 'block';
    } else {
      if (modalMainImg) modalMainImg.style.display = 'none';
    }

    if (modalCarouselNav) {
      modalCarouselNav.style.display = modalImages.length > 1 ? 'flex' : 'none';
    }

    if (modalThumbsRow) {
      modalThumbsRow.innerHTML = '';
      if (modalImages.length > 1) {
        modalImages.forEach((imgSrc, idx) => {
          const thumbBtn = document.createElement('button');
          thumbBtn.type = 'button';
          thumbBtn.className = `modal-thumb-btn ${idx === 0 ? 'active' : ''}`;
          thumbBtn.innerHTML = `<img src="/static/images/${imgSrc}" alt="${currentProduct.name} miniatura ${idx + 1}">`;
          thumbBtn.addEventListener('click', () => setModalImage(idx, modalImages));
          modalThumbsRow.appendChild(thumbBtn);
        });
      }
    }

    if (modalPrevImgBtn) {
      modalPrevImgBtn.onclick = () => setModalImage(modalImgIdx - 1, modalImages);
    }
    if (modalNextImgBtn) {
      modalNextImgBtn.onclick = () => setModalImage(modalImgIdx + 1, modalImages);
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

    // Tags da Peça no Modal Quick-View
    if (modalTagsBlock && modalTagsRow) {
      modalTagsRow.innerHTML = '';
      const prodTags = currentProduct.tags || [];
      if (prodTags.length > 0) {
        modalTagsBlock.style.display = 'block';
        prodTags.forEach(tagSlug => {
          const pill = document.querySelector(`.store-tag-pill[data-tag-slug="${tagSlug}"]`);
          const tagName = pill ? pill.dataset.tagName : tagSlug.replace(/-/g, ' ');
          const icon = pill ? pill.querySelector('.tag-emoji')?.textContent || '🏷️' : '🏷️';

          const tagBtn = document.createElement('button');
          tagBtn.type = 'button';
          tagBtn.className = 'modal-tag-pill';
          tagBtn.innerHTML = `<span>${icon}</span> <span>#${tagName}</span>`;
          tagBtn.title = `Filtrar catálogo por #${tagName}`;
          tagBtn.addEventListener('click', () => {
            closeModal();
            setActiveTag(tagSlug, true);
          });
          modalTagsRow.appendChild(tagBtn);
        });
      } else {
        modalTagsBlock.style.display = 'none';
      }
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

  // Delegação de cliques para abrir modal (ignora tags, compartilhamento e carrossel)
  document.addEventListener('click', e => {
    if (e.target.closest('[data-interest], [data-share-product], .store-card-carousel-nav, .store-card-carousel-dots, [data-card-tag], .store-card-tags')) return;
    const trigger = e.target.closest('[data-open-modal]');
    if (trigger) {
      const card = trigger.closest('.store-product-card');
      if (card) openModalForProduct(card);
    }
  });

  // Clique em mini-tag no card filtra o catálogo
  document.addEventListener('click', e => {
    const cardTagBtn = e.target.closest('[data-card-tag]');
    if (cardTagBtn) {
      e.stopPropagation();
      const slug = cardTagBtn.dataset.cardTag;
      setActiveTag(slug, true);
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
  function updateSliderVisuals(val) {
    if (!priceSlider) return;
    const min = Number(priceSlider.min) || 500;
    const max = Number(priceSlider.max) || maxPriceCeiling;
    const numericVal = Number(val);
    const pct = Math.max(0, Math.min(100, ((numericVal - min) / (max - min)) * 100));
    priceSlider.style.background = `linear-gradient(to right, #c85a17 0%, #c85a17 ${pct}%, #e2e8f0 ${pct}%, #e2e8f0 100%)`;

    if (numericVal >= max) {
      if (priceSliderDisplay) priceSliderDisplay.textContent = 'R$ 10.000+';
      if (priceSliderBadge) priceSliderBadge.textContent = 'Todos os valores';
    } else {
      if (priceSliderDisplay) priceSliderDisplay.textContent = money(numericVal);
      if (priceSliderBadge) priceSliderBadge.textContent = `Até ${money(numericVal)}`;
    }

    priceChips.forEach(btn => {
      const chipPrice = btn.dataset.chipPrice;
      const isCurrent = (chipPrice === 'all' && numericVal >= max) || Number(chipPrice) === numericVal;
      btn.classList.toggle('active', isCurrent);
    });
  }

  if (priceSlider) {
    updateSliderVisuals(priceSlider.value);
    priceSlider.addEventListener('input', () => {
      updateSliderVisuals(priceSlider.value);
      applyFilters();
    });
  }

  priceChips.forEach(btn => {
    btn.addEventListener('click', () => {
      if (!priceSlider) return;
      const chipPrice = btn.dataset.chipPrice;
      priceSlider.value = chipPrice === 'all' ? priceSlider.max : chipPrice;
      updateSliderVisuals(priceSlider.value);
      applyFilters();
    });
  });

  document.querySelectorAll('input[name="wood"], .category-filter').forEach(input => {
    input.addEventListener('change', applyFilters);
  });
  if (search) search.addEventListener('input', applyFilters);
  if (sort) sort.addEventListener('change', applyFilters);

  document.querySelectorAll('[data-quick-filter]').forEach(button => {
    button.addEventListener('click', () => {
      const val = button.dataset.quickFilter;
      document.querySelectorAll('[data-quick-filter]').forEach(b => b.classList.remove('active'));
      button.classList.add('active');
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

  // Eventos do Mar de Tags
  tagGroupBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      const grp = btn.dataset.groupFilter;
      tagGroupBtns.forEach(b => {
        const isCurrent = b === btn;
        b.classList.toggle('active', isCurrent);
        b.setAttribute('aria-selected', String(isCurrent));
      });
      tagPills.forEach(pill => {
        const matchesGroup = grp === 'all' || pill.dataset.tagGroup === grp;
        pill.style.display = matchesGroup ? 'inline-flex' : 'none';
      });
    });
  });

  tagPills.forEach(pill => {
    pill.addEventListener('click', () => {
      const slug = pill.dataset.tagSlug;
      setActiveTag(activeTag === slug ? null : slug, true);
    });
  });

  if (clearTagBtn) {
    clearTagBtn.addEventListener('click', () => {
      setActiveTag(null);
    });
  }

  const clearBtn = document.getElementById('clearStoreFilters');
  if (clearBtn) {
    clearBtn.addEventListener('click', () => {
      activeTag = null;
      if (priceSlider) {
        priceSlider.value = priceSlider.max;
        updateSliderVisuals(priceSlider.max);
      }
      const woodAll = document.querySelector('input[name="wood"][value="all"]');
      if (woodAll) woodAll.checked = true;
      document.querySelectorAll('.category-filter').forEach(input => { input.checked = false; });
      document.querySelectorAll('[data-quick-filter]').forEach(b => b.classList.remove('active'));
      document.querySelector('[data-quick-filter="all"]')?.classList.add('active');
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

  // Deep linking: abre produto solicitado na URL ou aplica filtro por tag
  const requested = new URLSearchParams(window.location.search);
  const requestedTag = requested.get('tag');
  if (requestedTag) {
    setActiveTag(requestedTag, false);
  }
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

  // -------------------------------------------------------------
  // ADMIN CARD EDITING MODAL & ACTIONS
  // -------------------------------------------------------------
  const adminEditModal = document.getElementById('adminProductEditModal');
  const closeAdminEditModalBtn = document.getElementById('closeAdminEditModal');
  const adminCancelEditBtn = document.getElementById('adminCancelEditBtn');
  const adminEditForm = document.getElementById('adminProductEditForm');
  const modalAdminEditTriggerBtn = document.getElementById('modalAdminEditTriggerBtn');

  function openAdminEditModal(productId) {
    if (!adminEditModal) return;
    const card = cards.find(c => c.dataset.id === productId);
    if (!card) return;
    const prod = productFor(card);

    const idInput = document.getElementById('adminEditProductId');
    const codeBadge = document.getElementById('adminEditProductCodeBadge');
    const nameInput = document.getElementById('adminEditName');
    const woodSelect = document.getElementById('adminEditWood');
    const catSelect = document.getElementById('adminEditCategory');
    const priceInput = document.getElementById('adminEditPrice');
    const oldPriceInput = document.getElementById('adminEditOldPrice');
    const badgeInput = document.getElementById('adminEditBadge');
    const soldSelect = document.getElementById('adminEditSoldOut');
    const sizesInput = document.getElementById('adminEditSizes');
    const tagsInput = document.getElementById('adminEditTags');
    const descInput = document.getElementById('adminEditDescription');
    const alertBox = document.getElementById('adminEditAlert');

    if (idInput) idInput.value = prod.id || '';
    if (codeBadge) codeBadge.textContent = prod.id || '';
    if (nameInput) nameInput.value = prod.name || '';
    if (woodSelect) woodSelect.value = prod.wood_type || '';
    if (catSelect) catSelect.value = prod.category || '';
    if (priceInput) priceInput.value = prod.price != null ? prod.price : '';
    if (oldPriceInput) oldPriceInput.value = prod.old_price != null ? prod.old_price : '';
    if (badgeInput) badgeInput.value = prod.badge || '';
    if (soldSelect) soldSelect.value = String(Boolean(prod.is_sold_out));
    if (sizesInput) sizesInput.value = (prod.sizes || []).join(', ');
    if (tagsInput) tagsInput.value = (prod.tags || []).join(', ');
    if (descInput) descInput.value = prod.description || '';

    if (alertBox) {
      alertBox.classList.add('d-none');
      alertBox.textContent = '';
    }

    if (modal && !modal.classList.contains('hidden')) {
      modal.classList.add('hidden');
    }

    adminEditModal.classList.remove('hidden');
    document.body.style.overflow = 'hidden';
  }

  function closeAdminEditModal() {
    if (!adminEditModal) return;
    adminEditModal.classList.add('hidden');
    document.body.style.overflow = '';
  }

  if (closeAdminEditModalBtn) closeAdminEditModalBtn.addEventListener('click', closeAdminEditModal);
  if (adminCancelEditBtn) adminCancelEditBtn.addEventListener('click', closeAdminEditModal);

  document.addEventListener('click', e => {
    const editBtn = e.target.closest('[data-admin-edit]');
    if (editBtn) {
      e.stopPropagation();
      e.preventDefault();
      const pId = editBtn.dataset.adminEdit;
      openAdminEditModal(pId);
      return;
    }

    if (adminEditModal && e.target === adminEditModal) {
      closeAdminEditModal();
    }
  });

  if (modalAdminEditTriggerBtn) {
    modalAdminEditTriggerBtn.addEventListener('click', () => {
      if (currentProduct) {
        openAdminEditModal(currentProduct.id);
      }
    });
  }

  window.salvarEdicaoProduto = async function(event) {
    if (event) event.preventDefault();
    if (!adminEditForm) return;

    const alertBox = document.getElementById('adminEditAlert');
    const saveBtn = document.getElementById('adminSaveBtn');
    const saveBtnText = document.getElementById('adminSaveBtnText');
    const originalText = saveBtnText ? saveBtnText.textContent : 'Salvar Alterações';

    const pId = document.getElementById('adminEditProductId').value;
    const payload = {
      id: pId,
      name: document.getElementById('adminEditName').value,
      wood_type: document.getElementById('adminEditWood').value,
      category: document.getElementById('adminEditCategory').value,
      price: document.getElementById('adminEditPrice').value,
      old_price: document.getElementById('adminEditOldPrice').value,
      badge: document.getElementById('adminEditBadge').value,
      is_sold_out: document.getElementById('adminEditSoldOut').value === 'true',
      sizes: document.getElementById('adminEditSizes').value,
      tags: document.getElementById('adminEditTags').value,
      description: document.getElementById('adminEditDescription').value
    };

    const csrfToken = document.getElementById('adminEditCsrfToken')?.value || '';

    try {
      if (saveBtn) saveBtn.disabled = true;
      if (saveBtnText) saveBtnText.textContent = 'Salvando...';

      const res = await fetch('/api/loja/produto/salvar', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken
        },
        body: JSON.stringify(payload)
      });

      const data = await res.json();
      if (!res.ok || !data.success) {
        throw new Error(data.message || 'Erro ao salvar alterações da peça.');
      }

      // Atualiza o Card no DOM diretamente
      const updated = data.product;
      const card = cards.find(c => c.dataset.id === pId);
      if (card && updated) {
        card.dataset.json = JSON.stringify(updated);
        card.dataset.name = (updated.name || '').toLowerCase();
        card.dataset.wood = updated.wood_type || '';
        card.dataset.category = updated.category || '';
        card.dataset.price = updated.price;
        card.dataset.tags = (updated.tags || []).join(',');

        const titleEl = card.querySelector('.card-title-clickable');
        if (titleEl) titleEl.textContent = updated.name;

        const badgeEl = card.querySelector('.card-badge-element');
        if (badgeEl) {
          badgeEl.textContent = updated.badge || '';
          badgeEl.style.display = updated.badge ? 'inline-block' : 'none';
        }

        const priceEl = card.querySelector('.card-price');
        if (priceEl) priceEl.textContent = money(updated.price);

        const oldPriceEl = card.querySelector('.card-old-price');
        if (oldPriceEl) {
          oldPriceEl.textContent = updated.old_price ? money(updated.old_price) : '';
        }

        const metaSpans = card.querySelectorAll('.store-product-meta span');
        if (metaSpans.length >= 2) {
          const woodNames = {
            'peroba-rosa': 'Peroba Rosa',
            'jacaranda': 'Jacarandá',
            'cumaru': 'Cumaru',
            'brauna': 'Braúna',
            'canela-preta': 'Canela Preta',
            'jatoba': 'Jatobá'
          };
          metaSpans[0].textContent = woodNames[updated.wood_type] || updated.wood_type;
          metaSpans[1].textContent = updated.category;
        }

        const sizesContainer = card.querySelector('.store-size-pills-row');
        if (sizesContainer && updated.sizes) {
          sizesContainer.innerHTML = updated.sizes.map(s => `<span class="store-size-pill">${s}</span>`).join('');
        }

        const tagsContainer = card.querySelector('.store-card-tags');
        if (tagsContainer && updated.tags) {
          tagsContainer.innerHTML = updated.tags.slice(0, 3).map(t => `
            <button type="button" class="store-card-tag-pill" data-card-tag="${t}" title="Filtrar por #${t}">
              #${t.replace(/-/g, ' ')}
            </button>
          `).join('') + (updated.tags.length > 3 ? `<span class="store-card-tag-more" title="${updated.tags.slice(3).join(', ')}">+${updated.tags.length - 3}</span>` : '');
        }
      }

      if (alertBox) {
        alertBox.className = 'alert alert-success mt-3 py-2 small';
        alertBox.textContent = 'Card atualizado com sucesso no catálogo!';
        alertBox.classList.remove('d-none');
      }

      setTimeout(() => {
        closeAdminEditModal();
        applyFilters();
      }, 600);

    } catch (err) {
      if (alertBox) {
        alertBox.className = 'alert alert-danger mt-3 py-2 small';
        alertBox.textContent = err.message || 'Erro ao comunicar com o servidor.';
        alertBox.classList.remove('d-none');
      }
    } finally {
      if (saveBtn) saveBtn.disabled = false;
      if (saveBtnText) saveBtnText.textContent = originalText;
    }
  };

  updateInterestButtons();
  applyFilters();
})();

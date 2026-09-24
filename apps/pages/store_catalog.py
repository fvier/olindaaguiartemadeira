"""Catálogo da Loja de Móveis e Arte em Madeira de Demolição (Olinda Arte em Madeira).

Inspirado na arquitetura e estrutura interativa do catálogo do cliente, adaptado para
o ecossistema de marcenaria artística, peças únicas e móveis sob medida de Olinda Aguiar.
"""

STORE_WOOD_TYPES = [
    {'id': 'peroba-rosa', 'name': 'Peroba Rosa', 'origin': 'Casarões Coloniais Século XIX'},
    {'id': 'jacaranda', 'name': 'Jacarandá da Bahia', 'origin': 'Vigas Centenárias Raras'},
    {'id': 'cumaru', 'name': 'Cumaru de Demolição', 'origin': 'Estruturas Portuárias Históricas'},
    {'id': 'brauna', 'name': 'Braúna Centenária', 'origin': 'Pilares de Engenhos do Nordeste'},
    {'id': 'canela-preta', 'name': 'Canela Preta', 'origin': 'Dormentes Ferroviários Históricos'},
]

STORE_CATEGORIES = [
    'Mesas & Pranchas',
    'Aparadores & Consoles',
    'Bancos & Banquetas',
    'Esculturas & Painéis',
    'Cristaleiras & Armários',
    'Linha Gourmet & Utilitários',
]

WOODWORK_PRODUCTS = [
    {
        'id': 'OLA-M01',
        'wood_type': 'peroba-rosa',
        'category': 'Mesas & Pranchas',
        'name': 'Mesa Orgânica com Borda Natural em Peroba Rosa',
        'price': 4800.00,
        'old_price': 5400.00,
        'icon': '🪵',
        'image': 'hero-fachada-luz-dourada.png',
        'badge': 'Peça Única',
        'sizes': ['2,20m x 1,00m', '2,60m x 1,15m', '3,00m x 1,20m'],
        'description': 'Mesa de jantar esculpida em prancha única de Peroba Rosa resgatada de casarão do século XIX. Borda orgânica natural preservada, pés maciços com encaixes de respiga e acabamento acetinado com ceras botânicas.',
        'colors': [
            {
                'id': 'carnauba',
                'name': 'Cera de Carnaúba & Óleo Botânico',
                'hex': '#a75d28',
                'price': 4800.00,
                'old_price': 5400.00,
                'badge': 'Acabamento Clássico'
            },
            {
                'id': 'rustico',
                'name': 'Pátina Rústica Envelhecida',
                'hex': '#4a2c11',
                'price': 5100.00,
                'old_price': 5700.00,
                'badge': 'Edição Histórica'
            },
            {
                'id': 'fosco',
                'name': 'Verniz Mate Atóxico UV',
                'hex': '#cb7d3a',
                'price': 4950.00,
                'old_price': 5500.00,
                'badge': 'Alta Proteção'
            }
        ]
    },
    {
        'id': 'OLA-A02',
        'wood_type': 'jacaranda',
        'category': 'Aparadores & Consoles',
        'name': 'Aparador Colonial Rústico em Jacarandá da Bahia',
        'price': 3200.00,
        'old_price': 3650.00,
        'icon': '🏛️',
        'image': 'hero-fachada-noite-azul.png',
        'badge': 'Destaque Ateliê',
        'sizes': ['1,60m x 0,45m', '1,90m x 0,50m', '2,20m x 0,50m'],
        'description': 'Aparador imponente com gavetas de encaixe rabo-de-andorinha e ferragens coloniais em ferro forjado manual. Madeira densa de jacarandá centenário com veios escuros marcantes e toque aveludado.',
        'colors': [
            {
                'id': 'natural',
                'name': 'Tonalidade Natural com Óleo Puro',
                'hex': '#3b2210',
                'price': 3200.00,
                'old_price': 3650.00,
                'badge': 'Mais Procurado'
            },
            {
                'id': 'acetinado',
                'name': 'Encerado Fosco Tradicional',
                'hex': '#5b3a1a',
                'price': 3350.00,
                'old_price': 3800.00,
                'badge': 'Pátina Nobre'
            }
        ]
    },
    {
        'id': 'OLA-B03',
        'wood_type': 'cumaru',
        'category': 'Bancos & Banquetas',
        'name': 'Banco Ripado Contemporâneo em Cumaru de Demolição',
        'price': 1450.00,
        'old_price': 1750.00,
        'icon': '🪑',
        'image': 'hero-fachada-coral-entardecer.png',
        'badge': 'Pronta-Entrega',
        'sizes': ['1,50m x 0,40m', '1,80m x 0,40m', '2,10m x 0,45m'],
        'description': 'Banco ripado com desenho modernista brasileiro inspirado no design colonial recriado por Olinda Aguiar. Estrutura maciça em cumaru de alta densidade, resistente para áreas internas ou varandas cobertas.',
        'colors': [
            {
                'id': 'natural-dourado',
                'name': 'Cumaru Dourado Natural',
                'hex': '#b87333',
                'price': 1450.00,
                'old_price': 1750.00,
                'badge': 'Pronta-Entrega'
            },
            {
                'id': 'carbonizado',
                'name': 'Carbonizado Yakisugi',
                'hex': '#1e1e1e',
                'price': 1650.00,
                'old_price': 1950.00,
                'badge': 'Modernista'
            }
        ]
    },
    {
        'id': 'OLA-E04',
        'wood_type': 'brauna',
        'category': 'Esculturas & Painéis',
        'name': 'Escultura Orgânica em Raiz Centenária de Braúna',
        'price': 2800.00,
        'old_price': 3200.00,
        'icon': '🏺',
        'image': 'byll-mestre-artesao.png',
        'badge': 'Obra Autoral Byll',
        'sizes': ['0,90m x 0,60m x 1,40m'],
        'description': 'Obra de arte entalhada à mão a partir de raízes centenárias recolhidas em antigos engenhos da Zona da Mata pernambucana. Homenagem viva ao traço pioneiro de Mestre Byll, com base em aço corten.',
        'colors': [
            {
                'id': 'escuro-profundo',
                'name': 'Braúna Negra com Óleo de Tungue',
                'hex': '#1c1511',
                'price': 2800.00,
                'old_price': 3200.00,
                'badge': 'Peça de Museu'
            }
        ]
    },
    {
        'id': 'OLA-C05',
        'wood_type': 'peroba-rosa',
        'category': 'Cristaleiras & Armários',
        'name': 'Cristaleira Colonial com Vidros Canelados Vintage',
        'price': 5600.00,
        'old_price': 6200.00,
        'icon': '🚪',
        'image': 'hero-fachada-luz-dourada.png',
        'badge': 'Sob Medida',
        'sizes': ['1,10m x 0,45m x 1,95m', '1,40m x 0,50m x 2,10m'],
        'description': 'Cristaleira de três prateleiras maciças com portas de vidro canelado original e fecho cremona em latão antigo. Estrutura 100% em peroba rosa com respigas artesanais ajustadas pelos mestres marceneiros.',
        'colors': [
            {
                'id': 'colonial-mel',
                'name': 'Mel Dourado Colonial',
                'hex': '#c67d34',
                'price': 5600.00,
                'old_price': 6200.00,
                'badge': 'Exclusiva'
            },
            {
                'id': 'patina-branca',
                'name': 'Pátina Provençal Olinda',
                'hex': '#d8c7b5',
                'price': 5900.00,
                'old_price': 6500.00,
                'badge': 'Personalizado'
            }
        ]
    },
    {
        'id': 'OLA-P06',
        'wood_type': 'canela-preta',
        'category': 'Esculturas & Painéis',
        'name': 'Painel Ripado em Dormentes de Canela Preta',
        'price': 2400.00,
        'old_price': 2800.00,
        'icon': '🪵',
        'image': 'hero-fachada-coral-entardecer.png',
        'badge': 'Tendência Arquitetura',
        'sizes': ['2,00m x 1,20m', '2,40m x 1,40m', '3,00m x 1,80m'],
        'description': 'Painel decorativo acústico e visual composto por ripas selecionadas de dormentes ferroviários desativados. Texturas profundas e marcas originais dos cravos de trilho preservadas.',
        'colors': [
            {
                'id': 'canela-natural',
                'name': 'Canela Escovada Natural',
                'hex': '#6f4e37',
                'price': 2400.00,
                'old_price': 2800.00,
                'badge': 'Acústico & Térmico'
            },
            {
                'id': 'carbonizado-fosco',
                'name': 'Preto Carvão Acetinado',
                'hex': '#242424',
                'price': 2600.00,
                'old_price': 3000.00,
                'badge': 'Design Contemporâneo'
            }
        ]
    },
    {
        'id': 'OLA-G07',
        'wood_type': 'cumaru',
        'category': 'Linha Gourmet & Utilitários',
        'name': 'Tábua de Corte Gourmet em Cumaru & Resina Âmbar',
        'price': 340.00,
        'old_price': 420.00,
        'icon': '🔪',
        'image': 'hero-fachada-noite-azul.png',
        'badge': 'Pronta-Entrega',
        'sizes': ['0,50m x 0,35m x 0,05m', '0,65m x 0,40m x 0,06m'],
        'description': 'Tábua nobre para churrasco e corte gastronômico, selada com óleo mineral atóxico USP e cera virgem de abelha tiúba. Sulco para gordura e detalhe em resina translúcida âmbar.',
        'colors': [
            {
                'id': 'ambar-dourado',
                'name': 'Cumaru com Filete Âmbar',
                'hex': '#b3541e',
                'price': 340.00,
                'old_price': 420.00,
                'badge': 'Alta Durabilidade'
            }
        ]
    },
    {
        'id': 'OLA-M08',
        'wood_type': 'jacaranda',
        'category': 'Mesas & Pranchas',
        'name': 'Mesa Lateral Tora Maciça com Fissuras Naturais',
        'price': 980.00,
        'old_price': 1200.00,
        'icon': '🪵',
        'image': 'byll-e-olinda-aguiar.png',
        'badge': 'Lançamento',
        'sizes': ['Ø 0,45m x 0,55m altura', 'Ø 0,60m x 0,50m altura'],
        'description': 'Mesa de apoio feita do corte transversal de uma tora de jacarandá secular. Detalhes de borboletas de madeira (marcenaria tradicional japonesa e colonial) contendo fissuras naturais.',
        'colors': [
            {
                'id': 'jacaranda-carnauba',
                'name': 'Cera de Abelha & Carnaúba',
                'hex': '#472814',
                'price': 980.00,
                'old_price': 1200.00,
                'badge': 'Madeira Rara'
            }
        ]
    },
    {
        'id': 'OLA-A09',
        'wood_type': 'brauna',
        'category': 'Aparadores & Consoles',
        'name': 'Console Minimalista Suspenso em Braúna Maciça',
        'price': 2100.00,
        'old_price': 2450.00,
        'icon': '🏛️',
        'image': 'hero-fachada-luz-dourada.png',
        'badge': 'Exclusiva',
        'sizes': ['1,40m x 0,35m', '1,80m x 0,35m'],
        'description': 'Peça suspensa com fixação oculta em parede, ideal para halls de entrada e livings modernos. A madeira de braúna centenária traz peso visual e elegância sóbria incomparável.',
        'colors': [
            {
                'id': 'brauna-oleo',
                'name': 'Braúna Acetinada',
                'hex': '#2b1d0c',
                'price': 2100.00,
                'old_price': 2450.00,
                'badge': 'Madeira de Lei'
            }
        ]
    }
]


def get_woodwork_products(include_hidden=True):
    """Return all catalog products with default attributes initialized."""
    import copy
    products = copy.deepcopy(WOODWORK_PRODUCTS)
    for p in products:
        p.setdefault('is_sold_out', False)
        p.setdefault('is_hidden', False)
        p.setdefault('hide_price', False)
        p.setdefault('stock_quantity', 1)
    return products


def get_store_categories():
    """Return list of distinct catalog categories."""
    return list(STORE_CATEGORIES)


def get_store_wood_types():
    """Return list of distinct wood types / collections."""
    return list(STORE_WOOD_TYPES)

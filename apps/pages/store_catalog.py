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
    {'id': 'jatoba', 'name': 'Jatobá de Demolição', 'origin': 'Vigas Estruturais Nobres Centenárias'},
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
        'id': 'OLA-M00',
        'wood_type': 'peroba-rosa',
        'category': 'Mesas & Pranchas',
        'name': 'Mesa Escultural com Tampo de Vidro e Base em Madeira de Demolição',
        'price': 6200.00,
        'old_price': 6900.00,
        'icon': '🪵',
        'image': 'mesa-base-escultural-vidro-1.png',
        'images': [
            'mesa-base-escultural-vidro-1.png',
            'mesa-base-escultural-vidro-2.png',
            'mesa-base-escultural-vidro-3.png',
        ],
        'badge': 'Destaque • Peça Única',
        'sizes': ['2,20m x 1,10m x 0,76m', '2,60m x 1,20m x 0,76m'],
        'description': 'A base é toda em madeira de demolição, cheia de história, e o tampo é de vidro, trazendo leveza e sofisticação. Estrutura escultural entalhada à mão com encaixes nobres que revelam os veios e a solidez da madeira sob a transparência límpida do cristal.',
        'colors': [
            {
                'id': 'natural-oleo',
                'name': 'Madeira de Demolição Natural com Óleo Botânico',
                'hex': '#a45a2a',
                'price': 6200.00,
                'old_price': 6900.00,
                'badge': 'Exclusiva'
            },
            {
                'id': 'carnauba-acetinado',
                'name': 'Enceramento Artesanal em Carnaúba',
                'hex': '#7e3e18',
                'price': 6400.00,
                'old_price': 7100.00,
                'badge': 'Acabamento Nobre'
            }
        ]
    },
    {
        'id': 'OLA-B15',
        'wood_type': 'peroba-rosa',
        'category': 'Mesas & Pranchas',
        'name': 'Bancada em Madeira de Demolição com Acabamento em Verniz PU',
        'price': 2450.00,
        'old_price': 2800.00,
        'icon': '🪵',
        'image': 'bancada-madeira-demolicao-verniz-pu-1.png',
        'images': [
            'bancada-madeira-demolicao-verniz-pu-1.png',
            'bancada-madeira-demolicao-verniz-pu-2.png',
        ],
        'badge': 'Sob Medida • Peça Única',
        'sizes': [
            '1,60m x 0,35m x 0,05m (espessura maciça)',
            '1,80m x 0,40m x 0,06m (espessura maciça)',
            '2,20m x 0,45m x 0,06m (espessura maciça)',
            'Sob Medida para sua alvenaria ou bancada americana'
        ],
        'description': 'Bancada de madeira de demolição com acabamento em verniz PU. Cada racha e marca contam uma história, transformando o que foi descartado em algo cheio de vida e propósito. Prancha maciça centenária com borda orgânica e acabamento em poliuretano de alta resistência contra calor, líquidos e manchas, perfeita para bancadas gourmet, passa-pratos e divisórias de ambientes.',
        'colors': [
            {
                'id': 'verniz-pu-acetinado',
                'name': 'Verniz PU Acetinado de Alta Resistência',
                'hex': '#9e5828',
                'price': 2450.00,
                'old_price': 2800.00,
                'badge': 'Acabamento Padrão'
            },
            {
                'id': 'verniz-pu-fosco',
                'name': 'Verniz PU Fosco Toque Natural',
                'hex': '#783e18',
                'price': 2450.00,
                'old_price': 2800.00,
                'badge': 'Fosco Toque Seda'
            },
            {
                'id': 'carnauba-botanico',
                'name': 'Cera de Carnaúba & Óleo Botânico',
                'hex': '#b86d29',
                'price': 2300.00,
                'old_price': 2650.00,
                'badge': '100% Ecológico'
            }
        ]
    },
    {
        'id': 'OLA-A16',
        'wood_type': 'jatoba',
        'category': 'Cristaleiras & Armários',
        'name': 'Armários em Jatobá com Madeira e Lambri de Demolição',
        'price': 8900.00,
        'old_price': 10200.00,
        'icon': '🗄️',
        'image': 'armarios-cozinha-jatoba-lambri-demolicao-1.png',
        'images': [
            'armarios-cozinha-jatoba-lambri-demolicao-1.png',
            'armarios-cozinha-jatoba-lambri-demolicao-2.png',
            'armarios-cozinha-jatoba-lambri-demolicao-3.png',
        ],
        'badge': 'Sob Medida • Projeto Especial',
        'sizes': [
            'Cozinha Completa: 3,40m lineares (inferiores + aéreos)',
            'Módulo Bancada: 2,40m x 0,60m x 0,90m altura',
            'Módulos Aéreos: 2,40m x 0,38m x 0,75m altura',
            'Projeto 100% Sob Medida conforme planta do cliente'
        ],
        'description': 'Armários em jatobá, com madeira e lambri de demolição. Projeto autoral de marcenaria artesanal com portas em lambri/veneziana maciço que oferecem circulação de ar e sofisticação rústica. Estrutura robusta em jatobá centenário com gaveteiros reforçados, puxadores ergonômicos em arco de aço escovado e acabamento com selador protetor contra vapores e umidade.',
        'colors': [
            {
                'id': 'jatoba-natural',
                'name': 'Jatobá Natural com Selador Náutico & Cera',
                'hex': '#883e1c',
                'price': 8900.00,
                'old_price': 10200.00,
                'badge': 'Projeto Assinado'
            },
            {
                'id': 'jatoba-escurecido',
                'name': 'Jatobá Colonial Envelhecido',
                'hex': '#582611',
                'price': 9200.00,
                'old_price': 10600.00,
                'badge': 'Rústico Nobre'
            },
            {
                'id': 'verniz-pu-maritimo',
                'name': 'Verniz PU Acetinado Hidrorrepelente',
                'hex': '#9c4d23',
                'price': 9450.00,
                'old_price': 10900.00,
                'badge': 'Máxima Proteção'
            }
        ]
    },
    {
        'id': 'OLA-B17',
        'wood_type': 'jatoba',
        'category': 'Linha Gourmet & Utilitários',
        'name': 'Bar de Praia e Varanda Gourmet todo em Lambri de Jatobá',
        'price': 9800.00,
        'old_price': 11500.00,
        'icon': '🍹',
        'image': 'bar-resort-lambri-jatoba.png',
        'images': ['bar-resort-lambri-jatoba.png'],
        'badge': 'Sob Medida • Projeto Resort',
        'sizes': [
            '3,00m x 2,20m x 1,10m altura (formato em L)',
            '2,40m x 1,80m x 1,10m altura',
            'Sob Medida conforme área gourmet, praia ou condomínio'
        ],
        'description': 'Bar todo em lambri de jatobá. Projeto autoral de marcenaria artesanal para resorts e áreas gourmets de praia, com revestimento integral em réguas maciças de lambri de jatobá, alta densidade e tratamento náutico especial resistente a sol, maresia e intempéries. Bancada de serviço anatômica e estrutura interna sob medida para caixas térmicas, cuba e atendimento.',
        'colors': [
            {
                'id': 'jatoba-maritimo',
                'name': 'Jatobá com Selador Náutico UV & Cera Marítima',
                'hex': '#883e1c',
                'price': 9800.00,
                'old_price': 11500.00,
                'badge': 'Proteção Marítima UV'
            },
            {
                'id': 'jatoba-envelhecido',
                'name': 'Jatobá Colonial Envelhecido Acetinado',
                'hex': '#582611',
                'price': 10200.00,
                'old_price': 11900.00,
                'badge': 'Rústico Nobre'
            },
            {
                'id': 'verniz-pu-naval',
                'name': 'Verniz PU Naval Fosco Hidrorrepelente',
                'hex': '#a05025',
                'price': 10500.00,
                'old_price': 12200.00,
                'badge': 'Alta Durabilidade Externa'
            }
        ]
    },
    {
        'id': 'OLA-B10',
        'wood_type': 'peroba-rosa',
        'category': 'Linha Gourmet & Utilitários',
        'name': 'Carrinho Bar Gourmet Colonial com Porta-Taças e Rodízios',
        'price': 2850.00,
        'old_price': 3200.00,
        'icon': '🍷',
        'image': 'carrinho-bar-colonial-madeira.png',
        'images': ['carrinho-bar-colonial-madeira.png'],
        'badge': 'Pronta-Entrega',
        'sizes': ['0,95m x 0,55m x 1,60m altura'],
        'description': 'Móvel bar volante confeccionado em peroba rosa de demolição. Possui prateleira superior com trilhos ranhurados para taças invertidas, bandeja intermediária com bordas de contenção para garrafas e rodízios reforçados em madeira e ferro para movimentação suave em áreas gourmets e varandas.',
        'colors': [
            {
                'id': 'carnauba-natural',
                'name': 'Cera de Carnaúba & Óleo Botânico',
                'hex': '#9e5828',
                'price': 2850.00,
                'old_price': 3200.00,
                'badge': 'Pronta-Entrega'
            },
            {
                'id': 'patina-colonial',
                'name': 'Pátina Colonial Envelhecida',
                'hex': '#472813',
                'price': 2980.00,
                'old_price': 3350.00,
                'badge': 'Rústico Nobre'
            }
        ]
    },
    {
        'id': 'OLA-A11',
        'wood_type': 'jacaranda',
        'category': 'Aparadores & Consoles',
        'name': 'Cômoda Balcão Colonial com 4 Gavetas e Portas Duplas',
        'price': 3450.00,
        'old_price': 3900.00,
        'icon': '🗄️',
        'image': 'comoda-balcao-gaveteiro-demolicao.png',
        'images': ['comoda-balcao-gaveteiro-demolicao.png'],
        'badge': 'Peça Única',
        'sizes': ['1,10m x 0,45m x 1,15m altura'],
        'description': 'Móvel de armazenamento robusto com 4 gavetas superiores de corrediças em madeira e portas inferiores de folha dupla em prancha maciça centenária. Tampo liso encerado com borda chanfrada e pés elevados, ideal para salas de jantar, recepções ou quartos.',
        'colors': [
            {
                'id': 'mel-dourado',
                'name': 'Mel Dourado Tradicional',
                'hex': '#b86d29',
                'price': 3450.00,
                'old_price': 3900.00,
                'badge': 'Mais Procurado'
            },
            {
                'id': 'envelhecido',
                'name': 'Envelhecido Colonial em Cera',
                'hex': '#4f2c14',
                'price': 3650.00,
                'old_price': 4100.00,
                'badge': 'Acabamento Clássico'
            }
        ]
    },
    {
        'id': 'OLA-E12',
        'wood_type': 'canela-preta',
        'category': 'Esculturas & Painéis',
        'name': 'Espelho Colonial de Corpo Inteiro com Moldura Maciça',
        'price': 1950.00,
        'old_price': 2300.00,
        'icon': '🪞',
        'image': 'espelho-corpo-inteiro-moldura-macica.png',
        'images': ['espelho-corpo-inteiro-moldura-macica.png'],
        'badge': 'Destaque Ateliê',
        'sizes': ['0,90m x 2,10m x 0,08m (moldura)'],
        'description': 'Espelho amplo de piso ou parede com moldura estruturada em vigas maciças resgatadas de casarão colonial. Divisão arquitetônica com travessa central anatômica e cantos com encaixes de respiga e cavilhas expostas em madeira escura.',
        'colors': [
            {
                'id': 'castanho-natural',
                'name': 'Castanho Natural com Cera',
                'hex': '#8a491f',
                'price': 1950.00,
                'old_price': 2300.00,
                'badge': 'Exclusiva'
            },
            {
                'id': 'canela-escura',
                'name': 'Canela Escura Acetinada',
                'hex': '#4d2912',
                'price': 2100.00,
                'old_price': 2450.00,
                'badge': 'Edição Limitada'
            }
        ]
    },
    {
        'id': 'OLA-C13',
        'wood_type': 'brauna',
        'category': 'Cristaleiras & Armários',
        'name': 'Estante Expositora Colonial de Parede com Cristaleira Central',
        'price': 7800.00,
        'old_price': 8900.00,
        'icon': '🏺',
        'image': 'estante-expositora-cristaleira-casarao.png',
        'images': ['estante-expositora-cristaleira-casarao.png'],
        'badge': 'Sob Medida • Projeto Especial',
        'sizes': ['2,60m x 0,45m x 2,40m altura', '3,20m x 0,50m x 2,60m altura'],
        'description': 'Imponente armário expositor de parede inteira desenvolvido para acomodar louçarias, vinhos, coleções e vestuário. Conta com nichos abertos com cabideiros em latão, vitrine central envidraçada com portas de correr, gaveteiro e armários com portas maciças na base.',
        'colors': [
            {
                'id': 'colonial-encerada',
                'name': 'Peroba Rosa Colonial Encerada',
                'hex': '#985627',
                'price': 7800.00,
                'old_price': 8900.00,
                'badge': 'Obra Autoral Byll'
            },
            {
                'id': 'patina-rustica',
                'name': 'Pátina Rústica Envelhecida',
                'hex': '#532f17',
                'price': 8200.00,
                'old_price': 9400.00,
                'badge': 'Peça Nobre'
            }
        ]
    },
    {
        'id': 'OLA-L14',
        'wood_type': 'cumaru',
        'category': 'Linha Gourmet & Utilitários',
        'name': 'Conjunto Lavabo Colonial: Gabinete Maciço com Espelho Redondo',
        'price': 3100.00,
        'old_price': 3600.00,
        'icon': '🚰',
        'image': 'conjunto-lavatorio-gabinete-espelho-redondo.png',
        'images': ['conjunto-lavatorio-gabinete-espelho-redondo.png'],
        'badge': 'Exclusiva',
        'sizes': ['Gabinete: 0,80m x 0,55m x 0,85m | Espelho: Ø 0,70m'],
        'description': 'Conjunto sob medida para lavabos e banheiros requintados. Gabinete suspenso com portas duplas em madeira tratada resistente a umidade, ferragens e dobradiças rústicas aparentes em ferro forjado, acompanhado de espelho circular bisotado com aro largo em madeira torneada.',
        'colors': [
            {
                'id': 'cumaru-impermeabilizado',
                'name': 'Cumaru Natural Impermeabilizado',
                'hex': '#9a5423',
                'price': 3100.00,
                'old_price': 3600.00,
                'badge': 'Resistente à Umidade'
            },
            {
                'id': 'cera-maritima',
                'name': 'Cera Marítima Protetora',
                'hex': '#6e3916',
                'price': 3250.00,
                'old_price': 3780.00,
                'badge': 'Alta Durabilidade'
            }
        ]
    },
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
        if 'images' not in p or not p['images']:
            p['images'] = [p['image']] if p.get('image') else []
    return products


def get_store_categories():
    """Return list of distinct catalog categories."""
    return list(STORE_CATEGORIES)


def get_store_wood_types():
    """Return list of distinct wood types / collections."""
    return list(STORE_WOOD_TYPES)

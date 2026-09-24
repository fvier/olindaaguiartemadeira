# Avaliação mobile first — Olinda Aguiar

Data: 24/09/2026. **Situação: a interface ainda precisa de correções para uso confortável no celular.**

## Escopo e método

34 telas/estados de rota, em 320, 360, 390 e 768 CSS px de largura, altura de 844 px: 136 carregamentos em Chrome headless com emulação mobile. Capturas da primeira dobra das 34 telas em 390 px foram inspecionadas visualmente. Testados também o abre/fecha do menu público e a abertura dos filtros da loja.

Aplicação executada localmente com SQLite em memória e usuário administrativo fictício, sem carregar o `.env` nem alterar o banco existente. Conteúdo inicial criado pela própria aplicação; não representa volume real de vendas, pedidos, logs ou clientes. Aliases `.html` e `/historia` compartilham templates e não foram contados como novas telas. APIs, POSTs e arquivos estáticos não são páginas. O editor foi examinado nos estados criar e editar. As duas telas 404 são templates, não uma certificação do tratamento de URLs inexistentes.

As larguras abaixo são `document.documentElement.scrollWidth`, comparadas com a largura configurada da emulação. `innerWidth` pode crescer com o transbordamento no modo mobile e não foi usado como referência de aprovação. **27 das 34 telas excederam a largura em 320, 360 e 390 px; 17 excederam em 768 px.** Ausência de excesso horizontal não equivale a aprovação completa.

## Prioridades

### P1 — Cabeçalho administrativo corta ações

Em tela de 390 px, a largura do documento chega a 668 px; em 320/360 px, a 658 px. A barra concentra marca, Linktree e ações em grupos horizontais. Ícones à direita ficam fora da primeira tela. Afeta o layout administrativo e a versão interna do 404.

Evidência causal: ocultar temporariamente o `header` no DOM de `/admin-cadastrar` reduziu a largura de 668 para 396 px. O restante veio do aviso de senha sem quebra (borda direita medida em 396 px). Nenhuma dessas experiências foi persistida na aplicação.

Arquivos: `apps/templates/partials/topbar.html`, `apps/templates/layouts/vertical.html`, `apps/templates/pages/admin-cadastrar.html`.

Ação: manter menu, identificação curta e conta na barra mobile; agrupar ações secundárias em menu; permitir encolhimento/quebra dos grupos e dos avisos. Não usar apenas `overflow-x:hidden`, que esconderia controles.

### P1 — Menu público inicia aberto e ocupa a primeira dobra

Nas páginas principais, a navegação inicia expandida. Em 390 px, o bloco do menu mede aproximadamente 338 px, antes do conteúdo principal. O DOM contém `show`, mas o botão anuncia `aria-expanded=false`. O primeiro clique fecha; o seguinte reabre corretamente.

Causa identificada: `apps/static/js/layout.js:49-54` percorre os ancestrais `.collapse` do link ativo e adiciona `show`. A inicialização do menu lateral administrativo alcança também a navegação pública.

Ação: restringir essa expansão ao menu lateral do painel e iniciar o menu público recolhido, com estado ARIA coerente. Verificar fechar após navegação e comportamento ao redimensionar.

### P1 — Rodapé público causa transbordamento compartilhado

Páginas públicas chegam a 340/380/410 px em telas de 320/360/390 px. O rodapé usa `row g-5` dentro de `.container`, com margens de gutters maiores que o espaço lateral disponível. Em 360 px, a linha mede 400 px. Ocultar o rodapé na home em 390 px reduziu a largura de 410 para 395 px: há ainda excesso residual na grade de artigos (`row g-4`).

Arquivos: `apps/templates/partials/public-footer.html:3` e `apps/templates/pages/landing.html`.

Ação: ajustar gutters e padding dos containers primeiro no mobile; verificar a grade de artigos separadamente. Confirmar largura do documento igual à largura da tela.

### P2 — Controles compactos e formulários

Na loja, o botão Filtrar mede aproximadamente 28 px de altura; indicadores das fotos, 7 px; compartilhar, 31 px. Na home há indicadores de carrossel de 10 px. Na consulta de pedido, exemplos têm 26–28 px. Ampliar a área interativa mantendo o desenho visual compacto; adotar 44 px como meta de conforto para ações principais.

Há campos com fonte inferior a 16 px em login, pedido, editor e painel. Ajustar fontes e espaçamento mobile; validar em iPhone real o comportamento de foco/zoom e teclado. O campo CPF declara `fs-13`; o grupo de busca usa `min-width:320px`, que deve ser revisto em telas de 320 px com margens.

As contagens brutas de elementos pequenos incluem controles fora da área visível, radios e elementos de componentes recolhidos. Não devem ser tratadas como número de violações de acessibilidade. Esta avaliação não é uma auditoria formal WCAG.

### P2 — Tabelas e prioridade de conteúdo

Vendas, validação, financeiro e comissionamento mantêm tabelas densas. Rolagem horizontal dentro da tabela é diferente do transbordamento do documento. Priorizar dados essenciais e oferecer detalhes por registro; manter indicação de rolagem quando a tabela for necessária. Em financeiro e ranking, filtros/regras ocupam grande parte da tela antes do resultado principal.

### P3 — Consistência de conteúdo

Recuperação de senha, cadastro, bloqueio e erros ainda têm textos em inglês. Algumas páginas internas conservam referências a GPS Paraíba, rastreamento e planos automotivos. Confirmar a finalidade dessas telas e adequar conteúdo e navegação ao ateliê.

## Avaliação por tela

As colunas numéricas mostram a largura real do documento em cada viewport. Valores maiores que o cabeçalho indicam excesso horizontal.

| Tela | 320 | 360 | 390 | 768 | Observação |
|---|---:|---:|---:|---:|---|
| `/` | 340 | 380 | 410 | 768 | Menu aberto ocupa a primeira dobra; carrossel com indicadores pequenos; rodapé excede a tela. |
| `/blog/1` | 340 | 380 | 410 | 768 | Artigo em coluna única; campos de interação pequenos; rodapé excede a tela. |
| `/blog/novo` | 340 | 380 | 410 | 768 | Formulário empilhado; campos menores que 16 px; revisar barra de ferramentas com teclado aberto. |
| `/blog/1/editar` | 340 | 380 | 410 | 768 | Mesma estrutura de criação; título longo fica parcialmente visível dentro do campo. |
| `/byll/historia` | 340 | 380 | 410 | 768 | Conteúdo em coluna; categorias horizontais; rodapé excede a tela. |
| `/admin-cadastrar` | 658 | 658 | 668 | 801 | Cabeçalho cortado e aviso de senha sem quebra (atinge 396 px em tela de 390 px). |
| `/admin-carrossel` | 658 | 658 | 668 | 801 | Upload empilhado; cabeçalho cortado; galeria e formulário longos. |
| `/admin-depoimentos` | 658 | 658 | 668 | 801 | Formulário empilhado; cabeçalho cortado; revisar ações da lista preenchida. |
| `/admin-integracoes` | 658 | 658 | 668 | 801 | Abas quebram em várias linhas; cabeçalho cortado; referências legadas a GPS Paraíba. |
| `/admin-logs` | 658 | 658 | 668 | 801 | Indicadores empilhados; filtros pequenos; cabeçalho cortado. |
| `/admin-privilegios` | 658 | 658 | 668 | 801 | Cartões empilhados; cabeçalho cortado; ações afastadas pela altura dos indicadores. |
| `/alterar-senha` | 658 | 658 | 668 | 801 | Formulário cabe na coluna; cabeçalho cortado; campos abaixo de 16 px. |
| `/auth-lock-screen` | 320 | 360 | 390 | 768 | Sem excesso horizontal; template em inglês e identidade de usuário demonstrativo. |
| `/auth-logout` | 320 | 360 | 390 | 768 | Sem excesso horizontal; ações principais visíveis. |
| `/auth-password` | 320 | 360 | 390 | 768 | Sem excesso horizontal; texto em inglês e campo pequeno; fluxo de recuperação não testado. |
| `/auth-signin` | 320 | 360 | 390 | 768 | Sem excesso horizontal; campos abaixo de 16 px e link de recuperação pequeno. |
| `/auth-signup` | 320 | 360 | 390 | 768 | Sem excesso horizontal; template em inglês; fluxo de cadastro não testado. |
| `/comissionamento` | 658 | 658 | 668 | 801 | Cabeçalho cortado; tabela densa e muitas ações compactas; escala horizontal. |
| `/dashboard-sales` | 658 | 658 | 668 | 801 | Cartões empilhados; cabeçalho cortado; indicadores ocupam várias dobras. |
| `/financeiro-categorias` | 658 | 658 | 668 | 801 | Cabeçalho cortado; empresas e categorias empilhadas; validar listas grandes. |
| `/financeiro-lancamentos` | 658 | 658 | 668 | 801 | Cabeçalho cortado; tabela com rolagem própria e texto denso; filtros compactos. |
| `/financeiro` | 658 | 658 | 668 | 801 | Cabeçalho cortado; filtros ocupam quase toda a primeira dobra; campos pequenos. |
| `/index` | 658 | 658 | 668 | 801 | Cabeçalho cortado; faixa de resumo também corta conteúdo à direita. |
| `/links` | 320 | 360 | 390 | 768 | Sem excesso horizontal; cartões grandes e empilhados; alguns subtítulos truncados. |
| `/pages-404-alt` | 622 | 622 | 632 | 768 | Cabeçalho cortado; mensagem de erro em inglês. |
| `/pages-404` | 320 | 360 | 390 | 768 | Sem excesso horizontal; mensagem de erro em inglês. |
| `/planos` | 658 | 658 | 668 | 801 | Cabeçalho cortado; ações e indicadores empilhados; conteúdo comercial legado. |
| `/ranking` | 658 | 658 | 668 | 801 | Cabeçalho cortado; seletores compactos; regras extensas antes do ranking. |
| `/validacao-vendas` | 658 | 658 | 668 | 801 | Cabeçalho cortado; tabela exige rolagem horizontal interna. |
| `/vendas` | 658 | 658 | 668 | 801 | Cabeçalho cortado; tabela densa e rolagem interna; contexto legado de rastreamento. |
| `/loja` | 340 | 380 | 410 | 768 | Menu aberto empurra catálogo; filtro de 28 px de altura; indicadores de fotos de 7 px. |
| `/pedido` | 340 | 380 | 410 | 768 | Busca com fonte de 13 px; exemplos com botões de 26–28 px; min-width de 320 px no grupo de busca. |
| `/blog` | 340 | 380 | 410 | 768 | Menu aberto empurra listagem; temas e busca compactos; rodapé excede a tela. |
| `/byll` | 340 | 380 | 410 | 768 | Menu aberto empurra apresentação; texto longo; rodapé excede a tela. |

## Evidências e limites

- [Medições por rota](mobile-first-2026-09-24/medicoes.json).
- [Capturas: administração e autenticação](mobile-first-2026-09-24/telas-1.jpg).
- [Capturas: blog, editor, institucional e financeiro](mobile-first-2026-09-24/telas-2.jpg).
- [Capturas: demais páginas](mobile-first-2026-09-24/telas-3.jpg).
- Capturas individuais e dados brutos temporários: `/tmp/olinda-mobile-audit/`.

Os filtros da loja abriram no clique. Imagens sem `naturalWidth` no primeiro carregamento incluíam lazy loading; não foram classificadas como imagens quebradas. Nenhuma imagem não lazy com URL preenchida estava quebrada na verificação complementar da loja.

Pendente: navegação completa sem autenticação e por outros perfis; modais, formulários enviados, erros e estados com muitos registros; teclado virtual e Safari/iOS; aparelhos reais, orientação paisagem e rede lenta; contraste, leitor de tela e foco; páginas publicadas em produção. Capturas cobrem a primeira dobra, enquanto a medição de largura cobre o documento renderizado inteiro. Sem aprovação global de todos os fluxos.

## Ordem de correção e aceite

1. Corrigir cabeçalho administrativo, inicialização do menu público e gutters do rodapé/home.
2. Ajustar áreas de toque, fontes de campos, busca de pedido e avisos sem quebra.
3. Adaptar tabelas/filtros e revisar conteúdo legado.
4. Repetir a matriz e completar os fluxos pendentes.

Aceite proposto: nenhuma rolagem horizontal no documento em 320/360/390/768 px; ações de conta e navegação acessíveis; menu público recolhido ao abrir; rolagem de tabelas contida; formulários utilizáveis com teclado aberto. Correções e publicação não foram realizadas nesta avaliação.

# 🤖 Prompt de Sistema Permanente para Assistentes de IA (Olinda Aguiar)

Ao interagir com o repositório **Olinda Aguiar — Artes em Madeira** (`fvier/olindaaguiartemadeira`), qualquer assistente de IA deve seguir rigorosamente as regras abaixo:

1. **Contexto do Negócio & Identidade de Marca**:
   - **Olinda Aguiar**: Ateliê e galeria especializada em arte em madeira nobre, marcenaria fina, esculturas e peças de design autoral.
   - **Identidade Visual**: Elegância rústico-contemporânea inspirada em casarões coloniais históricos. Cores marcantes: Coral terracota, azul cobalto, vermelho colonial, acabamentos em madeira natural e iluminação quente.
2. **Diretrizes de Governança**:
   - Respeitar estritamente as regras de [docs/diretrizes_documentacao.md](./diretrizes_documentacao.md).
   - Seguir a **Regra da Alimentação Incremental (Não-Substituição)** em `postmortem.md` e `troubleshooting.md` (novas entradas sempre no topo).
3. **Padrão Git & Commits**:
   - Branches no formato `feature/*`, `fix/*`, `docs/*`.
   - Commits no padrão Conventional Commits (`feat:`, `fix:`, `docs:`, etc.).
   - Utilização do alias oficial `git graph` para histórico visual.
4. **Segurança & Sanitização**:
   - Nunca comitar arquivos `.env`, chaves de API, webhooks ou certificados no repositório.
   - Utilizar variáveis de ambiente via `os.getenv` ou placeholders explícitos.

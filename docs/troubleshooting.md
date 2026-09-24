# 🔍 Troubleshooting & Diagnóstico (Olinda Aguiar)

Guia rápido para resolução de problemas comuns no repositório **Olinda Aguiar — Artes em Madeira**.

> [!IMPORTANT]
> **Alimentação Incremental:** Nunca remova soluções antigas deste documento. Adicione novos problemas e soluções incrementalmente no topo.

---

## 1. Problema: Banco SQLite Mantém Dados Legados de Rastreamento Veicular após Mudança de Marca

### Sintoma
Após alterar os textos das constantes em `apps/pages/routes.py`, a página inicial ainda exibia planos ou depoimentos antigos salvos no banco `apps/db.sqlite3`.

### Solução
A função `ensure_commercial_content()` foi configurada com auto-detecção de dados legados (`has_old_plans` e `has_old_reviews`). Ao detectar palavras-chave antigas como "veículo" ou "FIPE", a função limpa as tabelas `CommercialPlan`, `LandingCard` e `ClientReview`, recriando o seed com os dados e linhas da Olinda Arte em Madeira de forma totalmente atômica e segura.

---

## 2. Problema: Permissão Negada ao Realizar Push no GitHub (`Permission denied (publickey)`)

### Sintoma
Ao tentar rodar `git push origin main`, ocorre o erro:
`git@github.com: Permission denied (publickey). fatal: Could not read from remote repository.`

### Solução
1. Certifique-se de que o ssh-agent está em execução e sua chave privada carregada:
   ```bash
   ssh-add -l
   ```
2. Teste a conexão direta com o GitHub:
   ```bash
   ssh -T git@github.com
   ```

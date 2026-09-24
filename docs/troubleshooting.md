# 🔍 Troubleshooting & Diagnóstico (Olinda Aguiar)

Guia rápido para resolução de problemas comuns no repositório **Olinda Aguiar — Artes em Madeira**.

> [!IMPORTANT]
> **Alimentação Incremental:** Nunca remova soluções antigas deste documento. Adicione novos problemas e soluções incrementalmente no topo.

---

## 1. Problema: Permissão Negada ao Realizar Push no GitHub (`Permission denied (publickey)`)

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

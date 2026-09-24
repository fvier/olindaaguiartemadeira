# 🚚 Guia de Migração & Onboarding (Olinda Aguiar)

Instruções para clonar, configurar e preparar o ambiente de desenvolvimento do projeto **Olinda Aguiar — Artes em Madeira** em novas estações ou servidores.

---

## 1. Pré-requisitos
- Git e chave SSH cadastrada na conta GitHub (`git@github.com`).
- VS Code ou IDE Antigravity recomendada com extensão **Git Graph**.

---

## 2. Passo a Passo de Setup

```bash
# 1. Clonar o repositório oficial
git clone git@github.com:fvier/olindaaguiartemadeira.git
cd olindaaguiartemadeira

# 2. Configurar alias visual 'git graph'
git config --global alias.graph "log --graph --oneline --all --decorate"

# 3. Testar visualização
git graph
```

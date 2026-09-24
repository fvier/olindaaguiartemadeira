# 🏗️ Ajuda & Infraestrutura (Olinda Aguiar)

Visão geral da infraestrutura, arquitetura de diretórios e comandos rápidos para manutenção e desenvolvimento do projeto **Olinda Aguiar — Artes em Madeira**.

---

## 1. Estrutura e Ativos

- **Repositório**: `git@github.com:fvier/olindaaguiartemadeira.git`
- **Galeria de Referências**: Localizada em `referencias/` contendo a identidade visual, logotipos e fotos em alta definição da fachada colonial e ateliê.
- **Governança**: Localizada em `docs/` com padrões operacionais e regras de commit.

---

## 2. Comandos Rápidos do Git e Manutenção

```bash
# Verificar status da árvore de trabalho:
git status

# Visualizar gráfico de branches e commits:
git graph

# Sincronizar branch main com o GitHub:
git pull origin main
git push origin main
```

---

## 3. Comandos Rápidos da Aplicação

```bash
# Executar em modo desenvolvimento:
python3 run.py

# Executar com Gunicorn (Produção):
gunicorn --config gunicorn-cfg.py run:app

# Verificar compilação sintática de arquivos Python:
python3 -m py_compile run.py create_user.py apps/__init__.py apps/config.py apps/pages/models.py apps/pages/routes.py

# Criar usuário administrador:
python3 create_user.py
```

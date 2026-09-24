#!/usr/bin/env bash
set -euo pipefail

deploy_root=/data/olinda
source_dir="$deploy_root/source"
env_file="$deploy_root/.env.production"
admin_file="$deploy_root/initial-admin.txt"
repository=https://github.com/fvier/olindaaguiartemadeira.git

install -d -m 700 "$deploy_root"

if [[ ! -d "$source_dir/.git" ]]; then
    git clone "$repository" "$source_dir"
else
    git -C "$source_dir" fetch origin
    git -C "$source_dir" reset --hard origin/main
fi

if [[ ! -f "$env_file" ]]; then
    secret_key=$(openssl rand -hex 32)
    postgres_password=$(openssl rand -hex 32)
    integration_key=$(openssl rand -hex 32)
    initial_password=$(openssl rand -base64 24 | tr -d '\n')

    umask 077
    printf '%s\n' \
        "SERVICE_HEX_64_RASTREK=$secret_key" \
        "SERVICE_PASSWORD_64_POSTGRES=$postgres_password" \
        "API_INTEGRATION_KEY=$integration_key" \
        'POSTGRES_DB=olinda_db' \
        'POSTGRES_USER=olinda_user' \
        'INITIAL_ADMIN_EMAIL=admin@olindaaguiar.com' \
        "INITIAL_ADMIN_PASSWORD=$initial_password" \
        > "$env_file"

    printf '%s\n' \
        'Usuário inicial: admin@olindaaguiar.com' \
        "Senha temporária: $initial_password" \
        'Remova este arquivo depois do primeiro login e da troca de senha.' \
        > "$admin_file"
fi

chmod 600 "$env_file"
cd "$source_dir"

docker compose \
    --project-name olinda \
    --env-file "$env_file" \
    -f docker-compose.coolify.yml \
    -f deploy/docker-compose.vps.yml \
    up -d --build --remove-orphans

docker compose \
    --project-name olinda \
    --env-file "$env_file" \
    -f docker-compose.coolify.yml \
    -f deploy/docker-compose.vps.yml \
    ps

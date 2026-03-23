# Alembic Playbook (Local + Render)

## Show current head

alembic -c backend\alembic.ini current

## Create new migration

alembic -c backend\alembic.ini revision -m "description"

## Apply all migrations

alembic -c backend\alembic.ini upgrade head

## Downgrade example (use with care)

alembic -c backend\alembic.ini downgrade -1

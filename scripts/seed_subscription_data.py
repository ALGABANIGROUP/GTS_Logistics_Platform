#!/usr/bin/env python3
"""
Script to seed the database with initial subscription system data
"""
import json
import os
import sys
import asyncio
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

# Also add the backend directory itself
sys.path.insert(0, str(backend_path.parent))

from sqlalchemy.ext.asyncio import AsyncSession
from backend.database.config import get_sessionmaker
from backend.models.subscription import Plan, Role, Bot

async def load_json_file(filepath):
    """Load JSON file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

async def seed_plans():
    """Seed plans data"""
    plans_file = Path(__file__).parent.parent / "config" / "plans.json"
    plans_data = await load_json_file(plans_file)

    sessionmaker = get_sessionmaker()
    async with sessionmaker() as session:
        try:
            for plan_data in plans_data['plans']:
                plan = Plan(
                    key=plan_data['key'],
                    name_ar=plan_data['name_ar'],
                    name_en=plan_data['name_en'],
                    description=plan_data.get('description', ''),
                    price_monthly=plan_data.get('price_monthly'),
                    price_yearly=plan_data.get('price_yearly'),
                    features=plan_data.get('features', []),
                    limits=plan_data.get('limits', {}),
                    is_active=plan_data.get('is_active', True)
                )
                await session.merge(plan)  # Use merge to handle updates

            await session.commit()
            print("✅ Plans seeded successfully")

        except Exception as e:
            await session.rollback()
            print(f"❌ Error seeding plans: {e}")

async def seed_roles():
    """Seed roles data"""
    roles_file = Path(__file__).parent.parent / "config" / "roles.json"
    roles_data = await load_json_file(roles_file)

    sessionmaker = get_sessionmaker()
    async with sessionmaker() as session:
        try:
            for role_data in roles_data['roles']:
                role = Role(
                    key=role_data['key'],
                    name=role_data.get('name_en', role_data['name_ar']),  # Use English name as fallback
                    name_ar=role_data['name_ar'],
                    name_en=role_data['name_en'],
                    permissions=role_data.get('permissions', []),
                    features=role_data.get('features', []),
                    data_scope=role_data.get('data_scope', 'tenant_only'),
                    is_system=role_data.get('is_system', False)
                )
                await session.merge(role)

            await session.commit()
            print("✅ Roles seeded successfully")

        except Exception as e:
            await session.rollback()
            print(f"❌ Error seeding roles: {e}")

async def seed_bots():
    """Seed bots data from registry"""
    registry_file = Path(__file__).parent.parent / "backend" / "modules" / "ai-bots" / "registry" / "bots-registry.js"

    # Parse JavaScript registry file (simple approach)
    with open(registry_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract botsRegistry object (simplified parsing)
    start = content.find('botsRegistry = {')
    end = content.find('};', start) + 2
    registry_content = content[start:end]

    # Convert to Python dict (simplified approach)
    bots_data = parse_js_registry(registry_content)

    sessionmaker = get_sessionmaker()
    async with sessionmaker() as session:
        try:
            for bot_key, bot_data in bots_data.items():
                bot = Bot(
                    key=bot_key,
                    name_ar=bot_data.get('name_ar', ''),
                    name_en=bot_data.get('name_en', ''),
                    description=bot_data.get('description', ''),
                    type=bot_data.get('type', 'user'),
                    category=bot_data.get('category', ''),
                    icon=bot_data.get('icon', ''),
                    email_local_part=bot_data.get('email_local_part'),
                    version=bot_data.get('version', '1.0.0'),
                    status=bot_data.get('status', 'active'),
                    availability=bot_data.get('availability', 'all'),
                    endpoints=bot_data.get('endpoints', {}),
                    features=bot_data.get('features', []),
                    dependencies=bot_data.get('dependencies', []),
                    config=bot_data.get('config', {})
                )
                await session.merge(bot)

            await session.commit()
            print("✅ Bots seeded successfully")

        except Exception as e:
            await session.rollback()
            print(f"❌ Error seeding bots: {e}")

def parse_js_registry(js_content):
    """Simple parser for JavaScript registry (simplified)"""
    # This is a very basic parser - in production, you'd want a proper JS parser
    bots = {}

    # Extract bot definitions
    lines = js_content.split('\n')
    current_bot = None
    current_data = {}

    for line in lines:
        line = line.strip()
        if line.startswith('//') or line == '':
            continue

        if ':' in line and '{' in line:
            # New bot definition
            if current_bot:
                bots[current_bot] = current_data
            current_bot = line.split(':')[0].strip().strip("'\"")
            current_data = {}
        elif ':' in line and current_bot:
            # Bot property
            if ':' in line:
                parts = line.split(':', 1)
                key = parts[0].strip().strip("'\"")
                value = parts[1].strip().rstrip(',').strip()

                # Simple value parsing
                if value.startswith("'") or value.startswith('"'):
                    value = value.strip("'\"")
                elif value == 'null':
                    value = None
                elif value in ['true', 'false']:
                    value = value == 'true'
                elif value.startswith('[') or value.startswith('{'):
                    # Skip complex objects for now
                    value = {}

                current_data[key] = value

    if current_bot:
        bots[current_bot] = current_data

    return bots

async def main():
    """Main seeding function"""
    print("🌱 Seeding subscription system data...")

    await seed_plans()
    await seed_roles()
    await seed_bots()

    print("🎉 Seeding completed!")

if __name__ == "__main__":
    asyncio.run(main())
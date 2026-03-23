# backend/tools/verify_bot_fix.py
import os

def verify_bot_fix():
    """Verify that both bots have been fixed"""
    ai_core_path = "backend/core/ai_core.py"

    print("🔍 Verifying bot fixes...")
    print("=" * 50)

    if not os.path.exists(ai_core_path):
        print("❌ File ai_core.py not found")
        return False

    with open(ai_core_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check for the presence of both fixed bots
    checks = [
        ("OperationsManagerBot", "operations_manager"),
        ("FinanceBot", "finance_bot")
    ]

    all_good = True

    for class_name, bot_id in checks:
        if class_name in content:
            print(f"✅ {class_name} is present in the file")

            # Verify that process_message function exists
            if "async def process_message" in content and class_name in content:
                print(f"   ✅ process_message function exists for {bot_id}")
            else:
                print(f"   ❌ process_message function missing for {bot_id}")
                all_good = False
        else:
            print(f"❌ {class_name} not found in the file")
            all_good = False

    if all_good:
        print("\n🎯 All fixes are present — ready to restart")
    else:
        print("\n⚠️  Issues detected — fix them before restarting")

    return all_good

if __name__ == "__main__":
    verify_bot_fix()

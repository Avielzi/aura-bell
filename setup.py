import os
import re

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def main():
    clear_screen()
    print("="*50)
    print("🚀 Dori-Bell v2.0 - Easy Setup Script")
    print("="*50)
    print("\nThis script will help you configure your Dori-Bell smart doorbell.\n")

    # Collect Data
    family_name = input("🏠 Enter Family Name (e.g., Cohen Family): ") or "Dori-Bell Home"
    tg_token = input("🤖 Enter Telegram Bot Token: ")
    tg_chat_id = input("💬 Enter Telegram Chat ID: ")
    phone_number = input("📞 Enter Phone Number (e.g., +972501234567): ")
    site_key = input("🔑 Enter Turnstile Site Key: ")
    secret_key = input("🔒 Enter Turnstile Secret Key: ")

    # Update wrangler.toml
    print("\n📝 Updating wrangler.toml...")
    try:
        with open('wrangler.toml', 'r', encoding='utf-8') as f:
            content = f.read()

        content = re.sub(r'TG_BOT_TOKEN = ".*"', f'TG_BOT_TOKEN = "{tg_token}"', content)
        content = re.sub(r'TG_CHAT_ID = ".*"', f'TG_CHAT_ID = "{tg_chat_id}"', content)
        content = re.sub(r'TURNSTILE_SITE_KEY = ".*"', f'TURNSTILE_SITE_KEY = "{site_key}"', content)
        content = re.sub(r'TURNSTILE_SECRET = ".*"', f'TURNSTILE_SECRET = "{secret_key}"', content)
        content = re.sub(r'FAMILY_NAME = ".*"', f'FAMILY_NAME = "{family_name}"', content)
        content = re.sub(r'PHONE_NUMBER = ".*"', f'PHONE_NUMBER = "{phone_number}"', content)

        with open('wrangler.toml', 'w', encoding='utf-8') as f:
            f.write(content)
        print("✅ wrangler.toml updated!")
    except Exception as e:
        print(f"❌ Error updating wrangler.toml: {e}")

    # Create .env for local development
    print("📝 Creating .env file...")
    env_content = f"""TG_BOT_TOKEN="{tg_token}"
TG_CHAT_ID="{tg_chat_id}"
TURNSTILE_SITE_KEY="{site_key}"
TURNSTILE_SECRET="{secret_key}"
FAMILY_NAME="{family_name}"
PHONE_NUMBER="{phone_number}"
"""
    with open('.env', 'w', encoding='utf-8') as f:
        f.write(env_content)
    print("✅ .env file created!")

    print("\n" + "="*50)
    print("🎉 Setup Complete!")
    print("="*50)
    print("\nNext steps:")
    print("1. Run 'wrangler deploy' to push your doorbell to the cloud.")
    print("2. Visit your worker URL to test it out!")
    print("\nNeed help? Check GUIDE.he.md")

if __name__ == "__main__":
    main()

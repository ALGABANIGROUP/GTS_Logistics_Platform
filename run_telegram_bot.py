#!/usr/bin/env python
"""
Run Telegram bot in polling mode for local development
"""

import sys
import os

# أضف المسار الرئيسي
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from telegram_bot import gts_bot
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Start Telegram bot"""
    try:
        logger.info("🤖 Starting Telegram bot in polling mode...")
        gts_bot.run_polling()
    except KeyboardInterrupt:
        logger.info("🛑 Bot stopped by user")
    except Exception as e:
        logger.error(f"❌ Bot error: {e}")

if __name__ == "__main__":
    main()
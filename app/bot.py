import logging
import re
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, ConversationHandler, CallbackQueryHandler, PicklePersistence

from scrappers.linkedin import linkedin_scraper
from scrappers.instagram import instagram_scraper
from scrappers.facebook import facebook_scraper

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Define states for the conversation
NAME, SURNAME = range(2)

def escape_markdown_v2(text):
    """Helper function to escape special characters for Markdown V2."""
    escape_chars = r'\_*[]()~`>#+-=|{}.!'
    return re.sub(f'([{re.escape(escape_chars)}])', r'\\\1', text)

def start(update: Update, context: CallbackContext) -> None:
    keyboard = [[InlineKeyboardButton("Search Person", callback_data='search_person')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    update.message.reply_text(
        'Hello! I am your bot. How can I assist you today?\n'
        'You can use the button below to search for a person.',
        reply_markup=reply_markup
    )
    logger.info("Start command received, displaying options to user.")

def search_person(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()
    query.message.reply_text("Please enter the name of the person:")
    return NAME

def get_name(update: Update, context: CallbackContext) -> int:
    name = update.message.text
    if not name.isalpha():
        update.message.reply_text('Invalid name. Please enter a valid name (letters only):')
        return NAME
    context.user_data['name'] = name
    update.message.reply_text('Please enter the surname of the person:')
    logger.info(f"Name received: {name}")
    return SURNAME

def get_surname(update: Update, context: CallbackContext) -> int:
    surname = update.message.text
    if not surname.isalpha():
        update.message.reply_text('Invalid surname. Please enter a valid surname (letters only):')
        return SURNAME
    context.user_data['surname'] = surname
    
    name = escape_markdown_v2(context.user_data['name'])
    surname = escape_markdown_v2(context.user_data['surname'])

    logger.info(f"Surname received: {surname}")

    # Improved message format with proper markdown
    update.message.reply_text(
        f"🔍 Searching for LinkedIn user with the following details:\n"
        f"📌 *Name*: {name}\n"
        f"📌 *Surname*: {surname}\n\n"
        f"Please wait while we fetch the information...",
        parse_mode='MarkdownV2'
    )
    
    # Fetch data from LinkedIn
    try:
        linkedin_data = linkedin_scraper(context.user_data['name'], context.user_data['surname'])
        logger.info(f"LinkedIn data fetched: {linkedin_data}")

        # Fetch Instagram and Facebook data based on LinkedIn profile information
        instagram_data = instagram_scraper(linkedin_data.get('profile', ''))
        logger.info(f"Instagram data fetched: {instagram_data}")

        facebook_data = facebook_scraper(linkedin_data.get('profile', ''))
        logger.info(f"Facebook data fetched: {facebook_data}")

        # Combine all data
        combined_data = {
            "LinkedIn": linkedin_data,
            "Instagram": instagram_data,
            "Facebook": facebook_data
        }

        # Escape markdown in combined data
        combined_data_str = str(combined_data)
        combined_data_str = escape_markdown_v2(combined_data_str)

        # Display combined data to user
        update.message.reply_text(f'Fetched data: {combined_data_str}', parse_mode='MarkdownV2')
        logger.info(f"Combined data sent to user: {combined_data}")
    except Exception as e:
        logger.error(f"Error occurred: {e}")
        update.message.reply_text('An error occurred while fetching data. Please try again later.')
    
    return ConversationHandler.END

def cancel(update: Update, context: CallbackContext) -> int:
    update.message.reply_text('Operation cancelled.')
    logger.info("Operation cancelled by user.")
    return ConversationHandler.END

def error(update: Update, context: CallbackContext) -> None:
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)

def main():
    # Get the bot token from environment variable
    TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

    # Use PicklePersistence to store conversation states
    persistence = PicklePersistence(filename='/app/bot_data/persistence_data')
    updater = Updater(TOKEN, use_context=True, persistence=persistence)

    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(search_person, pattern='^search_person$')],
        states={
            NAME: [MessageHandler(Filters.text & ~Filters.command, get_name)],
            SURNAME: [MessageHandler(Filters.text & ~Filters.command, get_surname)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
        name="my_conversation",
        persistent=True,
    )

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(conv_handler)
    dp.add_error_handler(error)

    updater.start_polling()
    
    logger.info("Bot started. Press Ctrl-C to stop.")
    updater.idle()

if __name__ == '__main__':
    main()

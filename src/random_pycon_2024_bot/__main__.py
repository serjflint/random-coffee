import logging
import uuid

import telegram as t
import telegram.ext as te
import pydantic
import pydantic_settings as ps

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


class Settings(ps.BaseSettings):
    model_config = ps.SettingsConfigDict(env_file='.env')
    token: str = pydantic.Field()
    
    
async def start(update: t.Update, context: te.ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")


async def echo(update: t.Update, context: te.ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text=update.message.text)
    
    
async def inline_caps(update: t.Update, context: te.ContextTypes.DEFAULT_TYPE):
    query = update.inline_query.query
    if not query:
        return
    results = []
    results.append(
        t.InlineQueryResultArticle(
            id=str(uuid.uuid4()),
            title='Caps',
            input_message_content=t.InputTextMessageContent(query.upper())
        )
    )
    await context.bot.answer_inline_query(update.inline_query.id, results)


async def unknown(update: t.Update, context: te.ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I didn't understand that command.")


def main():
    settings = Settings()
    application = te.ApplicationBuilder().token(settings.token).build()
    
    start_handler = te.CommandHandler('start', start)
    echo_handler = te.MessageHandler(te.filters.TEXT & (~te.filters.COMMAND), echo)
    inline_caps_handler = te.InlineQueryHandler(inline_caps)
    unknown_handler = te.MessageHandler(te.filters.COMMAND, unknown)
    
    application.add_handler(start_handler)
    application.add_handler(echo_handler)
    application.add_handler(inline_caps_handler)
    application.add_handler(unknown_handler)
    
    application.run_polling()


if __name__ == '__main__':
    main()

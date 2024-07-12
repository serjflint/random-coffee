import logging

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


def main():
    settings = Settings()
    application = te.ApplicationBuilder().token(settings.token).build()
    
    start_handler = te.CommandHandler('start', start)
    echo_handler = te.MessageHandler(te.filters.TEXT & (~te.filters.COMMAND), echo)
    
    application.add_handler(start_handler)
    application.add_handler(echo_handler)
    
    application.run_polling()


if __name__ == '__main__':
    main()

import telebot
import difflib

from config import keys, TOKEN
from extensions import ConvertionException, Converter

bot = telebot.TeleBot(TOKEN)

def find_closest_key(user_input):
    closest_key = difflib.get_close_matches(user_input, keys.keys(), n=1, cutoff=0.6) #поиск соответствия в keys
    if closest_key:
        return closest_key[0]
    return None

@bot.message_handler(commands=['start', 'help'])
def help(message: telebot.types.Message):
    text = 'Чтобы начать работу введите команду боту в следующем формате:\n <имя валюты> \
<в какую валюту перевести> \
<количество переводимой валюты>\nУвидеть список всех доступных валют: /values'
    bot.reply_to(message, text)


@bot.message_handler(commands=['values'])
def values(message: telebot.types.Message):
    text = 'Доступные валюты:'
    for key in keys.keys():
        text = '\n'.join((text,key, ))
    bot.reply_to(message, text)


@bot.message_handler(content_types=['text', ])
def convert(message: telebot.types.Message):
    try:
        values = message.text.split(' ')

        if len(values) != 3:
            raise ConvertionException('Слишком много параметров.')

        quote, base, amount = values

        quote = find_closest_key(quote)
        base = find_closest_key(base)

        if not quote:
            raise ConvertionException(f'Не удалось обработать валюту {values[0]}')
        if not base:
            raise ConvertionException(f'Не удалось обработать валюту {values[1]}')

        total_base = Converter.get_price(quote, base, amount)
        total_amount = float(amount) * total_base
    except ConvertionException as e:
        bot.reply_to(message, f'Ошибка пользователя.\n{e}')
    except Exception as e:
        bot.reply_to(message, f'Не удалось обработать команду\n{e}')
    else:
        text = f'Цена {amount} {quote} в {base} - {"%.2f" % total_amount}'
        bot.send_message(message.chat.id, text)


bot.polling(none_stop=True)

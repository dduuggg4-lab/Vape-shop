import asyncio
import logging
from aiogram import Bot, Dispatcher, F, Router
from aiogram.filters import Command
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputMediaPhoto,
    Message,
)

# Твой актуальный токен
TOKEN = "9048872953:AAHJFcx1OHcqwBT4-AXzo-JdKmtQmr-msUc"

admin_router = Router()
logging.basicConfig(level=logging.INFO)

# Главный логотип-картинка при старте и для категорий
IMG_MAIN = "https://images.unsplash.com/photo-1527661591475-527312dd65f5?w=600"
IMG_CHECKOUT = (
    "https://images.unsplash.com/photo-1556742049-0a67d553c2a5?w=600"
)

# Каталог товаров с реальными вкусами и оптовыми ценами
CATALOG = {
    "vape": {
        "title": "💨 Курилки",
        "items": {
            "waka_38k": {
                "name": "WAKA 38.000",
                "price": 7500,
                "flavors": [
                    "Клубника арбуз",
                    "Лимон лайм",
                    "Капучино+шоколад",
                    "Табак+ваниль",
                ],
                "img": "https://images.unsplash.com/photo-1539185441755-769473a23570?w=600",
            },
            "waka_extra_20k": {
                "name": "Waka EXTRA PRO X 20000",
                "price": 8500,
                "flavors": [
                    "Ежевика Мята",
                    "Микс Ягод",
                    "Черника Вишня Клюкв",
                    "Клубника Арбуз",
                    "Арбуз",
                    "Кислое Яблоко",
                ],
                "img": "https://images.unsplash.com/photo-1539185441755-769473a23570?w=600",
            },
            "waka_10k_pro": {
                "name": "Waka 10000 PRO",
                "price": 8000,
                "flavors": [
                    "Виноград со льдом",
                    "Клубника Арбуз",
                    "Тройная Ягода",
                    "Черника Малина Лимон",
                    "Мармелад",
                    "Свежая Мята",
                ],
                "img": "https://images.unsplash.com/photo-1539185441755-769473a23570?w=600",
            },
            "elfbar_30k": {
                "name": "ELF BAR BC 30.000",
                "price": 6800,
                "flavors": [
                    "Ледяной арбуз",
                    "Лимонад вишня персик",
                    "Лимон лайм",
                    "Малина клубника",
                    "Черная смородина виноград",
                    "Двойная мята",
                ],
                "img": "https://images.unsplash.com/photo-1539185441755-769473a23570?w=600",
            },
        },
    },
    "cartridge": {
        "title": "🌿 Картриджи",
        "items": {
            "waka_kit_25k": {
                "name": "WAKA KIT 25.000 КАРТРИДЖ",
                "price": 6200,
                "flavors": [
                    "Quad Berry Ice / Rainbow Drop",
                    "Blueberry Raspberry / Strawberry Mango",
                    "Strawberry Banana Ice Cream / Cola",
                ],
                "img": "https://images.unsplash.com/photo-1527661591475-527312dd65f5?w=600",
            }
        },
    },
    "liquid": {
        "title": "🍸 Жидкости",
        "items": {
            "chrome_liquid": {
                "name": "Жидкость CHROME",
                "price": 4750,
                "flavors": ["Черника Лимон", "Ежевичный Мохито"],
                "img": "https://images.unsplash.com/photo-1563227812-0ea4c22e6cc8?w=600",
            }
        },
    },
    "snus": {
        "title": "🧊 Снюс",
        "items": {
            "iceberg": {
                "name": "Снюс ICEBERG",
                "price": 4500,
                "flavors": ["Extreme Mint", "Double Freeze"],
                "img": "https://images.unsplash.com/photo-1527661591475-527312dd65f5?w=600",
            }
        },
    },
    "pods": {
        "title": "💨 Под-системы",
        "items": {
            "xros_4": {
                "name": "Vaporesso XROS 4",
                "price": 11500,
                "flavors": ["Черный", "Синий", "Красный"],
                "img": "https://images.unsplash.com/photo-1539185441755-769473a23570?w=600",
            }
        },
    },
    "cotton": {
        "title": "🧬 Loops ватки",
        "items": {
            "loops_cotton": {
                "name": "Вата Loops",
                "price": 2500,
                "flavors": ["Оригинал"],
                "img": "https://images.unsplash.com/photo-1527661591475-527312dd65f5?w=600",
            }
        },
    },
}

carts = {}


def get_main_menu():
  return InlineKeyboardMarkup(
      inline_keyboard=[
          [
              InlineKeyboardButton(
                  text="💨 Курилки", callback_data="cat_vape"
              ),
              InlineKeyboardButton(
                  text="🍸 Жидкости", callback_data="cat_liquid"
              ),
          ],
          [
              InlineKeyboardButton(text="🧊 Снюс", callback_data="cat_snus"),
              InlineKeyboardButton(
                  text="🌿 Картриджи", callback_data="cat_cartridge"
              ),
          ],
          [
              InlineKeyboardButton(
                  text="💨 Под-системы", callback_data="cat_pods"
              ),
              InlineKeyboardButton(
                  text="🧬 Loops ватки", callback_data="cat_cotton"
              ),
          ],
          [
              InlineKeyboardButton(
                  text="ℹ️ Информация", callback_data="info"
              ),
              InlineKeyboardButton(text="🆘 Помощь", callback_data="help"),
          ],
          [
              InlineKeyboardButton(
                  text="🔗 Активный бот", url="https://t.me/vape_paradise_akb"
              )
          ],
      ]
  )


@admin_router.message(Command("start"))
async def cmd_start(message: Message):
  text = "👋 **Приветствуем! Ты попал на Vape Shop**\n\nВыберите категорию ниже: 👇"
  await message.answer_photo(
      photo=IMG_MAIN, caption=text, reply_markup=get_main_menu(), parse_mode="Markdown"
  )


@admin_router.callback_query(F.data == "back_to_main")
async def back_to_main(callback: CallbackQuery):
  text = "👋 **Приветствуем! Ты попал на Vape Shop**\n\nВыберите категорию ниже: 👇"
  try:
    await callback.message.edit_media(
        media=InputMediaPhoto(media=IMG_MAIN, caption=text, parse_mode="Markdown"),
        reply_markup=get_main_menu(),
    )
  except Exception:
    await callback.message.delete()
    await callback.message.answer_photo(
        photo=IMG_MAIN, caption=text, reply_markup=get_main_menu(), parse_mode="Markdown"
    )
  await callback.answer()


@admin_router.callback_query(F.data.startswith("cat_"))
async def show_category(callback: CallbackQuery):
  cat_key = callback.data.split("_")[1]
  category = CATALOG.get(cat_key)

  buttons = []
  for item_id, item_info in category["items"].items():
    buttons.append([
        InlineKeyboardButton(
            text=f"{item_info['name']} — {item_info['price']}₸",
            callback_data=f"item_{cat_key}_{item_id}",
        )
    ])

  buttons.append(
      [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_main")]
  )
  keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)

  try:
    await callback.message.edit_media(
        media=InputMediaPhoto(
            media=IMG_MAIN,
            caption=f"📂 **{category['title']}**\n\nВыберите товар:",
            parse_mode="Markdown",
        ),
        reply_markup=keyboard,
    )
  except Exception:
    await callback.message.edit_caption(
        caption=f"📂 **{category['title']}**\n\nВыберите товар:",
        reply_markup=keyboard,
        parse_mode="Markdown",
    )
  await callback.answer()


@admin_router.callback_query(F.data.startswith("item_"))
async def show_item(callback: CallbackQuery):
  _, cat_key, item_id = callback.data.split("_")
  item = CATALOG[cat_key]["items"][item_id]

  buttons = []
  for flavor in item["flavors"]:
    buttons.append([
        InlineKeyboardButton(
            text=f"🟢 {flavor} (ост: 1шт)",
            callback_data=f"buy_{item_id}_{flavor}",
        )
    ])

  buttons.append(
      [InlineKeyboardButton(text="⬅️ Назад", callback_data=f"cat_{cat_key}")]
  )
  keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)

  try:
    await callback.message.edit_media(
        media=InputMediaPhoto(
            media=item["img"],
            caption=f"📦 **{item['name']} — {item['price']}₸**\nВыберите вкус:",
            parse_mode="Markdown",
        ),
        reply_markup=keyboard,
    )
  except Exception:
    await callback.message.delete()
    await callback.message.answer_photo(
        photo=item["img"],
        caption=f"📦 **{item['name']} — {item['price']}₸**\nВыберите вкус:",
        reply_markup=keyboard,
        parse_mode="Markdown",
    )
  await callback.answer()


@admin_router.callback_query(F.data.startswith("buy_"))
async def add_to_cart(callback: CallbackQuery):
  parts = callback.data.split("_")
  item_id = parts[1]
  flavor = "_".join(parts[2:])

  user_id = callback.from_user.id
  if user_id not in carts:
    carts[user_id] = []

  item_name = ""
  item_price = 0
  for cat in CATALOG.values():
    if item_id in cat["items"]:
      item_name = cat["items"][item_id]["name"]
      item_price = cat["items"][item_id]["price"]

  carts[user_id].append(
      {"name": item_name, "price": item_price, "flavor": flavor}
  )

  keyboard = InlineKeyboardMarkup(
      inline_keyboard=[
          [
              InlineKeyboardButton(
                  text="🛒 Корзина", callback_data="show_cart"
              ),
              InlineKeyboardButton(
                  text="➕ Добавить еще", callback_data="back_to_main"
              ),
          ],
          [InlineKeyboardButton(text="❌ Отмена", callback_data="back_to_main")],
          [
              InlineKeyboardButton(
                  text="✅ Оформить заказ", callback_data="checkout"
              )
          ],
      ]
  )

  try:
    await callback.message.edit_caption(
        caption=(
            f"✅ **{item_name} — {item_price}₸**\nВкус: {flavor}\nДобавлен в"
            " корзину!\n\nМожете открыть корзину или перейти к оформлению."
        ),
        reply_markup=keyboard,
        parse_mode="Markdown",
    )
  except Exception:
    await callback.message.edit_text(
        text=(
            f"✅ **{item_name} — {item_price}₸**\nВкус: {flavor}\nДобавлен в"
            " корзину!\n\nМожете открыть корзину или перейти к оформлению."
        ),
        reply_markup=keyboard,
        parse_mode="Markdown",
    )
  await callback.answer()


@admin_router.callback_query(F.data == "show_cart")
async def show_cart(callback: CallbackQuery):
  user_id = callback.from_user.id
  user_cart = carts.get(user_id, [])

  if not user_cart:
    await callback.answer("Ваша корзина пуста!", show_alert=True)
    return

  cart_text = "🛒 **Ваша корзина:**\n\n"
  total = 0
  for idx, prod in enumerate(user_cart, 1):
    cart_text += f"{idx}. {prod['name']} ({prod['flavor']}) — {prod['price']}₸\n"
    total += prod["price"]

  cart_text += f"\n💰 **Итого: {total}₸**"

  keyboard = InlineKeyboardMarkup(
      inline_keyboard=[
          [
              InlineKeyboardButton(
                  text="✅ Оформить заказ", callback_data="checkout"
              )
          ],
          [InlineKeyboardButton(text="🗑 Очистить", callback_data="clear_cart")],
          [
              InlineKeyboardButton(
                  text="⬅️ Назад в меню", callback_data="back_to_main"
              )
          ],
      ]
  )

  try:
    await callback.message.edit_caption(
        caption=cart_text, reply_markup=keyboard, parse_mode="Markdown"
    )
  except Exception:
    await callback.message.edit_text(
        text=cart_text, reply_markup=keyboard, parse_mode="Markdown"
    )
  await callback.answer()


@admin_router.callback_query(F.data == "clear_cart")
async def clear_cart(callback: CallbackQuery):
  user_id = callback.from_user.id
  carts[user_id] = []
  keyboard = InlineKeyboardMarkup(
      inline_keyboard=[
          [InlineKeyboardButton(text="⬅️ В меню", callback_data="back_to_main")]
      ]
  )
  try:
    await callback.message.edit_caption(
        caption="🗑 Корзина очищена!",
        reply_markup=keyboard,
        parse_mode="Markdown",
    )
  except Exception:
    await callback.message.edit_text(
        text="🗑 Корзина очищена!", reply_markup=keyboard, parse_mode="Markdown"
    )
  await callback.answer()


@admin_router.callback_query(F.data == "checkout")
async def checkout(callback: CallbackQuery):
  user_id = callback.from_user.id
  user_cart = carts.get(user_id, [])
  total = sum(item["price"] for item in user_cart) if user_cart else 3000

  usdt_total = int(total * 0.9)
  discount = total - usdt_total

  text = (
      f"💳 **Выберите способ оплаты**\n\n"
      f"📦 **Ваш заказ**\n"
      f"💵 Сумма товаров: {total}₸\n\n"
      f"💳 **Банковский перевод**\n"
      f"🇰🇿 К оплате: {total}₸\n\n"
      f"🪙 **USDT TRC20**\n"
      f"🎁 Скидка за оплату криптой: -{discount}₸ (10%)\n"
      f"💵 К оплате в тенге: {usdt_total}₸\n\n"
      f"Нажмите кнопку с удобным способом оплаты ниже."
  )

  keyboard = InlineKeyboardMarkup(
      inline_keyboard=[
          [
              InlineKeyboardButton(
                  text="💳 Банковский перевод", callback_data="pay_card"
              )
          ],
          [
              InlineKeyboardButton(
                  text="🪙 USDT TRC20 (-10%)", callback_data="pay_usdt"
              )
          ],
          [
              InlineKeyboardButton(
                  text="❌ Отменить заказ", callback_data="back_to_main"
              )
          ],
      ]
  )

  try:
    await callback.message.edit_media(
        media=InputMediaPhoto(media=IMG_CHECKOUT, caption=text, parse_mode="Markdown"),
        reply_markup=keyboard,
    )
  except Exception:
    await callback.message.delete()
    await callback.message.answer_photo(
        photo=IMG_CHECKOUT, caption=text, reply_markup=keyboard, parse_mode="Markdown"
    )
  await callback.answer()


@admin_router.callback_query(F.data.startswith("pay_"))
async def process_payment(callback: CallbackQuery):
  pay_type = (
      "Банковский перевод"
      if callback.data == "pay_card"
      else "🪙 USDT TRC20 (со скидкой 10%)"
  )
  user_id = callback.from_user.id
  carts[user_id] = []

  keyboard = InlineKeyboardMarkup(
      inline_keyboard=[
          [InlineKeyboardButton(text="⬅️ Главное меню", callback_data="back_to_main")]
      ]
  )

  try:
    await callback.message.edit_caption(
        caption=(
            f"🎉 **Заказ успешно оформлен!**\n\nСпособ оплаты:"
            f" {pay_type}\n\nС вами свяжется менеджер для подтверждения."
        ),
        reply_markup=keyboard,
        parse_mode="Markdown",
    )
  except Exception:
    await callback.message.edit_text(
        text=(
            f"🎉 **Заказ успешно оформлен!**\n\nСпособ оплаты:"
            f" {pay_type}\n\nС вами свяжется менеджер для подтверждения."
        ),
        reply_markup=keyboard,
        parse_mode="Markdown",
    )
  await callback.answer()


@admin_router.callback_query(F.data == "info")
async def info_handler(callback: CallbackQuery):
  keyboard = InlineKeyboardMarkup(
      inline_keyboard=[
          [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_main")]
      ]
  )
  try:
    await callback.message.edit_caption(
        caption=(
            "ℹ️ **Информация**\n\nДобро пожаловать в наш магазин! Быстрая"
            " доставка и лучшие цены."
        ),
        reply_markup=keyboard,
        parse_mode="Markdown",
    )
  except Exception:
    await callback.message.edit_text(
        text=(
            "ℹ️ **Информация**\n\nДобро пожаловать в наш магазин! Быстрая"
            " доставка и лучшие цены."
        ),
        reply_markup=keyboard,
        parse_mode="Markdown",
    )
  await callback.answer()


@admin_router.callback_query(F.data == "help")
async def help_handler(callback: CallbackQuery):
  keyboard = InlineKeyboardMarkup(
      inline_keyboard=[
          [
              InlineKeyboardButton(
                  text="💬 Написать админу",
                  url="https://t.me/vape_paradise_akb",
              )
          ],
          [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_main")],
      ]
  )
  try:
    await callback.message.edit_caption(
        caption="🆘 **Помощь / Поддержка**\n\nПо всем вопросам пишите администратору:",
        reply_markup=keyboard,
        parse_mode="Markdown",
    )
  except Exception:
    await callback.message.edit_text(
        text="🆘 **Помощь / Поддержка**\n\nПо всем вопросам пишите администратору:",
        reply_markup=keyboard,
        parse_mode="Markdown",
    )
  await callback.answer()


async def main():
  bot = Bot(token=TOKEN)
  dp = Dispatcher()
  dp.include_router(admin_router)
  await bot.delete_webhook(drop_pending_updates=True)
  print("Бот успешно запущен!")
  await dp.start_polling(bot)


if __name__ == "__main__":
  try:
    asyncio.run(main())
  except (KeyboardInterrupt, SystemExit):
    print("Бот остановлен")

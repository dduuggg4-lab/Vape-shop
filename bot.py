import asyncio
import logging
import os
from pathlib import Path

from aiogram import Bot, Dispatcher, F, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
from aiogram.types import (
    CallbackQuery,
    FSInputFile,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputMediaPhoto,
    Message,
)

# ───────────── НАСТРОЙКИ (берутся из переменных окружения) ─────────────
# В Termux:
#   export BOT_TOKEN="9048872953:AAGUENAEcb0s5euHmeiiWXQyeMPwE4v_xnY"
#   export ADMIN_ID="8190923535"      (узнать: бот @userinfobot)
#   export CARD_INFO="Kaspi 4400 0000 0000 0000, Имя Ф."
#   export USDT_ADDRESS="адрес TRC20"
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
CARD_INFO = os.getenv("CARD_INFO", "Реквизиты уточняйте у менеджера")
USDT_ADDRESS = os.getenv("USDT_ADDRESS", "Адрес уточняйте у менеджера")
SUPPORT_URL = "https://t.me/vape_paradise_akb"
ACTIVE_BOT_URL = "https://t.me/vape_paradise_akb"
USDT_DISCOUNT = 0.10  # скидка за оплату криптой

logging.basicConfig(level=logging.INFO)
router = Router()

# ───────────── КАРТИНКИ ─────────────
# Положи свои картинки в папку images/ рядом с bot.py.
# Имя файла = название вкладки (jpg / jpeg / png / webp):
#   start      — приветствие (логотип)
#   menu       — главное меню
#   vape, liquid, snus, cartridge, pods, cotton — категории
#   cart       — корзина
#   checkout   — выбор оплаты
#   pay_card, pay_usdt — реквизиты
#   done       — заказ оформлен
#   info, help — информация и помощь
# Можно и для отдельного товара: имя файла = id товара (например waka_38k.jpg).
# Нет файла — ставится временная картинка из интернета.
IMG_DIR = Path(__file__).parent / "images"
EXTS = ("jpg", "jpeg", "png", "webp")
_URLS = [
    "https://images.unsplash.com/photo-1527661591475-527312dd65f5?w=600",
    "https://images.unsplash.com/photo-1539185441755-769473a23570?w=600",
    "https://images.unsplash.com/photo-1563227812-0ea4c22e6cc8?w=600",
    "https://images.unsplash.com/photo-1556742049-0a67d553c2a5?w=600",
]
file_ids = {}  # кэш file_id, чтобы не загружать файл заново


def photo(*names):
    """Первая найденная картинка из списка имён, иначе запасная ссылка."""
    for name in names:
        for ext in EXTS:
            path = IMG_DIR / f"{name}.{ext}"
            if path.exists():
                return file_ids.get(str(path)) or FSInputFile(path)
    return _URLS[sum(map(ord, names[0])) % len(_URLS)]


# ───────────── КАТАЛОГ ─────────────
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
            }
        },
    },
}

# Плоский словарь: id товара -> (категория, товар). id должны быть уникальны.
ITEMS = {
    item_id: (cat_key, item)
    for cat_key, cat in CATALOG.items()
    for item_id, item in cat["items"].items()
}

carts = {}  # user_id -> список товаров


# ───────────── ВСПОМОГАТЕЛЬНОЕ ─────────────
def fmt(n):
    return f"{int(n):,}".replace(",", ".")


def btn(text, data=None, url=None):
    if url:
        return InlineKeyboardButton(text=text, url=url)
    return InlineKeyboardButton(text=text, callback_data=data)


def kb(*rows):
    return InlineKeyboardMarkup(inline_keyboard=[list(r) for r in rows])


def cart_total(user_id):
    return sum(p["price"] for p in carts.get(user_id, []))


def menu_kb():
    return kb(
        [btn("💨 Курилки", "cat:vape"), btn("🍸 Жидкости", "cat:liquid")],
        [btn("🧊 Снюс", "cat:snus"), btn("🌿 Картриджи", "cat:cartridge")],
        [btn("💨 Под-системы", "cat:pods")],
        [btn("🧬 Loops ватки", "cat:cotton")],
        [btn("🛒 Корзина", "cart")],
        [btn("ℹ️ Информация", "info")],
        [btn("🆘 Помощь", "help")],
        [btn("🔗 Активный бот", url=ACTIVE_BOT_URL)],
    )


async def show(cb: CallbackQuery, img, text, keyboard):
    """Меняет картинку, текст и кнопки в том же сообщении.
    img=None — картинка остаётся, меняется только подпись."""
    msg = cb.message
    try:
        if img is None:
            await msg.edit_caption(caption=text, reply_markup=keyboard)
            return
        res = await msg.edit_media(
            media=InputMediaPhoto(media=img, caption=text),
            reply_markup=keyboard,
        )
        if isinstance(img, FSInputFile) and isinstance(res, Message) and res.photo:
            file_ids[str(img.path)] = res.photo[-1].file_id
    except TelegramBadRequest as e:
        if "not modified" in str(e):
            return
        logging.warning("edit не удался (%s), отправляю заново", e)
        try:
            await msg.delete()
        except Exception:
            pass
        sent = await msg.answer_photo(
            photo=img if img is not None else photo("menu", "start"),
            caption=text,
            reply_markup=keyboard,
        )
        if isinstance(img, FSInputFile) and sent.photo:
            file_ids[str(img.path)] = sent.photo[-1].file_id


# ───────────── СТАРТ И ВОЗРАСТ ─────────────
START_TEXT = (
    "👋 <b>Приветствуем! Ты попал на Vape Shop</b>\n\n"
    "🔞 Магазин только для совершеннолетних. Вам есть 18 лет?"
)
MENU_TEXT = "🏠 <b>Главное меню</b>\n\nВыберите категорию:"


@router.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer_photo(
        photo=photo("start"),
        caption=START_TEXT,
        reply_markup=kb(
            [btn("✅ Мне есть 18", "age_ok")],
            [btn("❌ Мне нет 18", "age_no")],
        ),
    )


@router.callback_query(F.data == "age_no")
async def age_no(cb: CallbackQuery):
    await cb.answer("Доступ только с 18 лет.", show_alert=True)


@router.callback_query(F.data.in_({"age_ok", "menu"}))
async def main_menu(cb: CallbackQuery):
    await show(cb, photo("menu", "start"), MENU_TEXT, menu_kb())
    await cb.answer()


# ───────────── КАТЕГОРИИ И ТОВАРЫ ─────────────
@router.callback_query(F.data.startswith("cat:"))
async def show_category(cb: CallbackQuery):
    cat_key = cb.data.split(":", 1)[1]
    cat = CATALOG.get(cat_key)
    if not cat:
        await cb.answer("Категория не найдена", show_alert=True)
        return
    rows = [
        [btn(f"{it['name']} — {fmt(it['price'])}₸", f"item:{item_id}")]
        for item_id, it in cat["items"].items()
    ]
    rows.append([btn("⬅️ Назад", "menu")])
    await show(
        cb,
        photo(cat_key, "menu"),
        f"<b>{cat['title']}</b>\n\nВыберите товар:",
        kb(*rows),
    )
    await cb.answer()


@router.callback_query(F.data.startswith("item:"))
async def show_item(cb: CallbackQuery):
    item_id = cb.data.split(":", 1)[1]
    if item_id not in ITEMS:
        await cb.answer("Товар не найден", show_alert=True)
        return
    cat_key, item = ITEMS[item_id]
    rows = [
        [btn(f"🟢 {flavor}", f"buy:{item_id}:{i}")]
        for i, flavor in enumerate(item["flavors"])
    ]
    rows.append([btn("⬅️ Назад", f"cat:{cat_key}")])
    await show(
        cb,
        photo(item_id, cat_key, "menu"),
        f"📦 <b>{item['name']} — {fmt(item['price'])}₸</b>\nВыберите вкус:",
        kb(*rows),
    )
    await cb.answer()


@router.callback_query(F.data.startswith("buy:"))
async def add_to_cart(cb: CallbackQuery):
    _, item_id, idx = cb.data.split(":")
    cat_key, item = ITEMS[item_id]
    flavor = item["flavors"][int(idx)]
    carts.setdefault(cb.from_user.id, []).append(
        {"name": item["name"], "price": item["price"], "flavor": flavor}
    )
    await show(
        cb,
        None,  # картинка товара остаётся
        f"✅ <b>{item['name']} — {fmt(item['price'])}₸</b>\n"
        f"Вкус: {flavor}\nДобавлен в корзину!",
        kb(
            [btn("🛒 Корзина", "cart"), btn("➕ Добавить ещё", f"cat:{cat_key}")],
            [btn("✅ Оформить заказ", "checkout")],
            [btn("❌ Отмена", "cancel")],
        ),
    )
    await cb.answer("Добавлено в корзину")


# ───────────── КОРЗИНА ─────────────
@router.callback_query(F.data == "cart")
async def show_cart(cb: CallbackQuery):
    user_cart = carts.get(cb.from_user.id, [])
    if not user_cart:
        await cb.answer("Ваша корзина пуста!", show_alert=True)
        return
    lines = [
        f"{i}. {p['name']} ({p['flavor']}) — {fmt(p['price'])}₸"
        for i, p in enumerate(user_cart, 1)
    ]
    text = (
        "🛒 <b>Ваша корзина:</b>\n\n"
        + "\n".join(lines)
        + f"\n\n💰 <b>Итого: {fmt(cart_total(cb.from_user.id))}₸</b>"
    )
    await show(
        cb,
        photo("cart", "menu"),
        text,
        kb(
            [btn("✅ Оформить заказ", "checkout")],
            [btn("🗑 Очистить", "clear")],
            [btn("⬅️ Назад в меню", "menu")],
        ),
    )
    await cb.answer()


@router.callback_query(F.data == "clear")
async def clear_cart(cb: CallbackQuery):
    carts[cb.from_user.id] = []
    await show(
        cb,
        photo("menu", "start"),
        "🗑 Корзина очищена!\n\nВыберите категорию:",
        menu_kb(),
    )
    await cb.answer()


@router.callback_query(F.data == "cancel")
async def cancel_order(cb: CallbackQuery):
    carts[cb.from_user.id] = []
    await show(
        cb,
        photo("menu", "start"),
        "❌ Оформление отменено.\n\nВыберите категорию:",
        menu_kb(),
    )
    await cb.answer()


# ───────────── ОПЛАТА ─────────────
@router.callback_query(F.data == "checkout")
async def checkout(cb: CallbackQuery):
    total = cart_total(cb.from_user.id)
    if not total:
        await cb.answer("Корзина пуста — сначала выберите товар", show_alert=True)
        return
    usdt_total = int(total * (1 - USDT_DISCOUNT))
    discount = total - usdt_total
    pct = int(USDT_DISCOUNT * 100)
    text = (
        "💳 <b>Выберите способ оплаты</b>\n\n"
        f"📦 <b>Ваш заказ</b>\n💵 Сумма товаров: {fmt(total)}₸\n\n"
        f"💳 <b>Банковский перевод</b>\n🇰🇿 К оплате: {fmt(total)}₸\n\n"
        f"🪙 <b>USDT TRC20</b>\n"
        f"🎁 Скидка за оплату криптой: -{fmt(discount)}₸ ({pct}%)\n"
        f"💵 К оплате в тенге: {fmt(usdt_total)}₸\n\n"
        "Нажмите кнопку с удобным способом оплаты ниже."
    )
    await show(
        cb,
        photo("checkout", "menu"),
        text,
        kb(
            [btn("💳 Банковский перевод", "pay:card")],
            [btn(f"🪙 USDT TRC20 (-{pct}%)", "pay:usdt")],
            [btn("❌ Отменить заказ", "cancel")],
        ),
    )
    await cb.answer()


@router.callback_query(F.data.in_({"pay:card", "pay:usdt"}))
async def pay_details(cb: CallbackQuery):
    method = cb.data.split(":")[1]
    total = cart_total(cb.from_user.id)
    if not total:
        await cb.answer("Корзина пуста", show_alert=True)
        return
    if method == "card":
        title, amount, requisites = "💳 Банковский перевод", total, CARD_INFO
    else:
        title = "🪙 USDT TRC20"
        amount = int(total * (1 - USDT_DISCOUNT))
        requisites = USDT_ADDRESS
    text = (
        f"<b>{title}</b>\n\n"
        f"К оплате: <b>{fmt(amount)}₸</b>\n\n"
        f"Реквизиты:\n<code>{requisites}</code>\n\n"
        "После оплаты нажмите «Я оплатил»."
    )
    await show(
        cb,
        photo(f"pay_{method}", "checkout", "menu"),
        text,
        kb(
            [btn("✅ Я оплатил", f"paid:{method}")],
            [btn("⬅️ Другой способ", "checkout")],
            [btn("❌ Отменить заказ", "cancel")],
        ),
    )
    await cb.answer()


@router.callback_query(F.data.in_({"paid:card", "paid:usdt"}))
async def paid(cb: CallbackQuery):
    user_id = cb.from_user.id
    user_cart = carts.get(user_id, [])
    if not user_cart:
        await cb.answer("Заказ уже оформлен или корзина пуста", show_alert=True)
        return
    method = cb.data.split(":")[1]
    total = cart_total(user_id)
    if method == "card":
        pay_name, amount = "Банковский перевод", total
    else:
        pay_name, amount = "USDT TRC20", int(total * (1 - USDT_DISCOUNT))

    lines = [
        f"{i}. {p['name']} ({p['flavor']}) — {fmt(p['price'])}₸"
        for i, p in enumerate(user_cart, 1)
    ]
    order_text = (
        "🆕 <b>Новый заказ</b>\n"
        f"Покупатель: {cb.from_user.mention_html()} (id <code>{user_id}</code>)\n"
        + (f"Username: @{cb.from_user.username}\n" if cb.from_user.username else "")
        + "\n"
        + "\n".join(lines)
        + f"\n\n💰 Сумма товаров: {fmt(total)}₸"
        f"\n💳 Оплата: {pay_name}, к оплате {fmt(amount)}₸"
    )
    if ADMIN_ID:
        try:
            await cb.bot.send_message(ADMIN_ID, order_text)
        except Exception as e:
            logging.error("Не удалось отправить заказ админу: %s", e)
    else:
        logging.warning("ADMIN_ID не задан, заказ никому не отправлен:\n%s", order_text)

    carts[user_id] = []
    await show(
        cb,
        photo("done", "menu"),
        "🎉 <b>Заказ оформлен!</b>\n\n"
        f"Способ оплаты: {pay_name}\n"
        "С вами свяжется менеджер для подтверждения.",
        kb([btn("⬅️ Главное меню", "menu")]),
    )
    await cb.answer()


# ───────────── ИНФО И ПОМОЩЬ ─────────────
@router.callback_query(F.data == "info")
async def info_handler(cb: CallbackQuery):
    await show(
        cb,
        photo("info", "menu"),
        "ℹ️ <b>Информация</b>\n\nДобро пожаловать в наш магазин! "
        "Быстрая доставка и лучшие цены.",
        kb([btn("⬅️ Назад", "menu")]),
    )
    await cb.answer()


@router.callback_query(F.data == "help")
async def help_handler(cb: CallbackQuery):
    await show(
        cb,
        photo("help", "menu"),
        "🆘 <b>Помощь / Поддержка</b>\n\nПо всем вопросам пишите администратору:",
        kb(
            [btn("💬 Написать админу", url=SUPPORT_URL)],
            [btn("⬅️ Назад", "menu")],
        ),
    )
    await cb.answer()


# Любая необработанная кнопка (например, из старого сообщения)
@router.callback_query()
async def unknown(cb: CallbackQuery):
    await cb.answer("Кнопка устарела, нажмите /start", show_alert=True)


async def main():
    if not TOKEN:
        raise SystemExit("Не задан BOT_TOKEN. В Termux: export BOT_TOKEN='токен'")
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()
    dp.include_router(router)
    await bot.delete_webhook(drop_pending_updates=True)
    print("Бот успешно запущен!")
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("Бот остановлен")

# bot.py
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from utils import call_llm
from books import search_books
from orders import create_order, get_orders  # ← get_orders added
from courier import book_shipment
import re
import time

TOKEN = "8190358089:AAF5bZuZ3MtSaFEDUCGCxIHIkEdry9txuv8"

# === COLOR LOGS ===
class C:
    GREEN  = '\033[92m'
    YELLOW = '\033[93m'
    CYAN   = '\033[96m'
    BLUE   = '\033[94m'
    RED    = '\033[91m'
    END    = '\033[0m'

def log(msg, color=C.BLUE):
    print(f"{color}[{time.strftime('%H:%M:%S')}] {msg}{C.END}")

# === GLOBAL STATE ===
user_data = {}

# === START ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_data[user_id] = {"history": [], "last_books": []}
    log(f"User {user_id} STARTED", C.YELLOW)
    reply = await call_llm([{"role": "user", "content": "Hello"}])
    log(f"BOT → {reply}", C.GREEN)
    await update.message.reply_text(reply)

# === MAIN HANDLER ===
async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()

    if user_id not in user_data:
        user_data[user_id] = {"history": [], "last_books": []}

    user_short = str(user_id)[:6]
    log(f"USER {user_short} → {text}", C.CYAN)

    history = user_data[user_id]["history"]
    history.append({"role": "user", "content": text})

    reply = ""

    # === SEARCH ===
    if any(k in text.lower() for k in ['find', 'search', 'want', 'show']):
        query = re.sub(r'\b(find|search|want|show|me|for|books?)\b', '', text, flags=re.IGNORECASE).strip() or "best"
        log(f"SEARCH → '{query}'", C.BLUE)
        books = search_books(query, 3)
        user_data[user_id]["last_books"] = books
        context.user_data["last_books"] = books  # for order

        if books:
            lines = [f"{i+1}. *{b['title']}* - {b.get('price','N/A')}" for i, b in enumerate(books)]
            context_str = "\n".join(lines)
            reply = await call_llm(history + [{"role": "system", "content": context_str}])
        else:
            reply = "No books found."

    # === ORDER (SMART SELECTION) ===
    elif any(k in text.lower() for k in ['order', 'buy', 'this one', 'first', 'second', 'third']):
        books = context.user_data.get("last_books", [])
        if not books:
            reply = "Search for a book first!"
        else:
            # Smart: extract number or "this one"
            idx = 0
            m = re.search(r'\b(\d+)\b', text)
            if m:
                idx = min(int(m.group(1)) - 1, len(books) - 1)
            elif "first" in text.lower(): idx = 0
            elif "second" in text.lower(): idx = 1
            elif "third" in text.lower(): idx = 2

            book = books[idx]
            log(f"ORDER → {book['title']}", C.YELLOW)

            # === CREATE ORDER (NO PRICE) ===
            order_id = create_order(
                user_id=str(user_id),
                isbn=book.get('isbn'),
                title=book['title'],
                address="Pending"  # ← No price
            )
            if not order_id:
                reply = "Order failed. Try again."
            else:
                # === MOCK SHIPMENT (NO REAL API) ===
                shipment = book_shipment(
                    invoice=str(order_id),
                    recipient_name="Customer",
                    phone="01700000000",
                    address="Demo Address",
                    cod_amount=550
                )
                track = shipment.get("tracking_code", "TRK-MOCK-123")

                reply = (
                    f"Order placed!\n"
                    f"Book: *{book['title']}*\n"
                    f"Price: *{book.get('price', 'N/A')}*\n"
                    f"ID: `{order_id}`\n"
                    f"Track: `{track}`\n\n"
                    f"Share address to confirm!"
                )

    # === CHAT / FALLBACK ===
    else:
        log("LLM → Generating...", C.BLUE)
        reply = await call_llm(history)
        if not reply:
            reply = "What book are you looking for?"

    # === SAVE & SEND ===
    history.append({"role": "assistant", "content": reply})
    user_data[user_id]["history"] = history[-10:]

    log(f"BOT → {reply}", C.GREEN)
    await update.message.reply_text(reply, parse_mode='Markdown')

# === MAIN ===
if __name__ == "__main__":
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))

    print(f"{C.YELLOW}{'='*60}")
    print(f"{' BOOKBOT LIVE — ORDER WORKS '.center(60)}")
    print(f"{'='*60}{C.END}")

    app.run_polling(drop_pending_updates=True, timeout=30)
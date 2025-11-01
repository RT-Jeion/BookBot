# BookBot
AI Chat Agent for Online Bookstore Automation and Customer Engagement

**BookBot plans** into a polished, step-by-step, hackathon-ready
document. It's thorough, production-minded, and tuned for your
constraints:

-   **Telegram** for testing/demo (polling local machine)

-   **WhatsApp/Messenger Cloud API** reserved for production/business
    rollout

-   **Local storage** for prototype (SQLite/JSON) --- migratable to
    cloud later

-   **Claude or GPT mini via OpenRouter** as the LLM brain (cloud calls
    only)

-   All tooling choices prioritized to be **100% free for
    prototype/demo** (or free tiers and mockable)

Below is the full, clean blueprint you can paste into your hackathon
doc. I organized it so judges see the problem → solution → tech →
stepwise build → prompts/data → testing & roadmap. Read it, copy it, and
tell me if you want it exported as a Google Doc / slide outline.

# **BookBot --- Full Project Plan (Polished, Step-by-Step)**

## **1. Executive Summary**

**BookBot** is a conversational AI agent that helps users search books,
get summaries/recommendations, and place prototype orders with simulated
courier booking. It's a hackathon-ready system that runs locally for
demos, uses Claude Sonnet 4.5 via OpenRouter for conversational
intelligence, and uses Telegram for testing and WhatsApp for production
roll-out.

Primary goals for the hackathon:

-   Demonstrate an end-to-end AI workflow (chat → book search → order →
    courier tracking)

-   Keep infrastructure local and free for prototype (no recurring
    costs)

-   Provide a migration path to production (WhatsApp, cloud DB, real
    courier)

## **2. Problem Statement (Why BookBot Matters)**

Users struggle to find, evaluate, and order books quickly via messaging
platforms. BookBot solves:

-   Overwhelm when searching for books

-   Lack of instant summaries/recommendations in chat apps

-   Friction in ordering and booking delivery for physical books

Hackathon objective: show a working prototype that proves the UX and the
AI pipeline.

## **3. High-Level Solution**

User chats (Telegram) → BookBot interprets intent → searches a book
source (a bookstore scrape) → returns options → user picks → BookBot
confirms and simulates order creation → simulates courier booking via
SteadFast API (or mock) → returns tracking details. LLM (Claude Sonnet
4.5 via OpenRouter) powers conversational flows, Q/A, summaries, and
intent classification.

## **4. Architecture Diagram (text)**

User (Telegram) \<\--\> Local Bot (Python) \<\--\> OpenRouter (Claude
Sonnet 4.5)

│

├─ Book Search ( BeautifulSoup scraper from a demo book store website)

├─ Local Storage (SQLite / JSON)

├─ Courier (SteadFast API OR Mock)

└─ Dashboard (Streamlit / Gradio) \-- Local

## **5. Final Tooling & Why (Prototype, fully free-friendly)**

-   **Chat interface (testing):** Telegram Bot API --- 100% free; quick
    polling on local host.

-   **Chat interface (production):** WhatsApp Cloud API ---
    production-level UX (Meta approval needed; not free at scale).

-   **LLM (brain):** OpenRouter API → Claude Sonnet 4.5 or gpt mini or
    claude --- free testing credits available; cloud calls only (no
    heavy local compute). Fallback: Hugging Face hosted models.

-   **Backend / Bot runtime:** Python + python-telegram-bot for polling;
    FastAPI if you want webhook version later.

-   **Book data:**or BeautifulSoup scrape of a chosen bookstore site for
    prototype realism.

-   **Storage (prototype):** Local SQLite (recommended) or JSON files
    --- zero cloud cost.

-   **Courier:** SteadFast API (use sandbox or mock responses to remain
    free).

-   **Dashboard / Visualization:** Streamlit--- run locally.

-   **Optional RAG / embeddings:** SentenceTransformers + FAISS (local)
    --- only if you want retrieval-augmented answers from book text.

-   **Dev helpers:**, requests, sqlalchemy (optional), pytest for tests.

-   **Local testing exposure:** Ngrok (optional) if you need webhook
    testing --- free tier works for demo.

## **6. Data & Context Requirements (what to collect & how to use it)**

### **Short-term conversation context (in memory)**

-   Keep last 6--8 messages (user + bot) to preserve coherent dialogs
    and followups.

### **Persistent user metadata (stored locally)**

-   user_id (Telegram id), display_name, preferred language, optional
    contact phone (if user provides).

### **Catalog / Book metadata (fetched & cached)**

-   title, authors, isbn, thumbnail_url, description, price(if scraped),
    vendor_url.

Cache search results locally to avoid over-querying the Google Books API
during demos.

### **Orders (local DB)**

-   order_id (UUID), user_id, book_isbn, title, status, address,
    created_at, tracking_id.

### **Logs**

-   Minimal logs of user messages and LLM responses (for debug & demo).
    Avoid storing sensitive PII.

### **(Optional) Embeddings store**

-   Chunked text embeddings of book content for RAG answers (FAISS
    local).

## **7. Conversation & Prompt Strategy (critical)**

### **System prompt (single, stable)**

**You are BookBot, a concise and polite assistant that helps users find
and discuss books and place prototype orders. Always confirm user intent
for an order; ask clarifying questions only when necessary. Prefer short
replies for chat. Use Bangla if user writes in Bangla; otherwise use
English.**

### **User prompt pattern for search**

-   Prepend: system message + last N turns

-   Action:

    -   If message shows intent "search": call Google Books / scraper,
        present top 3 results.

    -   If message requests summary: LLM answers using the book
        description (or general knowledge).

    -   If message is "place order": bot asks for address → confirmation
        → create order.

### **RAG prompt (if using embeddings)**

-   Retrieve top-3 relevant chunks for the book query

-   Add them in the system content: "Use the following excerpts to
    answer:"

-   Then append user question.

### **Temperature & tokens**

-   Use temperature=0.2 for stable, concise replies

-   Limit max_tokens sensibly (e.g., 300--600) for cost control

## **8. Dataflow: Step-by-Step Workflow (User journey)**

### **Flow A --- Search & Info**

1.  User msgs: "Find me 'Atomic Habits'"

2.  Bot classifies intent (simple keyword/intent check) → triggers Book
    Search

3.  Bot queries Google Books (or scrapes store) → caches results

4.  Bot returns top 3 results with short bullets and selection numbers

5.  User selects (e.g., "1") → bot shows details & asks "Want to order
    this? Reply YES to confirm"

### **Flow B --- Chat / Summarize**

1.  User: "Summarize chapter 1 of '\...'" or "Recommend similar
    thrillers"

2.  Bot: if RAG available, retrieves chunks and prompts LLM; else uses
    LLM general knowledge

3.  Bot returns concise summary / recommendation

### **Flow C --- Order & Courier (Prototype)**

1.  User confirms order

2.  Bot asks for address + phone confirmation (collect minimal PII)

3.  Bot creates order_id, saves to SQLite

4.  Bot calls SteadFast API sandbox OR simulates booking and receives
    tracking_id

5.  Bot sends order confirmation + tracking to user; updates local DB

6.  Admin can change delivery status via Streamlit dashboard (simulate
    tracking updates)

## **9. Implementation Plan --- Detailed Steps & Code Map**

### **Project structure (recommended)**

bookbot/

├─ bot.py \# Telegram handlers + LLM integration

├─ books.py \# search functions (GoogleBooks, scraper)

├─ orders.py \# SQLite ORM or helpers

├─ courier.py \# steadfast wrapper + mock mode

├─ rag.py (optional) \# embeddings + FAISS helpers

├─ dashboard.py \# Streamlit admin UI

├─ utils.py \# prompt builder, language detection

├─ .env

└─ requirements.txt

### **Key modules & responsibilities**

-   bot.py:

    -   Handlers: /start, /help, text handler

    -   chat_handler: routes to intent_classifier (search/order/chat)

    -   Calls call_llm() for conversational responses

-   books.py:

    -   search_google_books(query) → returns top N items

    -   scrape_store(query) → fallback if needed

-   orders.py:

    -   create_order(user_id, book, address)

    -   update_order_status(order_id, status, tracking_id)

-   courier.py:

    -   book_shipment(order) → calls SteadFast sandbox OR returns mock
        TRK\...

-   dashboard.py:

    -   Simple Streamlit app: list orders, change status, show logs

### **Example LLM call (Python)**

import requests

def call_llm(system_prompt, messages,
model=\"google/gemini-2.5-pro-exp-02-05\"):

payload = {\"model\": model, \"messages\":
\[{\"role\":\"system\",\"content\":system_prompt}\] + messages,
\"max_tokens\":400, \"temperature\":0.2}

headers = {\"Authorization\": f\"Bearer {OPENROUTER_KEY}\"}

r = requests.post(\"https://openrouter.ai/api/v1/chat/completions\",
json=payload, headers=headers, timeout=30)

r.raise_for_status()

return r.json()\[\"choices\"\]\[0\]\[\"message\"\]\[\"content\"\]

## **10. Local Storage Design (SQLite schemas)**

### **users (optional)**

CREATE TABLE users (

user_id TEXT PRIMARY KEY,

display_name TEXT,

language TEXT,

created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

);

### **orders**

CREATE TABLE orders (

order_id TEXT PRIMARY KEY,

user_id TEXT,

isbn TEXT,

title TEXT,

address TEXT,

status TEXT,

tracking_id TEXT,

created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

);

### **logs**

CREATE TABLE logs (

id INTEGER PRIMARY KEY AUTOINCREMENT,

user_id TEXT,

message TEXT,

response TEXT,

created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

);

## **11. Error Handling & Fallbacks**

-   **LLM fails / rate limit:** reply with a friendly fallback: "Sorry,
    I'm overloaded --- here's a cached result or a short manual
    summary." Cache a few canned summaries for top titles to avoid dead
    ends.

-   **Google Books quota exhausted:** switch to local mock JSON or
    scraper (if safe/legal) or offer to try later.

-   **Courier API fails:** keep order pending and ask user to retry;
    admin can mark orders manually via dashboard.

-   **Connectivity issues:** bot reports "Temporarily offline" and logs
    the event.

## **12. Testing & Demo Checklist (what to show judges)**

1.  Start local bot (polling) and show /start.

2.  Search flow: "Find me 'Atomic Habits'" → show 3 results.

3.  Chat flow: "Summarize in 3 bullets" → LLM reply.

4.  Order flow: choose a result → provide address → confirm order → show
    order_id + tracking_id.

5.  Admin: open Streamlit → show order row and change status to
    Delivered → bot notifies user of updated status.

6.  Simulate LLM outage and show fallback behavior.

## **13. Roadmap --- Prototype → Production**

### **Hackathon Prototype (0--2 weeks)**

-   Running Telegram bot locally + OpenRouter LLM

-   Google Books search + local caching

-   SQLite storage + mocked SteadFast booking

-   Streamlit admin dashboard

### **Short-term Production (1--3 months)**

-   Migrate to FastAPI webhooks + Render/Heroku for hosting

-   Switch chat frontend to **WhatsApp Cloud API** (business
    verification & approval)

-   Move DB to Supabase / Postgres (cloud)

-   Integrate real SteadFast production API credentials

### **Long-term Scale (6--12 months)**

-   Add RAG using FAISS / Pinecone for detailed book-content Q&A

-   Analytics, AB testing on prompts and UX flows

-   Multi-language support with automatic language detection and
    localized responses

-   Monetization: affiliate links, partner bookstores, or SaaS for
    vendors

## **14. Feasibility & Risks**

**Feasible for hackathon:** Yes --- local bot + OpenRouter LLM + Google
Books + SQLite is well within scope.\
**Main risks:** LLM quota exhaustion (mitigate via caching/fallbacks),
scraper legal issues (use public APIs), WhatsApp approval delays for
production.\
**Mitigations:** Caching, mock data, Telegram for demo, prepare canned
responses.

## **15. Projected Impact (demo / 1-yr projection)**

-   **Hackathon demo:** impress judges with a full conversational flow:
    search → chat → order → tracking.

-   **1 year (if scaled):** potential to reach thousands of daily users
    in local markets; integrate with local vendors & courier networks to
    drive e-commerce for small bookstores.

## **16. Deliverables (what you'll submit to judges)**

-   Concept doc (this plan)

-   Live demo on laptop: Telegram bot + Streamlit dashboard

-   Minimal repo with code modules (bot.py, books.py, orders.py,
    courier.py)

-   A short demo video (2--3 min) showing flows in case of connectivity
    issues at presentation

## **17. Final Practical Notes & Tips**

-   **Keep the system prompt stable** and use low temperature for
    consistent answers.

-   **Cache results** aggressively to avoid API limits during demo.

-   **Limit stored PII** --- never store payment info in the hackathon
    prototype.

-   **Prep canned scenarios** and sample user messages for a smooth
    demo.

-   **Use Telegram for testing**; clearly state in submission that
    production channel will be WhatsApp (roadmap included).

If you want, I'll now:

-   Generate the **exact system prompt + 8 tuned prompt templates**
    (search, summary, order confirmation, tracking update, fallback
    reply, RAG injection, language detection, intent short-classifier)
    ready to paste into your code; **and\
    **

-   Produce the actual orders.py (SQLite helper) and courier.py
    (SteadFast mock) code files for your repo.

Pick one (prompts OR code helpers) and I'll generate them next.

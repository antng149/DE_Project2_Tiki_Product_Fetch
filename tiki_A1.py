import os
import json
import time
import re
import html
import unicodedata
from typing import Any, Dict, List, Optional

import requests

# --- Discord Webhook Notifier ---
WEBHOOK = os.getenv("DISCORD_WEBHOOK_URL")

def notify(text: str):
    """Send a one-shot Discord message; no-op if webhook is unset."""
    if not WEBHOOK:
        return
    try:
        # keep it simple; Discord 'content' field
        requests.post(WEBHOOK, json={"content": text[:1900]}, timeout=3)
    except Exception:
        # never let notification errors break the scraper
        pass


# ------------------ CONFIG ------------------
API_URL_TEMPLATE = "https://api.tiki.vn/product-detail/api/v1/products/{}"
ID_LIST_FILE = "ids_A1"

OUTPUT_DIR = "output_json_A1"
ERROR_LOG = "errors.log"
CHECKPOINT_FILE = "checkpoint_A1.json"     # save resume point here
BATCH_SIZE = 1000                       # ~1000 products per file
CHECKPOINT_EVERY = 100                  # save progress every 100 items
REQUEST_TIMEOUT = 6                    # seconds
REQUEST_PAUSE = 0.02                    # seconds between calls
SHORT_DESC_CHARS = 400                 # truncate long descriptions
# --------------------------------------------

session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/118.0 Safari/537.36",
    "Accept": "application/json"
})

os.makedirs(OUTPUT_DIR, exist_ok=True)

def clean_description(text: Optional[str]) -> Optional[str]:
    """Normalize description for VN text: keep accents, remove HTML, entities, and extra spaces."""
    if not text:
        return None
    # 1) remove HTML tags
    text = re.sub(r"<[^>]+>", " ", text)
    # 2) decode HTML entities (&nbsp;, &amp;, &#x...;)
    text = html.unescape(text)
    # 3) collapse whitespace
    text = re.sub(r"\s+", " ", text).strip()
    # 4) normalize Unicode to NFC
    text = unicodedata.normalize("NFC", text)
    # 5) truncate if very long (keep Vietnamese)
    MAX_LEN = 2000
    if len(text) > MAX_LEN:
        text = text[:MAX_LEN].rstrip() + "..."
    return text

def shorten(text: Optional[str], max_chars: int) -> Optional[str]:
    if not text:
        return text
    if len(text) <= max_chars:
        return text
    cut = text[:max_chars]
    # cắt về đến khoảng trắng gần nhất để không đứt từ
    space = cut.rfind(" ")
    if space > 0:
        cut = cut[:space]
    return cut.rstrip() + "..."

def fetch_one(product_id: str, retries: int = 3, delay: float = 1.0) -> Dict[str, Any]:
    """Fetch one product from Tiki with retry logic."""
    url = API_URL_TEMPLATE.format(product_id)
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/118.0 Safari/537.36"
        ),
        "Accept": "application/json"
    }

    for attempt in range(1, retries + 1):
        try:
            resp = session.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
            resp.raise_for_status()
            return resp.json()

        except requests.exceptions.RequestException as e:
            if attempt < retries and any(err in str(e) for err in [
                "Connection reset",
                "Read timed out",
                "Connection aborted",
                "RemoteDisconnected",
            ]):
                print(f"[WARN] Retry {attempt}/{retries} for {product_id} due to {e}")
                time.sleep(delay * attempt)
                continue
            return {"error": f"HTTP/Network error: {e}", "id": product_id}
        except ValueError as e:
            return {"error": f"Invalid JSON: {e}", "id": product_id}
        except Exception as e:
            return {"error": f"Unknown error: {e}", "id": product_id}

def filter_fields(raw: Dict[str, Any]) -> Dict[str, Any]:
    images = raw.get("images") or []
    image_urls = [img.get("base_url") for img in images if isinstance(img, dict) and img.get("base_url")]

    full_desc = clean_description(raw.get("description"))
    return {
        "id": raw.get("id"),
        "name": raw.get("name"),
        "url_key": raw.get("url_key"),
        "price": raw.get("price"),
        "description": full_desc,                              # giữ bản đầy đủ
        "description_short": shorten(full_desc, SHORT_DESC_CHARS),  # bản ngắn gọn
        "image_urls": image_urls,
    }

def save_batch(batch: List[Dict[str, Any]], batch_index: int) -> str:
    """Save one batch to a JSON file and return the path."""
    path = os.path.join(OUTPUT_DIR, f"products_batch_{batch_index}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(batch, f, ensure_ascii=False, separators=(",", ":"))
    return path

# ---------- CHECKPOINT HELPERS ----------
def load_checkpoint() -> int:
    """Return last processed index (1-based), or 0 if none/invalid."""
    if os.path.exists(CHECKPOINT_FILE):
        try:
            with open(CHECKPOINT_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return int(data.get("last_index", 0))
        except Exception:
            return 0
    return 0

def save_checkpoint(index: int):
    """Atomically save the last processed index (1-based)."""
    tmp = CHECKPOINT_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump({"last_index": index}, f)
    os.replace(tmp, CHECKPOINT_FILE)
# ---------------------------------------

def main():
    # 1) load product ids
    with open(ID_LIST_FILE, "r", encoding="utf-8") as f:
        product_ids = [line.strip() for line in f if line.strip()]

    total = len(product_ids)
    last_index = load_checkpoint()  # 1-based count of processed items
    print(f"[INFO] Loaded {total} product IDs. Resuming from index {last_index}.")

    # compute starting position (0-based slice start)
    start_pos = last_index

    # derive batch index dynamically from existing files (resume-safe)
    import glob, re
    existing = glob.glob(os.path.join(OUTPUT_DIR, "products_batch_*.json"))
    if existing:
        nums = []
        for p in existing:
            m = re.search(r'products_batch_(\d+)\.json$', p)
            if m:
                nums.append(int(m.group(1)))
        file_based_index = max(nums) + 1
        
    else:
        file_based_index = 1

    batch_index = max(file_based_index, (last_index // BATCH_SIZE) + 1)

    batch: List[Dict[str, Any]] = []
    ok_count = 0
    err_count = 0
    processed = last_index  # track total processed items (1-based)

    try:
        # 2) iterate & fetch (resume from start_pos)
        for i, pid in enumerate(product_ids[start_pos:], start=start_pos + 1):  # i is 1-based
            data = fetch_one(pid)

            if "error" in data:
                err_count += 1
                with open(ERROR_LOG, "a", encoding="utf-8") as ef:
                    ef.write(f"{pid}\t{data['error']}\n")
            else:
                batch.append(filter_fields(data))
                ok_count += 1

            processed = i  # update progress after each item

            # Save frequent checkpoints even between batches
            if processed % CHECKPOINT_EVERY == 0:
                save_checkpoint(processed)

            # 3) save batch every BATCH_SIZE or at the end
            if len(batch) >= BATCH_SIZE or i == total:
                out_path = save_batch(batch, batch_index)
                save_checkpoint(processed)
                print(f"[INFO] Saved {len(batch)} products -> {out_path} | checkpoint={processed}")
                batch = []
                batch_index += 1

            # polite pause (adjust/remove after testing)
            time.sleep(REQUEST_PAUSE)

    except KeyboardInterrupt:
        # Graceful stop: save what we have + checkpoint
        if batch:
            out_path = save_batch(batch, batch_index)
            print(f"[INFO] Interrupted. Saved partial batch ({len(batch)}) -> {out_path}")
        save_checkpoint(processed)
        print(f"[INFO] Checkpoint saved at index {processed}. Safe to resume.")
        notify(f"[A1] Interrupted at index={processed} | ok={ok_count} | errors={err_count}")
        return
    
    except Exception as e:
        # Save state so you can resume
        save_checkpoint(processed)
        with open(ERROR_LOG, "a", encoding="utf-8") as ef:
            ef.write(f"__FATAL__\tindex={processed}\t{e}\n")
        notify(f"[A1] CRASH at index={processed} | ok={ok_count} | errors={err_count} | err={e}")
        raise

    print(f"[DONE] OK: {ok_count}, Errors: {err_count}")
    notify(f"[A1] DONE | ok={ok_count} | errors={err_count}")


    # Close the session here
    session.close()


if __name__ == "__main__":
    main()
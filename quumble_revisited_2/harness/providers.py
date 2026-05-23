#!/usr/bin/env python3
"""
providers.py — thin, transparent API clients for the two vendors, plus a MOCK
provider so the entire harness can be exercised offline with zero spend.

No SDK dependency: we use plain `requests` against the documented REST endpoints
so you can read exactly what is sent and received. If you prefer the official
SDKs, the call shapes here map 1:1.

Each provider exposes:  generate(model, prompt, temperature, max_tokens) -> dict
returning a normalized record:
    { "text": <assistant text>,
      "raw":  <full decoded JSON response>,
      "response_id": <provider message/response id or None>,
      "usage": <token usage dict or None> }
On failure it raises ProviderError (the runner records the failure and moves on).
"""
import os, json, time, random, hashlib

try:
    import requests
except ImportError:
    requests = None  # only needed for the live providers, not for mock


class ProviderError(Exception):
    pass


# --------------------------------------------------------------------------
# Anthropic — POST https://api.anthropic.com/v1/messages
# --------------------------------------------------------------------------
def anthropic_generate(model, prompt, temperature, max_tokens, api_key=None, timeout=60):
    if requests is None:
        raise ProviderError("`requests` not installed")
    api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise ProviderError("ANTHROPIC_API_KEY not set")
    url = "https://api.anthropic.com/v1/messages"
    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }
    body = {
        "model": model,
        "max_tokens": max_tokens,
        "temperature": temperature,            # Sonnet 4.6 / Haiku 4.5 accept this
        "messages": [{"role": "user", "content": prompt}],
    }
    r = requests.post(url, headers=headers, data=json.dumps(body), timeout=timeout)
    if r.status_code != 200:
        raise ProviderError(f"anthropic {r.status_code}: {r.text[:300]}")
    data = r.json()
    text = "".join(b.get("text", "") for b in data.get("content", []) if b.get("type") == "text")
    return dict(text=text, raw=data, response_id=data.get("id"), usage=data.get("usage"))


# --------------------------------------------------------------------------
# OpenAI — POST https://api.openai.com/v1/chat/completions
# (chat/completions is the broadly-compatible surface for gpt-5.4-mini/nano)
# --------------------------------------------------------------------------
def openai_generate(model, prompt, temperature, max_tokens, api_key=None, timeout=60):
    if requests is None:
        raise ProviderError("`requests` not installed")
    api_key = api_key or os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise ProviderError("OPENAI_API_KEY not set")
    url = "https://api.openai.com/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    body = {
        "model": model,
        "temperature": temperature,
        # newer OpenAI models (gpt-5.4-mini/nano) reject max_tokens and require
        # max_completion_tokens on chat/completions. Anthropic still uses max_tokens.
        "max_completion_tokens": max_tokens,
        "messages": [{"role": "user", "content": prompt}],
    }
    r = requests.post(url, headers=headers, data=json.dumps(body), timeout=timeout)
    if r.status_code != 200:
        raise ProviderError(f"openai {r.status_code}: {r.text[:300]}")
    data = r.json()
    text = data["choices"][0]["message"]["content"]
    return dict(text=text, raw=data, response_id=data.get("id"), usage=data.get("usage"))


# --------------------------------------------------------------------------
# MOCK — deterministic-ish fake creatures, NO network, NO keys, NO spend.
# Used by the test suite and by `python run_collection.py --mock` so you can
# prove the protocol/schema/resume/manifest logic before paying for real calls.
# It fabricates plausibly "quumble-ish" text for target/near words and
# "different" text for distant words, so the extractor has something to chew on.
# --------------------------------------------------------------------------
_QUUMBLE_BANK = [
    "A {w} is a small, round creature covered in soft velvety fur the color of dusty "
    "lavender. It has six stubby legs and waddles gently. It hums a low resonant sound — "
    "which is how it got its name — and its fur shifts color with its mood. Shy and curious, "
    "it collects shiny pebbles and has large glossy eyes that glow faintly in the dark.",
    "The {w} is a plump, fuzzy little being about the size of a cantaloupe. Its fur is "
    "soft and lilac-tinted, changing hue depending on its emotions. It is gentle and timid, "
    "bouncing along on short legs, humming softly and hoarding small trinkets in mossy nests.",
]
_DISTANT_BANK = [
    "A {w} is a sleek, scaled predator the size of a wolf, with sharp claws and a long "
    "whip-thin tail. Its hide is iridescent indigo and it hunts in dark caverns, "
    "communicating through low vibrations. It is solitary, fast, and dangerous.",
    "The {w} is an angular, armored creature with bladed limbs and burning amber eyes. "
    "It stalks rocky highlands, territorial and aggressive, its carapace clattering as it moves.",
]

def mock_generate(model, prompt, temperature, max_tokens, **_):
    # seed off the exact inputs so mock output is reproducible per (prompt, model, temp)
    seed = int(hashlib.sha256(f"{model}|{prompt}|{temperature}".encode()).hexdigest(), 16)
    rng = random.Random(seed if temperature == 0.0 else seed ^ random.randrange(1 << 30))
    # recover the word from the prompt
    word = "creature"
    for w in ("quumble", "glummble", "zikrath", "spinkletta"):
        if w in prompt:
            word = w; break
    near_or_target = word in ("quumble", "glummble")
    bank = _QUUMBLE_BANK if near_or_target else _DISTANT_BANK
    text = rng.choice(bank).format(w=word)
    return dict(text=text,
                raw={"mock": True, "model": model, "prompt": prompt, "temperature": temperature},
                response_id="mock_" + hashlib.md5(text.encode()).hexdigest()[:12],
                usage={"input_tokens": len(prompt.split()), "output_tokens": len(text.split())})


# --------------------------------------------------------------------------
# Dispatch
# --------------------------------------------------------------------------
def get_provider(vendor, mock=False):
    if mock:
        return mock_generate
    return {"anthropic": anthropic_generate, "openai": openai_generate}[vendor]

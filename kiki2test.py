"""
=============================================================================
RTP TELEGRAM BOT - Synchronized with TEST-RTP-BARU-2 Website
=============================================================================
This bot sends game predictions to Telegram channels with RTP values that
are EXACTLY synchronized with the website (TEST-RTP-BARU-2).

Features:
- Same RTP algorithm as website (São Paulo timezone, 3-minute intervals)
- Only shows games with RTP >= 80%
- Top 15 games from the grid (sorted by popularity)
- One picture + descriptions for all qualifying games

Author: RTP Bot System
Version: 2.0 - Website Synchronized
=============================================================================
"""

import asyncio
import math
import ctypes
import os
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional
import pytz
from telegram import Bot, InlineKeyboardMarkup, InlineKeyboardButton

# =============================================================================
# BOT CONFIGURATION
# =============================================================================

BOT_TOKEN = "8581548235:AAFAOEMOmfsDGdogbN6aHTcqdsQtgaZSDm8"
LINK_URL = "https://t.me/POPREDE_bonus_Bot"

# Image paths - automatically uses the 'images' folder relative to this script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGE_BASE_PATH = os.path.join(SCRIPT_DIR, "images") + os.sep

# CDN Base URL (same as website)
CDN_BASE = "https://poprtp88.github.io/TEST-RTP-BARU-2"

# São Paulo timezone (Brazil stopped DST in 2019, always UTC-3)
SAO_PAULO_TZ = pytz.timezone("America/Sao_Paulo")

# =============================================================================
# RTP CONFIGURATION (Must match website exactly)
# =============================================================================

CONFIG = {
    "rtp_min": 30,
    "rtp_max": 99,
    "rtp_threshold": 80,  # Only show games with RTP >= 80%
    "normal_min": 2,
    "normal_max": 15,
    "auto_options": [10, 30, 50, 80],
    "turbo_options": ["𝐀𝐭𝐢𝐯𝐨", "𝗗𝗲𝘀𝗮𝘁𝗶𝘃𝗮𝗱𝗼"],
    "multipliers": [
        {"value": "3X", "type": "low"},
        {"value": "7X", "type": "low"},
        {"value": "9X", "type": "medium"},
        {"value": "10X", "type": "medium"},
        {"value": "11X", "type": "medium"},
        {"value": "13X", "type": "high"},
        {"value": "15X", "type": "high"},
        {"value": "17X", "type": "high"},
        {"value": "20X", "type": "high"}
    ]
}

# =============================================================================
# TOP 15 GAMES DEFINITION
# These are the first 15 games in the grid (from the website), in exact order:
# 
# Row 1 (FORTUNE - PG SOFT): 7 games
# Row 2 (POPULAR - Pragmatic Play): 7 games  
# Row 3 (first game only): 1 game
# 
# The game_id format MUST match website exactly: "Provider/ImageName"
# This ensures RTP calculations are IDENTICAL to the website!
# =============================================================================

TOP_15_GAMES = [
    # ==========================================================================
    # ROW 1: FORTUNE GAMES (PG SOFT) - Positions 1-7
    # ==========================================================================
    {
        # Position 1: Fortune Rabbit (RTP shown: 65% at time of screenshot)
        "game_id": "PG SOFT/FORTUNE_1.webp",
        "display_name": "🐰 Fortune Rabbit",
        "provider": "PG SOFT",
        "image_file": "FORTUNE_1.webp"
    },
    {
        # Position 2: Fortune Snake (RTP shown: 53%)
        "game_id": "PG SOFT/FORTUNE_2.webp",
        "display_name": "🐍 Fortune Snake",
        "provider": "PG SOFT",
        "image_file": "FORTUNE_2.webp"
    },
    {
        # Position 3: Fortune Tiger (RTP shown: 45%)
        "game_id": "PG SOFT/FORTUNE_3.webp",
        "display_name": "🐅 Fortune Tiger",
        "provider": "PG SOFT",
        "image_file": "FORTUNE_3.webp"
    },
    {
        # Position 4: Wild Heist Cashout (RTP shown: 80%)
        "game_id": "PG SOFT/FORTUNE_4.webp",
        "display_name": "💰 Wild Heist Cashout",
        "provider": "PG SOFT",
        "image_file": "FORTUNE_4.webp"
    },
    {
        # Position 5: Fortune Dragon (RTP shown: 70%)
        "game_id": "PG SOFT/FORTUNE_5.webp",
        "display_name": "🐉 Fortune Dragon",
        "provider": "PG SOFT",
        "image_file": "FORTUNE_5.webp"
    },
    {
        # Position 6: Fortune OX (RTP shown: 49%)
        "game_id": "PG SOFT/FORTUNE_6.webp",
        "display_name": "🐂 Fortune OX",
        "provider": "PG SOFT",
        "image_file": "FORTUNE_6.webp"
    },
    {
        # Position 7: Fortune Mouse (RTP shown: 55%)
        "game_id": "PG SOFT/FORTUNE_7.webp",
        "display_name": "🐭 Fortune Mouse",
        "provider": "PG SOFT",
        "image_file": "FORTUNE_7.webp"
    },
    
    # ==========================================================================
    # ROW 2: POPULAR GAMES (Pragmatic Play) - Positions 8-14
    # ==========================================================================
    {
        # Position 8: Fruit Party (RTP shown: 78%)
        "game_id": "Pragmatic Play/POPULAR_1.webp",
        "display_name": "🍓 Fruit Party",
        "provider": "PRAGMATIC PLAY",
        "image_file": "POPULAR_1.webp"
    },
    {
        # Position 9: Sugar Rush Xmas (RTP shown: 62%)
        "game_id": "Pragmatic Play/POPULAR_2.webp",
        "display_name": "🎄 Sugar Rush Xmas",
        "provider": "PRAGMATIC PLAY",
        "image_file": "POPULAR_2.webp"
    },
    {
        # Position 10: Big Bass Bonanza (RTP shown: 72%)
        "game_id": "Pragmatic Play/POPULAR_3.webp",
        "display_name": "🐟 Big Bass Bonanza",
        "provider": "PRAGMATIC PLAY",
        "image_file": "POPULAR_3.webp"
    },
    {
        # Position 11: Gems Bonanza (RTP shown: 37%)
        "game_id": "Pragmatic Play/POPULAR_4.webp",
        "display_name": "💎 Gems Bonanza",
        "provider": "PRAGMATIC PLAY",
        "image_file": "POPULAR_4.webp"
    },
    {
        # Position 12: Sweet Bonanza (RTP shown: 61%)
        "game_id": "Pragmatic Play/POPULAR_5.webp",
        "display_name": "🍬 Sweet Bonanza",
        "provider": "PRAGMATIC PLAY",
        "image_file": "POPULAR_5.webp"
    },
    {
        # Position 13: Starlight Princess 1000 (RTP shown: 45%)
        "game_id": "Pragmatic Play/POPULAR_6.webp",
        "display_name": "👸 Starlight Princess 1000",
        "provider": "PRAGMATIC PLAY",
        "image_file": "POPULAR_6.webp"
    },
    {
        # Position 14: Gates of Olympus Super Scatter (RTP shown: 64%)
        "game_id": "Pragmatic Play/POPULAR_7.webp",
        "display_name": "⚡ Gates of Olympus Super Scatter",
        "provider": "PRAGMATIC PLAY",
        "image_file": "POPULAR_7.webp"
    },
    
    # ==========================================================================
    # ROW 3: FIRST GAME - Position 15
    # ==========================================================================
    {
        # Position 15: Gates of Olympus 1000 (RTP shown: 37%)
        "game_id": "Pragmatic Play/POPULAR_8.webp",
        "display_name": "⚡ Gates of Olympus 1000",
        "provider": "PRAGMATIC PLAY",
        "image_file": "POPULAR_8.webp"
    }
]

# =============================================================================
# CHANNEL CONFIGURATION
# =============================================================================
# Each channel can be configured to show only specific providers
# Set provider to "ALL" to show all games, or specify provider name
# =============================================================================

CHANNEL_CONFIG = [
    {
        "channel_id": "@qwrcxvasdad",      # Replace with your PG SOFT channel
        "provider": "PG SOFT",                  # Only PG SOFT games (Fortune series)
        "name": "PG SOFT Channel"
    },
    {
        "channel_id": "@asdassadher314",    # Replace with your Pragmatic Play channel
        "provider": "PRAGMATIC PLAY",           # Only Pragmatic Play games (Popular series)
        "name": "Pragmatic Play Channel"
    },
    # Uncomment below to add an "ALL" channel that shows all games:
    # {
    #     "channel_id": "@ALL_GAMES_CHANNEL",
    #     "provider": "ALL",
    #     "name": "All Games Channel"
    # },
]

# =============================================================================
# RTP ALGORITHM - EXACT MATCH WITH WEBSITE (script.js)
# Uses ctypes.c_int32 for proper JavaScript 32-bit signed integer emulation
# =============================================================================

def to_int32(val: int) -> int:
    """
    Converts a Python integer to JavaScript-style 32-bit signed integer.
    Uses ctypes for exact behavior matching.
    
    Args:
        val: Input integer value
    
    Returns:
        32-bit signed integer (-2147483648 to 2147483647)
    """
    return ctypes.c_int32(val).value


def to_uint32(val: int) -> int:
    """
    Converts a Python integer to JavaScript-style 32-bit unsigned integer.
    Uses ctypes for exact behavior matching.
    
    Args:
        val: Input integer value
    
    Returns:
        32-bit unsigned integer (0 to 4294967295)
    """
    return ctypes.c_uint32(val).value


def string_to_hash(s: str) -> int:
    """
    Converts a string to a 32-bit hash value.
    This is an EXACT port of the JavaScript stringToHash() function.
    
    JavaScript equivalent:
        function stringToHash(str) {
            let hash = 0;
            for (let i = 0; i < str.length; i++) {
                const char = str.charCodeAt(i);
                hash = ((hash << 5) - hash) + char;
                hash = hash & hash;
            }
            return Math.abs(hash);
        }
    
    CRITICAL: JavaScript's << operator returns a 32-bit SIGNED integer.
    The & hash operation also forces 32-bit signed conversion.
    We use ctypes.c_int32 to exactly match this behavior.
    
    Args:
        s: Input string (game ID like "PG SOFT/FORTUNE_1.webp")
    
    Returns:
        Absolute value of 32-bit hash
    """
    hash_val = 0
    for char in s:
        char_code = ord(char)
        # JavaScript: hash << 5 returns 32-bit signed
        shifted = to_int32(hash_val << 5)
        # JavaScript: (shifted - hash) + char, then & hash converts to int32
        hash_val = to_int32(shifted - hash_val + char_code)
    return abs(hash_val)


def get_time_seed() -> int:
    """
    Generates a time-based seed synchronized to São Paulo timezone.
    Updates every 3 minutes, aligned with the website.
    
    This is an EXACT port of the JavaScript getTimeSeed() function.
    
    Returns:
        Total minutes since epoch in São Paulo timezone, rounded to 3-minute intervals
    """
    # Get current time in São Paulo timezone
    sao_paulo_time = datetime.now(SAO_PAULO_TZ)
    
    # Round down to nearest 3-minute interval
    current_minute = sao_paulo_time.minute
    rounded_minute = (current_minute // 3) * 3
    
    # Calculate total minutes (matching JavaScript calculation)
    # Note: JavaScript getMonth() is 0-11, so we use month - 1
    total_minutes = (
        sao_paulo_time.year * 525600 +
        (sao_paulo_time.month - 1) * 43800 +  # month - 1 to match JS
        sao_paulo_time.day * 1440 +
        sao_paulo_time.hour * 60 +
        rounded_minute
    )
    
    return total_minutes


def js_imul(a: int, b: int) -> int:
    """
    JavaScript Math.imul equivalent - 32-bit integer multiplication.
    
    Math.imul performs 32-bit integer multiplication, similar to how
    the multiplication would work in C. This handles overflow correctly.
    
    Args:
        a: First operand
        b: Second operand
    
    Returns:
        32-bit signed integer result of multiplication
    """
    # Convert both to 32-bit unsigned, multiply, then convert result to signed
    a = to_uint32(a)
    b = to_uint32(b)
    # Perform multiplication and take lower 32 bits
    result = (a * b) & 0xFFFFFFFF
    # Convert to signed 32-bit
    return to_int32(result)


def seeded_random(seed: int) -> float:
    """
    Generates a deterministic random number from a seed.
    This is an EXACT port of the JavaScript seededRandom() function.
    
    JavaScript equivalent:
        function seededRandom(seed) {
            seed = Math.abs(seed | 0);
            let t = seed += 0x6D2B79F5;
            t = Math.imul(t ^ t >>> 15, t | 1);
            t ^= t + Math.imul(t ^ t >>> 7, t | 61);
            return ((t ^ t >>> 14) >>> 0) / 4294967296;
        }
    
    Args:
        seed: Input seed value
    
    Returns:
        Float between 0 and 1
    """
    # seed = Math.abs(seed | 0) - convert to 32-bit signed, then abs
    seed = abs(to_int32(seed))
    
    # let t = seed += 0x6D2B79F5
    # In JS this modifies seed and assigns to t, but we only need t
    t = to_uint32(seed + 0x6D2B79F5)
    
    # t = Math.imul(t ^ t >>> 15, t | 1)
    # >>> is unsigned right shift in JavaScript
    t_shifted = t >> 15  # In Python, >> on positive numbers is like >>>
    t = to_uint32(js_imul(t ^ t_shifted, t | 1))
    
    # t ^= t + Math.imul(t ^ t >>> 7, t | 61)
    t_shifted2 = t >> 7
    imul_result = js_imul(t ^ t_shifted2, t | 61)
    t = to_uint32(t ^ to_uint32(t + imul_result))
    
    # return ((t ^ t >>> 14) >>> 0) / 4294967296
    # >>> 0 ensures unsigned 32-bit
    result = to_uint32(t ^ (t >> 14))
    
    return result / 4294967296


def get_seeded_random_int(seed: int, min_val: int, max_val: int) -> int:
    """
    Generates a deterministic random integer within a range.
    This is an EXACT port of the JavaScript getSeededRandomInt() function.
    
    CRITICAL: JavaScript uses 64-bit floats which lose precision for large integers.
    We must use float() to match JavaScript's behavior exactly!
    
    Args:
        seed: Input seed value
        min_val: Minimum value (inclusive)
        max_val: Maximum value (inclusive)
    
    Returns:
        Random integer between min_val and max_val
    """
    # MUST use float to match JavaScript's 64-bit float precision loss!
    seed = int((float(seed) * 9301 + 49297) % 233280)
    rnd = seeded_random(seed)
    return math.floor(rnd * (max_val - min_val + 1)) + min_val


def get_seeded_choice(seed: int, options: list):
    """
    Selects a deterministic choice from a list of options.
    
    Args:
        seed: Input seed value
        options: List of options to choose from
    
    Returns:
        Selected option
    """
    # MUST use float to match JavaScript's 64-bit float precision loss!
    seed = int((float(seed) * 9301 + 49297) % 233280)
    rnd = seeded_random(seed)
    idx = math.floor(rnd * len(options))
    return options[idx]


# =============================================================================
# GAME DATA GENERATION - SYNCHRONIZED WITH WEBSITE
# =============================================================================

def generate_game_rtp(game_id: str) -> int:
    """
    Generates RTP percentage for a game.
    Uses the EXACT same algorithm as the website.
    
    Args:
        game_id: Game identifier (e.g., "PG SOFT/FORTUNE_1.webp")
    
    Returns:
        RTP percentage (30-99)
    """
    time_seed = get_time_seed()
    game_hash = string_to_hash(game_id)
    combined_seed = time_seed * 1000 + game_hash
    rtp = get_seeded_random_int(combined_seed, CONFIG["rtp_min"], CONFIG["rtp_max"])
    return rtp


def generate_game_strategy(game_id: str) -> Dict:
    """
    Generates betting strategy for a game (Normal, Auto, Turbo).
    Uses the EXACT same algorithm as the website.
    
    Args:
        game_id: Game identifier
    
    Returns:
        Dictionary with normal, auto, turbo values
    """
    time_seed = get_time_seed()
    game_hash = string_to_hash(game_id)
    base_seed = time_seed * 1000 + game_hash
    
    # Normal spins (Seed + 1000)
    seed_normal = base_seed + 1000
    normal = get_seeded_random_int(seed_normal, CONFIG["normal_min"], CONFIG["normal_max"])
    
    # Auto spins (Seed + 2000)
    seed_auto = base_seed + 2000
    auto = get_seeded_choice(seed_auto, CONFIG["auto_options"])
    
    # Turbo (Seed + 3000)
    seed_turbo = base_seed + 3000
    turbo = get_seeded_choice(seed_turbo, CONFIG["turbo_options"])
    
    return {
        "normal": normal,
        "auto": auto,
        "turbo": turbo
    }


def generate_multiplier(game_id: str) -> Dict:
    """
    Generates multiplier data for a game.
    Uses the EXACT same algorithm as the website.
    
    Args:
        game_id: Game identifier
    
    Returns:
        Dictionary with multiplier value and type
    """
    time_seed = get_time_seed()
    game_hash = string_to_hash(game_id)
    
    multiplier_seed = (time_seed * 1000 + game_hash) * 7
    multiplier_index = get_seeded_random_int(
        multiplier_seed, 0, len(CONFIG["multipliers"]) - 1
    )
    
    return CONFIG["multipliers"][multiplier_index]


# =============================================================================
# HIGH RTP GAMES FILTER
# =============================================================================

def get_high_rtp_games(provider_filter: str = "ALL") -> List[Dict]:
    """
    Filters the top 15 games to find those with RTP >= 80%.
    Can filter by provider.
    
    Args:
        provider_filter: "ALL" for all games, or specific provider name
                        (e.g., "PG SOFT", "PRAGMATIC PLAY")
    
    Returns:
        List of game dictionaries with RTP >= 80%, including:
        - game_id, display_name, provider, image_file
        - rtp, strategy (normal, auto, turbo), multiplier
    """
    high_rtp_games = []
    
    for game in TOP_15_GAMES:
        # Filter by provider if specified
        if provider_filter != "ALL":
            if game["provider"].upper() != provider_filter.upper():
                continue
        
        rtp = generate_game_rtp(game["game_id"])
        
        if rtp >= CONFIG["rtp_threshold"]:
            strategy = generate_game_strategy(game["game_id"])
            multiplier = generate_multiplier(game["game_id"])
            
            high_rtp_games.append({
                **game,
                "rtp": rtp,
                "strategy": strategy,
                "multiplier": multiplier
            })
    
    # Sort by RTP (highest first)
    high_rtp_games.sort(key=lambda x: x["rtp"], reverse=True)
    
    return high_rtp_games


# =============================================================================
# TELEGRAM MESSAGE FORMATTING
# =============================================================================

def format_single_game_message(game: Dict, valid_until: str) -> str:
    """
    Formats a Telegram message for a SINGLE high RTP game.
    Each game gets its own message with its own picture.
    
    Args:
        game: Single game dictionary with RTP >= 80%
        valid_until: Time string when the prediction expires
    
    Returns:
        Formatted HTML message for one game
    """
    lines = []
    
    # Header
    
    # Game info
    lines.append(f"🎮 {game['display_name']}")
    lines.append("")
    lines.append(f"📊 <b>Porcentagem (RTP):</b> {game['rtp']}%\n")
    lines.append(f"🎯 <b>Estratégia de Apostas:</b>")
    lines.append(f"Normal: {game['strategy']['normal']} X")
    lines.append(f"Auto: {game['strategy']['auto']}")
    lines.append(f"Turbo: {game['strategy']['turbo']}\n")
    lines.append(f"⏳ <b>Válido até:</b> {valid_until}\n")
    lines.append("Jogue agora e ganhe!")
    lines.append("Boa sorte! 🍀")
    
    return "\n".join(lines)


def get_game_image_path(game: Dict) -> str:
    """
    Gets the image path for a specific game.
    
    Args:
        game: Game dictionary
    
    Returns:
        Full path to the image file
    """
    return f"{IMAGE_BASE_PATH}{game['image_file']}"


# =============================================================================
# TELEGRAM BOT FUNCTIONS
# =============================================================================

# Initialize bot
bot = Bot(token=BOT_TOKEN)


async def send_prediction(channel_id: str, provider_filter: str = "ALL", channel_name: str = ""):
    """
    Sends prediction messages to a Telegram channel.
    Each game with RTP >= 80% gets its OWN separate message with its own picture.
    
    Args:
        channel_id: Telegram channel ID (e.g., "@PPSinaisPOP")
        provider_filter: "ALL" for all games, or specific provider name
        channel_name: Display name for logging
    """
    # Get games with RTP >= 80% filtered by provider
    high_rtp_games = get_high_rtp_games(provider_filter)
    
    if not high_rtp_games:
        display_name = channel_name if channel_name else channel_id
        provider_info = f" ({provider_filter})" if provider_filter != "ALL" else ""
        print(f"📊 {display_name}{provider_info}: Nenhum jogo com RTP >= 80% neste momento")
        return
    
    # Calculate valid until time (3 minutes from now, aligned with website)
    now = datetime.now(SAO_PAULO_TZ)
    current_minute = now.minute
    next_update_minute = ((current_minute // 3) + 1) * 3
    
    # Handle hour rollover
    if next_update_minute >= 60:
        valid_until = now.replace(minute=next_update_minute - 60) + timedelta(hours=1)
    else:
        valid_until = now.replace(minute=next_update_minute, second=0, microsecond=0)
    
    valid_until_str = valid_until.strftime("%H:%M")

    # Create keyboard (same for all messages)
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🎰 JOGUE AGORA 🔥", url="https://popduqo.com/?ch=23890")],
        [InlineKeyboardButton("🎁 BOT BÔNUS", url=LINK_URL)]
    ])

    # Send a SEPARATE message for EACH high RTP game
    sent_count = 0
    for game in high_rtp_games:
        # Format message for this specific game
        caption = format_single_game_message(game, valid_until_str)
        
        # Get image path for this specific game
        image_path = get_game_image_path(game)
        
        try:
            with open(image_path, "rb") as photo:
                await bot.send_photo(
                    chat_id=channel_id,
                    photo=photo,
                    caption=caption,
                    parse_mode="HTML",
                    reply_markup=keyboard
                )
            
            print(f"✅ Enviado: {game['display_name']} (RTP: {game['rtp']}%)")
            sent_count += 1
            
            # Small delay between messages to avoid rate limiting
            await asyncio.sleep(1)
            
        except FileNotFoundError:
            print(f"❌ Imagem não encontrada: {image_path}")
            # Try sending without image
            try:
                await bot.send_message(
                    chat_id=channel_id,
                    text=caption,
                    parse_mode="HTML",
                    reply_markup=keyboard
                )
                print(f"✅ Mensagem enviada sem imagem: {game['display_name']}")
                sent_count += 1
            except Exception as e:
                print(f"❌ Erro ao enviar mensagem: {e}")
        
        except Exception as e:
            print(f"❌ Erro ao enviar {game['display_name']}: {e}")
    
    display_name = channel_name if channel_name else channel_id
    provider_info = f" ({provider_filter})" if provider_filter != "ALL" else ""
    print(f"📤 Total enviado para {display_name}{provider_info}: {sent_count}/{len(high_rtp_games)} jogos")


def verify_hash_calculation():
    """
    Verifies hash calculation matches JavaScript.
    Run this to debug if RTP values don't match website.
    """
    print("\n" + "=" * 70)
    print("🔍 VERIFICAÇÃO DE HASH - Comparar com JavaScript")
    print("=" * 70)
    
    # Test with a known game ID
    test_id = "PG SOFT/FORTUNE_1.webp"
    hash_val = string_to_hash(test_id)
    time_seed = get_time_seed()
    combined_seed = time_seed * 1000 + hash_val
    
    print(f"Game ID: {test_id}")
    print(f"Hash: {hash_val}")
    print(f"Time Seed: {time_seed}")
    print(f"Combined Seed: {combined_seed}")
    print()
    print("Para verificar no console do navegador, cole este código:")
    print("-" * 70)
    print(f'''
// Cole no console do navegador (F12) na página do website:
const testId = "{test_id}";
const hash = stringToHash(testId);
const timeSeed = getTimeSeed();
const combined = timeSeed * 1000 + hash;
console.log("Hash:", hash);
console.log("Time Seed:", timeSeed);
console.log("Combined:", combined);
console.log("RTP:", getSeededRandomInt(combined, 30, 99));
''')
    print("-" * 70)
    print("=" * 70 + "\n")


def debug_print_all_games():
    """
    Prints RTP values for all top 15 games (for debugging).
    Helps verify synchronization with website.
    """
    print("\n" + "=" * 70)
    print("📊 DEBUG: RTP DOS TOP 15 JOGOS")
    print("=" * 70)
    
    time_seed = get_time_seed()
    now = datetime.now(SAO_PAULO_TZ)
    
    print(f"⏰ Hora São Paulo: {now.strftime('%H:%M:%S')}")
    print(f"🔢 Time Seed: {time_seed}")
    print("-" * 70)
    
    # Print header
    print(f"{'#':<3} {'Game':<35} {'Hash':<12} {'RTP':<6} {'Status'}")
    print("-" * 70)
    
    for i, game in enumerate(TOP_15_GAMES, 1):
        game_hash = string_to_hash(game["game_id"])
        rtp = generate_game_rtp(game["game_id"])
        strategy = generate_game_strategy(game["game_id"])
        
        status = "🔥 HOT!" if rtp >= CONFIG["rtp_threshold"] else ""
        
        print(f"{i:<3} {game['display_name']:<35} {game_hash:<12} {rtp}%   {status}")
        print(f"    └ Normal: {strategy['normal']}X | Auto: {strategy['auto']} | Turbo: {strategy['turbo']}")
    
    print("-" * 70)
    
    high_rtp = [g for g in TOP_15_GAMES if generate_game_rtp(g["game_id"]) >= CONFIG["rtp_threshold"]]
    print(f"📈 Jogos com RTP >= 80%: {len(high_rtp)}")
    print("=" * 70 + "\n")


# =============================================================================
# MAIN LOOP
# =============================================================================

async def main():
    """
    Main bot loop.
    Checks for high RTP games every 3 minutes (synchronized with website).
    Sends to different channels based on provider configuration.
    """
    print("=" * 70)
    print("🎰 RTP BOT v2.0 - Sincronizado com Website")
    print("=" * 70)
    print(f"📍 Timezone: São Paulo (UTC-3)")
    print(f"🔄 Intervalo de atualização: 3 minutos")
    print(f"📊 Limite RTP: >= {CONFIG['rtp_threshold']}%")
    print(f"🎮 Jogos monitorados: {len(TOP_15_GAMES)}")
    print()
    print("📢 Canais configurados:")
    for ch in CHANNEL_CONFIG:
        print(f"   • {ch['name']}: {ch['channel_id']} ({ch['provider']})")
    print("=" * 70)
    
    # Show hash verification info on startup
    verify_hash_calculation()
    
    while True:
        # Debug: Show all games RTP
        debug_print_all_games()
        
        # Send to each configured channel with its provider filter
        for channel_cfg in CHANNEL_CONFIG:
            await send_prediction(
                channel_id=channel_cfg["channel_id"],
                provider_filter=channel_cfg["provider"],
                channel_name=channel_cfg["name"]
            )
            await asyncio.sleep(2)  # Small delay between channels
        
        # Wait until next 3-minute interval
        now = datetime.now(SAO_PAULO_TZ)
        current_second = now.second + (now.minute % 3) * 60
        seconds_until_next = (3 * 60) - current_second
        
        print(f"\n⏳ Aguardando {seconds_until_next} segundos até próxima atualização...")
        print(f"   Próxima verificação: {(now + timedelta(seconds=seconds_until_next)).strftime('%H:%M:%S')}\n")
        
        await asyncio.sleep(seconds_until_next + 1)  # +1 to ensure we're in the new interval


# =============================================================================
# ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        print("\n🛑 Bot encerrado pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro fatal: {e}")
    finally:
        loop.close()

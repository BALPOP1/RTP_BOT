"""
=============================================================================
RTP SYNC TEST - Verify bot matches website
=============================================================================
Run this script to compare RTP values between bot and website.
Open website console (F12) and compare the output values.
=============================================================================
"""

import ctypes
import math
from datetime import datetime
import pytz

SAO_PAULO_TZ = pytz.timezone("America/Sao_Paulo")

# =============================================================================
# EXACT COPIES OF THE RTP FUNCTIONS
# =============================================================================

def to_int32(val):
    return ctypes.c_int32(val).value

def to_uint32(val):
    return ctypes.c_uint32(val).value

def string_to_hash(s):
    hash_val = 0
    for char in s:
        char_code = ord(char)
        shifted = to_int32(hash_val << 5)
        hash_val = to_int32(shifted - hash_val + char_code)
    return abs(hash_val)

def get_time_seed():
    sao_paulo_time = datetime.now(SAO_PAULO_TZ)
    current_minute = sao_paulo_time.minute
    rounded_minute = (current_minute // 3) * 3
    total_minutes = (
        sao_paulo_time.year * 525600 +
        (sao_paulo_time.month - 1) * 43800 +
        sao_paulo_time.day * 1440 +
        sao_paulo_time.hour * 60 +
        rounded_minute
    )
    return total_minutes

def js_imul(a, b):
    a = to_uint32(a)
    b = to_uint32(b)
    result = (a * b) & 0xFFFFFFFF
    return to_int32(result)

def seeded_random(seed):
    seed = abs(to_int32(seed))
    t = to_uint32(seed + 0x6D2B79F5)
    t_shifted = t >> 15
    t = to_uint32(js_imul(t ^ t_shifted, t | 1))
    t_shifted2 = t >> 7
    imul_result = js_imul(t ^ t_shifted2, t | 61)
    t = to_uint32(t ^ to_uint32(t + imul_result))
    result = to_uint32(t ^ (t >> 14))
    return result / 4294967296

def get_seeded_random_int(seed, min_val, max_val):
    # MUST use float to match JavaScript's 64-bit float precision loss!
    seed = int((float(seed) * 9301 + 49297) % 233280)
    rnd = seeded_random(seed)
    return math.floor(rnd * (max_val - min_val + 1)) + min_val

def generate_rtp(game_id):
    time_seed = get_time_seed()
    game_hash = string_to_hash(game_id)
    combined_seed = time_seed * 1000 + game_hash
    rtp = get_seeded_random_int(combined_seed, 30, 99)
    return rtp, game_hash, time_seed, combined_seed

# =============================================================================
# TEST
# =============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("🔍 RTP SYNC TEST - Compare with Website")
    print("=" * 70)
    
    # Simple hash verification
    print("\n📋 STEP 1: HASH VERIFICATION")
    print("-" * 70)
    test_strings = ["test", "PG SOFT/FORTUNE_1.webp"]
    for s in test_strings:
        h = string_to_hash(s)
        print(f'stringToHash("{s}") = {h}')
    print()
    print("Run this in browser console to compare:")
    print('console.log(stringToHash("test"));')
    print('console.log(stringToHash("PG SOFT/FORTUNE_1.webp"));')
    print("-" * 70)
    
    now = datetime.now(SAO_PAULO_TZ)
    print(f"\n⏰ São Paulo Time: {now.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🔢 Time Seed: {get_time_seed()}")
    print()
    
    # Test games
    games = [
        ("PG SOFT/FORTUNE_1.webp", "Fortune Rabbit"),
        ("PG SOFT/FORTUNE_2.webp", "Fortune Snake"),
        ("PG SOFT/FORTUNE_3.webp", "Fortune Tiger"),
        ("PG SOFT/FORTUNE_4.webp", "Wild Heist Cashout"),
        ("PG SOFT/FORTUNE_5.webp", "Fortune Dragon"),
        ("PG SOFT/FORTUNE_6.webp", "Fortune OX"),
        ("PG SOFT/FORTUNE_7.webp", "Fortune Mouse"),
        ("Pragmatic Play/POPULAR_1.webp", "Fruit Party"),
        ("Pragmatic Play/POPULAR_2.webp", "Sugar Rush Xmas"),
        ("Pragmatic Play/POPULAR_3.webp", "Big Bass Bonanza"),
        ("Pragmatic Play/POPULAR_4.webp", "Gems Bonanza"),
        ("Pragmatic Play/POPULAR_5.webp", "Sweet Bonanza"),
        ("Pragmatic Play/POPULAR_6.webp", "Starlight Princess 1000"),
        ("Pragmatic Play/POPULAR_7.webp", "Gates of Olympus Super Scatter"),
        ("Pragmatic Play/POPULAR_8.webp", "Gates of Olympus 1000"),
    ]
    
    print(f"{'#':<3} {'Game':<30} {'Hash':<12} {'Seed':<15} {'RTP'}")
    print("-" * 70)
    
    for i, (game_id, name) in enumerate(games, 1):
        rtp, game_hash, time_seed, combined = generate_rtp(game_id)
        print(f"{i:<3} {name:<30} {game_hash:<12} {combined:<15} {rtp}%")
    
    print("-" * 70)
    print()
    print("📋 JAVASCRIPT TEST CODE - Paste in browser console (F12):")
    print("-" * 70)
    print("""
// Paste this in the website's browser console to compare:
const testGames = [
    "PG SOFT/FORTUNE_1.webp",
    "PG SOFT/FORTUNE_2.webp",
    "PG SOFT/FORTUNE_3.webp",
    "PG SOFT/FORTUNE_4.webp",
    "PG SOFT/FORTUNE_5.webp",
    "PG SOFT/FORTUNE_6.webp",
    "PG SOFT/FORTUNE_7.webp",
    "Pragmatic Play/POPULAR_1.webp",
    "Pragmatic Play/POPULAR_2.webp",
    "Pragmatic Play/POPULAR_3.webp",
    "Pragmatic Play/POPULAR_4.webp",
    "Pragmatic Play/POPULAR_5.webp",
    "Pragmatic Play/POPULAR_6.webp",
    "Pragmatic Play/POPULAR_7.webp",
    "Pragmatic Play/POPULAR_8.webp"
];

console.log("Time Seed:", getTimeSeed());
testGames.forEach((id, i) => {
    const hash = stringToHash(id);
    const combined = getTimeSeed() * 1000 + hash;
    const rtp = getSeededRandomInt(combined, 30, 99);
    console.log(`${i+1}. ${id} | Hash: ${hash} | RTP: ${rtp}%`);
});
""")
    print("-" * 70)


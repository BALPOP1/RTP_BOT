"""Verify the RTP fix works - compare with website values"""
import ctypes
import math

def to_int32(val):
    return ctypes.c_int32(val).value

def to_uint32(val):
    return ctypes.c_uint32(val).value

def string_to_hash(s):
    hash_val = 0
    for char in s:
        shifted = to_int32(hash_val << 5)
        hash_val = to_int32(shifted - hash_val + ord(char))
    return abs(hash_val)

def js_imul(a, b):
    return to_int32((to_uint32(a) * to_uint32(b)) & 0xFFFFFFFF)

def seeded_random(seed):
    seed = abs(to_int32(seed))
    t = to_uint32(seed + 0x6D2B79F5)
    t = to_uint32(js_imul(t ^ (t >> 15), t | 1))
    t = to_uint32(t ^ to_uint32(t + js_imul(t ^ (t >> 7), t | 61)))
    return to_uint32(t ^ (t >> 14)) / 4294967296

def get_seeded_random_int(seed, min_val, max_val):
    # FIXED: Use float to match JavaScript's 64-bit float precision loss!
    seed = int((float(seed) * 9301 + 49297) % 233280)
    rnd = seeded_random(seed)
    return math.floor(rnd * (max_val - min_val + 1)) + min_val

# Test with the EXACT time seed from website: 1064842017
time_seed = 1064842017

print("=" * 60)
print("TESTING WITH TIME SEED:", time_seed)
print("=" * 60)
print()

# Website showed these values at this time seed:
expected = {
    "PG SOFT/FORTUNE_1.webp": 85,
    "PG SOFT/FORTUNE_2.webp": 88,
    "PG SOFT/FORTUNE_3.webp": 86,
    "PG SOFT/FORTUNE_4.webp": 36,
    "PG SOFT/FORTUNE_5.webp": 30,
}

games = [
    ("PG SOFT/FORTUNE_1.webp", "Fortune Rabbit"),
    ("PG SOFT/FORTUNE_2.webp", "Fortune Snake"),
    ("PG SOFT/FORTUNE_3.webp", "Fortune Tiger"),
    ("PG SOFT/FORTUNE_4.webp", "Wild Heist Cashout"),
    ("PG SOFT/FORTUNE_5.webp", "Fortune Dragon"),
]

all_match = True
for i, (game_id, name) in enumerate(games):
    game_hash = string_to_hash(game_id)
    combined = time_seed * 1000 + game_hash
    rtp = get_seeded_random_int(combined, 30, 99)
    exp = expected[game_id]
    match = "✓" if rtp == exp else "✗"
    if rtp != exp:
        all_match = False
    print(f"{i+1}. {name:<20} | RTP: {rtp:2}% (expected: {exp}%) {match}")

print()
if all_match:
    print("🎉 ALL VALUES MATCH! The fix works!")
else:
    print("❌ Some values don't match.")


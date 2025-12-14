"""Debug script to trace RTP calculation differences"""
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
    seed = (seed * 9301 + 49297) % 233280
    rnd = seeded_random(seed)
    return math.floor(rnd * (max_val - min_val + 1)) + min_val

# Test with the EXACT time seed from website
time_seed = 1064842017

# Test FORTUNE_2 specifically
game_id = "PG SOFT/FORTUNE_2.webp"
game_hash = string_to_hash(game_id)
combined_seed = time_seed * 1000 + game_hash

print(f"Game ID: {game_id}")
print(f"Time Seed: {time_seed}")
print(f"Game Hash: {game_hash}")
print(f"Combined Seed: {combined_seed}")

# Step through get_seeded_random_int
seed_after_transform = (combined_seed * 9301 + 49297) % 233280
print(f"Seed after transform: {seed_after_transform}")

rnd = seeded_random(seed_after_transform)
print(f"seeded_random result: {rnd}")

rtp = math.floor(rnd * (99 - 30 + 1)) + 30
print(f"RTP: {rtp}%")

print()
print("=" * 60)
print("PASTE THIS IN BROWSER CONSOLE TO COMPARE:")
print("=" * 60)
print(f'''
const gameId = "{game_id}";
const timeSeed = {time_seed};
const gameHash = stringToHash(gameId);
const combined = timeSeed * 1000 + gameHash;
const seedAfterTransform = (combined * 9301 + 49297) % 233280;

console.log("Game Hash:", gameHash);
console.log("Combined:", combined);  
console.log("Seed after transform:", seedAfterTransform);
console.log("RTP:", getSeededRandomInt(combined, 30, 99));
''')


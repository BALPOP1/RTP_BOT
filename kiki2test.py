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
# For Railway: Set these as environment variables in your Railway dashboard
# Or they will use the default values below for local development
# =============================================================================

BOT_TOKEN = os.getenv("BOT_TOKEN", "8581548235:AAFAOEMOmfsDGdogbN6aHTcqdsQtgaZSDm8")
LINK_URL = os.getenv("LINK_URL", "https://t.me/POPREDE_bonus_Bot")
PLAY_URL = os.getenv("PLAY_URL", "https://popduqo.com/?ch=23890")

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
# EXPANDED GAMES LIST - 100 PG SOFT + 100 PRAGMATIC PLAY GAMES
# The game_id format MUST match website exactly: "Provider/ImageName"
# This ensures RTP calculations are IDENTICAL to the website!
# =============================================================================

# Maximum games to show per notification
MAX_GAMES_PER_NOTIFICATION = 5

# PG SOFT Games (100 games)
PG_SOFT_GAMES = [
    # Named Fortune Games (7)
    {"game_id": "PG SOFT/FORTUNE_1.webp", "display_name": "🐰 Fortune Rabbit", "provider": "PG SOFT", "image_file": "FORTUNE_1.webp"},
    {"game_id": "PG SOFT/FORTUNE_2.webp", "display_name": "🐍 Fortune Snake", "provider": "PG SOFT", "image_file": "FORTUNE_2.webp"},
    {"game_id": "PG SOFT/FORTUNE_3.webp", "display_name": "🐅 Fortune Tiger", "provider": "PG SOFT", "image_file": "FORTUNE_3.webp"},
    {"game_id": "PG SOFT/FORTUNE_4.webp", "display_name": "💰 Wild Heist Cashout", "provider": "PG SOFT", "image_file": "FORTUNE_4.webp"},
    {"game_id": "PG SOFT/FORTUNE_5.webp", "display_name": "🐉 Fortune Dragon", "provider": "PG SOFT", "image_file": "FORTUNE_5.webp"},
    {"game_id": "PG SOFT/FORTUNE_6.webp", "display_name": "🐂 Fortune OX", "provider": "PG SOFT", "image_file": "FORTUNE_6.webp"},
    {"game_id": "PG SOFT/FORTUNE_7.webp", "display_name": "🐭 Fortune Mouse", "provider": "PG SOFT", "image_file": "FORTUNE_7.webp"},
    # Hash-named PG SOFT games (93 more to reach 100)
    {"game_id": "PG SOFT/00a551e721df0397dec7670b58bdd51707b88f6944451c47fd929e8bfbb97083.webp", "display_name": "🎰 PG Slot 01", "provider": "PG SOFT", "image_file": "00a551e721df0397dec7670b58bdd51707b88f6944451c47fd929e8bfbb97083.webp"},
    {"game_id": "PG SOFT/0383908af3539ad060baa90833f03c15742031a906d1c104445d5cdd78e7cdf1.webp", "display_name": "🎰 PG Slot 02", "provider": "PG SOFT", "image_file": "0383908af3539ad060baa90833f03c15742031a906d1c104445d5cdd78e7cdf1.webp"},
    {"game_id": "PG SOFT/0783fd411d9e05082875f6a2a09c52ae2cc82e1449b00f7850d8ae37f3d3d2bb.webp", "display_name": "🎰 PG Slot 03", "provider": "PG SOFT", "image_file": "0783fd411d9e05082875f6a2a09c52ae2cc82e1449b00f7850d8ae37f3d3d2bb.webp"},
    {"game_id": "PG SOFT/0e266d67bbb5dd084ec7f70bc758b502a52a258692009e6544c2bb61267f7468.webp", "display_name": "🎰 PG Slot 04", "provider": "PG SOFT", "image_file": "0e266d67bbb5dd084ec7f70bc758b502a52a258692009e6544c2bb61267f7468.webp"},
    {"game_id": "PG SOFT/0f471a2be468714d161c9051fb7ff57179252d199f98e92d1e967be9786e2017.webp", "display_name": "🎰 PG Slot 05", "provider": "PG SOFT", "image_file": "0f471a2be468714d161c9051fb7ff57179252d199f98e92d1e967be9786e2017.webp"},
    {"game_id": "PG SOFT/0f7a0139c997fb49499bdd5fe6d9b3c0b53f839770b12be6fa6467e5cd3d84e2.webp", "display_name": "🎰 PG Slot 06", "provider": "PG SOFT", "image_file": "0f7a0139c997fb49499bdd5fe6d9b3c0b53f839770b12be6fa6467e5cd3d84e2.webp"},
    {"game_id": "PG SOFT/15c15dad7ed21ae72991e66194d0a24651f27f34fe9ca3a32e9ee6aea2c4729e.webp", "display_name": "🎰 PG Slot 07", "provider": "PG SOFT", "image_file": "15c15dad7ed21ae72991e66194d0a24651f27f34fe9ca3a32e9ee6aea2c4729e.webp"},
    {"game_id": "PG SOFT/1663801e30484b58dd67ea075ae766eb74bb0943f5bae1ea4d5e6c7ac112fb4c.webp", "display_name": "🎰 PG Slot 08", "provider": "PG SOFT", "image_file": "1663801e30484b58dd67ea075ae766eb74bb0943f5bae1ea4d5e6c7ac112fb4c.webp"},
    {"game_id": "PG SOFT/18a559e861fb310540293ee4191f8d8fd0df4febab7453e80e885f714c6b5bb3.webp", "display_name": "🎰 PG Slot 09", "provider": "PG SOFT", "image_file": "18a559e861fb310540293ee4191f8d8fd0df4febab7453e80e885f714c6b5bb3.webp"},
    {"game_id": "PG SOFT/19b3440364161ede8c85c9cbb3bbe39f0adb8bf53d8ae7ffe4da1a622c340997.webp", "display_name": "🎰 PG Slot 10", "provider": "PG SOFT", "image_file": "19b3440364161ede8c85c9cbb3bbe39f0adb8bf53d8ae7ffe4da1a622c340997.webp"},
    {"game_id": "PG SOFT/1e0ff105d1f1d9ffca7b826fe3d84d63f24a216f060b2783b5077a3c002f07ce.webp", "display_name": "🎰 PG Slot 11", "provider": "PG SOFT", "image_file": "1e0ff105d1f1d9ffca7b826fe3d84d63f24a216f060b2783b5077a3c002f07ce.webp"},
    {"game_id": "PG SOFT/1e5d818e614417f723e793b377c8988b531be669d5916f0066090dcfb547dc7a.webp", "display_name": "🎰 PG Slot 12", "provider": "PG SOFT", "image_file": "1e5d818e614417f723e793b377c8988b531be669d5916f0066090dcfb547dc7a.webp"},
    {"game_id": "PG SOFT/206c543474a411164b4955b204fa7ec3b0a28dd260207e9f49e66f42bfa4fc61.webp", "display_name": "🎰 PG Slot 13", "provider": "PG SOFT", "image_file": "206c543474a411164b4955b204fa7ec3b0a28dd260207e9f49e66f42bfa4fc61.webp"},
    {"game_id": "PG SOFT/231e682dc941d4fee28c159217a85b849a5644174d04a5e7e6cca53c7ffc6559.webp", "display_name": "🎰 PG Slot 14", "provider": "PG SOFT", "image_file": "231e682dc941d4fee28c159217a85b849a5644174d04a5e7e6cca53c7ffc6559.webp"},
    {"game_id": "PG SOFT/27992dc65d125e58b650a44db23a5564174d9cc4b6193498507c6b43340f9cfe.webp", "display_name": "🎰 PG Slot 15", "provider": "PG SOFT", "image_file": "27992dc65d125e58b650a44db23a5564174d9cc4b6193498507c6b43340f9cfe.webp"},
    {"game_id": "PG SOFT/28689642bb26ac2711280fd846841fb70c02d4df0ac32215d1ec7ee47287b0c3.webp", "display_name": "🎰 PG Slot 16", "provider": "PG SOFT", "image_file": "28689642bb26ac2711280fd846841fb70c02d4df0ac32215d1ec7ee47287b0c3.webp"},
    {"game_id": "PG SOFT/2c7bccf6b837082ce28c2bc78a83c4366f0ba041700059d092bccb9bd8e66219.webp", "display_name": "🎰 PG Slot 17", "provider": "PG SOFT", "image_file": "2c7bccf6b837082ce28c2bc78a83c4366f0ba041700059d092bccb9bd8e66219.webp"},
    {"game_id": "PG SOFT/2e34322c98847518039606f308d1387726496d8175fb7f0af65e49209818bf5b.webp", "display_name": "🎰 PG Slot 18", "provider": "PG SOFT", "image_file": "2e34322c98847518039606f308d1387726496d8175fb7f0af65e49209818bf5b.webp"},
    {"game_id": "PG SOFT/304f08dcb2037f6f48c83d0878bb9495d044019ebe64dae192312b8316921e71.webp", "display_name": "🎰 PG Slot 19", "provider": "PG SOFT", "image_file": "304f08dcb2037f6f48c83d0878bb9495d044019ebe64dae192312b8316921e71.webp"},
    {"game_id": "PG SOFT/305c9006b8580e1ed4fd44831fdd6fdcd75308ee1d5e206a4765865c7edbac89.webp", "display_name": "🎰 PG Slot 20", "provider": "PG SOFT", "image_file": "305c9006b8580e1ed4fd44831fdd6fdcd75308ee1d5e206a4765865c7edbac89.webp"},
    {"game_id": "PG SOFT/3086b80ed6350fbaeaf265007a8db67018e45bf577f85b46b69e7ab91204b6c1.webp", "display_name": "🎰 PG Slot 21", "provider": "PG SOFT", "image_file": "3086b80ed6350fbaeaf265007a8db67018e45bf577f85b46b69e7ab91204b6c1.webp"},
    {"game_id": "PG SOFT/3165842615badb659169b005972d3322c179681b9fa40ed0bd4d4b38240039ff.webp", "display_name": "🎰 PG Slot 22", "provider": "PG SOFT", "image_file": "3165842615badb659169b005972d3322c179681b9fa40ed0bd4d4b38240039ff.webp"},
    {"game_id": "PG SOFT/36a56c751761daafa24e39f299b9c7514db1e38a6c2974ebe5d8fb0d15c8f974.webp", "display_name": "🎰 PG Slot 23", "provider": "PG SOFT", "image_file": "36a56c751761daafa24e39f299b9c7514db1e38a6c2974ebe5d8fb0d15c8f974.webp"},
    {"game_id": "PG SOFT/36b789a430850114370377fb0a3157a937c9f4537b87e4f51859ec2e3b31e4ca.webp", "display_name": "🎰 PG Slot 24", "provider": "PG SOFT", "image_file": "36b789a430850114370377fb0a3157a937c9f4537b87e4f51859ec2e3b31e4ca.webp"},
    {"game_id": "PG SOFT/44171610fd2b532cf0359fabc730b90ba9cdc6ce83e5cfc693d28c4118544ff9.webp", "display_name": "🎰 PG Slot 25", "provider": "PG SOFT", "image_file": "44171610fd2b532cf0359fabc730b90ba9cdc6ce83e5cfc693d28c4118544ff9.webp"},
    {"game_id": "PG SOFT/4ad6cd019f1a59b142d165ce9bfe46bd082de2e22729d01c5a8072b30a32e6b5.webp", "display_name": "🎰 PG Slot 26", "provider": "PG SOFT", "image_file": "4ad6cd019f1a59b142d165ce9bfe46bd082de2e22729d01c5a8072b30a32e6b5.webp"},
    {"game_id": "PG SOFT/4bef33625ecea66eaec5cbba7af3f87cc0ccd9cf4f5de447f912bc4438f74c77.webp", "display_name": "🎰 PG Slot 27", "provider": "PG SOFT", "image_file": "4bef33625ecea66eaec5cbba7af3f87cc0ccd9cf4f5de447f912bc4438f74c77.webp"},
    {"game_id": "PG SOFT/4eef0671e220f626402d069eeac75402c276c4d8d2447276921bd23a28127930.webp", "display_name": "🎰 PG Slot 28", "provider": "PG SOFT", "image_file": "4eef0671e220f626402d069eeac75402c276c4d8d2447276921bd23a28127930.webp"},
    {"game_id": "PG SOFT/501cfd29c5161aaebc4e74a29a619689d55cf59c04f8ba5450e08fd86e5341c4.webp", "display_name": "🎰 PG Slot 29", "provider": "PG SOFT", "image_file": "501cfd29c5161aaebc4e74a29a619689d55cf59c04f8ba5450e08fd86e5341c4.webp"},
    {"game_id": "PG SOFT/51ac0bac746b4cdd135084f85b6e1907ff5a0bd67788ba29e2259119a13753d1.webp", "display_name": "🎰 PG Slot 30", "provider": "PG SOFT", "image_file": "51ac0bac746b4cdd135084f85b6e1907ff5a0bd67788ba29e2259119a13753d1.webp"},
    {"game_id": "PG SOFT/5767d78a5dad829da3696033c52703effadaeecc63368976a9c819abef7e316a.webp", "display_name": "🎰 PG Slot 31", "provider": "PG SOFT", "image_file": "5767d78a5dad829da3696033c52703effadaeecc63368976a9c819abef7e316a.webp"},
    {"game_id": "PG SOFT/5df44a36f199216628bd6e6a29e2c100af4792aec54412eb4243293c98685d44.webp", "display_name": "🎰 PG Slot 32", "provider": "PG SOFT", "image_file": "5df44a36f199216628bd6e6a29e2c100af4792aec54412eb4243293c98685d44.webp"},
    {"game_id": "PG SOFT/688e084e49eff7f1ac0db6bb8d947a22b6406604aacfd85749ec163c7c2cbc52.webp", "display_name": "🎰 PG Slot 33", "provider": "PG SOFT", "image_file": "688e084e49eff7f1ac0db6bb8d947a22b6406604aacfd85749ec163c7c2cbc52.webp"},
    {"game_id": "PG SOFT/6d970637c00b524fb7374ae49bb4cb81b8bca04e970822d9b20dc4fc2f3f9342.webp", "display_name": "🎰 PG Slot 34", "provider": "PG SOFT", "image_file": "6d970637c00b524fb7374ae49bb4cb81b8bca04e970822d9b20dc4fc2f3f9342.webp"},
    {"game_id": "PG SOFT/72cdaf43de85c8a1f96b81d590d9917d5c5dd559e3cc105654589fddc581abad.webp", "display_name": "🎰 PG Slot 35", "provider": "PG SOFT", "image_file": "72cdaf43de85c8a1f96b81d590d9917d5c5dd559e3cc105654589fddc581abad.webp"},
    {"game_id": "PG SOFT/786b1ff57f062d116e6bbc7a5a64a071c2cc33762540d4fe88537d281e9d362a.webp", "display_name": "🎰 PG Slot 36", "provider": "PG SOFT", "image_file": "786b1ff57f062d116e6bbc7a5a64a071c2cc33762540d4fe88537d281e9d362a.webp"},
    {"game_id": "PG SOFT/7c31008ca65f8b938d44c6dd4f37083bf4d70eadfd1361d00100bd9849c64886.webp", "display_name": "🎰 PG Slot 37", "provider": "PG SOFT", "image_file": "7c31008ca65f8b938d44c6dd4f37083bf4d70eadfd1361d00100bd9849c64886.webp"},
    {"game_id": "PG SOFT/7dbec5678181612dc2ea2257b42e7244836a24f7758cb48786bd59dd6cde0d8b.webp", "display_name": "🎰 PG Slot 38", "provider": "PG SOFT", "image_file": "7dbec5678181612dc2ea2257b42e7244836a24f7758cb48786bd59dd6cde0d8b.webp"},
    {"game_id": "PG SOFT/81371649118a5aff0f7a48e70b6e70a88276831fbbb8121ede76b0700b73c24a.webp", "display_name": "🎰 PG Slot 39", "provider": "PG SOFT", "image_file": "81371649118a5aff0f7a48e70b6e70a88276831fbbb8121ede76b0700b73c24a.webp"},
    {"game_id": "PG SOFT/8668d1bee3eb2776c5182e32e69134244e75100e8431617d2974ce3bd2059434.webp", "display_name": "🎰 PG Slot 40", "provider": "PG SOFT", "image_file": "8668d1bee3eb2776c5182e32e69134244e75100e8431617d2974ce3bd2059434.webp"},
    {"game_id": "PG SOFT/8693e6eab04ef6966315f076752f80469a8ee938e01adb247bea3475e64955ef.webp", "display_name": "🎰 PG Slot 41", "provider": "PG SOFT", "image_file": "8693e6eab04ef6966315f076752f80469a8ee938e01adb247bea3475e64955ef.webp"},
    {"game_id": "PG SOFT/888b90ccd4249552b071c02b9cc37dca8ed19433f45c81ba4a2a6b2d34c2cbd7.webp", "display_name": "🎰 PG Slot 42", "provider": "PG SOFT", "image_file": "888b90ccd4249552b071c02b9cc37dca8ed19433f45c81ba4a2a6b2d34c2cbd7.webp"},
    {"game_id": "PG SOFT/8b344c6ddca073c38a6ab5eead9a076b7d71d06d7675f76cd29c1541b465a627.webp", "display_name": "🎰 PG Slot 43", "provider": "PG SOFT", "image_file": "8b344c6ddca073c38a6ab5eead9a076b7d71d06d7675f76cd29c1541b465a627.webp"},
    {"game_id": "PG SOFT/8cdd8efbd41092eb47bd902ef4a2b77f4a83b1338b04dbb9f4ab3e004387e55f.webp", "display_name": "🎰 PG Slot 44", "provider": "PG SOFT", "image_file": "8cdd8efbd41092eb47bd902ef4a2b77f4a83b1338b04dbb9f4ab3e004387e55f.webp"},
    {"game_id": "PG SOFT/8d55964f5a2914be1a72e528febe099432c867db6bcda7c45477c04644ff8722.webp", "display_name": "🎰 PG Slot 45", "provider": "PG SOFT", "image_file": "8d55964f5a2914be1a72e528febe099432c867db6bcda7c45477c04644ff8722.webp"},
    {"game_id": "PG SOFT/9687532f7e0035f3acec8dff4f8f19a785178e9d83a30f8710913bad8252352d.webp", "display_name": "🎰 PG Slot 46", "provider": "PG SOFT", "image_file": "9687532f7e0035f3acec8dff4f8f19a785178e9d83a30f8710913bad8252352d.webp"},
    {"game_id": "PG SOFT/9fd67b536b36a8bb524440f8c51844bff116538ccf53cd4324ac7f0b07c6e2eb.webp", "display_name": "🎰 PG Slot 47", "provider": "PG SOFT", "image_file": "9fd67b536b36a8bb524440f8c51844bff116538ccf53cd4324ac7f0b07c6e2eb.webp"},
    {"game_id": "PG SOFT/a58269307024a4b61d36d2ade5ae82ae20d5d34ab118c52ae1b4a6148e20a2cb.webp", "display_name": "🎰 PG Slot 48", "provider": "PG SOFT", "image_file": "a58269307024a4b61d36d2ade5ae82ae20d5d34ab118c52ae1b4a6148e20a2cb.webp"},
    {"game_id": "PG SOFT/a6e4218c56f254dbc12e2d124f5af070b42247634aa4d045489349218ee5d580.webp", "display_name": "🎰 PG Slot 49", "provider": "PG SOFT", "image_file": "a6e4218c56f254dbc12e2d124f5af070b42247634aa4d045489349218ee5d580.webp"},
    {"game_id": "PG SOFT/aa68cc308dd757091dcd668d3a6c4344b5fe1be285b36953426e6d0ae239274a.webp", "display_name": "🎰 PG Slot 50", "provider": "PG SOFT", "image_file": "aa68cc308dd757091dcd668d3a6c4344b5fe1be285b36953426e6d0ae239274a.webp"},
    {"game_id": "PG SOFT/ab71c0e54d919a05caaf76be86bb5f46743791165c110e1790b3baea94e9839c.webp", "display_name": "🎰 PG Slot 51", "provider": "PG SOFT", "image_file": "ab71c0e54d919a05caaf76be86bb5f46743791165c110e1790b3baea94e9839c.webp"},
    {"game_id": "PG SOFT/b12988a7565b01014829ad93b4e7019bf75ab3186266c6acfb52139f505f646c.webp", "display_name": "🎰 PG Slot 52", "provider": "PG SOFT", "image_file": "b12988a7565b01014829ad93b4e7019bf75ab3186266c6acfb52139f505f646c.webp"},
    {"game_id": "PG SOFT/b2ea1e9d093897e77ee5cf107213b22591b60a8d221080f698b94718bce53f28.webp", "display_name": "🎰 PG Slot 53", "provider": "PG SOFT", "image_file": "b2ea1e9d093897e77ee5cf107213b22591b60a8d221080f698b94718bce53f28.webp"},
    {"game_id": "PG SOFT/b4de37d456458c68a628594df3a05c454e5ec4ae61eb7526a5a71fc91f7380af.webp", "display_name": "🎰 PG Slot 54", "provider": "PG SOFT", "image_file": "b4de37d456458c68a628594df3a05c454e5ec4ae61eb7526a5a71fc91f7380af.webp"},
    {"game_id": "PG SOFT/b733ac0b664b9b0b7aa1faa4ec788a998d79353286062733d19b45f93e80c6de.webp", "display_name": "🎰 PG Slot 55", "provider": "PG SOFT", "image_file": "b733ac0b664b9b0b7aa1faa4ec788a998d79353286062733d19b45f93e80c6de.webp"},
    {"game_id": "PG SOFT/bf60e4e05d738e2cbfbc1b42a46664c3b50e194564ddf63b2350d70f7ec98277.webp", "display_name": "🎰 PG Slot 56", "provider": "PG SOFT", "image_file": "bf60e4e05d738e2cbfbc1b42a46664c3b50e194564ddf63b2350d70f7ec98277.webp"},
    {"game_id": "PG SOFT/bfffecea030a24a526007bbcfc231774dcb7560b421ceef1e9917ce7736ea6bc.webp", "display_name": "🎰 PG Slot 57", "provider": "PG SOFT", "image_file": "bfffecea030a24a526007bbcfc231774dcb7560b421ceef1e9917ce7736ea6bc.webp"},
    {"game_id": "PG SOFT/c227b1bb327a8fd31e90e8eaf1bdf7b61c39f8fc05afa73222c7079ac3f8e6a0.webp", "display_name": "🎰 PG Slot 58", "provider": "PG SOFT", "image_file": "c227b1bb327a8fd31e90e8eaf1bdf7b61c39f8fc05afa73222c7079ac3f8e6a0.webp"},
    {"game_id": "PG SOFT/c5005543fef7245219afa13116b2ff09d9ab3b5cb93f1f299c14fe85141d4895.webp", "display_name": "🎰 PG Slot 59", "provider": "PG SOFT", "image_file": "c5005543fef7245219afa13116b2ff09d9ab3b5cb93f1f299c14fe85141d4895.webp"},
    {"game_id": "PG SOFT/cba13601a1b83715abda91a5a6195319192b5b288c878966b9d5bd4a1a87fae8.webp", "display_name": "🎰 PG Slot 60", "provider": "PG SOFT", "image_file": "cba13601a1b83715abda91a5a6195319192b5b288c878966b9d5bd4a1a87fae8.webp"},
    {"game_id": "PG SOFT/d10245e2aab6d911a4e3cbb5e3a1463f426313725b4f96cde9879ff4b279a02b.webp", "display_name": "🎰 PG Slot 61", "provider": "PG SOFT", "image_file": "d10245e2aab6d911a4e3cbb5e3a1463f426313725b4f96cde9879ff4b279a02b.webp"},
    {"game_id": "PG SOFT/d3710a8bf2e94dc80524b5b1d8a185f31d414a0eaf9dbdd6b997d2de2a2e5e9a.webp", "display_name": "🎰 PG Slot 62", "provider": "PG SOFT", "image_file": "d3710a8bf2e94dc80524b5b1d8a185f31d414a0eaf9dbdd6b997d2de2a2e5e9a.webp"},
    {"game_id": "PG SOFT/dd87c3e26e691394644f73fd585a6110b59f8585f080bbd1e472dbfccf991c26.webp", "display_name": "🎰 PG Slot 63", "provider": "PG SOFT", "image_file": "dd87c3e26e691394644f73fd585a6110b59f8585f080bbd1e472dbfccf991c26.webp"},
    {"game_id": "PG SOFT/e0ba91c17c2d2b2af5bae040c981e4531ac94406797d5427f199e17ac9eba05c.webp", "display_name": "🎰 PG Slot 64", "provider": "PG SOFT", "image_file": "e0ba91c17c2d2b2af5bae040c981e4531ac94406797d5427f199e17ac9eba05c.webp"},
    {"game_id": "PG SOFT/e3aff371bba17c1db7572ff07512aafb8c4ae473f0f0d95d1461e7daf319fe1a.webp", "display_name": "🎰 PG Slot 65", "provider": "PG SOFT", "image_file": "e3aff371bba17c1db7572ff07512aafb8c4ae473f0f0d95d1461e7daf319fe1a.webp"},
    {"game_id": "PG SOFT/e682e8740cb65b3620c148693d1aa4cdd90d0b3f1690b98f697fb7e6b072e0ef.webp", "display_name": "🎰 PG Slot 66", "provider": "PG SOFT", "image_file": "e682e8740cb65b3620c148693d1aa4cdd90d0b3f1690b98f697fb7e6b072e0ef.webp"},
    {"game_id": "PG SOFT/e7f15a5d4fb512510ce01f7473211aebdbdf5f77545d0091003f1e1335a317bf.webp", "display_name": "🎰 PG Slot 67", "provider": "PG SOFT", "image_file": "e7f15a5d4fb512510ce01f7473211aebdbdf5f77545d0091003f1e1335a317bf.webp"},
    {"game_id": "PG SOFT/f1048986d68bd8492a6ad219afd5f3137561bc8a772594b9deb8a058903d6188.webp", "display_name": "🎰 PG Slot 68", "provider": "PG SOFT", "image_file": "f1048986d68bd8492a6ad219afd5f3137561bc8a772594b9deb8a058903d6188.webp"},
    {"game_id": "PG SOFT/f2a4f2677fe5582eee5b8697294e0991027b0b98358828ee4bd6dce909b992a2.webp", "display_name": "🎰 PG Slot 69", "provider": "PG SOFT", "image_file": "f2a4f2677fe5582eee5b8697294e0991027b0b98358828ee4bd6dce909b992a2.webp"},
    {"game_id": "PG SOFT/f2cf678febd959e953600562ec6549fd8cd58a882c65d1fd97ce892679fd12d7.webp", "display_name": "🎰 PG Slot 70", "provider": "PG SOFT", "image_file": "f2cf678febd959e953600562ec6549fd8cd58a882c65d1fd97ce892679fd12d7.webp"},
    {"game_id": "PG SOFT/f2d40f0a0ede301a5ea6e1c21a7bd744d144ce4429240a20c362d50845b75fa6.webp", "display_name": "🎰 PG Slot 71", "provider": "PG SOFT", "image_file": "f2d40f0a0ede301a5ea6e1c21a7bd744d144ce4429240a20c362d50845b75fa6.webp"},
    {"game_id": "PG SOFT/f8851c0c514b0ae10397f841dfd2b54f563dfd032a5bb23ed06294a3cadf3488.webp", "display_name": "🎰 PG Slot 72", "provider": "PG SOFT", "image_file": "f8851c0c514b0ae10397f841dfd2b54f563dfd032a5bb23ed06294a3cadf3488.webp"},
    {"game_id": "PG SOFT/f90bde94d4c692be0656cb87f4a5b8f5aefae22994a9692bee7d27b752dc9b75.webp", "display_name": "🎰 PG Slot 73", "provider": "PG SOFT", "image_file": "f90bde94d4c692be0656cb87f4a5b8f5aefae22994a9692bee7d27b752dc9b75.webp"},
    {"game_id": "PG SOFT/fd2b972e7879166ad09cd693a58ead3b062d5c1b7e598e39670b07729dac90ea.webp", "display_name": "🎰 PG Slot 74", "provider": "PG SOFT", "image_file": "fd2b972e7879166ad09cd693a58ead3b062d5c1b7e598e39670b07729dac90ea.webp"},
    {"game_id": "PG SOFT/fda969baceb517b392506ce27e181e3f27a7a093c906e6a2b2080ea14eb9cde1.webp", "display_name": "🎰 PG Slot 75", "provider": "PG SOFT", "image_file": "fda969baceb517b392506ce27e181e3f27a7a093c906e6a2b2080ea14eb9cde1.webp"},
]

# Pragmatic Play Games (100 games)
PRAGMATIC_GAMES = [
    # Named Popular Games (12)
    {"game_id": "Pragmatic Play/OLYMPUS.webp", "display_name": "⚡ Gates of Olympus", "provider": "PRAGMATIC PLAY", "image_file": "OLYMPUS.webp"},
    {"game_id": "Pragmatic Play/POPULAR_1.webp", "display_name": "🍓 Fruit Party", "provider": "PRAGMATIC PLAY", "image_file": "POPULAR_1.webp"},
    {"game_id": "Pragmatic Play/POPULAR_2.webp", "display_name": "🎄 Sugar Rush Xmas", "provider": "PRAGMATIC PLAY", "image_file": "POPULAR_2.webp"},
    {"game_id": "Pragmatic Play/POPULAR_3.webp", "display_name": "🐟 Big Bass Bonanza", "provider": "PRAGMATIC PLAY", "image_file": "POPULAR_3.webp"},
    {"game_id": "Pragmatic Play/POPULAR_4.webp", "display_name": "💎 Gems Bonanza", "provider": "PRAGMATIC PLAY", "image_file": "POPULAR_4.webp"},
    {"game_id": "Pragmatic Play/POPULAR_5.webp", "display_name": "🍬 Sweet Bonanza", "provider": "PRAGMATIC PLAY", "image_file": "POPULAR_5.webp"},
    {"game_id": "Pragmatic Play/POPULAR_6.webp", "display_name": "👸 Starlight Princess 1000", "provider": "PRAGMATIC PLAY", "image_file": "POPULAR_6.webp"},
    {"game_id": "Pragmatic Play/POPULAR_7.webp", "display_name": "⚡ Gates of Olympus SS", "provider": "PRAGMATIC PLAY", "image_file": "POPULAR_7.webp"},
    {"game_id": "Pragmatic Play/POPULAR_8.webp", "display_name": "⚡ Gates of Olympus 1000", "provider": "PRAGMATIC PLAY", "image_file": "POPULAR_8.webp"},
    {"game_id": "Pragmatic Play/POPULAR_9.webp", "display_name": "🎰 Popular Slot 9", "provider": "PRAGMATIC PLAY", "image_file": "POPULAR_9.webp"},
    {"game_id": "Pragmatic Play/POPULAR_10.webp", "display_name": "🎰 Popular Slot 10", "provider": "PRAGMATIC PLAY", "image_file": "POPULAR_10.webp"},
    # Hash-named Pragmatic Play games (88 more to reach 100)
    {"game_id": "Pragmatic Play/01eb804c6f183be20037c9c767a8552f5c01a31351017717d7a49de4b4d43844.webp", "display_name": "🎲 PP Slot 01", "provider": "PRAGMATIC PLAY", "image_file": "01eb804c6f183be20037c9c767a8552f5c01a31351017717d7a49de4b4d43844.webp"},
    {"game_id": "Pragmatic Play/0b269cceb05d0f0a368c87fc7d6412c77574a0414f451cb9b9c550c0b1381a2d.webp", "display_name": "🎲 PP Slot 02", "provider": "PRAGMATIC PLAY", "image_file": "0b269cceb05d0f0a368c87fc7d6412c77574a0414f451cb9b9c550c0b1381a2d.webp"},
    {"game_id": "Pragmatic Play/0e12554e0954c76443375cdde490b4ee1ed170eaa7b157909675f8d683afee3c.webp", "display_name": "🎲 PP Slot 03", "provider": "PRAGMATIC PLAY", "image_file": "0e12554e0954c76443375cdde490b4ee1ed170eaa7b157909675f8d683afee3c.webp"},
    {"game_id": "Pragmatic Play/0e544b224c23d04c0d9677a65ada5d87749027cec56af4ce419b8a4bde1e31da.webp", "display_name": "🎲 PP Slot 04", "provider": "PRAGMATIC PLAY", "image_file": "0e544b224c23d04c0d9677a65ada5d87749027cec56af4ce419b8a4bde1e31da.webp"},
    {"game_id": "Pragmatic Play/0eeb084b421e2e96d17fce52d9bd81ca5c7396e8035beaf30e84a8510169e1b4.webp", "display_name": "🎲 PP Slot 05", "provider": "PRAGMATIC PLAY", "image_file": "0eeb084b421e2e96d17fce52d9bd81ca5c7396e8035beaf30e84a8510169e1b4.webp"},
    {"game_id": "Pragmatic Play/14d5410c6cf4c303d291262a10e949dc14b0ac2eca2a7a730b0401919c01358e.webp", "display_name": "🎲 PP Slot 06", "provider": "PRAGMATIC PLAY", "image_file": "14d5410c6cf4c303d291262a10e949dc14b0ac2eca2a7a730b0401919c01358e.webp"},
    {"game_id": "Pragmatic Play/179ea3eb0e30b31875d7889466c65b52f028eb05d5153cab9e7aaddc1007e18c.webp", "display_name": "🎲 PP Slot 07", "provider": "PRAGMATIC PLAY", "image_file": "179ea3eb0e30b31875d7889466c65b52f028eb05d5153cab9e7aaddc1007e18c.webp"},
    {"game_id": "Pragmatic Play/181ccd872939a7a23b955a3de13bb83cc2c923e20fe358c37f70d3f9af533e7e.webp", "display_name": "🎲 PP Slot 08", "provider": "PRAGMATIC PLAY", "image_file": "181ccd872939a7a23b955a3de13bb83cc2c923e20fe358c37f70d3f9af533e7e.webp"},
    {"game_id": "Pragmatic Play/1b79532a239bd087f3c3ea7d3fc831587d03ee765a07fcb4b1ca104a055544b2.webp", "display_name": "🎲 PP Slot 09", "provider": "PRAGMATIC PLAY", "image_file": "1b79532a239bd087f3c3ea7d3fc831587d03ee765a07fcb4b1ca104a055544b2.webp"},
    {"game_id": "Pragmatic Play/1f8f74ee5cdbcd77a1bdb882e6218ada8f29a21de3c77f7c028fe021e13ab4c5.webp", "display_name": "🎲 PP Slot 10", "provider": "PRAGMATIC PLAY", "image_file": "1f8f74ee5cdbcd77a1bdb882e6218ada8f29a21de3c77f7c028fe021e13ab4c5.webp"},
    {"game_id": "Pragmatic Play/254be69fcde2ce6dc6ffda3319d00af47708a4285de4196cbf58e33139a5e552.webp", "display_name": "🎲 PP Slot 11", "provider": "PRAGMATIC PLAY", "image_file": "254be69fcde2ce6dc6ffda3319d00af47708a4285de4196cbf58e33139a5e552.webp"},
    {"game_id": "Pragmatic Play/26802168dc5361febe0325f36cfc6af8a4b8535c8d6181961d4d6d948d4f5ee0.webp", "display_name": "🎲 PP Slot 12", "provider": "PRAGMATIC PLAY", "image_file": "26802168dc5361febe0325f36cfc6af8a4b8535c8d6181961d4d6d948d4f5ee0.webp"},
    {"game_id": "Pragmatic Play/2859df47036f5c6d3f33fead0d26c9538046589c90d5b59621306d9e4e7bfcc0.webp", "display_name": "🎲 PP Slot 13", "provider": "PRAGMATIC PLAY", "image_file": "2859df47036f5c6d3f33fead0d26c9538046589c90d5b59621306d9e4e7bfcc0.webp"},
    {"game_id": "Pragmatic Play/2cef1d4fc88f4f91ab86775d25b4cc3fed042af3ac81d641a559a4c517f3d9ef.webp", "display_name": "🎲 PP Slot 14", "provider": "PRAGMATIC PLAY", "image_file": "2cef1d4fc88f4f91ab86775d25b4cc3fed042af3ac81d641a559a4c517f3d9ef.webp"},
    {"game_id": "Pragmatic Play/2e0fb5d8d19a26f8dabafc4076ce81c7eb653a613219a9fbb7cc44ec936ce993.webp", "display_name": "🎲 PP Slot 15", "provider": "PRAGMATIC PLAY", "image_file": "2e0fb5d8d19a26f8dabafc4076ce81c7eb653a613219a9fbb7cc44ec936ce993.webp"},
    {"game_id": "Pragmatic Play/2e2aac1c67740ba49ee4a3e5c8e7e5397d5cdb477298db45b82916e2431e898b.webp", "display_name": "🎲 PP Slot 16", "provider": "PRAGMATIC PLAY", "image_file": "2e2aac1c67740ba49ee4a3e5c8e7e5397d5cdb477298db45b82916e2431e898b.webp"},
    {"game_id": "Pragmatic Play/2f62c75034b67e30d769838612cc8cd0021eb2033acccf98c5e889cab847be05.webp", "display_name": "🎲 PP Slot 17", "provider": "PRAGMATIC PLAY", "image_file": "2f62c75034b67e30d769838612cc8cd0021eb2033acccf98c5e889cab847be05.webp"},
    {"game_id": "Pragmatic Play/308ef68e4faa11eeea79ebe1a428a6b8e51681e4a5393a1ecfe3ba5db5adf196.webp", "display_name": "🎲 PP Slot 18", "provider": "PRAGMATIC PLAY", "image_file": "308ef68e4faa11eeea79ebe1a428a6b8e51681e4a5393a1ecfe3ba5db5adf196.webp"},
    {"game_id": "Pragmatic Play/31704ea553666f0d08ef9edffe97996f367f38aa5bc32b280f305c2e25f96d57.webp", "display_name": "🎲 PP Slot 19", "provider": "PRAGMATIC PLAY", "image_file": "31704ea553666f0d08ef9edffe97996f367f38aa5bc32b280f305c2e25f96d57.webp"},
    {"game_id": "Pragmatic Play/31d384b25e3d6c8704f84b3db84e31bceacf2ff16279fbcc25ad9e1bf55a7564.webp", "display_name": "🎲 PP Slot 20", "provider": "PRAGMATIC PLAY", "image_file": "31d384b25e3d6c8704f84b3db84e31bceacf2ff16279fbcc25ad9e1bf55a7564.webp"},
    {"game_id": "Pragmatic Play/33ea7f514199523216fbb025355f8fdbb0a29bae063e751655e64c99743f16ac.webp", "display_name": "🎲 PP Slot 21", "provider": "PRAGMATIC PLAY", "image_file": "33ea7f514199523216fbb025355f8fdbb0a29bae063e751655e64c99743f16ac.webp"},
    {"game_id": "Pragmatic Play/35ad71ac5000b070bf9d5ab332602ae69f8e22c8e1c8d24a1f4418a20bd18eda.webp", "display_name": "🎲 PP Slot 22", "provider": "PRAGMATIC PLAY", "image_file": "35ad71ac5000b070bf9d5ab332602ae69f8e22c8e1c8d24a1f4418a20bd18eda.webp"},
    {"game_id": "Pragmatic Play/385705dc3bc1b5cff015de7acb337ccb6767a42e19ed12a5f70089b67361218d.webp", "display_name": "🎲 PP Slot 23", "provider": "PRAGMATIC PLAY", "image_file": "385705dc3bc1b5cff015de7acb337ccb6767a42e19ed12a5f70089b67361218d.webp"},
    {"game_id": "Pragmatic Play/3ae0cb707dd63ad5ff0618d8a38ddf31cc74c371fc35a3644d0122b116252504.webp", "display_name": "🎲 PP Slot 24", "provider": "PRAGMATIC PLAY", "image_file": "3ae0cb707dd63ad5ff0618d8a38ddf31cc74c371fc35a3644d0122b116252504.webp"},
    {"game_id": "Pragmatic Play/3b1de17d4f265d5ca39a883d651bd70a6b0a6859203e519d2f67e2598a4704aa.webp", "display_name": "🎲 PP Slot 25", "provider": "PRAGMATIC PLAY", "image_file": "3b1de17d4f265d5ca39a883d651bd70a6b0a6859203e519d2f67e2598a4704aa.webp"},
    {"game_id": "Pragmatic Play/4751adaff8999760e52bbdc76cd404fc064ad198c8778cfb8fdfaae50b003f98.webp", "display_name": "🎲 PP Slot 26", "provider": "PRAGMATIC PLAY", "image_file": "4751adaff8999760e52bbdc76cd404fc064ad198c8778cfb8fdfaae50b003f98.webp"},
    {"game_id": "Pragmatic Play/47638ff859b79996b7fdc10cd3b14360b708c640536acdc5ad5aa879c6fe7044.webp", "display_name": "🎲 PP Slot 27", "provider": "PRAGMATIC PLAY", "image_file": "47638ff859b79996b7fdc10cd3b14360b708c640536acdc5ad5aa879c6fe7044.webp"},
    {"game_id": "Pragmatic Play/47b80f887282c2e75f1d398eb58823e9ecf0abd0bcf72d25f8c38e64a33a577e.webp", "display_name": "🎲 PP Slot 28", "provider": "PRAGMATIC PLAY", "image_file": "47b80f887282c2e75f1d398eb58823e9ecf0abd0bcf72d25f8c38e64a33a577e.webp"},
    {"game_id": "Pragmatic Play/49950a8148c358e88455c78d8dd1abfbeb8d2dd31a7b7971f5515ae4091b6429.webp", "display_name": "🎲 PP Slot 29", "provider": "PRAGMATIC PLAY", "image_file": "49950a8148c358e88455c78d8dd1abfbeb8d2dd31a7b7971f5515ae4091b6429.webp"},
    {"game_id": "Pragmatic Play/4a8e119e4fc2dfd38439f8adbd315ed6c377f5ea825bb293f28fabbe0a34cd38.webp", "display_name": "🎲 PP Slot 30", "provider": "PRAGMATIC PLAY", "image_file": "4a8e119e4fc2dfd38439f8adbd315ed6c377f5ea825bb293f28fabbe0a34cd38.webp"},
    {"game_id": "Pragmatic Play/4af24920ee5ecb18c43c754e17f03803bb465100ae71123e40db0f34f10b0b84.webp", "display_name": "🎲 PP Slot 31", "provider": "PRAGMATIC PLAY", "image_file": "4af24920ee5ecb18c43c754e17f03803bb465100ae71123e40db0f34f10b0b84.webp"},
    {"game_id": "Pragmatic Play/4cb1ded0004d8bfc0133b38ad1ba357ecb1610eae73c8587cd09d5aa4becaf98.webp", "display_name": "🎲 PP Slot 32", "provider": "PRAGMATIC PLAY", "image_file": "4cb1ded0004d8bfc0133b38ad1ba357ecb1610eae73c8587cd09d5aa4becaf98.webp"},
    {"game_id": "Pragmatic Play/4d7d6df43e4183cb9f149bdb96f15da63de78efa52daeb7fc4cf0b2dc37608e9.webp", "display_name": "🎲 PP Slot 33", "provider": "PRAGMATIC PLAY", "image_file": "4d7d6df43e4183cb9f149bdb96f15da63de78efa52daeb7fc4cf0b2dc37608e9.webp"},
    {"game_id": "Pragmatic Play/4dd82e4a742d93dc80c411ea0b7bde677a01727287535e07946f831cfccf0957.webp", "display_name": "🎲 PP Slot 34", "provider": "PRAGMATIC PLAY", "image_file": "4dd82e4a742d93dc80c411ea0b7bde677a01727287535e07946f831cfccf0957.webp"},
    {"game_id": "Pragmatic Play/4e9386ce838d3c59b1905529a13063930ea1bc11cc9bd29a5062dd7d47c383d1.webp", "display_name": "🎲 PP Slot 35", "provider": "PRAGMATIC PLAY", "image_file": "4e9386ce838d3c59b1905529a13063930ea1bc11cc9bd29a5062dd7d47c383d1.webp"},
    {"game_id": "Pragmatic Play/4f656be5970a7314078d68157aa835ef7e821a2f5fa16bdddf0b175f927fe791.webp", "display_name": "🎲 PP Slot 36", "provider": "PRAGMATIC PLAY", "image_file": "4f656be5970a7314078d68157aa835ef7e821a2f5fa16bdddf0b175f927fe791.webp"},
    {"game_id": "Pragmatic Play/513989e83e5078b3a03a8d1d3c71b5ac8dfdc8a064430adc3e34eca732733b8e.webp", "display_name": "🎲 PP Slot 37", "provider": "PRAGMATIC PLAY", "image_file": "513989e83e5078b3a03a8d1d3c71b5ac8dfdc8a064430adc3e34eca732733b8e.webp"},
    {"game_id": "Pragmatic Play/515b7aad8b76748956fe3c8fc75a80604ff1b3aa6507e90cdf67663d7a47c3b2.webp", "display_name": "🎲 PP Slot 38", "provider": "PRAGMATIC PLAY", "image_file": "515b7aad8b76748956fe3c8fc75a80604ff1b3aa6507e90cdf67663d7a47c3b2.webp"},
    {"game_id": "Pragmatic Play/516dd23e24bc643b9f6d77362b11b8b077ccea882a4dffb2913e023d7131fbef.webp", "display_name": "🎲 PP Slot 39", "provider": "PRAGMATIC PLAY", "image_file": "516dd23e24bc643b9f6d77362b11b8b077ccea882a4dffb2913e023d7131fbef.webp"},
    {"game_id": "Pragmatic Play/58c26df3887b38eec9946ebe7ec61016f3cd1bb443540019fc85584af52d78f2.webp", "display_name": "🎲 PP Slot 40", "provider": "PRAGMATIC PLAY", "image_file": "58c26df3887b38eec9946ebe7ec61016f3cd1bb443540019fc85584af52d78f2.webp"},
    {"game_id": "Pragmatic Play/58d261aa0cb26e3647956d9cedb3d6efbd8bf9fc12d1498dda8ee053c64cc064.webp", "display_name": "🎲 PP Slot 41", "provider": "PRAGMATIC PLAY", "image_file": "58d261aa0cb26e3647956d9cedb3d6efbd8bf9fc12d1498dda8ee053c64cc064.webp"},
    {"game_id": "Pragmatic Play/5befbb8621f3b529ef0a8576edc94bce337c013f8788e9fb71d8b552a0bd5f9e.webp", "display_name": "🎲 PP Slot 42", "provider": "PRAGMATIC PLAY", "image_file": "5befbb8621f3b529ef0a8576edc94bce337c013f8788e9fb71d8b552a0bd5f9e.webp"},
    {"game_id": "Pragmatic Play/5f66bd7f515175883d6d66e609e125fcf33f53508ea9a986841a822b63dbc9cf.webp", "display_name": "🎲 PP Slot 43", "provider": "PRAGMATIC PLAY", "image_file": "5f66bd7f515175883d6d66e609e125fcf33f53508ea9a986841a822b63dbc9cf.webp"},
    {"game_id": "Pragmatic Play/60206bb76f8d15dd2975ea5d5c908194c66a1183683e6988c83027ada9befbef.webp", "display_name": "🎲 PP Slot 44", "provider": "PRAGMATIC PLAY", "image_file": "60206bb76f8d15dd2975ea5d5c908194c66a1183683e6988c83027ada9befbef.webp"},
    {"game_id": "Pragmatic Play/61aff4b0576e94af8e472da08694b9d63c47a08401e90fbecb381578704175c4.webp", "display_name": "🎲 PP Slot 45", "provider": "PRAGMATIC PLAY", "image_file": "61aff4b0576e94af8e472da08694b9d63c47a08401e90fbecb381578704175c4.webp"},
    {"game_id": "Pragmatic Play/628496a33da1c9c2c781d908a993a0de45f6672a1a4187b03e014743280f9f71.webp", "display_name": "🎲 PP Slot 46", "provider": "PRAGMATIC PLAY", "image_file": "628496a33da1c9c2c781d908a993a0de45f6672a1a4187b03e014743280f9f71.webp"},
    {"game_id": "Pragmatic Play/62b2449f9a8577d4908ca4c2478e8db46ce6ef3f306eaa4497d607e0db853d5b.webp", "display_name": "🎲 PP Slot 47", "provider": "PRAGMATIC PLAY", "image_file": "62b2449f9a8577d4908ca4c2478e8db46ce6ef3f306eaa4497d607e0db853d5b.webp"},
    {"game_id": "Pragmatic Play/63b93076df813efb83ee33b4d4f8cb4500ac4bfd0c454c4d3a051b0da7f8af9a.webp", "display_name": "🎲 PP Slot 48", "provider": "PRAGMATIC PLAY", "image_file": "63b93076df813efb83ee33b4d4f8cb4500ac4bfd0c454c4d3a051b0da7f8af9a.webp"},
    {"game_id": "Pragmatic Play/64436402c8e5d5331d04d615796f0f74da0260f52cef74e61acfac0378466309.webp", "display_name": "🎲 PP Slot 49", "provider": "PRAGMATIC PLAY", "image_file": "64436402c8e5d5331d04d615796f0f74da0260f52cef74e61acfac0378466309.webp"},
    {"game_id": "Pragmatic Play/6b106c589bb9482c20e5716667face26cbd017abc13ed84e2dc2d2beb4d31ebf.webp", "display_name": "🎲 PP Slot 50", "provider": "PRAGMATIC PLAY", "image_file": "6b106c589bb9482c20e5716667face26cbd017abc13ed84e2dc2d2beb4d31ebf.webp"},
    {"game_id": "Pragmatic Play/6bd16708800d460b31c2ee7996f01a806496830fe5cff923daa003eeca3d0fd8.webp", "display_name": "🎲 PP Slot 51", "provider": "PRAGMATIC PLAY", "image_file": "6bd16708800d460b31c2ee7996f01a806496830fe5cff923daa003eeca3d0fd8.webp"},
    {"game_id": "Pragmatic Play/6cc2add248e5f0abe721f03240b12cb42b7c3cb4661504b521d91859bedcddad.webp", "display_name": "🎲 PP Slot 52", "provider": "PRAGMATIC PLAY", "image_file": "6cc2add248e5f0abe721f03240b12cb42b7c3cb4661504b521d91859bedcddad.webp"},
    {"game_id": "Pragmatic Play/6d6b5cda13c1b3cacf27c22c7a5842dc539c71f962b5d2c2ba51b47cc19b9079.webp", "display_name": "🎲 PP Slot 53", "provider": "PRAGMATIC PLAY", "image_file": "6d6b5cda13c1b3cacf27c22c7a5842dc539c71f962b5d2c2ba51b47cc19b9079.webp"},
    {"game_id": "Pragmatic Play/6de4ad5cbac5be1dbb06c9bbee87bea4b08b1d30fa4715229cc421f972a65337.webp", "display_name": "🎲 PP Slot 54", "provider": "PRAGMATIC PLAY", "image_file": "6de4ad5cbac5be1dbb06c9bbee87bea4b08b1d30fa4715229cc421f972a65337.webp"},
    {"game_id": "Pragmatic Play/6eba0e3bad33c83a24477372960f6abdcb7087e42a8fd35423beb4e083c33060.webp", "display_name": "🎲 PP Slot 55", "provider": "PRAGMATIC PLAY", "image_file": "6eba0e3bad33c83a24477372960f6abdcb7087e42a8fd35423beb4e083c33060.webp"},
    {"game_id": "Pragmatic Play/73754d4bf421b78fbd3895bbc7890d379797588cb699d6cbe47f3656aa93613b.webp", "display_name": "🎲 PP Slot 56", "provider": "PRAGMATIC PLAY", "image_file": "73754d4bf421b78fbd3895bbc7890d379797588cb699d6cbe47f3656aa93613b.webp"},
    {"game_id": "Pragmatic Play/741f8f9dd2ead70e1e3fb9b34ef4058b0b431ea93f60f17b71ac65fa7f41bf17.webp", "display_name": "🎲 PP Slot 57", "provider": "PRAGMATIC PLAY", "image_file": "741f8f9dd2ead70e1e3fb9b34ef4058b0b431ea93f60f17b71ac65fa7f41bf17.webp"},
    {"game_id": "Pragmatic Play/767b3f62a9beb01c841faca3bb76846e7a4626efe2f8b67e195880d9bebe817f.webp", "display_name": "🎲 PP Slot 58", "provider": "PRAGMATIC PLAY", "image_file": "767b3f62a9beb01c841faca3bb76846e7a4626efe2f8b67e195880d9bebe817f.webp"},
    {"game_id": "Pragmatic Play/7681efb7a93a1213310cb40d18f06111d8809ce1becf6b77ef033ac83d2d1d24.webp", "display_name": "🎲 PP Slot 59", "provider": "PRAGMATIC PLAY", "image_file": "7681efb7a93a1213310cb40d18f06111d8809ce1becf6b77ef033ac83d2d1d24.webp"},
    {"game_id": "Pragmatic Play/78460943fb9a9ceb88066262c9d5a208212383b6a8b530ea7a2a302257e8bfa2.webp", "display_name": "🎲 PP Slot 60", "provider": "PRAGMATIC PLAY", "image_file": "78460943fb9a9ceb88066262c9d5a208212383b6a8b530ea7a2a302257e8bfa2.webp"},
    {"game_id": "Pragmatic Play/796957e88a7a9d2531a60ccde77ed922ebb028c6e3d2d3a3eb683ca3e7dd9feb.webp", "display_name": "🎲 PP Slot 61", "provider": "PRAGMATIC PLAY", "image_file": "796957e88a7a9d2531a60ccde77ed922ebb028c6e3d2d3a3eb683ca3e7dd9feb.webp"},
    {"game_id": "Pragmatic Play/7a73d0321e7b6501b7f92b3522c7e6410f4ba8a94ffbf2a260b92a4c509e8cec.webp", "display_name": "🎲 PP Slot 62", "provider": "PRAGMATIC PLAY", "image_file": "7a73d0321e7b6501b7f92b3522c7e6410f4ba8a94ffbf2a260b92a4c509e8cec.webp"},
    {"game_id": "Pragmatic Play/7afa70087cd305cd29c1e27e2dd61c71982ceefb16fe17fb593da1214ca20276.webp", "display_name": "🎲 PP Slot 63", "provider": "PRAGMATIC PLAY", "image_file": "7afa70087cd305cd29c1e27e2dd61c71982ceefb16fe17fb593da1214ca20276.webp"},
    {"game_id": "Pragmatic Play/7beb8d9a3555d964d702dc7c466dbb8970db965854a7ef1863591a5fa030e91c.webp", "display_name": "🎲 PP Slot 64", "provider": "PRAGMATIC PLAY", "image_file": "7beb8d9a3555d964d702dc7c466dbb8970db965854a7ef1863591a5fa030e91c.webp"},
    {"game_id": "Pragmatic Play/7f65a3148997321a5a97908745726044e003b310bc0e52a397acef36b525dcbe.webp", "display_name": "🎲 PP Slot 65", "provider": "PRAGMATIC PLAY", "image_file": "7f65a3148997321a5a97908745726044e003b310bc0e52a397acef36b525dcbe.webp"},
    {"game_id": "Pragmatic Play/80987919d4aa387ebdd70045c930a556e6905899121577da102dcb19f728e026.webp", "display_name": "🎲 PP Slot 66", "provider": "PRAGMATIC PLAY", "image_file": "80987919d4aa387ebdd70045c930a556e6905899121577da102dcb19f728e026.webp"},
    {"game_id": "Pragmatic Play/80cef3c2101ccc6abeb74df85fe242c1ba7cb741f4d1c16c8791818721495943.webp", "display_name": "🎲 PP Slot 67", "provider": "PRAGMATIC PLAY", "image_file": "80cef3c2101ccc6abeb74df85fe242c1ba7cb741f4d1c16c8791818721495943.webp"},
    {"game_id": "Pragmatic Play/83f635b69fd26ecd4a7c43a983302ad110a1150ffc23b930fa04d99f6fb186bf.webp", "display_name": "🎲 PP Slot 68", "provider": "PRAGMATIC PLAY", "image_file": "83f635b69fd26ecd4a7c43a983302ad110a1150ffc23b930fa04d99f6fb186bf.webp"},
    {"game_id": "Pragmatic Play/83fbc67b1edc1081b2394e3650cb62cfd17456ebf68727ac287b4c55de00c0db.webp", "display_name": "🎲 PP Slot 69", "provider": "PRAGMATIC PLAY", "image_file": "83fbc67b1edc1081b2394e3650cb62cfd17456ebf68727ac287b4c55de00c0db.webp"},
    {"game_id": "Pragmatic Play/84b9e198ab9afe0b9624816c00d6ebebb7df1cf348bc26ed055235bd9ee1ab07.webp", "display_name": "🎲 PP Slot 70", "provider": "PRAGMATIC PLAY", "image_file": "84b9e198ab9afe0b9624816c00d6ebebb7df1cf348bc26ed055235bd9ee1ab07.webp"},
    {"game_id": "Pragmatic Play/8641f39a396b6d38f7259c16f09f320f5f1b5652c4ce8ec4a231bd585ff9ba5b.webp", "display_name": "🎲 PP Slot 71", "provider": "PRAGMATIC PLAY", "image_file": "8641f39a396b6d38f7259c16f09f320f5f1b5652c4ce8ec4a231bd585ff9ba5b.webp"},
    {"game_id": "Pragmatic Play/8777ab38250f62af7f6f7f0d4665cb12354a2774ca5e2be7e78958c8a118fa64.webp", "display_name": "🎲 PP Slot 72", "provider": "PRAGMATIC PLAY", "image_file": "8777ab38250f62af7f6f7f0d4665cb12354a2774ca5e2be7e78958c8a118fa64.webp"},
    {"game_id": "Pragmatic Play/884da2c4d7b719ff5078a4960928d11f831314f1c4fe6db828d3fced07404d13.webp", "display_name": "🎲 PP Slot 73", "provider": "PRAGMATIC PLAY", "image_file": "884da2c4d7b719ff5078a4960928d11f831314f1c4fe6db828d3fced07404d13.webp"},
    {"game_id": "Pragmatic Play/88d127f9829aa7336afc1d00ef0513e7c48d412ef33138b73f7a7746314375bd.webp", "display_name": "🎲 PP Slot 74", "provider": "PRAGMATIC PLAY", "image_file": "88d127f9829aa7336afc1d00ef0513e7c48d412ef33138b73f7a7746314375bd.webp"},
    {"game_id": "Pragmatic Play/8b7b4969e2d28e603176bd8efe2e2e791efe6435ed4c1ab8456948e3f6d6cfb8.webp", "display_name": "🎲 PP Slot 75", "provider": "PRAGMATIC PLAY", "image_file": "8b7b4969e2d28e603176bd8efe2e2e791efe6435ed4c1ab8456948e3f6d6cfb8.webp"},
]

# Combine all games
ALL_GAMES = PG_SOFT_GAMES + PRAGMATIC_GAMES

# =============================================================================
# CHANNEL CONFIGURATION
# =============================================================================
# Each channel can be configured to show only specific providers
# Set provider to "ALL" to show all games, or specify provider name
# =============================================================================

CHANNEL_CONFIG = [
    {
        "channel_id": "@asdassadher314",      # Replace with your PG SOFT channel
        "provider": "PG SOFT",                  # Only PG SOFT games (Fortune series)
        "name": "PG SOFT Channel"
    },
    {
        "channel_id": "@qwrcxvasdad",    # Replace with your Pragmatic Play channel
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
    Filters ALL_GAMES to find those with RTP >= 80%.
    Returns only the TOP 5 highest RTP games per channel.
    Can filter by provider. Skips games where image file doesn't exist.
    
    Args:
        provider_filter: "ALL" for all games, or specific provider name
                        (e.g., "PG SOFT", "PRAGMATIC PLAY")
    
    Returns:
        List of top 5 game dictionaries with RTP >= 80%, including:
        - game_id, display_name, provider, image_file
        - rtp, strategy (normal, auto, turbo), multiplier
    """
    high_rtp_games = []
    
    for game in ALL_GAMES:
        # Filter by provider if specified
        if provider_filter != "ALL":
            if game["provider"].upper() != provider_filter.upper():
                continue
        
        # Skip games where image file doesn't exist
        image_path = f"{IMAGE_BASE_PATH}{game['image_file']}"
        if not os.path.exists(image_path):
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
    
    # Return only top 5 highest RTP games
    return high_rtp_games[:MAX_GAMES_PER_NOTIFICATION]


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
    
    for i, game in enumerate(ALL_GAMES, 1):
        game_hash = string_to_hash(game["game_id"])
        rtp = generate_game_rtp(game["game_id"])
        strategy = generate_game_strategy(game["game_id"])
        
        status = "🔥 HOT!" if rtp >= CONFIG["rtp_threshold"] else ""
        
        print(f"{i:<3} {game['display_name']:<35} {game_hash:<12} {rtp}%   {status}")
        print(f"    └ Normal: {strategy['normal']}X | Auto: {strategy['auto']} | Turbo: {strategy['turbo']}")
    
    print("-" * 70)
    
    high_rtp = [g for g in ALL_GAMES if generate_game_rtp(g["game_id"]) >= CONFIG["rtp_threshold"]]
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
    print(f"🎮 Jogos monitorados: {len(ALL_GAMES)}")
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

import logging
import sqlite3
import asyncio
from datetime import datetime, time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ContextTypes, ConversationHandler
)

# ==================== تنظیمات ====================
BOT_TOKEN =  ""
ADMIN_ID = ""


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ==================== حالت‌های مکالمه ====================
(MAIN_MENU, SELECT_COUNTRY, SELECT_GROUP, COUNTRY_MENU,
 SHOP_MENU, SHOP_CATEGORY, SHOP_ITEM, SHOP_QUANTITY,
 COMPANY_MENU, TRADE_MENU, TRADE_SELECT_ITEM, TRADE_QUANTITY,
 TRADE_PRICE, TRADE_SELECT_COUNTRY, TRADE_CONFIRM,
 DECLARATION_TEXT, DECLARATION_CONFIRM) = range(17)

# ==================== لیست کشورها ====================
COUNTRIES = {
    "USA": {"name": "ایالات متحده آمریکا", "flag": "🇺🇸", "oil": False, "vip": True},
    "ISRAEL": {"name": "اسرائیل", "flag": "🇮🇱", "oil": False, "vip": False},
    "IRAN": {"name": "ایران", "flag": "🇮🇷", "oil": True, "vip": False},
    "RUSSIA": {"name": "روسیه", "flag": "🇷🇺", "oil": True, "vip": True},
    "IRAQ": {"name": "عراق", "flag": "🇮🇶", "oil": True, "vip": False},
    "SAUDI": {"name": "عربستان سعودی", "flag": "🇸🇦", "oil": True, "vip": False},
    "UAE": {"name": "امارات", "flag": "🇦🇪", "oil": True, "vip": False},
    "PAKISTAN": {"name": "پاکستان", "flag": "🇵🇰", "oil": False, "vip": False},
    "INDIA": {"name": "هند", "flag": "🇮🇳", "oil": False, "vip": False},
    "NORTH_KOREA": {"name": "کره شمالی", "flag": "🇰🇵", "oil": False, "vip": True},
    "SOUTH_KOREA": {"name": "کره جنوبی", "flag": "🇰🇷", "oil": False, "vip": False},
    "JAPAN": {"name": "ژاپن", "flag": "🇯🇵", "oil": False, "vip": False},
    "CHINA": {"name": "چین", "flag": "🇨🇳", "oil": False, "vip": True},
    "CANADA": {"name": "کانادا", "flag": "🇨🇦", "oil": False, "vip": False},
    "UK": {"name": "انگلیس", "flag": "🇬🇧", "oil": False, "vip": True},
    "FRANCE": {"name": "فرانسه", "flag": "🇫🇷", "oil": False, "vip": True},
    "VENEZUELA": {"name": "ونزوئلا", "flag": "🇻🇪", "oil": True, "vip": False},
    "ITALY": {"name": "ایتالیا", "flag": "🇮🇹", "oil": False, "vip": False},
    "GERMANY": {"name": "آلمان", "flag": "🇩🇪", "oil": False, "vip": True},
    "ARGENTINA": {"name": "آرژانتین", "flag": "🇦🇷", "oil": False, "vip": False},
    "TURKEY": {"name": "ترکیه", "flag": "🇹🇷", "oil": False, "vip": False},
    "SPAIN": {"name": "اسپانیا", "flag": "🇪🇸", "oil": False, "vip": False},
    "YEMEN": {"name": "یمن", "flag": "🇾🇪", "oil": True, "vip": False},
    "BRAZIL": {"name": "برزیل", "flag": "🇧🇷", "oil": True, "vip": False},
    "MEXICO": {"name": "مکزیک", "flag": "🇲🇽", "oil": True, "vip": False},
    "EGYPT": {"name": "مصر", "flag": "🇪🇬", "oil": False, "vip": False},
    "NIGERIA": {"name": "نیجریه", "flag": "🇳🇬", "oil": True, "vip": False},
    "SOUTH_AFRICA": {"name": "آفریقای جنوبی", "flag": "🇿🇦", "oil": False, "vip": False},
    "ETHIOPIA": {"name": "اتیوپی", "flag": "🇪🇹", "oil": False, "vip": False},
    "KENYA": {"name": "کنیا", "flag": "🇰🇪", "oil": False, "vip": False},
    "MOROCCO": {"name": "مراکش", "flag": "🇲🇦", "oil": False, "vip": False},
    "ALGERIA": {"name": "الجزایر", "flag": "🇩🇿", "oil": True, "vip": False},
    "LIBYA": {"name": "لیبی", "flag": "🇱🇾", "oil": True, "vip": False},
    "JORDAN": {"name": "اردن", "flag": "🇯🇴", "oil": False, "vip": False},
    "SYRIA": {"name": "سوریه", "flag": "🇸🇾", "oil": False, "vip": False},
    "LEBANON": {"name": "لبنان", "flag": "🇱🇧", "oil": False, "vip": False},
    "AFGHANISTAN": {"name": "افغانستان", "flag": "🇦🇫", "oil": False, "vip": False},
    "UKRAINE": {"name": "اوکراین", "flag": "🇺🇦", "oil": False, "vip": False},
    "POLAND": {"name": "لهستان", "flag": "🇵🇱", "oil": False, "vip": False},
    "NETHERLANDS": {"name": "هلند", "flag": "🇳🇱", "oil": False, "vip": False},
    "SWEDEN": {"name": "سوئد", "flag": "🇸🇪", "oil": False, "vip": False},
    "NORWAY": {"name": "نروژ", "flag": "🇳🇴", "oil": True, "vip": False},
    "DENMARK": {"name": "دانمارک", "flag": "🇩🇰", "oil": False, "vip": False},
    "FINLAND": {"name": "فنلاند", "flag": "🇫🇮", "oil": False, "vip": False},
    "SWITZERLAND": {"name": "سوئیس", "flag": "🇨🇭", "oil": False, "vip": False},
    "AUSTRIA": {"name": "اتریش", "flag": "🇦🇹", "oil": False, "vip": False},
    "PORTUGAL": {"name": "پرتغال", "flag": "🇵🇹", "oil": False, "vip": False},
    "GREECE": {"name": "یونان", "flag": "🇬🇷", "oil": False, "vip": False},
    "BELGIUM": {"name": "بلژیک", "flag": "🇧🇪", "oil": False, "vip": False},
    "CZECH": {"name": "چک", "flag": "🇨🇿", "oil": False, "vip": False},
    "HUNGARY": {"name": "مجارستان", "flag": "🇭🇺", "oil": False, "vip": False},
    "ROMANIA": {"name": "رومانی", "flag": "🇷🇴", "oil": False, "vip": False},
    "SERBIA": {"name": "صربستان", "flag": "🇷🇸", "oil": False, "vip": False},
    "KAZAKHSTAN": {"name": "قزاقستان", "flag": "🇰🇿", "oil": True, "vip": False},
    "UZBEKISTAN": {"name": "ازبکستان", "flag": "🇺🇿", "oil": False, "vip": False},
    "AZERBAIJAN": {"name": "آذربایجان", "flag": "🇦🇿", "oil": True, "vip": False},
    "GEORGIA": {"name": "گرجستان", "flag": "🇬🇪", "oil": False, "vip": False},
    "THAILAND": {"name": "تایلند", "flag": "🇹🇭", "oil": False, "vip": False},
    "VIETNAM": {"name": "ویتنام", "flag": "🇻🇳", "oil": False, "vip": False},
    "INDONESIA": {"name": "اندونزی", "flag": "🇮🇩", "oil": True, "vip": False},
    "MALAYSIA": {"name": "مالزی", "flag": "🇲🇾", "oil": True, "vip": False},
    "PHILIPPINES": {"name": "فیلیپین", "flag": "🇵🇭", "oil": False, "vip": False},
    "MYANMAR": {"name": "میانمار", "flag": "🇲🇲", "oil": False, "vip": False},
    "BANGLADESH": {"name": "بنگلادش", "flag": "🇧🇩", "oil": False, "vip": False},
    "SRI_LANKA": {"name": "سریلانکا", "flag": "🇱🇰", "oil": False, "vip": False},
    "NEPAL": {"name": "نپال", "flag": "🇳🇵", "oil": False, "vip": False},
    "MONGOLIA": {"name": "مغولستان", "flag": "🇲🇳", "oil": False, "vip": False},
    "TAIWAN": {"name": "تایوان", "flag": "🇹🇼", "oil": False, "vip": False},
    "SINGAPORE": {"name": "سنگاپور", "flag": "🇸🇬", "oil": False, "vip": False},
    "AUSTRALIA": {"name": "استرالیا", "flag": "🇦🇺", "oil": True, "vip": True},
    "NEW_ZEALAND": {"name": "نیوزیلند", "flag": "🇳🇿", "oil": False, "vip": False},
    "CUBA": {"name": "کوبا", "flag": "🇨🇺", "oil": False, "vip": False},
    "COLOMBIA": {"name": "کلمبیا", "flag": "🇨🇴", "oil": True, "vip": False},
    "PERU": {"name": "پرو", "flag": "🇵🇪", "oil": False, "vip": False},
    "CHILE": {"name": "شیلی", "flag": "🇨🇱", "oil": False, "vip": False},
    "ECUADOR": {"name": "اکوادور", "flag": "🇪🇨", "oil": True, "vip": False},
    "BOLIVIA": {"name": "بولیوی", "flag": "🇧🇴", "oil": False, "vip": False},
    "GHANA": {"name": "غنا", "flag": "🇬🇭", "oil": True, "vip": False},
    "ANGOLA": {"name": "آنگولا", "flag": "🇦🇴", "oil": True, "vip": False},
    "MOZAMBIQUE": {"name": "موزامبیک", "flag": "🇲🇿", "oil": False, "vip": False},
    "TANZANIA": {"name": "تانزانیا", "flag": "🇹🇿", "oil": False, "vip": False},
    "SUDAN": {"name": "سودان", "flag": "🇸🇩", "oil": True, "vip": False},
    "SOMALIA": {"name": "سومالی", "flag": "🇸🇴", "oil": False, "vip": False},
    "OMAN": {"name": "عمان", "flag": "🇴🇲", "oil": True, "vip": False},
    "KUWAIT": {"name": "کویت", "flag": "🇰🇼", "oil": True, "vip": False},
    "QATAR": {"name": "قطر", "flag": "🇶🇦", "oil": True, "vip": False},
    "BAHRAIN": {"name": "بحرین", "flag": "🇧🇭", "oil": True, "vip": False},
    "ARMENIA": {"name": "ارمنستان", "flag": "🇦🇲", "oil": False, "vip": False},
    "BELARUS": {"name": "بلاروس", "flag": "🇧🇾", "oil": False, "vip": False},
    "CROATIA": {"name": "کرواسی", "flag": "🇭🇷", "oil": False, "vip": False},
    "SLOVAKIA": {"name": "اسلواکی", "flag": "🇸🇰", "oil": False, "vip": False},
    "BULGARIA": {"name": "بلغارستان", "flag": "🇧🇬", "oil": False, "vip": False},
    "IRELAND": {"name": "ایرلند", "flag": "🇮🇪", "oil": False, "vip": False},
    "IRAQ2": {"name": "اقلیم کردستان", "flag": "🏴", "oil": True, "vip": False},
    "MYANMAR2": {"name": "تایلند شمالی", "flag": "🏴", "oil": False, "vip": False},
}

GROUPS = {
    "CENTCOM": {"name": "سنتکام", "flag": "🏴‍☠️"},
    "HAMAS": {"name": "حماس", "flag": "🏴‍☠️"},
    "DAESH": {"name": "داعش", "flag": "🏴‍☠️"},
    "AL_QAEDA": {"name": "القاعده", "flag": "🏴‍☠️"},
    "MOSSAD": {"name": "موساد", "flag": "🏴‍☠️"},
    "ANONYMOUS": {"name": "انانیموس", "flag": "🏴‍☠️"},
}

# ==================== قیمت‌های شاپ ====================
SHOP_ITEMS = {
    "ground": {
        "name": "نیروی زمینی 🔫",
        "items": {
            "commander": {"name": "فرمانده", "price": 40000},
            "soldier": {"name": "سرباز", "price": 20000},
            "police": {"name": "پلیس", "price": 20000},
            "border_guard": {"name": "مرزبان", "price": 30000},
            "bomb_defuser": {"name": "خنثی کننده بمب", "price": 50000},
            "bomber": {"name": "بمب گذار", "price": 40000},
            "special_forces": {"name": "یگان ویژه", "price": 30000},
            "mine_layer": {"name": "مین گذار", "price": 25000},
            "mine_defuser": {"name": "خنثی کننده مین", "price": 30000},
            "spy": {"name": "جاسوس", "price": 50000},
            "sniper": {"name": "تک تیرانداز", "price": 20000},
            "rpg": {"name": "ار پی جی زن", "price": 20000},
        }
    },
    "air": {
        "name": "نیروی هوایی ✈️",
        "items": {
            "f16": {"name": "F-16", "price": 1000000},
            "f18": {"name": "F-18", "price": 1200000},
            "f22": {"name": "F-22", "price": 1500000},
            "f35": {"name": "F-35", "price": 2000000, "vip": True},
            "b1": {"name": "B-1", "price": 1000000},
            "b2": {"name": "B-2", "price": 10000000, "vip": True},
            "b52": {"name": "B-52", "price": 15000000, "vip": True},
        }
    },
    "navy": {
        "name": "نیروی دریایی ⚓️",
        "items": {
            "oil_tanker": {"name": "نفت کش", "price": 1000000},
            "cargo_ship": {"name": "کشتی صادرات واردات", "price": 1000000},
            "aircraft_carrier": {"name": "ناو هواپیمابر", "price": 5000000},
            "warboat": {"name": "قایق جنگی", "price": 200000},
            "submarine": {"name": "زیر دریایی آیداهو", "price": 500000},
            "gerald_ford": {"name": "ناو جرالد فورد", "price": 10000000},
            "abraham_lincoln": {"name": "ناو ابراهام لینکن", "price": 40000000, "vip": True},
        }
    },
    "missile": {
        "name": "موشک 🚀",
        "items": {
            "precision": {"name": "موشک نقطه زن", "price": 200000},
            "cruise": {"name": "موشک کروز", "price": 300000},
            "khaibar": {"name": "موشک خیبرشکن", "price": 500000},
            "khorramshahr": {"name": "موشک خرمشهر ۴", "price": 800000, "vip": True},
            "df26": {"name": "موشک DF-26", "price": 1000000, "vip": True},
            "atom_bomb": {"name": "بمب اتم", "price": 60000000},
        }
    },
    "drone": {
        "name": "پهباد 🛬",
        "items": {
            "suicide_drone": {"name": "پهباد انتحاری", "price": 100000},
            "precision_drone": {"name": "پهباد نقطه زن", "price": 200000},
            "recon_drone": {"name": "پهباد شناسایی", "price": 300000},
        }
    },
    "helicopter": {
        "name": "بالگرد 🚁",
        "items": {
            "crocodile": {"name": "بالگرد تمساح", "price": 50000},
            "apache": {"name": "بالگرد آپاچی", "price": 100000},
            "cobra": {"name": "بالگرد کبری", "price": 150000},
            "bell12": {"name": "بالگرد بل ۱۲", "price": 200000},
        }
    },
    "defense": {
        "name": "پدافند 🛰",
        "items": {
            "patriot": {"name": "پدافند پاتریوت", "price": 100000},
            "phalanx": {"name": "پدافند فلانکس", "price": 100000},
            "thaad": {"name": "پدافند تاد", "price": 300000},
        }
    },
    "tank": {
        "name": "تانک 🚜",
        "items": {
            "zolfaghar": {"name": "تانک ذوالفقار", "price": 30000},
            "panther": {"name": "تانک پنتر", "price": 50000},
            "karrar": {"name": "تانک کرار", "price": 150000},
        }
    },
    "system": {
        "name": "سیستم 💻",
        "items": {
            "asset_hack": {"name": "هک دارایی", "price": 100000},
            "anti_asset_hack": {"name": "ضد هک دارایی", "price": 200000},
            "military_hack": {"name": "هک نظامی", "price": 400000},
            "anti_military_hack": {"name": "ضد هک نظامی", "price": 600000},
        }
    },
    "public": {
        "name": "مردمی 📈",
        "items": {
            "supermarket": {"name": "سوپر مارکت", "price": 30000},
            "school": {"name": "مدرسه", "price": 100000},
            "kindergarten": {"name": "مهد کودک", "price": 50000},
            "mall": {"name": "پاساژ", "price": 500000},
            "shelter": {"name": "پناهگاه", "price": 700000},
            "pool": {"name": "استخر", "price": 50000},
            "hotel": {"name": "هتل", "price": 200000},
            "metro": {"name": "مترو", "price": 5000000},
            "bus": {"name": "اتوبوس", "price": 20000},
            "airplane": {"name": "هواپیما", "price": 1000000},
            "amusement_park": {"name": "شهربازی", "price": 300000},
        }
    },
    "mine": {
        "name": "معدن 🚧",
        "items": {
            "diamond_mine": {"name": "معدن الماس", "price": 30000000, "daily_income": 20000000},
            "gold_mine": {"name": "معدن طلا", "price": 20000000, "daily_income": 7000000},
            "silver_mine": {"name": "معدن نقره", "price": 10000000, "daily_income": 5000000},
        }
    },
}

# ==================== شرکت‌ها ====================
COMPANIES = {
    "airplane_co": {
        "name": "شرکت هواپیماسازی ✈️",
        "price": 700000000,
        "income": 200000000,
        "oil_needed": 85000000,
        "daily_produce": {"airplane": 500},
        "description": "تولید روزانه ۵۰۰ عدد از هر نوع هواپیما"
    },
    "tank_co": {
        "name": "شرکت تانک‌سازی 🚜",
        "price": 500000000,
        "income": 120000000,
        "oil_needed": 30000000,
        "daily_produce": {"zolfaghar": 500, "panther": 500, "karrar": 500},
        "description": "تولید روزانه ۵۰۰ عدد تانک"
    },
    "public_co": {
        "name": "شرکت ساخت وسایل مردمی 🏙️",
        "price": 300000000,
        "income": 90000000,
        "oil_needed": 10000000,
        "daily_produce": {"supermarket": 100},
        "satisfaction_bonus": 20,
        "description": "تولید روزانه ۱۰۰ عدد + ۲۰٪ رضایت مردم"
    },
    "drone_co": {
        "name": "شرکت ساخت پهباد 🛬",
        "price": 500000000,
        "income": 100000000,
        "oil_needed": 35000000,
        "daily_produce": {"suicide_drone": 500, "precision_drone": 500, "recon_drone": 500},
        "description": "تولید روزانه ۵۰۰ عدد از هر نوع پهباد"
    },
    "missile_co": {
        "name": "شرکت ساخت موشک 🚀",
        "price": 600000000,
        "income": 140000000,
        "oil_needed": 40000000,
        "daily_produce": {"precision": 500, "cruise": 500, "khaibar": 500},
        "description": "تولید روزانه ۵۰۰ عدد از هر نوع موشک"
    },
    "hack_co": {
        "name": "شرکت هکری 💻",
        "price": 500000000,
        "income": 100000000,
        "oil_needed": 25000000,
        "daily_produce": {"asset_hack": 500, "anti_asset_hack": 500, "military_hack": 500, "anti_military_hack": 500},
        "description": "تولید روزانه ۵۰۰ عدد از هر سیستم"
    },
    "navy_co": {
        "name": "شرکت نیروی دریایی ⚓️",
        "price": 500000000,
        "income": 130000000,
        "oil_needed": 45000000,
        "daily_produce": {"warboat": 200, "submarine": 200, "oil_tanker": 200},
        "description": "تولید روزانه ۲۰۰ عدد از هر کدام"
    },
    "apple_co": {
        "name": "شرکت ساخت آیفون 📱",
        "price": 400000000,
        "income": 150000000,
        "oil_needed": 30000000,
        "daily_produce": {},
        "description": "بدون تولید محصول، فقط درآمد"
    },
    "helicopter_co": {
        "name": "شرکت ساخت بالگرد 🚁",
        "price": 450000000,
        "income": 110000000,
        "oil_needed": 28000000,
        "daily_produce": {"apache": 200, "cobra": 200, "crocodile": 200},
        "description": "تولید روزانه ۲۰۰ عدد از هر نوع بالگرد"
    },
    "defense_co": {
        "name": "شرکت پدافند 🛰️",
        "price": 550000000,
        "income": 125000000,
        "oil_needed": 32000000,
        "daily_produce": {"patriot": 300, "phalanx": 300, "thaad": 300},
        "description": "تولید روزانه ۳۰۰ عدد از هر نوع پدافند"
    },
    "mine_co": {
        "name": "شرکت معدن‌کاری ⛏️",
        "price": 800000000,
        "income": 180000000,
        "oil_needed": 50000000,
        "daily_produce": {},
        "description": "افزایش ۳۰٪ به درآمد معادن"
    },
    "ship_co": {
        "name": "شرکت کشتی‌سازی 🚢",
        "price": 600000000,
        "income": 140000000,
        "oil_needed": 42000000,
        "daily_produce": {"cargo_ship": 100, "aircraft_carrier": 50},
        "description": "تولید روزانه ۱۰۰ کشتی و ۵۰ ناو"
    },
    "ground_co": {
        "name": "شرکت تجهیزات زمینی 🔫",
        "price": 350000000,
        "income": 95000000,
        "oil_needed": 20000000,
        "daily_produce": {"soldier": 1000, "special_forces": 300, "sniper": 200},
        "description": "تولید روزانه ۱۰۰۰ سرباز + ۳۰۰ یگان ویژه + ۲۰۰ تک‌تیرانداز"
    },
    "energy_co": {
        "name": "شرکت انرژی ⚡",
        "price": 700000000,
        "income": 200000000,
        "oil_needed": 60000000,
        "daily_produce": {},
        "description": "افزایش ۱۵٪ درآمد روزانه کشور"
    },
    "intel_co": {
        "name": "شرکت اطلاعاتی 🕵️",
        "price": 480000000,
        "income": 115000000,
        "oil_needed": 22000000,
        "daily_produce": {"spy": 200, "recon_drone": 100},
        "description": "تولید روزانه ۲۰۰ جاسوس + ۱۰۰ پهباد شناسایی"
    },
}

# ==================== دیتابیس ====================
def init_db():
    conn = sqlite3.connect("game.db")
    c = conn.cursor()
    
    c.execute("""CREATE TABLE IF NOT EXISTS players (
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        country TEXT,
        is_group INTEGER DEFAULT 0,
        budget INTEGER DEFAULT 150000000,
        daily_income INTEGER DEFAULT 70000000,
        oil_income INTEGER DEFAULT 0,
        oil_reserves INTEGER DEFAULT 0,
        satisfaction INTEGER DEFAULT 100,
        commander INTEGER DEFAULT 0,
        soldier INTEGER DEFAULT 0,
        police INTEGER DEFAULT 0,
        border_guard INTEGER DEFAULT 0,
        bomb_defuser INTEGER DEFAULT 0,
        bomber INTEGER DEFAULT 0,
        special_forces INTEGER DEFAULT 0,
        mine_layer INTEGER DEFAULT 0,
        mine_defuser INTEGER DEFAULT 0,
        spy INTEGER DEFAULT 0,
        sniper INTEGER DEFAULT 0,
        rpg INTEGER DEFAULT 0,
        f16 INTEGER DEFAULT 0,
        f18 INTEGER DEFAULT 0,
        f22 INTEGER DEFAULT 0,
        f35 INTEGER DEFAULT 0,
        b1 INTEGER DEFAULT 0,
        b2 INTEGER DEFAULT 0,
        b52 INTEGER DEFAULT 0,
        oil_tanker INTEGER DEFAULT 0,
        cargo_ship INTEGER DEFAULT 0,
        aircraft_carrier INTEGER DEFAULT 0,
        warboat INTEGER DEFAULT 0,
        submarine INTEGER DEFAULT 0,
        gerald_ford INTEGER DEFAULT 0,
        abraham_lincoln INTEGER DEFAULT 0,
        precision INTEGER DEFAULT 0,
        cruise INTEGER DEFAULT 0,
        khaibar INTEGER DEFAULT 0,
        khorramshahr INTEGER DEFAULT 0,
        df26 INTEGER DEFAULT 0,
        atom_bomb INTEGER DEFAULT 0,
        suicide_drone INTEGER DEFAULT 0,
        precision_drone INTEGER DEFAULT 0,
        recon_drone INTEGER DEFAULT 0,
        crocodile INTEGER DEFAULT 0,
        apache INTEGER DEFAULT 0,
        cobra INTEGER DEFAULT 0,
        bell12 INTEGER DEFAULT 0,
        patriot INTEGER DEFAULT 0,
        phalanx INTEGER DEFAULT 0,
        thaad INTEGER DEFAULT 0,
        zolfaghar INTEGER DEFAULT 0,
        panther INTEGER DEFAULT 0,
        karrar INTEGER DEFAULT 0,
        asset_hack INTEGER DEFAULT 0,
        anti_asset_hack INTEGER DEFAULT 0,
        military_hack INTEGER DEFAULT 0,
        anti_military_hack INTEGER DEFAULT 0,
        supermarket INTEGER DEFAULT 0,
        school INTEGER DEFAULT 0,
        kindergarten INTEGER DEFAULT 0,
        mall INTEGER DEFAULT 0,
        shelter INTEGER DEFAULT 0,
        pool INTEGER DEFAULT 0,
        hotel INTEGER DEFAULT 0,
        metro INTEGER DEFAULT 0,
        bus INTEGER DEFAULT 0,
        airplane INTEGER DEFAULT 0,
        amusement_park INTEGER DEFAULT 0,
        diamond_mine INTEGER DEFAULT 0,
        gold_mine INTEGER DEFAULT 0,
        silver_mine INTEGER DEFAULT 0
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS companies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company_key TEXT,
        owner_country TEXT,
        owner_user_id INTEGER
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS trades (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sender_country TEXT,
        receiver_country TEXT,
        item TEXT,
        quantity INTEGER,
        price INTEGER,
        status TEXT DEFAULT 'pending',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS declarations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        country TEXT,
        text TEXT,
        status TEXT DEFAULT 'pending',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""")

    # ── Migration: ستون‌های جدید رو به دیتابیس‌های قدیمی اضافه کن ──
    new_columns = [
        ("oil_reserves", "INTEGER DEFAULT 0"),
    ]
    c.execute("PRAGMA table_info(players)")
    existing = {row[1] for row in c.fetchall()}
    for col_name, col_def in new_columns:
        if col_name not in existing:
            c.execute(f"ALTER TABLE players ADD COLUMN {col_name} {col_def}")
            logger.info(f"✅ ستون {col_name} به دیتابیس اضافه شد")

    conn.commit()
    conn.close()

def get_player(user_id):
    conn = sqlite3.connect("game.db")
    c = conn.cursor()
    c.execute("SELECT * FROM players WHERE user_id=?", (user_id,))
    row = c.fetchone()
    conn.close()
    if row:
        cols = [d[0] for d in c.description] if c.description else []
        return dict(zip(cols, row)) if cols else None
    return None

def get_player_by_country(country):
    conn = sqlite3.connect("game.db")
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM players WHERE country=?", (country,))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None

def save_player(user_id, data: dict):
    conn = sqlite3.connect("game.db")
    c = conn.cursor()
    cols = ", ".join(data.keys())
    placeholders = ", ".join(["?" for _ in data])
    updates = ", ".join([f"{k}=?" for k in data])
    vals = list(data.values())
    c.execute(f"INSERT OR REPLACE INTO players (user_id, {cols}) VALUES (?, {placeholders})",
              [user_id] + vals)
    conn.commit()
    conn.close()

def update_player(user_id, updates: dict):
    conn = sqlite3.connect("game.db")
    c = conn.cursor()
    set_clause = ", ".join([f"{k}=?" for k in updates])
    vals = list(updates.values()) + [user_id]
    c.execute(f"UPDATE players SET {set_clause} WHERE user_id=?", vals)
    conn.commit()
    conn.close()

def is_country_taken(country):
    conn = sqlite3.connect("game.db")
    c = conn.cursor()
    c.execute("SELECT user_id FROM players WHERE country=?", (country,))
    row = c.fetchone()
    conn.close()
    return row is not None

def get_all_active_countries():
    conn = sqlite3.connect("game.db")
    c = conn.cursor()
    c.execute("SELECT country FROM players WHERE country IS NOT NULL")
    rows = c.fetchall()
    conn.close()
    return [r[0] for r in rows]

def get_player_by_id_full(user_id):
    conn = sqlite3.connect("game.db")
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM players WHERE user_id=?", (user_id,))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None

# ==================== توابع کمکی ====================
def fmt(n):
    return f"{n:,}"

def get_country_info(code):
    if code in COUNTRIES:
        return COUNTRIES[code]
    if code in GROUPS:
        return GROUPS[code]
    return None



def country_status_text(p):
    code = p.get("country", "")
    info = get_country_info(code)
    name = info["name"] if info else code
    flag = info.get("flag", "") if info else ""
    oil_line = ""
    if p.get('oil_income', 0) > 0:
        oil_line = f"\n🛢️ درآمد نفتی روزانه: `{fmt(p.get('oil_income',0))}`\n🛢️ ذخایر نفت: `{fmt(p.get('oil_reserves',0))}`"

    sat = p.get('satisfaction', 100)
    if sat >= 80:
        sat_emoji = "😍"
    elif sat >= 50:
        sat_emoji = "😐"
    else:
        sat_emoji = "😡"

    text = (
        f"{'━'*20}\n"
        f"🏛️ *داشبورد فرماندهی*\n"
        f"{'━'*20}\n\n"
        f"{flag} *{name}*\n\n"
        f"💰 درآمد روزانه: `{fmt(p.get('daily_income', 70000000))}`\n"
        f"🏦 بودجه دولت: `{fmt(p.get('budget', 150000000))}`\n"
        f"{oil_line}\n"
        f"{sat_emoji} رضایت مردمی: `{sat}٪`\n\n"
        f"{'─'*18}\n"
        f"⚔️ *نیروی زمینی*\n"
        f"{'─'*18}\n"
        f"🎖️ فرمانده: `{p.get('commander',0)}`   🪖 سرباز: `{p.get('soldier',0)}`\n"
        f"👮 پلیس: `{p.get('police',0)}`   🛡️ مرزبان: `{p.get('border_guard',0)}`\n"
        f"🕵️ جاسوس: `{p.get('spy',0)}`   🦅 یگان ویژه: `{p.get('special_forces',0)}`\n"
        f"🎯 تک‌تیرانداز: `{p.get('sniper',0)}`   💥 ار پی جی: `{p.get('rpg',0)}`\n"
        f"💣 بمب‌گذار: `{p.get('bomber',0)}`   🔧 خنثی‌کننده: `{p.get('bomb_defuser',0)}`\n"
        f"🌋 مین‌گذار: `{p.get('mine_layer',0)}`   🧹 خنثی‌کننده مین: `{p.get('mine_defuser',0)}`\n\n"
        f"{'─'*18}\n"
        f"✈️ *نیروی هوایی*\n"
        f"{'─'*18}\n"
        f"F‑16: `{p.get('f16',0)}`  F‑18: `{p.get('f18',0)}`  F‑22: `{p.get('f22',0)}`\n"
        f"F‑35: `{p.get('f35',0)}`  B‑1: `{p.get('b1',0)}`  B‑2: `{p.get('b2',0)}`  B‑52: `{p.get('b52',0)}`\n\n"
        f"{'─'*18}\n"
        f"⚓ *نیروی دریایی*\n"
        f"{'─'*18}\n"
        f"🛢️ نفت‌کش: `{p.get('oil_tanker',0)}`   🚢 کشتی: `{p.get('cargo_ship',0)}`\n"
        f"🛳️ ناو هواپیمابر: `{p.get('aircraft_carrier',0)}`   ⛵ قایق: `{p.get('warboat',0)}`\n"
        f"🤿 زیردریایی: `{p.get('submarine',0)}`   ⚔️ ناو جرالد فورد: `{p.get('gerald_ford',0)}`\n"
        f"👑 ناو ابراهام لینکن: `{p.get('abraham_lincoln',0)}`\n\n"
        f"{'─'*18}\n"
        f"🚀 *زرادخانه موشکی*\n"
        f"{'─'*18}\n"
        f"🎯 نقطه‌زن: `{p.get('precision',0)}`   💨 کروز: `{p.get('cruise',0)}`\n"
        f"⚡ خیبرشکن: `{p.get('khaibar',0)}`   🔥 خرمشهر ۴: `{p.get('khorramshahr',0)}`\n"
        f"🌐 DF‑26: `{p.get('df26',0)}`   ☢️ بمب اتم: `{p.get('atom_bomb',0)}`\n\n"
        f"{'─'*18}\n"
        f"🛬 *پهباد*\n"
        f"{'─'*18}\n"
        f"💥 انتحاری: `{p.get('suicide_drone',0)}`   🎯 نقطه‌زن: `{p.get('precision_drone',0)}`   👁️ شناسایی: `{p.get('recon_drone',0)}`\n\n"
        f"{'─'*18}\n"
        f"🚁 *بالگرد*\n"
        f"{'─'*18}\n"
        f"🐊 تمساح: `{p.get('crocodile',0)}`   🦅 آپاچی: `{p.get('apache',0)}`   🐍 کبری: `{p.get('cobra',0)}`   🔔 بل ۱۲: `{p.get('bell12',0)}`\n\n"
        f"{'─'*18}\n"
        f"🛡️ *پدافند*\n"
        f"{'─'*18}\n"
        f"🇺🇸 پاتریوت: `{p.get('patriot',0)}`   🌀 فلانکس: `{p.get('phalanx',0)}`   🔵 تاد: `{p.get('thaad',0)}`\n\n"
        f"{'─'*18}\n"
        f"🚜 *زرهپوش و تانک*\n"
        f"{'─'*18}\n"
        f"⚔️ ذوالفقار: `{p.get('zolfaghar',0)}`   🐆 پنتر: `{p.get('panther',0)}`   🦁 کرار: `{p.get('karrar',0)}`\n\n"
        f"{'─'*18}\n"
        f"💻 *جنگ سایبری*\n"
        f"{'─'*18}\n"
        f"🔓 هک دارایی: `{p.get('asset_hack',0)}`   🔒 ضد هک: `{p.get('anti_asset_hack',0)}`\n"
        f"⚔️ هک نظامی: `{p.get('military_hack',0)}`   🛡️ ضد هک نظامی: `{p.get('anti_military_hack',0)}`\n\n"
        f"{'─'*18}\n"
        f"🏙️ *زیرساخت مردمی*\n"
        f"{'─'*18}\n"
        f"🛒 سوپرمارکت: `{p.get('supermarket',0)}`   🏫 مدرسه: `{p.get('school',0)}`   🎒 مهد کودک: `{p.get('kindergarten',0)}`\n"
        f"🏬 پاساژ: `{p.get('mall',0)}`   ⛺ پناهگاه: `{p.get('shelter',0)}`   🏊 استخر: `{p.get('pool',0)}`\n"
        f"🏨 هتل: `{p.get('hotel',0)}`   🚇 مترو: `{p.get('metro',0)}`   🚌 اتوبوس: `{p.get('bus',0)}`\n"
        f"✈️ هواپیما: `{p.get('airplane',0)}`   🎡 شهربازی: `{p.get('amusement_park',0)}`\n\n"
        f"{'─'*18}\n"
        f"⛏️ *معادن*\n"
        f"{'─'*18}\n"
        f"💎 الماس: `{p.get('diamond_mine',0)}`   🥇 طلا: `{p.get('gold_mine',0)}`   🥈 نقره: `{p.get('silver_mine',0)}`\n"
        f"{'━'*20}"
    )
    return text

def main_menu_keyboard(user_id=None):
    rows = [
        [InlineKeyboardButton("🌍 کشور من", callback_data="my_country"),
         InlineKeyboardButton("🛒 بازار تسلیحات", callback_data="shop")],
        [InlineKeyboardButton("🏢 شرکت‌های بین‌المللی", callback_data="companies"),
         InlineKeyboardButton("📦 صادرات/واردات", callback_data="trade")],
        [InlineKeyboardButton("📢 بیانیه رسمی", callback_data="declaration"),
         InlineKeyboardButton("⚔️ قوانین جنگ", callback_data="rules")],
        [InlineKeyboardButton("💣 حمله نظامی", callback_data="attack")],
    ]
    if user_id and user_id == ADMIN_ID:
        rows.append([InlineKeyboardButton("👑 پنل ادمین", callback_data="admin_panel")])
    return InlineKeyboardMarkup(rows)

# ==================== هندلرها ====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    
    p = get_player_by_id_full(user_id)
    if p and p.get("country"):
        info = get_country_info(p['country'])
        kbd = main_menu_keyboard(user_id)
        await update.message.reply_text(
            f"🎖️ *فرمانده، خوش برگشتی!*\n\n"
            f"🌍 کشور: {info['flag']} *{info['name']}*\n"
            f"🏦 بودجه: `{fmt(p.get('budget', 0))}`\n\n"
            f"میدان جنگ منتظرته... ⚔️",
            reply_markup=kbd,
            parse_mode="Markdown"
        )
        return MAIN_MENU

    keyboard = [
        [InlineKeyboardButton("🌍 انتخاب کشور", callback_data="pick_country")],
        [InlineKeyboardButton("🏴‍☠️ انتخاب گروهک", callback_data="pick_group")],
    ]
    await update.message.reply_text(
        "☠️ *به جنگ جهانی خوش اومدی!*\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "⚔️ اینجا کشورها با هم می‌جنگن\n"
        "💰 بودجه‌ات رو مدیریت کن\n"
        "🚀 ارتشت رو قوی کن\n"
        "🌐 با دیگران تجارت کن\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "کشور یا گروهک خودت رو انتخاب کن:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )
    return SELECT_COUNTRY

async def pick_country_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    taken = get_all_active_countries()
    rows = []
    row = []
    for code, info in COUNTRIES.items():
        oil = " 🛢️" if info["oil"] else ""
        taken_mark = " ✅" if code in taken else ""
        label = f"{info['flag']}{oil}{taken_mark}"
        row.append(InlineKeyboardButton(label, callback_data=f"sel_country_{code}"))
        if len(row) == 3:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    rows.append([InlineKeyboardButton("🔙 برگشت", callback_data="back_start")])
    
    await query.edit_message_text(
        "🌍 *انتخاب کشور*\n\n🛢️ = نفت‌خیز | ✅ = گرفته شده\n\nروی کشور دلخواه بزن:",
        reply_markup=InlineKeyboardMarkup(rows),
        parse_mode="Markdown"
    )
    return SELECT_COUNTRY

async def pick_group_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    taken = get_all_active_countries()
    rows = []
    for code, info in GROUPS.items():
        taken_mark = " ✅" if code in taken else ""
        rows.append([InlineKeyboardButton(f"{info['flag']} {info['name']}{taken_mark}", callback_data=f"sel_country_{code}")])
    rows.append([InlineKeyboardButton("🔙 برگشت", callback_data="back_start")])
    
    await query.edit_message_text(
        "🏴‍☠️ *انتخاب گروهک*\n\n✅ = گرفته شده\n\nروی گروهک دلخواه بزن:",
        reply_markup=InlineKeyboardMarkup(rows),
        parse_mode="Markdown"
    )
    return SELECT_COUNTRY

async def select_country(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    
    code = query.data.replace("sel_country_", "")
    
    if is_country_taken(code):
        info = get_country_info(code)
        await query.answer(f"❌ {info['name']} قبلاً گرفته شده!", show_alert=True)
        return SELECT_COUNTRY
    
    info = get_country_info(code)
    is_oil = info.get("oil", False) if info else False
    oil_income = 30000000 if is_oil else 0
    
    # ذخیره کاربر
    conn = sqlite3.connect("game.db")
    c = conn.cursor()
    c.execute("""INSERT OR REPLACE INTO players 
        (user_id, username, country, budget, daily_income, oil_income, satisfaction)
        VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (user_id, query.from_user.username or query.from_user.first_name,
         code, 150000000, 70000000, oil_income, 100))
    conn.commit()
    conn.close()
    
    oil_msg = f"\n🛢️ درآمد نفتی: `{fmt(oil_income)}` در روز" if is_oil else ""
    vip_msg = "\n👑 *کشور VIP — دسترسی به سلاح‌های ویژه!*" if info.get("vip") else ""

    await query.edit_message_text(
        f"✅ *فرماندهی {info['flag']} {info['name']} رو به دست گرفتی!*\n\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"💰 درآمد روزانه: `{fmt(70000000)}`\n"
        f"🏦 بودجه اولیه: `{fmt(150000000)}`{oil_msg}{vip_msg}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🎯 حالا وقت استراتژیه فرمانده!\n"
        f"ارتشت رو بساز و دنیا رو تسخیر کن ⚔️",
        reply_markup=main_menu_keyboard(user_id),
        parse_mode="Markdown"
    )
    return MAIN_MENU

async def back_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [
        [InlineKeyboardButton("🌍 انتخاب کشور", callback_data="pick_country")],
        [InlineKeyboardButton("🏴‍☠️ انتخاب گروهک", callback_data="pick_group")],
    ]
    await query.edit_message_text(
        "⚔️ *به جنگ جهانی خوش اومدی!*\n\nکشور یا گروهک انتخاب کن:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )
    return SELECT_COUNTRY

# ==================== منوی اصلی ====================
async def main_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    

    data = query.data
    
    if data == "my_country":
        return await show_my_country(update, context)
    elif data == "shop":
        return await show_shop(update, context)
    elif data == "companies":
        return await show_companies(update, context)
    elif data == "trade":
        return await show_trade(update, context)
    elif data == "declaration":
        return await show_declaration(update, context)
    elif data == "rules":
        return await show_rules(update, context)
    elif data == "attack":
        return await show_attack(update, context)
    elif data == "adm_manual_income":
        return await admin_manual_income(update, context)
    elif data == "admin_panel":
        if user_id == ADMIN_ID:
            await query.edit_message_text(
                "👑 *پنل ادمین*\n━━━━━━━━━━━━━━━━━━━━",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("💰 واریز دستی برای همه", callback_data="adm_manual_income")],
                    [InlineKeyboardButton("🔙 برگشت", callback_data="main_menu")],
                ]),
                parse_mode="Markdown"
            )
        return MAIN_MENU
    elif data == "main_menu":
        p = get_player_by_id_full(user_id)
        info = get_country_info(p["country"])
        await query.edit_message_text(
            f"🎖️ *مرکز فرماندهی*\n\n"
            f"{info['flag']} *{info['name']}*\n"
            f"🏦 بودجه: `{fmt(p.get('budget',0))}`\n\n"
            f"دستورت رو بده فرمانده ⚔️",
            reply_markup=main_menu_keyboard(user_id),
            parse_mode="Markdown"
        )
        return MAIN_MENU

# ==================== کشور من ====================
async def show_my_country(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    p = get_player_by_id_full(user_id)
    
    if not p:
        await query.answer("ابتدا /start بزن!", show_alert=True)
        return MAIN_MENU
    
    # شرکت‌های کاربر
    conn = sqlite3.connect("game.db")
    c = conn.cursor()
    c.execute("SELECT company_key FROM companies WHERE owner_user_id=?", (user_id,))
    user_companies = [r[0] for r in c.fetchall()]
    conn.close()
    
    text = country_status_text(p)
    
    if user_companies:
        text += "\n\n🏢 *شرکت‌های شما:*\n"
        for ck in user_companies:
            co = COMPANIES.get(ck)
            if co:
                text += f"• {co['name']}\n"
    
    keyboard = [[InlineKeyboardButton("🔙 برگشت", callback_data="main_menu")]]
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
    return MAIN_MENU

# ==================== شاپ ====================
async def show_shop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    p = get_player_by_id_full(user_id)
    
    rows = []
    for cat_key, cat in SHOP_ITEMS.items():
        rows.append([InlineKeyboardButton(cat["name"], callback_data=f"shop_cat_{cat_key}")])

    cart = context.user_data.get("cart", {})
    cart_text = ""
    if cart:
        total = sum(v["price"] * v["qty"] for v in cart.values())
        cart_text = f"\n\n🛒 سبد خرید: *{len(cart)}* آیتم | جمع: `{fmt(total)}`"
        rows.append([InlineKeyboardButton("✅ تسویه حساب", callback_data="checkout"),
                     InlineKeyboardButton("🗑️ خالی کردن سبد", callback_data="clear_cart")])

    rows.append([InlineKeyboardButton("🔙 برگشت", callback_data="main_menu")])

    await query.edit_message_text(
        f"🏪 *بازار تسلیحات جهانی*\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"💰 بودجه موجود: `{fmt(p.get('budget',0))}`{cart_text}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"دسته‌بندی مورد نظرت رو انتخاب کن:",
        reply_markup=InlineKeyboardMarkup(rows),
        parse_mode="Markdown"
    )
    return SHOP_MENU

async def shop_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    p = get_player_by_id_full(user_id)
    cat_key = query.data.replace("shop_cat_", "")
    cat = SHOP_ITEMS[cat_key]
    
    # بررسی VIP
    country_info = get_country_info(p.get("country", ""))
    is_vip = country_info.get("vip", False) if country_info else False
    
    context.user_data["shop_cat"] = cat_key
    
    rows = []
    for item_key, item in cat["items"].items():
        if item.get("vip") and not is_vip:
            continue
        cart = context.user_data.get("cart", {})
        in_cart = cart.get(item_key, {}).get("qty", 0)
        cart_badge = f" [{in_cart}]" if in_cart > 0 else ""
        rows.append([InlineKeyboardButton(
            f"{item['name']} - {fmt(item['price'])}{cart_badge}",
            callback_data=f"shop_item_{item_key}"
        )])
    
    rows.append([InlineKeyboardButton("🔙 برگشت به شاپ", callback_data="shop")])
    
    cart = context.user_data.get("cart", {})
    cart_text = ""
    if cart:
        total = sum(v["price"] * v["qty"] for v in cart.values())
        cart_text = f"\n🛒 سبد: *{len(cart)}* آیتم | `{fmt(total)}`"

    await query.edit_message_text(
        f"🏪 *{cat['name']}*\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"💰 بودجه: `{fmt(p.get('budget',0))}`{cart_text}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"محصول مورد نظرت رو انتخاب کن:",
        reply_markup=InlineKeyboardMarkup(rows),
        parse_mode="Markdown"
    )
    return SHOP_CATEGORY

async def shop_item(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    item_key = query.data.replace("shop_item_", "")
    
    # پیدا کردن آیتم
    item = None
    for cat in SHOP_ITEMS.values():
        if item_key in cat["items"]:
            item = cat["items"][item_key]
            break
    
    if not item:
        return SHOP_CATEGORY
    
    context.user_data["shop_item"] = item_key
    cart = context.user_data.get("cart", {})
    in_cart = cart.get(item_key, {}).get("qty", 0)
    subtotal = item["price"] * in_cart

    rows = [
        [
            InlineKeyboardButton("1️⃣ +۱", callback_data="add_1"),
            InlineKeyboardButton("🔟 +۱۰", callback_data="add_10"),
        ],
        [
            InlineKeyboardButton("💯 +۱۰۰", callback_data="add_100"),
            InlineKeyboardButton("🔢 +۱۰۰۰", callback_data="add_1000"),
        ],
        [InlineKeyboardButton("🛒 مشاهده سبد خرید", callback_data="view_cart")],
        [InlineKeyboardButton("🔙 برگشت", callback_data=f"shop_cat_{context.user_data.get('shop_cat','')}")],
    ]

    await query.edit_message_text(
        f"🔫 *{item['name']}*\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"💵 قیمت هر عدد: `{fmt(item['price'])}`\n"
        f"📦 در سبد: `{in_cart}` عدد\n"
        f"💰 جمع: `{fmt(subtotal)}`\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"چند تا اضافه کنم به سبدت؟",
        reply_markup=InlineKeyboardMarkup(rows),
        parse_mode="Markdown"
    )
    return SHOP_ITEM

async def add_to_cart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    qty_map = {"add_1": 1, "add_10": 10, "add_100": 100, "add_1000": 1000}
    qty = qty_map.get(query.data, 1)
    
    item_key = context.user_data.get("shop_item")
    if not item_key:
        return SHOP_ITEM
    
    item = None
    for cat in SHOP_ITEMS.values():
        if item_key in cat["items"]:
            item = cat["items"][item_key]
            break
    
    if not item:
        return SHOP_ITEM
    
    cart = context.user_data.get("cart", {})
    if item_key not in cart:
        cart[item_key] = {"name": item["name"], "price": item["price"], "qty": 0}
    cart[item_key]["qty"] += qty
    context.user_data["cart"] = cart
    
    in_cart = cart[item_key]["qty"]
    total_this = item["price"] * in_cart

    rows = [
        [
            InlineKeyboardButton("1️⃣ +۱", callback_data="add_1"),
            InlineKeyboardButton("🔟 +۱۰", callback_data="add_10"),
        ],
        [
            InlineKeyboardButton("💯 +۱۰۰", callback_data="add_100"),
            InlineKeyboardButton("🔢 +۱۰۰۰", callback_data="add_1000"),
        ],
        [InlineKeyboardButton("🛒 مشاهده سبد خرید", callback_data="view_cart")],
        [InlineKeyboardButton("🔙 برگشت", callback_data=f"shop_cat_{context.user_data.get('shop_cat','')}")],
    ]

    await query.edit_message_text(
        f"✅ *{item['name']}* اضافه شد!\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"💵 قیمت هر عدد: `{fmt(item['price'])}`\n"
        f"📦 در سبد: `{in_cart}` عدد\n"
        f"💰 جمع این محصول: `{fmt(total_this)}`\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"بیشتر اضافه کنم؟",
        reply_markup=InlineKeyboardMarkup(rows),
        parse_mode="Markdown"
    )
    return SHOP_ITEM

async def view_cart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    p = get_player_by_id_full(user_id)

    cart = context.user_data.get("cart", {})
    if not cart:
        await query.answer("🛒 سبد خریدت خالیه!", show_alert=True)
        return SHOP_ITEM

    text = (
        "🛒 *سبد خرید شما*\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
    )
    total = 0
    rows = []
    for k, v in cart.items():
        subtotal = v["price"] * v["qty"]
        total += subtotal
        text += f"• *{v['name']}*\n  `{v['qty']}` عدد × `{fmt(v['price'])}` = `{fmt(subtotal)}`\n\n"
        rows.append([InlineKeyboardButton(f"🗑️ حذف {v['name']}", callback_data=f"remove_item_{k}")])

    text += f"━━━━━━━━━━━━━━━━━━━━\n"
    text += f"💰 *جمع کل: `{fmt(total)}`*\n"
    text += f"🏦 بودجه: `{fmt(p.get('budget',0))}`"

    if total > p.get("budget", 0):
        text += "\n\n❌ *بودجه کافی نیست!*"
        rows.append([InlineKeyboardButton("🗑️ خالی کردن سبد", callback_data="clear_cart")])
        rows.append([InlineKeyboardButton("🔙 برگشت به بازار", callback_data="shop")])
    else:
        rows.append([InlineKeyboardButton("✅ تسویه و خرید", callback_data="checkout")])
        rows.append([InlineKeyboardButton("🗑️ خالی کردن سبد", callback_data="clear_cart")])
        rows.append([InlineKeyboardButton("🔙 ادامه خرید", callback_data="shop")])

    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(rows), parse_mode="Markdown")
    return SHOP_MENU

async def remove_cart_item(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    item_key = query.data.replace("remove_item_", "")
    cart = context.user_data.get("cart", {})
    if item_key in cart:
        del cart[item_key]
    context.user_data["cart"] = cart
    if not cart:
        await query.edit_message_text(
            "🛒 سبد خریدت خالی شد!",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏪 برگشت به بازار", callback_data="shop")]])
        )
        return SHOP_MENU
    return await view_cart(update, context)

async def checkout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    p = get_player_by_id_full(user_id)

    cart = context.user_data.get("cart", {})
    if not cart:
        await query.answer("🛒 سبد خالیه!", show_alert=True)
        return SHOP_MENU

    total = sum(v["price"] * v["qty"] for v in cart.values())

    if total > p.get("budget", 0):
        await query.answer("❌ بودجه کافی نیست!", show_alert=True)
        return SHOP_MENU

    updates = {"budget": p["budget"] - total}
    for k, v in cart.items():
        current = p.get(k, 0) or 0
        updates[k] = current + v["qty"]
        mine_income = SHOP_ITEMS.get("mine", {}).get("items", {}).get(k, {}).get("daily_income", 0)
        if mine_income:
            updates["daily_income"] = updates.get("daily_income", p.get("daily_income", 70000000)) + mine_income * v["qty"]

    update_player(user_id, updates)
    context.user_data["cart"] = {}

    # اعلام در گروه
    info = get_country_info(p.get("country", ""))
    items_text = "\n".join([f"  • {v['name']}: {v['qty']} عدد" for v in cart.values()])
   
    

async def clear_cart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data["cart"] = {}
    await query.edit_message_text(
        "🗑️ *سبد خرید خالی شد!*\n\nمیتونی دوباره خرید کنی فرمانده.",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏪 برگشت به بازار", callback_data="shop")]]),
        parse_mode="Markdown"
    )
    return SHOP_MENU

# ==================== شرکت‌ها ====================
async def show_companies(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    p = get_player_by_id_full(user_id)
    
    # شرکت‌های خریداری شده
    conn = sqlite3.connect("game.db")
    c = conn.cursor()
    c.execute("SELECT company_key, owner_country FROM companies")
    owned = {r[0]: r[1] for r in c.fetchall()}
    conn.close()
    
    country_info = get_country_info(p.get("country", ""))
    is_oil = country_info.get("oil", False) if country_info else False
    oil = p.get("oil_income", 0)
    
    rows = []
    for co_key, co in COMPANIES.items():
        owner = owned.get(co_key)
        if owner:
            owner_info = get_country_info(owner)
            owner_name = owner_info["name"] if owner_info else owner
            label = f"🔒 {co['name']} | {owner_name}"
        else:
            label = f"🏢 {co['name']} | {fmt(co['price'])}"
        rows.append([InlineKeyboardButton(label, callback_data=f"co_detail_{co_key}")])
    
    rows.append([InlineKeyboardButton("🔙 برگشت", callback_data="main_menu")])
    
    await query.edit_message_text(
        f"🏢 *شرکت‌ها*\n💰 بودجه: {fmt(p.get('budget',0))}\n🛢️ نفت: {fmt(oil)}\n\nروی شرکت بزن:",
        reply_markup=InlineKeyboardMarkup(rows),
        parse_mode="Markdown"
    )
    return COMPANY_MENU

async def company_detail(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    p = get_player_by_id_full(user_id)
    
    co_key = query.data.replace("co_detail_", "")
    co = COMPANIES.get(co_key)
    if not co:
        return COMPANY_MENU
    
    conn = sqlite3.connect("game.db")
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT owner_country FROM companies WHERE company_key=?", (co_key,))
    row = c.fetchone()
    conn.close()
    
    oil = p.get("oil_reserves", 0) or 0
    can_afford_budget = p.get("budget", 0) >= co["price"]
    can_afford_oil = oil >= co["oil_needed"] if co["oil_needed"] > 0 else True
    
    if row:
        owner = row["owner_country"]
        owner_info = get_country_info(owner)
        text = (
            f"🏢 *{co['name']}*\n\n"
            f"✅ خریداری شده توسط: {owner_info['flag']} {owner_info['name']}\n\n"
            f"💰 قیمت: {fmt(co['price'])}\n"
            f"📈 درآمد روزانه: {fmt(co['income'])}\n"
            f"🛢️ نفت مورد نیاز: {fmt(co['oil_needed'])}\n"
            f"📦 {co['description']}"
        )
        rows = [[InlineKeyboardButton("🔙 برگشت", callback_data="companies")]]
    else:
        text = (
            f"🏢 *{co['name']}*\n\n"
            f"💰 قیمت: {fmt(co['price'])}\n"
            f"📈 درآمد روزانه: {fmt(co['income'])}\n"
            f"🛢️ نفت مورد نیاز: {fmt(co['oil_needed'])}\n"
            f"📦 {co['description']}\n\n"
            f"💼 بودجه شما: {fmt(p.get('budget',0))}\n"
            f"🛢️ ذخایر نفت شما: {fmt(oil)}"
        )
        rows = []
        if can_afford_budget and can_afford_oil:
            rows.append([InlineKeyboardButton("✅ خرید شرکت", callback_data=f"buy_co_{co_key}")])
        else:
            rows.append([InlineKeyboardButton("❌ بودجه یا نفت کافی نیست", callback_data="companies")])
        rows.append([InlineKeyboardButton("🔙 برگشت", callback_data="companies")])
    
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(rows), parse_mode="Markdown")
    return COMPANY_MENU

async def buy_company(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    p = get_player_by_id_full(user_id)
    
    co_key = query.data.replace("buy_co_", "")
    co = COMPANIES.get(co_key)
    
    # چک دوباره
    conn = sqlite3.connect("game.db")
    c = conn.cursor()
    c.execute("SELECT id FROM companies WHERE company_key=?", (co_key,))
    if c.fetchone():
        await query.answer("این شرکت قبلاً خریداری شده!", show_alert=True)
        conn.close()
        return COMPANY_MENU
    
    new_budget = p["budget"] - co["price"]
    new_income = p.get("daily_income", 70000000) + co["income"]
    new_oil_reserves = (p.get("oil_reserves", 0) or 0) - co.get("oil_needed", 0)

    c.execute("INSERT INTO companies (company_key, owner_country, owner_user_id) VALUES (?,?,?)",
              (co_key, p["country"], user_id))
    conn.commit()
    conn.close()

    update_player(user_id, {"budget": new_budget, "daily_income": new_income, "oil_reserves": max(0, new_oil_reserves)})



# ==================== صادرات/واردات ====================
async def show_trade(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    p = get_player_by_id_full(user_id)
    
    # محصولاتی که کاربر داره
    tradeable = []
    
    # بررسی همه فیلدها
    all_items = {}
    for cat in SHOP_ITEMS.values():
        for k, v in cat["items"].items():
            all_items[k] = v["name"]
    
    for k, name in all_items.items():
        qty = p.get(k, 0) or 0
        if qty > 0:
            tradeable.append((k, name, qty))
    
    # نفت
    oil = p.get("oil_reserves", 0) or 0
    if oil > 0:
        tradeable.append(("oil", "نفت 🛢️", oil))
    
    if not tradeable:
        await query.edit_message_text(
            "📦 *صادرات/واردات*\n\n❌ هیچ محصولی برای صادرات نداری!",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 برگشت", callback_data="main_menu")]]),
            parse_mode="Markdown"
        )
        return MAIN_MENU
    
    rows = []
    for k, name, qty in tradeable:
        rows.append([InlineKeyboardButton(f"{name} ({qty})", callback_data=f"trade_item_{k}")])
    rows.append([InlineKeyboardButton("🔙 برگشت", callback_data="main_menu")])
    
    context.user_data["tradeable"] = {k: qty for k, _, qty in tradeable}
    
    await query.edit_message_text(
        f"📦 *صادرات/واردات*\n\nمحصولی که میخوای بفروشی رو انتخاب کن:",
        reply_markup=InlineKeyboardMarkup(rows),
        parse_mode="Markdown"
    )
    return TRADE_SELECT_ITEM

async def trade_item_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    item_key = query.data.replace("trade_item_", "")
    context.user_data["trade_item"] = item_key
    
    tradeable = context.user_data.get("tradeable", {})
    max_qty = tradeable.get(item_key, 0)
    
    # پیدا کردن نام
    item_name = "نفت 🛢️"
    for cat in SHOP_ITEMS.values():
        if item_key in cat["items"]:
            item_name = cat["items"][item_key]["name"]
            break
    
    context.user_data["trade_item_name"] = item_name
    context.user_data["trade_max_qty"] = max_qty
    
    await query.edit_message_text(
        f"📦 *{item_name}*\n\nحداکثر تعداد: {max_qty}\n\nتعداد که میخوای بفرستی رو تایپ کن (عدد انگلیسی):",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 لغو", callback_data="main_menu")]]),
        parse_mode="Markdown"
    )
    context.user_data["trade_step"] = "qty"
    return TRADE_QUANTITY

async def trade_quantity_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()
    
    step = context.user_data.get("trade_step")
    
    if step == "qty":
        try:
            qty = int(text)
        except ValueError:
            await update.message.reply_text("❌ عدد انگلیسی وارد کن!")
            return TRADE_QUANTITY
        
        max_qty = context.user_data.get("trade_max_qty", 0)
        if qty <= 0 or qty > max_qty:
            await update.message.reply_text(f"❌ تعداد باید بین ۱ تا {max_qty} باشه!")
            return TRADE_QUANTITY
        
        context.user_data["trade_qty"] = qty
        context.user_data["trade_step"] = "price"
        
        await update.message.reply_text(
            f"✅ تعداد: {qty}\n\nحالا قیمت کل رو بنویس (عدد انگلیسی):",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🎁 رایگان", callback_data="trade_free")]
            ])
        )
        return TRADE_PRICE
    
    elif step == "price":
        try:
            price = int(text)
        except ValueError:
            await update.message.reply_text("❌ عدد انگلیسی وارد کن!")
            return TRADE_PRICE
        
        context.user_data["trade_price"] = price
        return await show_trade_confirm(update, context)

async def trade_free(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data["trade_price"] = 0
    return await show_trade_confirm_query(update, context)

async def show_trade_confirm(update, context):
    item_name = context.user_data.get("trade_item_name", "")
    qty = context.user_data.get("trade_qty", 0)
    price = context.user_data.get("trade_price", 0)
    
    price_text = "رایگان 🎁" if price == 0 else fmt(price)
    
    rows = [
        [InlineKeyboardButton("✅ تایید", callback_data="trade_confirm"),
         InlineKeyboardButton("✏️ ویرایش", callback_data="trade_edit")],
        [InlineKeyboardButton("❌ لغو", callback_data="main_menu")]
    ]
    
    await update.message.reply_text(
        f"📋 *خلاصه صادرات*\n\n"
        f"📦 محصول: {item_name}\n"
        f"🔢 تعداد: {qty}\n"
        f"💰 قیمت: {price_text}\n\n"
        f"تایید میکنی؟",
        reply_markup=InlineKeyboardMarkup(rows),
        parse_mode="Markdown"
    )
    return TRADE_CONFIRM

async def show_trade_confirm_query(update, context):
    query = update.callback_query
    await query.answer()
    
    item_name = context.user_data.get("trade_item_name", "")
    qty = context.user_data.get("trade_qty", 0)
    price = context.user_data.get("trade_price", 0)
    price_text = "رایگان 🎁" if price == 0 else fmt(price)
    
    rows = [
        [InlineKeyboardButton("✅ تایید", callback_data="trade_confirm"),
         InlineKeyboardButton("✏️ ویرایش", callback_data="trade_edit")],
        [InlineKeyboardButton("❌ لغو", callback_data="main_menu")]
    ]
    
    await query.edit_message_text(
        f"📋 *خلاصه صادرات*\n\n"
        f"📦 محصول: {item_name}\n"
        f"🔢 تعداد: {qty}\n"
        f"💰 قیمت: {price_text}\n\n"
        f"تایید میکنی؟",
        reply_markup=InlineKeyboardMarkup(rows),
        parse_mode="Markdown"
    )
    return TRADE_CONFIRM

async def trade_confirm_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    p = get_player_by_id_full(user_id)
    
    # نمایش لیست کشورهای فعال
    active = get_all_active_countries()
    my_country = p.get("country")
    
    rows = []
    for code in active:
        if code == my_country:
            continue
        info = get_country_info(code)
        if info:
            rows.append([InlineKeyboardButton(f"{info['flag']} {info['name']}", callback_data=f"trade_to_{code}")])
    
    rows.append([InlineKeyboardButton("❌ لغو", callback_data="main_menu")])
    
    await query.edit_message_text(
        "🌍 کشور مقصد رو انتخاب کن:",
        reply_markup=InlineKeyboardMarkup(rows)
    )
    return TRADE_SELECT_COUNTRY

async def trade_to_country(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    p = get_player_by_id_full(user_id)
    
    target_country = query.data.replace("trade_to_", "")
    context.user_data["trade_target"] = target_country
    
    target_info = get_country_info(target_country)
    item_name = context.user_data.get("trade_item_name", "")
    qty = context.user_data.get("trade_qty", 0)
    price = context.user_data.get("trade_price", 0)
    price_text = "رایگان 🎁" if price == 0 else fmt(price)
    
    rows = [
        [InlineKeyboardButton("🚀 ارسال", callback_data="trade_send"),
         InlineKeyboardButton("🔙 برگشت", callback_data="trade_confirm")]
    ]
    
    await query.edit_message_text(
        f"📤 *تایید نهایی*\n\n"
        f"📦 {item_name} × {qty}\n"
        f"💰 {price_text}\n"
        f"🎯 مقصد: {target_info['flag']} {target_info['name']}\n\n"
        f"ارسال کنم؟",
        reply_markup=InlineKeyboardMarkup(rows),
        parse_mode="Markdown"
    )
    return TRADE_SELECT_COUNTRY

async def trade_send(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    p = get_player_by_id_full(user_id)
    
    item_key = context.user_data.get("trade_item")
    qty = context.user_data.get("trade_qty", 0)
    price = context.user_data.get("trade_price", 0)
    target_country = context.user_data.get("trade_target")
    item_name = context.user_data.get("trade_item_name", "")
    
    target_player = get_player_by_country(target_country)
    if not target_player:
        await query.answer("کشور مقصد پیدا نشد!", show_alert=True)
        return MAIN_MENU
    
    # بررسی بودجه خریدار
    if price > 0 and target_player.get("budget", 0) < price:
        await query.answer("❌ بودجه کشور مقصد کافی نیست!", show_alert=True)
        return MAIN_MENU
    
    # ذخیره معامله
    conn = sqlite3.connect("game.db")
    c = conn.cursor()
    c.execute("INSERT INTO trades (sender_country, receiver_country, item, quantity, price) VALUES (?,?,?,?,?)",
              (p["country"], target_country, item_key, qty, price))
    trade_id = c.lastrowid
    conn.commit()
    conn.close()
    
    # ارسال پیام به کشور مقصد
    sender_info = get_country_info(p["country"])
    price_text = "🎁 رایگان" if price == 0 else f"`{fmt(price)}`"

    try:
        await context.bot.send_message(
            target_player["user_id"],
            f"📬 *پیشنهاد رسمی صادرات!*\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"🌍 از: {sender_info['flag']} *{sender_info['name']}*\n"
            f"📦 محصول: *{item_name}* × `{qty}`\n"
            f"💰 قیمت: {price_text}\n"
            f"━━━━━━━━━━━━━━━━━━━━\n\n"
            f"آیا این معامله رو قبول میکنی فرمانده؟",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ قبول معامله", callback_data=f"trade_accept_{trade_id}"),
                 InlineKeyboardButton("❌ رد معامله", callback_data=f"trade_reject_{trade_id}")]
            ]),
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.error(f"Error sending trade offer: {e}")

    target_info = get_country_info(target_country)
    await query.edit_message_text(
        f"📤 *پیشنهاد صادرات ارسال شد!*\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📦 {item_name} × `{qty}`\n"
        f"💰 قیمت: {price_text}\n"
        f"🎯 مقصد: {target_info['flag']} *{target_info['name']}*\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"⏳ منتظر تایید طرف مقابل باش فرمانده...",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 مرکز فرماندهی", callback_data="main_menu")]]),
        parse_mode="Markdown"
    )
    return MAIN_MENU

async def trade_accept(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    trade_id = int(query.data.replace("trade_accept_", ""))

    conn = sqlite3.connect("game.db")
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM trades WHERE id=? AND status='pending'", (trade_id,))
    trade = c.fetchone()

    if not trade:
        await query.answer("⚠️ این معامله دیگه معتبر نیست!", show_alert=True)
        conn.close()
        return

    trade = dict(trade)
    sender = get_player_by_country(trade["sender_country"])
    receiver = get_player_by_id_full(user_id)

    if not sender or not receiver:
        await query.answer("❌ خطا در اطلاعات بازیکنان!", show_alert=True)
        conn.close()
        return

    price = trade["price"]
    item_key = trade["item"]
    qty = trade["quantity"]

    if price > 0 and receiver.get("budget", 0) < price:
        await query.answer("❌ بودجه کافی نداری!", show_alert=True)
        conn.close()
        return

    sender_item = sender.get(item_key, 0) or 0
    if sender_item < qty:
        await query.answer("❌ فرستنده دیگه این مقدار رو نداره!", show_alert=True)
        conn.close()
        return

    # درآمد معدنی
    mine_income_per = SHOP_ITEMS.get("mine", {}).get("items", {}).get(item_key, {}).get("daily_income", 0)

    # آپدیت فرستنده
    sender_upd = {item_key: sender_item - qty, "budget": sender.get("budget", 0) + price}
    if mine_income_per > 0:
        sender_upd["daily_income"] = max(70000000, sender.get("daily_income", 70000000) - mine_income_per * qty)
    update_player(sender["user_id"], sender_upd)

    # آپدیت گیرنده
    receiver_item = receiver.get(item_key, 0) or 0
    recv_upd = {item_key: receiver_item + qty, "budget": receiver.get("budget", 0) - price}
    if mine_income_per > 0:
        recv_upd["daily_income"] = receiver.get("daily_income", 70000000) + mine_income_per * qty
    update_player(user_id, recv_upd)

    c.execute("UPDATE trades SET status='accepted' WHERE id=?", (trade_id,))
    conn.commit()
    conn.close()

    sender_info = get_country_info(sender["country"])
    receiver_info = get_country_info(receiver["country"])
    item_name = item_key
    for cat in SHOP_ITEMS.values():
        if item_key in cat["items"]:
            item_name = cat["items"][item_key]["name"]
            break

    price_text = f"`{fmt(price)}`" if price > 0 else "🎁 رایگان"

    # ویرایش پیام گیرنده (حذف دکمه‌ها)
    try:
        await query.edit_message_text(
            f"✅ *معامله قبول شد!*\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"📦 {item_name} × `{qty}`\n"
            f"💰 پرداختی: {price_text}\n"
            f"━━━━━━━━━━━━━━━━━━━━\n\n"
            f"🚚 محموله داره حرکت میکنه... ۱۵ دقیقه دیگه میرسه!",
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.error(f"Edit trade msg error: {e}")
        try:
            await context.bot.send_message(user_id,
                "✅ *معامله قبول شد!* محموله ۱۵ دقیقه دیگه میرسه 🚚",
                parse_mode="Markdown")
        except:
            pass

    # اطلاع به فرستنده
    try:
        await context.bot.send_message(
            sender["user_id"],
            f"✅ *معامله تایید شد!*\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"🌍 {receiver_info['flag']} *{receiver_info['name']}* قبول کرد!\n"
            f"📦 {item_name} × `{qty}` در راهه...\n"
            f"⏱️ تحویل در ۱۵ دقیقه\n"
            f"{'💰 دریافتی: ' + fmt(price) if price > 0 else '🎁 رایگان ارسال کردی'}\n"
            f"━━━━━━━━━━━━━━━━━━━━",
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.error(f"Sender notify error: {e}")

    

    asyncio.create_task(deliver_trade_animated(context, user_id, item_name, qty, 15 * 60))

async def deliver_trade_animated(context, user_id, item_name, qty, delay):
    steps = [
        (delay // 3, "🚛 *محموله آماده ارسال شد...*\n📦 بارگیری کامل شد"),
        (delay // 3, "🛣️ *محموله در مسیره...*\n⏳ کمی صبر کن فرمانده"),
        (delay // 3, None),  # تحویل نهایی
    ]
    for wait, msg in steps:
        await asyncio.sleep(wait)
        if msg:
            try:
                await context.bot.send_message(user_id, msg, parse_mode="Markdown")
            except:
                pass
    try:
        await context.bot.send_message(
            user_id,
            f"🎉 *محموله رسید فرمانده!*\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"✅ {item_name} × `{qty}` به زرادخانه‌ات اضافه شد!\n"
            f"━━━━━━━━━━━━━━━━━━━━",
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.error(f"Deliver error: {e}")

async def trade_reject(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    trade_id = int(query.data.replace("trade_reject_", ""))

    conn = sqlite3.connect("game.db")
    c = conn.cursor()
    c.execute("SELECT sender_country FROM trades WHERE id=? AND status='pending'", (trade_id,))
    row = c.fetchone()
    if not row:
        await query.edit_message_text("⚠️ این معامله قبلاً پردازش شده.")
        conn.close()
        return
    c.execute("UPDATE trades SET status='rejected' WHERE id=?", (trade_id,))
    conn.commit()
    conn.close()

    receiver_p = get_player_by_id_full(query.from_user.id)
    receiver_info = get_country_info(receiver_p.get("country", "")) if receiver_p else None

    sender = get_player_by_country(row[0])
    if sender:
        try:
            rej_msg = (
                f"❌ *معامله رد شد!*\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
            )
            if receiver_info:
                rej_msg += f"🌍 {receiver_info['flag']} *{receiver_info['name']}* پیشنهاد رو رد کرد.\n"
            rej_msg += f"━━━━━━━━━━━━━━━━━━━━\n\nمیتونی پیشنهاد جدید بدی فرمانده."
            await context.bot.send_message(sender["user_id"], rej_msg, parse_mode="Markdown")
        except Exception as e:
            logger.error(f"Trade reject notify error: {e}")

    # حذف دکمه‌های قبول/رد از پیام گیرنده
    try:
        await query.edit_message_text(
            f"❌ *معامله رد شد.*\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"پیشنهاد فرستنده رو رد کردی فرمانده.\n"
            f"━━━━━━━━━━━━━━━━━━━━",
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.error(f"Edit reject msg error: {e}")

async def trade_edit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    item_name = context.user_data.get("trade_item_name", "")
    max_qty = context.user_data.get("trade_max_qty", 0)
    context.user_data["trade_step"] = "qty"
    
    await query.edit_message_text(
        f"📦 *{item_name}*\n\nحداکثر: {max_qty}\n\nتعداد جدید رو تایپ کن:",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("❌ لغو", callback_data="main_menu")]]),
        parse_mode="Markdown"
    )
    return TRADE_QUANTITY

# ==================== بیانیه ====================
async def show_declaration(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    p = get_player_by_id_full(user_id)

    info = get_country_info(p.get("country", ""))

    await query.edit_message_text(
        f"📢 *صدور بیانیه رسمی*\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🌍 کشور: {info['flag']} *{info['name']}*\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"✍️ متن بیانیه‌ات رو بنویس:\n"
        f"_(بعد از ارسال، ادمین بررسی میکنه)_",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 لغو", callback_data="main_menu")]]),
        parse_mode="Markdown"
    )
    context.user_data["decl_step"] = "text"
    return DECLARATION_TEXT

async def declaration_text_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    p = get_player_by_id_full(user_id)
    info = get_country_info(p.get("country", ""))

    text = update.message.text.strip()
    context.user_data["decl_text"] = text

    rows = [
        [InlineKeyboardButton("📤 ارسال برای تایید ادمین", callback_data="decl_submit")],
        [InlineKeyboardButton("❌ لغو", callback_data="main_menu")]
    ]

    await update.message.reply_text(
        f"📋 *پیش‌نمایش بیانیه*\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🌍 {info['flag']} *{info['name']}*\n\n"
        f"📝 {text}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"ارسال میکنم برای تایید ادمین؟",
        reply_markup=InlineKeyboardMarkup(rows),
        parse_mode="Markdown"
    )
    return DECLARATION_CONFIRM

async def declaration_submit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    p = get_player_by_id_full(user_id)

    text = context.user_data.get("decl_text", "")
    info = get_country_info(p.get("country", ""))

    conn = sqlite3.connect("game.db")
    c = conn.cursor()
    c.execute("INSERT INTO declarations (country, text) VALUES (?,?)", (p["country"], text))
    decl_id = c.lastrowid
    conn.commit()
    conn.close()

    try:
        await context.bot.send_message(
            ADMIN_ID,
            f"📢 *بیانیه جدید برای بررسی*\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"🌍 کشور: {info['flag']} *{info['name']}*\n"
            f"🆔 شناسه: `{decl_id}`\n\n"
            f"📝 *متن بیانیه:*\n{text}\n"
            f"━━━━━━━━━━━━━━━━━━━━",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ تایید و انتشار", callback_data=f"adm_decl_ok_{decl_id}"),
                 InlineKeyboardButton("❌ رد کردن", callback_data=f"adm_decl_no_{decl_id}")]
            ]),
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.error(f"Error sending to admin: {e}")

    await query.edit_message_text(
        f"✅ *بیانیه ارسال شد!*\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"⏳ منتظر بررسی ادمین باش فرمانده.\n"
        f"بعد از تایید، بیانیه‌ات در گروه منتشر میشه 📢",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 مرکز فرماندهی", callback_data="main_menu")]]),
        parse_mode="Markdown"
    )
    return MAIN_MENU

async def admin_decl_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id

    if user_id != ADMIN_ID:
        await query.answer("❌ فقط ادمین میتونه این کارو بکنه!", show_alert=True)
        return

    await query.answer("⏳ در حال پردازش...")

    # ──── تایید بیانیه ────
    if query.data.startswith("adm_decl_ok_"):
        decl_id = int(query.data.replace("adm_decl_ok_", ""))

        conn = sqlite3.connect("game.db")
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT * FROM declarations WHERE id=? AND status='pending'", (decl_id,))
        decl = c.fetchone()
        if not decl:
            conn.close()
            try:
                await query.edit_message_text(
                    "⚠️ این بیانیه قبلاً پردازش شده یا وجود نداره.",
                    parse_mode="Markdown"
                )
            except:
                pass
            return

        decl = dict(decl)
        c.execute("UPDATE declarations SET status='approved' WHERE id=?", (decl_id,))
        conn.commit()
        conn.close()

        info = get_country_info(decl["country"])
        flag = info["flag"] if info else "🌍"
        name = info["name"] if info else decl["country"]

        # متن بیانیه برای گروه/کانال
        pub_msg = (
            f"📜 *بیانیه رسمی*\n"
            f"{'━'*22}\n"
            f"{flag} *{name}*\n\n"
            f"🗣️ {decl['text']}\n\n"
            f"{'━'*22}\n"
            f"_این بیانیه توسط سازمان جهانی تایید شده است_ ✅"
        )

        

        # پیام به کاربر صاحب بیانیه
        player = get_player_by_country(decl["country"])
        if player:
            try:
                await context.bot.send_message(
                    player["user_id"],
                    f"🎉 *بیانیه‌ات تایید شد فرمانده!*\n"
                    f"{'━'*22}\n"
                    f"📢 بیانیه‌ات رسماً در گروه منتشر شد.\n"
                    f"همه کشورها الان میتونن ببیننش! 🌍\n"
                    f"{'━'*22}",
                    parse_mode="Markdown"
                )
            except Exception as e:
                logger.error(f"Notify decl user error: {e}")

    # ──── رد بیانیه ────
    elif query.data.startswith("adm_decl_no_"):
        decl_id = int(query.data.replace("adm_decl_no_", ""))

        conn = sqlite3.connect("game.db")
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT * FROM declarations WHERE id=? AND status='pending'", (decl_id,))
        row = c.fetchone()
        if not row:
            conn.close()
            try:
                await query.edit_message_text(
                    "⚠️ این بیانیه قبلاً پردازش شده یا وجود نداره.",
                    parse_mode="Markdown"
                )
            except:
                pass
            return

        row = dict(row)
        c.execute("UPDATE declarations SET status='rejected' WHERE id=?", (decl_id,))
        conn.commit()
        conn.close()

        info = get_country_info(row["country"])
        flag = info["flag"] if info else "🌍"
        name = info["name"] if info else row["country"]

        # پیام رد به کاربر
        player = get_player_by_country(row["country"])
        if player:
            try:
                await context.bot.send_message(
                    player["user_id"],
                    f"❌ *بیانیه‌ات رد شد فرمانده!*\n"
                    f"{'━'*22}\n"
                    f"متن بیانیه‌ات توسط ادمین تایید نشد.\n"
                    f"میتونی بیانیه جدیدی صادر کنی. ✍️\n"
                    f"{'━'*22}",
                    parse_mode="Markdown"
                )
            except Exception as e:
                logger.error(f"Notify decl reject error: {e}")

        # ویرایش پیام ادمین — دکمه‌ها حذف میشن
        try:
            await query.edit_message_text(
                f"❌ *بیانیه رد شد*\n"
                f"{'━'*22}\n"
                f"{flag} {name}\n"
                f"🆔 شناسه: `{decl_id}`\n"
                f"کاربر مطلع شد.",
                parse_mode="Markdown"
            )
        except Exception as e:
            logger.error(f"Edit admin decl no msg error: {e}")

# ==================== دستورات ادمین ====================
async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != ADMIN_ID:
        return
    await update.message.reply_text(
        "👑 *پنل ادمین*\n━━━━━━━━━━━━━━━━━━━━",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("💰 واریز دستی برای همه", callback_data="adm_manual_income")],
        ]),
        parse_mode="Markdown"
    )

async def admin_manual_income(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    if user_id != ADMIN_ID:
        await query.answer("❌ دسترسی ندارید!", show_alert=True)
        return

    await query.edit_message_text(
        "⏳ *در حال واریز دستی برای همه کشورها...*\n🔄 لطفاً صبر کن.",
        parse_mode="Markdown"
    )

    conn = sqlite3.connect("game.db")
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM players")
    players = [dict(r) for r in c.fetchall()]
    conn.close()

    count = 0
    for p in players:
        total_income = p.get("daily_income", 70000000) + p.get("oil_income", 0)
        new_budget = p["budget"] + total_income
        oil_add = p.get("oil_income", 0)  # نفت‌خیزها ۳۰ میلیون نفت هم میگیرن
        upd = {"budget": new_budget}
        if oil_add > 0:
            upd["oil_reserves"] = (p.get("oil_reserves", 0) or 0) + oil_add
        update_player(p["user_id"], upd)

        conn2 = sqlite3.connect("game.db")
        c2 = conn2.cursor()
        c2.execute("SELECT company_key FROM companies WHERE owner_user_id=?", (p["user_id"],))
        companies = [r[0] for r in c2.fetchall()]
        conn2.close()

        co_income = sum(COMPANIES[ck]["income"] for ck in companies if ck in COMPANIES)
        if co_income > 0:
            p2 = get_player_by_id_full(p["user_id"])
            update_player(p["user_id"], {"budget": p2["budget"] + co_income})
            for ck in companies:
                co = COMPANIES.get(ck)
                if co and co.get("daily_produce"):
                    p3 = get_player_by_id_full(p["user_id"])
                    prod_updates = {}
                    for prod_key, prod_qty in co["daily_produce"].items():
                        curr = p3.get(prod_key, 0) or 0
                        prod_updates[prod_key] = curr + prod_qty
                    if prod_updates:
                        update_player(p["user_id"], prod_updates)

        try:
            info = get_country_info(p.get("country", ""))
            p_final = get_player_by_id_full(p["user_id"])
            lines = [
                f"💰 *واریز دستی توسط ادمین!*",
                f"{'━'*20}",
                f"{info['flag']} *{info['name']}*",
                f"",
                f"💰 درآمد روزانه: +`{fmt(p.get('daily_income',70000000))}`",
            ]
            if p.get("oil_income", 0) > 0:
                lines.append(f"🛢️ درآمد نفتی: +`{fmt(p.get('oil_income',0))}`")
            if co_income > 0:
                lines.append(f"🏢 درآمد شرکت‌ها: +`{fmt(co_income)}`")
            lines += [
                f"{'─'*18}",
                f"🏦 بودجه جدید: `{fmt(p_final.get('budget',0))}`",
                f"{'━'*20}",
            ]
            await context.bot.send_message(
                p["user_id"],
                "\n".join(lines),
                parse_mode="Markdown"
            )
            count += 1
        except Exception as e:
            logger.error(f"Manual income notify error: {e}")

    await query.edit_message_text(
        f"✅ *واریز دستی انجام شد!*\n\n"
        f"💰 به `{count}` کشور واریز شد.\n\n"
        f"👑 پنل ادمین",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("💰 واریز مجدد", callback_data="adm_manual_income")],
            [InlineKeyboardButton("🔙 برگشت", callback_data="main_menu")],
        ]),
        parse_mode="Markdown"
    )
    return MAIN_MENU




# ==================== حمله نظامی ====================
DANCE_FRAMES = [
    "🕺",
    "🕺💃",
    "🕺💃🕺",
    "💃🕺💃",
    "🕺💃🕺💃",
    "⚡🕺💃🕺⚡",
    "🔥💃🕺💃🔥",
    "💥🕺💃🕺💃💥",
]

async def show_attack(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    p = get_player_by_id_full(user_id)
    info = get_country_info(p.get("country", ""))

    msg = await query.edit_message_text(
        f"💣 *سامانه حمله نظامی*\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"{info['flag']} *{info['name']}*\n\n"
        f"🔄 در حال آماده‌سازی سامانه...",
        parse_mode="Markdown"
    )

    loading_frames = ["⬛⬛⬛⬛⬛", "🟥⬛⬛⬛⬛", "🟥🟥⬛⬛⬛", "🟥🟥🟥⬛⬛", "🟥🟥🟥🟥⬛", "🟥🟥🟥🟥🟥"]
    for frame in loading_frames:
        await asyncio.sleep(0.4)
        try:
            await msg.edit_text(
                f"💣 *سامانه حمله نظامی*\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"{info['flag']} *{info['name']}*\n\n"
                f"🔄 آماده‌سازی: {frame}",
                parse_mode="Markdown"
            )
        except:
            pass

    await asyncio.sleep(0.3)

    for frame in DANCE_FRAMES:
        await asyncio.sleep(0.35)
        try:
            await msg.edit_text(
                f"💣 *سامانه حمله نظامی*\n"
                f"━━━━━━━━━━━━━━━━━━━━\n\n"
                f"{frame}\n\n"
                f"🎵 *فرمانده داره گرم میشه...*",
                parse_mode="Markdown"
            )
        except:
            pass

    await asyncio.sleep(0.5)
    try:
        await msg.edit_text(
            f"💣 *سامانه حمله نظامی*\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"{info['flag']} *{info['name']}*\n\n"
            f"⚠️ *هشدار سیستم:*\n"
            f"این بخش هنوز در حال توسعه‌ست!\n\n"
            f"🕺💃🕺💃🕺💃\n\n"
            f"فرمانده... یه کم صبر داشته باش 😅\n"
            f"بزودی حملات سنگین اضافه میشه! 🔥",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 برگشت", callback_data="main_menu")]
            ]),
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.error(f"Attack animation error: {e}")
    return MAIN_MENU

async def show_rules(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    text = """⚔️ *قوانین جنگ جهانی*

🗓 *روزهای انتحاری:* یکشنبه، سه‌شنبه، پنج‌شنبه
⏰ *زمان انتحاری:* ۱۲ تا ۱۹

🚫 *مجازات‌ها:*
پهپاد انتحاری، نقطه‌زن، شناسایی، جاسوس، بمب‌گذار
بعد از پیدا شدن رهبر = مجوز حمله با موشک/پهپاد/جنگنده

⚓ *دزدیدن ناو:*
تا ۵۰ کیلومتر نزدیک شوید + قایق/زیرسطحی + هک نظامی
اگه دفاعش کم باشه = دزدی موفق

🏴‍☠️ *دزدان دریایی:*
روزی یک‌بار می‌توانند هنگام صادرات به ناوها حمله کنند

⛔ *بستن تنگه هرمز:*
بدون دلیل = ۳۰٪ تحریم | در زمان جنگ = مجاز

☢️ *بمب اتم:*
نیاز به مجوز سازمان ملل + دلیل محکم
کشور هدف کاملاً نابود می‌شود

🛡️ *مرزبانی:*
داشتن مرزبان اجباری است

⏰ *زمان‌بندی:*
خرید تجهیزات: ۱۲ ظهر تا ۱۲:۱۵ شب
جنگ اصلی: ۱۲ تا ۲۰"""
    
    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 برگشت", callback_data="main_menu")]]),
        parse_mode="Markdown"
    )
    return MAIN_MENU

# ==================== واریز شبانه ====================
async def midnight_income(context: ContextTypes.DEFAULT_TYPE):
    conn = sqlite3.connect("game.db")
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM players")
    players = [dict(r) for r in c.fetchall()]
    conn.close()

    for p in players:
        total_income = p.get("daily_income", 70000000) + p.get("oil_income", 0)
        new_budget = p["budget"] + total_income
        oil_add = p.get("oil_income", 0)  # نفت‌خیزها ۳۰ میلیون نفت هم میگیرن
        upd = {"budget": new_budget}
        if oil_add > 0:
            upd["oil_reserves"] = (p.get("oil_reserves", 0) or 0) + oil_add
        update_player(p["user_id"], upd)

        # واریز شرکت‌ها
        conn2 = sqlite3.connect("game.db")
        c2 = conn2.cursor()
        c2.execute("SELECT company_key FROM companies WHERE owner_user_id=?", (p["user_id"],))
        companies = [r[0] for r in c2.fetchall()]
        conn2.close()

        co_income = sum(COMPANIES[ck]["income"] for ck in companies if ck in COMPANIES)
        if co_income > 0:
            p2 = get_player_by_id_full(p["user_id"])
            update_player(p["user_id"], {"budget": p2["budget"] + co_income})

            for ck in companies:
                co = COMPANIES.get(ck)
                if co and co.get("daily_produce"):
                    p3 = get_player_by_id_full(p["user_id"])
                    prod_updates = {}
                    for prod_key, prod_qty in co["daily_produce"].items():
                        curr = p3.get(prod_key, 0) or 0
                        prod_updates[prod_key] = curr + prod_qty
                    if prod_updates:
                        update_player(p["user_id"], prod_updates)

        try:
            info = get_country_info(p.get("country", ""))
            p_final = get_player_by_id_full(p["user_id"])
            mine_income = 0
            for mine_key in ["diamond_mine", "gold_mine", "silver_mine"]:
                cnt = p.get(mine_key, 0) or 0
                inc = SHOP_ITEMS["mine"]["items"].get(mine_key, {}).get("daily_income", 0)
                mine_income += cnt * inc

            lines = [
                f"🌙 *گزارش مالی شبانه*",
                f"{'━'*20}",
                f"{info['flag']} *{info['name']}*",
                f"",
                f"💰 درآمد روزانه: +`{fmt(p.get('daily_income',70000000))}`",
            ]
            if p.get("oil_income", 0) > 0:
                lines.append(f"🛢️ درآمد نفتی: +`{fmt(p.get('oil_income',0))}`")
                lines.append(f"🛢️ ذخایر نفت جدید: `{fmt(p_final.get('oil_reserves',0))}`")
            if co_income > 0:
                lines.append(f"🏢 درآمد شرکت‌ها: +`{fmt(co_income)}`")
            if mine_income > 0:
                lines.append(f"⛏️ درآمد معادن: +`{fmt(mine_income)}`")
            lines += [
                f"{'─'*18}",
                f"🏦 بودجه جدید: `{fmt(p_final.get('budget',0))}`",
                f"{'━'*20}",
                f"",
                f"🌅 صبح بخیر فرمانده! آماده جنگ باش ⚔️",
            ]
            await context.bot.send_message(
                p["user_id"],
                "\n".join(lines),
                parse_mode="Markdown"
            )
        except Exception as e:
            logger.error(f"Error sending midnight income to {p['user_id']}: {e}")

# ==================== اجرای اصلی ====================
def main():
    init_db()
    
    app = Application.builder().token(BOT_TOKEN).build()
    
    # جاب صبح‌گاهی ساعت ۰۰:۰۰
    app.job_queue.run_daily(midnight_income, time=time(hour=0, minute=0))
    
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            SELECT_COUNTRY: [
                CallbackQueryHandler(pick_country_menu, pattern="^pick_country$"),
                CallbackQueryHandler(pick_group_menu, pattern="^pick_group$"),
                CallbackQueryHandler(select_country, pattern="^sel_country_"),
                CallbackQueryHandler(back_start, pattern="^back_start$"),
            ],
            MAIN_MENU: [
                CallbackQueryHandler(main_menu_handler),
            ],
            SHOP_MENU: [
                CallbackQueryHandler(show_shop, pattern="^shop$"),
                CallbackQueryHandler(shop_category, pattern="^shop_cat_"),
                CallbackQueryHandler(main_menu_handler, pattern="^main_menu$"),
                CallbackQueryHandler(view_cart, pattern="^view_cart$"),
                CallbackQueryHandler(checkout, pattern="^checkout$"),
                CallbackQueryHandler(clear_cart, pattern="^clear_cart$"),
                CallbackQueryHandler(remove_cart_item, pattern="^remove_item_"),
            ],
            SHOP_CATEGORY: [
                CallbackQueryHandler(show_shop, pattern="^shop$"),
                CallbackQueryHandler(shop_category, pattern="^shop_cat_"),
                CallbackQueryHandler(shop_item, pattern="^shop_item_"),
                CallbackQueryHandler(main_menu_handler, pattern="^main_menu$"),
                CallbackQueryHandler(remove_cart_item, pattern="^remove_item_"),
            ],
            SHOP_ITEM: [
                CallbackQueryHandler(add_to_cart, pattern="^add_"),
                CallbackQueryHandler(view_cart, pattern="^view_cart$"),
                CallbackQueryHandler(shop_category, pattern="^shop_cat_"),
                CallbackQueryHandler(main_menu_handler, pattern="^main_menu$"),
                CallbackQueryHandler(remove_cart_item, pattern="^remove_item_"),
            ],
            COMPANY_MENU: [
                CallbackQueryHandler(show_companies, pattern="^companies$"),
                CallbackQueryHandler(company_detail, pattern="^co_detail_"),
                CallbackQueryHandler(buy_company, pattern="^buy_co_"),
                CallbackQueryHandler(main_menu_handler, pattern="^main_menu$"),
            ],
            TRADE_SELECT_ITEM: [
                CallbackQueryHandler(trade_item_selected, pattern="^trade_item_"),
                CallbackQueryHandler(main_menu_handler, pattern="^main_menu$"),
            ],
            TRADE_QUANTITY: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, trade_quantity_input),
                CallbackQueryHandler(main_menu_handler, pattern="^main_menu$"),
            ],
            TRADE_PRICE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, trade_quantity_input),
                CallbackQueryHandler(trade_free, pattern="^trade_free$"),
                CallbackQueryHandler(main_menu_handler, pattern="^main_menu$"),
            ],
            TRADE_CONFIRM: [
                CallbackQueryHandler(trade_confirm_handler, pattern="^trade_confirm$"),
                CallbackQueryHandler(trade_edit, pattern="^trade_edit$"),
                CallbackQueryHandler(main_menu_handler, pattern="^main_menu$"),
            ],
            TRADE_SELECT_COUNTRY: [
                CallbackQueryHandler(trade_to_country, pattern="^trade_to_"),
                CallbackQueryHandler(trade_send, pattern="^trade_send$"),
                CallbackQueryHandler(trade_confirm_handler, pattern="^trade_confirm$"),
                CallbackQueryHandler(main_menu_handler, pattern="^main_menu$"),
            ],
            DECLARATION_TEXT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, declaration_text_input),
                CallbackQueryHandler(main_menu_handler, pattern="^main_menu$"),
            ],
            DECLARATION_CONFIRM: [
                CallbackQueryHandler(declaration_submit, pattern="^decl_submit$"),
                CallbackQueryHandler(main_menu_handler, pattern="^main_menu$"),
            ],
        },
        fallbacks=[CommandHandler("start", start)],
        per_user=True,
        per_chat=True,
    )
    
    # ── ادمین و trade handlers باید قبل از ConversationHandler باشن ──
    app.add_handler(CallbackQueryHandler(admin_decl_handler, pattern="^adm_decl_"), group=0)
    app.add_handler(CallbackQueryHandler(trade_accept, pattern="^trade_accept_"), group=0)
    app.add_handler(CallbackQueryHandler(trade_reject, pattern="^trade_reject_"), group=0)
    app.add_handler(CallbackQueryHandler(admin_manual_income, pattern="^adm_manual_income$"), group=0)
    app.add_handler(CommandHandler("admin", admin_panel), group=0)

    app.add_handler(conv_handler, group=1)
    
    print("🤖 بات در حال اجراست...")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()


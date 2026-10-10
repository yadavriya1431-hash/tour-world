from flask import Flask, request, session, render_template_string, redirect, jsonify
import urllib.parse, random, time, requests, qrcode
from io import BytesIO
import base64
import os

app = Flask(__name__)
app.secret_key = 'tour_world_final_commission_riya'

# ===== SETTINGS - YAHAN COMMISSION SET KARO =====
YOUR_UPI_ID = "yadavri2005@oksbi"
YOUR_NAME = "Tour World"
COMMISSION_RATE = 10 # 10% commission - isko 15 kar do agar 15% chahiye
FAST2SMS_API_KEY = "M70GOxuWBKcqoTZ8IF5vsjC2rdpHnVhy3Pf9w6JSXkeADbiRNaIm9kthjPZM7XeULWwi8S6ap4AszV13"
# ===============================================

registered_users = {"riya": "1234"}
likes = {"count": 312}
bookings = []
wallets = {"riya": 12500}
commission_earnings = {"total": 0, "history": []} # TUMHARA COMMISSION

FAMOUS_PLACES = {
    "mumbai": ["Gateway of India", "Marine Drive", "Juhu Beach", "Siddhivinayak Temple", "Elephanta Caves", "Bandra Sea Link", "Colaba Market", "Haji Ali Dargah"],
    "delhi": ["Red Fort", "India Gate", "Qutub Minar", "Lotus Temple", "Chandni Chowk", "Humayun's Tomb", "Akshardham"],
    "goa": ["Baga Beach", "Fort Aguada", "Dudhsagar Waterfall", "Anjuna Market", "Basilica of Bom Jesus"],
    "russia": ["Red Square", "Kremlin", "Saint Basil's Cathedral", "Lake Baikal", "Hermitage Museum", "Moscow River"],
    "dubai": ["Burj Khalifa", "Dubai Mall", "Palm Jumeirah", "Dubai Fountain", "Gold Souk", "Desert Safari"],
    "south korea": ["Gyeongbokgung Palace", "N Seoul Tower", "Bukchon Hanok Village", "Jeju Island", "Myeongdong", "Busan Beach", "DMZ Zone", "Gangnam Street"],
    "korea": ["Gyeongbokgung Palace", "N Seoul Tower", "Bukchon Village", "Myeongdong", "Jeju Island"],
}

def send_real_sms(mobile, name, city, amount):
    mobile = str(mobile)[-10:]
    url = "https://www.fast2sms.com/dev/bulkV2"
    msg = f"Hello {name}, Tour World booking {city} Rs.{amount} confirmed. ID TW{random.randint(10000,99999)}"
    if "CANCELLED" in city: msg = f"Hello {name}, {city}. 90% refund wallet me. Tour World"
    payload = f"message={msg}&language=english&route=q&numbers={mobile}"
    headers = {'authorization': FAST2SMS_API_KEY, 'Content-Type': "application/x-www-form-urlencoded"}
    try: requests.post(url, data=payload, headers=headers)
    except: pass

VIDEO_MAP = {"mumbai": "l5aZJBLAu1E", "delhi": "l5aZJBLAu1E", "goa": "3SsK-cxlj_w", "russia": "l5aZJBLAu1E", "dubai": "l5aZJBLAu1E", "south korea": "9bZkp7q19f0", "default": "l5aZJBLAu1E"}

AUTH_HTML = """<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width, initial-scale=1"><title>TOUR WORLD</title><style>*{font-family:sans-serif;box-sizing:border-box}body{margin:0;min-height:100vh;background:#000;display:flex;justify-content:center;align-items:center;padding:20px}.main{width:100%;max-width:1000px;background:#fff;border-radius:30px;overflow:hidden;display:flex}.l{flex:1.2;background:#000;color:white;padding:40px}.l h1{font-size:48px;margin:0;color:#FFD700}.badge{display:inline-block;background:#FFD700;color:#000;padding:6px 12px;border-radius:20px;font-size:11px;font-weight:700;margin:3px}.r{flex:1;padding:35px}input{width:100%;padding:14px;border-radius:12px;border:2px solid #eee;margin:8px 0}.btn{width:100%;padding:14px;border-radius:12px;border:none;font-weight:700;cursor:pointer}.btn-b{background:#000;color:#fff}.btn-y{background:#FFD700;color:#000}@media(max-width:700px){.main{flex-direction:column}}</style></head><body><div class="main"><div class="l"><h1>TOUR<br>WORLD</h1><p>By <b style="color:#FFD700">Riya Yadav</b></p><div style="margin-top:20px"><span class="badge">Hotels</span><span class="badge">Taxi</span><span class="badge">Bus</span><span class="badge">Train</span><span class="badge">Flight</span><span class="badge">Food</span><span class="badge">Map</span><span class="badge">Video Search</span><span class="badge">Gallery Search</span><span class="badge">Real Wallet</span><span class="badge">Real UPI QR</span><span class="badge">Commission 10%</span><span class="badge">SMS</span></div></div><div class="r"><h2>Login to TOUR WORLD</h2><form method="POST" action="/login"><input type="text" name="username" placeholder="Username" required><input type="password" name="password" placeholder="Password" required><button class="btn btn-b" type="submit">Login</button></form><div style="text-align:center;margin:15px 0;color:#aaa">— OR —</div><form method="POST" action="/register"><input type="text" name="username" placeholder="New Username" required><input type="password" name="password" placeholder="New Password" required><button class="btn btn-y" type="submit">Create Account</button></form></div></div></body></html>"""

HOME_HTML = """
<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width, initial-scale=1"><title>TOUR WORLD</title><style>*{font-family:sans-serif;box-sizing:border-box}body{margin:0;background:#f5f5f7}.header{background:#000;color:#fff;padding:15px 20px;display:flex;justify-content:space-between;align-items:center;position:sticky;top:0;z-index:99;border-bottom:3px solid #FFD700}.logo{font-weight:800;color:#FFD700;font-size:20px}.strip{display:flex;gap:12px;overflow-x:auto;padding:14px 18px;background:#fff}.strip img{width:250px;height:150px;border-radius:18px;object-fit:cover;flex-shrink:0}.wrap{max-width:1100px;margin:0 auto;padding:10px}.card{background:#fff;border-radius:22px;padding:20px;margin:16px 0;box-shadow:0 8px 25px rgba(0,0,0,0.06)}.inp{padding:13px 16px;border-radius:12px;border:2px solid #eee;margin:5px}.btn-p{background:#000;color:#fff;padding:13px 22px;border-radius:12px;border:none;font-weight:700;cursor:pointer}.tool{border:2px solid #eee;background:#fff;padding:10px 14px;border-radius:12px;font-weight:600;cursor:pointer;margin:4px}.map-box{border-radius:18px;overflow:hidden;border:2px solid #eee}.grid4{display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:10px}.grid2{display:grid;grid-template-columns:1fr 1fr;gap:14px}.h-card{border-radius:16px;overflow:hidden;border:2px solid #eee;background:#fff;text-decoration:none;color:#000;display:block}.h-card img{width:100%;height:110px;object-fit:cover}.h-card div{padding:10px;font-size:13px}.book-btn{background:#000;color:#FFD700;padding:6px 10px;border-radius:20px;font-size:10px;font-weight:700;display:inline-block;margin-top:5px}.search-box{display:flex;gap:8px;margin:10px 0}.search-box input{flex:1;padding:12px;border-radius:10px;border:2px solid #FFD700;outline:none}.search-box button{padding:12px 14px;border-radius:10px;border:none;background:#000;color:#FFD700;font-weight:700;cursor:pointer}.modal{display:none;position:fixed;z-index:1000;left:0;top:0;width:100%;height:100%;background:rgba(0,0,0,0.7);justify-content:center;align-items:center}.modal-content{background:#fff;padding:25px;border-radius:20px;max-width:420px;width:92%;text-align:center;position:relative}.close{position:absolute;right:15px;top:10px;font-size:24px;cursor:pointer}@media(max-width:700px){.grid4{grid-template-columns:1fr 1fr}.grid2{grid-template-columns:1fr}}</style>
<script>function toggleLang(){let hi=document.getElementById('map-hi');let en=document.getElementById('map-en');let b=document.getElementById('lang-btn');if(hi.style.display=='none'){hi.style.display='block';en.style.display='none';b.innerText='English';}else{hi.style.display='none';en.style.display='block';b.innerText='हिंदी';}}function searchGalleryChrome(){let q=document.getElementById('gallerySearch').value.trim()||'Mumbai';window.open(`https://unsplash.com/s/photos/${encodeURIComponent(q)}`,'_blank');let imgs=document.querySelectorAll('.gal-img');imgs.forEach((img,i)=>{ img.src=`https://picsum.photos/seed/${encodeURIComponent(q)}${i}${Date.now()}/400/300`; });}function searchVideoChrome(){let q=document.getElementById('videoSearch').value.trim()||'Mumbai';window.open(`https://www.youtube.com/results?search_query=${encodeURIComponent(q+' travel vlog 4k')}`,'_blank');}function openModal(id){document.getElementById(id).style.display='flex';}function closeModal(id){document.getElementById(id).style.display='none';}function downloadPDF(){window.print();}function likeTrip(){fetch('/thumbs_api').then(r=>r.json()).then(d=>{document.getElementById('likeBtn').innerText=d.count+' Likes ❤️';});}</script></head><body>
<div class="header"><div class="logo">TOUR WORLD</div><div style="display:flex;gap:6px;align-items:center;flex-wrap:wrap"><a href="/my-earnings" style="background:#25D366;color:#fff;padding:6px 12px;border-radius:20px;font-size:11px;font-weight:700;text-decoration:none">Commission Rs.{{ commission_total }}</a><a href="/wallet" style="background:#FFD700;color:#000;padding:6px 12px;border-radius:20px;font-size:11px;font-weight:700;text-decoration:none">Wallet Rs.{{ wallet_bal }}</a><a href="/my-bookings" style="background:#fff;color:#000;padding:6px 12px;border-radius:20px;font-size:11px;font-weight:700;text-decoration:none">My Bookings ({{ bookings_count }})</a><span style="background:#222;color:#FFD700;padding:6px 10px;border-radius:20px;font-size:11px">Hi {{ user }}</span><button id="lang-btn" onclick="toggleLang()" style="background:#fff;color:#000;border:none;padding:6px 10px;border-radius:20px;font-weight:700;font-size:11px">हिंदी</button><a href="/logout" style="color:#999;font-size:11px;text-decoration:none">Logout</a></div></div>
<div class="strip"><img src="https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e"><img src="https://images.unsplash.com/photo-1502602898657-3e91760cbb34"><img src="https://images.unsplash.com/photo-1528164344705-47542687000d"><img src="https://images.unsplash.com/photo-1540959733332-eab4deabeeaf"><img src="https://images.unsplash.com/photo-1492571350019-22de08371fd3"></div>
<div class="wrap"><div class="card" style="border:2px solid #FFD700"><h3>Search Any Country / City</h3><form method="POST" action="/"><input class="inp" type="text" name="city" placeholder="Ex: Russia, Mumbai, Dubai, South Korea..." required style="width:40%"><input class="inp" type="number" name="days" placeholder="Days" min="1" max="15" required style="width:18%"><button class="btn-p" type="submit">Plan Banao</button></form></div>
{% if data %}<div class="card"><h2>{{ data.city }} - {{ data.days }} Days</h2><p><b>Rs.{{ data.total_cost }} + Your Commission {{ commission_rate }}% = Rs.{{ data.commission }} extra</b></p><div style="background:#fffbe6;border:2px dashed #FFD700;border-radius:16px;padding:14px"><h3>Famous Places in {{ data.city }}</h3><div style="display:flex;flex-wrap:wrap;gap:8px">{% for place in data.famous %}<span style="background:#000;color:#FFD700;padding:7px 12px;border-radius:20px;font-size:12px">{{ place }}</span>{% endfor %}</div></div><div style="background:#fafafa;border-radius:16px;padding:12px;margin-top:12px">{% for p in data.plan %}<div style="padding:10px;border-bottom:1px solid #eee"><b>Day {{ loop.index }}:</b> {{ p }}</div>{% endfor %}</div><h3>Hotels - Click to Book ({{ commission_rate }}% Commission)</h3><div class="grid4">{% for h in data.hotels %}<a href="/book?type=hotel&city={{ data.city }}&name={{ h.name }}&price={{ h.price }}&img={{ h.img }}" class="h-card"><img src="{{ h.img }}"><div><b>{{ h.name }}</b><br>Rs.{{ h.price }}<br><small style="color:green">+Rs.{{ (h.price*commission_rate/100)|int }} commission</small><br><span class="book-btn">Book Now</span></div></a>{% endfor %}</div><h3>Taxi | Bus | Train | Flight - Click to Book</h3><div class="grid4">{% for t in data.transport %}<a href="/book?type={{ t.type }}&city={{ data.city }}&name={{ t.name }}&price={{ t.price }}&img={{ t.img }}" class="h-card"><img src="{{ t.img }}"><div><b>{{ t.name }}</b><br>Rs.{{ t.price }}<br><small style="color:green">+Rs.{{ (t.price*commission_rate/100)|int }} comm.</small><br><span class="book-btn">Book</span></div></a>{% endfor %}</div><h3>Food - Click to Order</h3><div class="grid4">{% for f in data.food %}<a href="/book?type=food&city={{ data.city }}&name={{ f.name }}&price={{ f.price }}&img={{ f.img }}" class="h-card"><img src="{{ f.img }}"><div><b>{{ f.name }}</b><br>Rs.{{ f.price }}<br><small style="color:green">+Rs.{{ (f.price*commission_rate/100)|int }} comm.</small><br><span class="book-btn">Order</span></div></a>{% endfor %}</div>
<h3 style="margin-top:22px">Live Map - {{ data.city }}</h3><div class="map-box" id="map-en"><iframe width="100%" height="340" style="border:0" src="https://www.google.com/maps?q={{ data.city }}&z=10&output=embed"></iframe></div><div class="map-box" id="map-hi" style="display:none"><iframe width="100%" height="340" style="border:0" src="https://www.google.com/maps?q={{ data.city }}&hl=hi&z=10&output=embed"></iframe></div>
<div class="grid2" style="margin-top:18px"><div><h3>Video - {{ data.city }}</h3><div class="search-box"><input id="videoSearch" type="text" value="{{ data.city }}"><button onclick="searchVideoChrome()">Search Video</button></div><div class="map-box"><iframe width="100%" height="280" src="{{ data.video }}" frameborder="0" allowfullscreen></iframe></div></div><div><h3>Gallery - {{ data.city }}</h3><div class="search-box"><input id="gallerySearch" type="text" value="{{ data.city }}"><button onclick="searchGalleryChrome()">Search Photo</button></div><div style="display:grid;grid-template-columns:1fr 1fr;gap:10px">{% for img in data.gallery %}<img class="gal-img" src="{{ img }}" style="width:100%;height:135px;border-radius:14px;object-fit:cover;border:2px solid #eee">{% endfor %}</div></div></div>
<h3 style="margin-top:18px">Pro Tools</h3><div style="display:flex;flex-wrap:wrap;gap:6px"><button class="tool" onclick="downloadPDF()">PDF</button><button class="tool" onclick="openModal('qrModal')">Real UPI QR 💰</button><button class="tool" onclick="window.location.href='/wallet'">Wallet</button><button class="tool" onclick="window.location.href='/my-earnings'">My Commission</button><button class="tool" id="likeBtn" onclick="likeTrip()">{{ likes_count }} Likes</button><a href=https://wa.me/?text={{ data.wa_text }} target="_blank" style="text-decoration:none"><button class="tool">WhatsApp</button></a></div></div>{% endif %}
<div class="card" style="text-align:center;background:#000;color:#fff"><div style="color:#FFD700;font-weight:800">TOUR WORLD - Real App with Commission</div><div style="font-size:11px;opacity:0.7">By Riya Yadav | Commission: {{ commission_rate }}% | Earnings: Rs.{{ commission_total }}</div></div></div>

<div id="qrModal" class="modal"><div class="modal-content">
<span class="close" onclick="closeModal('qrModal')">&times;</span>
<h3 style="color:#000;margin:0">Real UPI Payment QR</h3>
{% if data %}
<p style="font-size:13px;margin:8px 0">Scan to Pay - <b>Rs.{{ data.total_cost }}</b> for {{ data.city }}</p>
<img src="https://api.qrserver.com/v1/create-qr-code/?size=320x320&data=upi%3A%2F%2Fpay%3Fpa%3Dyadavri2005%40oksbi%26pn%3DTour%2520World%26am%3D{{ data.total_cost }}%26cu%3DINR%26tn%3DTrip%2520to%2520{{ data.city }}%2520by%2520{{ user }}" style="border-radius:14px;border:3px solid #FFD700;padding:6px;width:100%;max-width:320px">
<div style="background:#fffbe6;border:2px dashed #FFD700;border-radius:12px;padding:12px;margin-top:12px;font-size:12px;text-align:left;line-height:1.5">
<b>UPI ID:</b> yadavri2005@oksbi<br><b>Name:</b> Tour World (Riya)<br><b>Amount:</b> Rs.{{ data.total_cost }}<br><b>Your Commission:</b> Rs.{{ data.commission }} ({{ commission_rate }}%)<br><b>Note:</b> Trip to {{ data.city }}<br></div>
<p style="font-size:11px;color:#25D366;font-weight:700;margin-top:10px">✅ PhonePe / GPay / Paytm / BHIM se scan karo - Real payment</p>
{% endif %}
</div></div>
</body></html>
"""

WALLET_HTML = """<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width, initial-scale=1"><title>Real Wallet</title><style>*{font-family:sans-serif;box-sizing:border-box}body{margin:0;background:#f5f5f7;padding:20px}.header{background:#000;color:#fff;padding:15px 20px;display:flex;justify-content:space-between;align-items:center;border-bottom:3px solid #FFD700}.card{background:#fff;border-radius:22px;padding:22px;max-width:500px;margin:20px auto;box-shadow:0 8px 25px rgba(0,0,0,0.06)}.bal{background:#fffbe6;border:2px dashed #FFD700;border-radius:16px;padding:20px;margin:15px 0;text-align:center}.inp{width:100%;padding:14px;border-radius:12px;border:2px solid #FFD700;margin:10px 0;outline:none}.btn{width:100%;padding:14px;border-radius:12px;border:none;font-weight:700;cursor:pointer}.btn-gold{background:#FFD700;color:#000}.btn-black{background:#000;color:#FFD700}</style></head><body>
<div class="header"><div style="font-weight:800;color:#FFD700">TOUR WORLD - Wallet + Commission</div><div><a href="/" style="background:#fff;color:#000;padding:6px 12px;border-radius:20px;text-decoration:none;font-size:12px">Home</a> <a href="/my-earnings" style="background:#25D366;color:#fff;padding:6px 12px;border-radius:20px;text-decoration:none;font-size:12px;margin-left:6px">Commission</a></div></div>
<div class="card"><h2>Hi {{ user }} 👋</h2><div class="bal"><h1>Rs. {{ balance }}</h1><p>Wallet Balance</p><p style="color:green;font-weight:700">Total Commission Earned: Rs.{{ commission_total }}</p></div><h3>Add Money</h3>
<form method="POST" action="/add-money"><input class="inp" type="number" name="amount" placeholder="Ex: 500" required min="10"><button class="btn btn-black" type="submit">Add Money to Wallet</button></form>
<div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:8px;margin:10px 0"><form method="POST" action="/add-money"><input type="hidden" name="amount" value="100"><button class="btn btn-gold">+ Rs.100</button></form><form method="POST" action="/add-money"><input type="hidden" name="amount" value="500"><button class="btn btn-gold">+ Rs.500</button></form><form method="POST" action="/add-money"><input type="hidden" name="amount" value="1000"><button class="btn btn-gold">+ Rs.1000</button></form></div></div></body></html>"""

BOOK_HTML = """<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width, initial-scale=1"><title>Book</title><style>*{font-family:sans-serif;box-sizing:border-box}body{margin:0;background:#f5f5f7;padding:20px}.card{max-width:500px;margin:0 auto;background:#fff;border-radius:24px;overflow:hidden}.card img{width:100%;height:220px;object-fit:cover}.info{padding:22px}.inp{width:100%;padding:14px;border-radius:12px;border:2px solid #FFD700;margin:10px 0}.pay-btn{width:100%;padding:16px;border-radius:14px;border:none;font-weight:700;background:#000;color:#FFD700;cursor:pointer}.comm-box{background:#e6ffe6;border:2px dashed #25D366;border-radius:12px;padding:10px;margin:10px 0;font-size:13px}</style></head><body><div class="card"><img src="{{ img }}"><div class="info"><h2>{{ name }}</h2><p>{{ city }} | Rs.{{ price }} | Wallet: Rs.{{ wallet_bal }}</p><div class="comm-box">💰 <b>Your Commission:</b> Rs.{{ commission }} ({{ commission_rate }}% of Rs.{{ price }})<br>Booking karte hi ye tumhare Commission me add hoga!</div><form method="GET" action="/pay"><input type="hidden" name="city" value="{{ city }}"><input type="hidden" name="name" value="{{ name }}"><input type="hidden" name="price" value="{{ price }}"><input type="hidden" name="commission" value="{{ commission }}"><input class="inp" type="tel" name="phone" placeholder="Mobile - 9876543210" required pattern="[0-9]{10}" maxlength="10"><select name="method" class="inp"><option value="Wallet">My Wallet (Real)</option><option value="UPI">UPI Pay (Real QR - {{ upi_id }})</option><option value="Card">Card</option></select><button type="submit" class="pay-btn">Pay Now - Rs.{{ price }} (You Earn Rs.{{ commission }})</button></form><div style="text-align:center;margin-top:12px"><a href="/wallet">Wallet</a> | <a href="/my-earnings">My Commission</a> | <a href="/">Back</a></div></div></div></body></html>"""

PAY_HTML = """<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width, initial-scale=1"><title>Success</title><style>*{font-family:sans-serif}body{margin:0;background:#000;display:flex;justify-content:center;align-items:center;min-height:100vh;padding:20px}.box{background:#fff;border-radius:24px;padding:35px;text-align:center;max-width:450px;width:100%}.tick{width:70px;height:70px;background:#000;color:#FFD700;border-radius:50%;display:flex;justify-content:center;align-items:center;font-size:35px;margin:0 auto 15px auto}.comm{background:#e6ffe6;border:2px dashed #25D366;border-radius:12px;padding:12px;margin:12px 0}</style></head><body><div class="box"><div class="tick">✓</div><h2>Payment Successful!</h2><p>{{ name }}<br>{{ city }}<br><b>Rs.{{ price }}</b> via {{ method }}</p><div class="comm"><b>💰 Commission Earned: Rs.{{ commission }}</b><br><small>{{ commission_rate }}% of Rs.{{ price }} - Added to your Earnings</small><br><small>Total Earnings: Rs.{{ total_earnings }}</small></div><p>Wallet Remaining: Rs.{{ wallet_bal }}</p><div style="background:#fffbe6;border:2px dashed #FFD700;border-radius:14px;padding:12px;margin:15px 0">ID: <b>TW{{ booking_id }}</b><br><small>SMS to {{ phone }} - Message wala feature</small></div><a href="/my-earnings" style="background:#25D366;color:#fff;padding:12px 20px;border-radius:20px;text-decoration:none;font-weight:700;display:inline-block">My Commission - Rs.{{ total_earnings }}</a><br><br><a href="/my-bookings" style="background:#000;color:#FFD700;padding:12px 20px;border-radius:20px;text-decoration:none;font-weight:700;display:inline-block">My Bookings</a><br><br><a href="/">Home</a></div></body></html>"""

MY_BOOKINGS_HTML = """<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width, initial-scale=1"><title>My Bookings</title><style>body{font-family:sans-serif;background:#f5f5f7;margin:0;padding:20px}.header{background:#000;color:#fff;padding:15px 20px;display:flex;justify-content:space-between;align-items:center;border-bottom:3px solid #FFD700}.card{background:#fff;border-radius:18px;padding:18px;margin:12px 0}.status-conf{background:#e6f7e6;color:#0a7a0a;padding:4px 10px;border-radius:20px;font-size:11px;font-weight:700}.status-canc{background:#ffe6e6;color:#a00;padding:4px 10px;border-radius:20px;font-size:11px;font-weight:700}.btn-canc{background:#000;color:#FFD700;border:none;padding:12px 16px;border-radius:10px;font-weight:700;cursor:pointer;width:100%;margin-top:10px}</style></head><body>
<div class="header"><div style="font-weight:800;color:#FFD700">TOUR WORLD</div><div><a href="/my-earnings" style="background:#25D366;color:#fff;padding:6px 12px;border-radius:20px;text-decoration:none;font-size:12px">Commission Rs.{{ commission_total }}</a> <a href="/wallet" style="background:#FFD700;color:#000;padding:6px 12px;border-radius:20px;text-decoration:none;font-size:12px">Wallet Rs.{{ wallet_bal }}</a> <a href="/" style="background:#fff;color:#000;padding:6px 12px;border-radius:20px;text-decoration:none;font-size:12px;margin-left:6px">Home</a></div></div>
<h2>My Bookings - {{ user }} ({{ bookings|length }})</h2>
{% if not bookings %}<div class="card" style="text-align:center">Koi booking nahi</div>{% endif %}
{% for b in bookings|reverse %}
<div class="card"><div style="display:flex;justify-content:space-between"><b>{{ b.name }}</b>{% if b.status=='Confirmed' %}<span class="status-conf">{{ b.status }}</span>{% else %}<span class="status-canc">{{ b.status }}</span>{% endif %}</div><p style="font-size:13px">{{ b.city }} | Rs.{{ b.price }} | {{ b.method }}<br>Phone: {{ b.phone }} | Commission: <b style="color:green">Rs.{{ b.commission }}</b><br>ID: TW{{ b.id }}</p>
{% if b.status=='Confirmed' %}<form method="POST" action="/cancel-booking/{{ b.id }}" onsubmit="return confirm('Cancel? 90% refund wallet me ayega')"><button class="btn-canc" type="submit">❌ Trip Cancel - 90% Refund Wallet Me</button></form>{% else %}<div style="background:#fffbe6;border:2px dashed #FFD700;padding:10px;border-radius:10px;font-size:12px"><b>{{ b.refund }}</b></div>{% endif %}</div>
{% endfor %}</body></html>"""

EARNINGS_HTML = """<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width, initial-scale=1"><title>My Earnings</title><style>body{font-family:sans-serif;background:#f5f5f7;margin:0;padding:20px}.header{background:#000;color:#fff;padding:15px 20px;display:flex;justify-content:space-between;align-items:center;border-bottom:3px solid #25D366}.card{background:#fff;border-radius:18px;padding:18px;margin:12px 0}.big{font-size:42px;font-weight:800;color:#25D366;margin:0}.bal{background:linear-gradient(135deg,#25D366,#128C7E);color:#fff;border-radius:22px;padding:25px;text-align:center}</style></head><body>
<div class="header"><div style="font-weight:800;color:#FFD700">TOUR WORLD - My Commission</div><div><a href="/" style="background:#fff;color:#000;padding:6px 12px;border-radius:20px;text-decoration:none;font-size:12px">Home</a></div></div>
<div class="card bal"><p style="margin:0;opacity:0.9">Total Commission Earned ({{ commission_rate }}% per booking)</p><div class="big">Rs.{{ total }}</div><p style="margin:5px 0">From {{ count }} Bookings</p><p style="font-size:12px;opacity:0.8">Har booking pe {{ commission_rate }}% tumhara</p></div>
<h3>Commission History</h3>
{% if not history %}<div class="card" style="text-align:center">Abhi tak koi commission nahi</div>{% endif %}
{% for h in history|reverse %}
<div class="card"><div style="display:flex;justify-content:space-between"><b>{{ h.city }} - {{ h.name }}</b><b style="color:#25D366">+ Rs.{{ h.commission }}</b></div><p style="font-size:12px;margin:5px 0">Booking Rs.{{ h.price }} ka {{ commission_rate }}% | ID: TW{{ h.id }} | Phone: {{ h.phone }}<br><small>{{ h.date }}</small></p></div>
{% endfor %}
<div class="card" style="background:#fffbe6;border:2px dashed #FFD700"><b>UPI Withdraw:</b> Commission ko nikalne ke liye UPI ID {{ upi_id }} pe withdraw kar sakte ho<br><small>Abhi wallet me hai, manual withdraw</small></div>
</body></html>"""

def get_dynamic_data(city):
    hotels=[{"name": f"{city} Grand 5 Star", "price": 4500, "rating": "4.8", "img": "https://images.unsplash.com/photo-1566073771259-6a8506099945?w=400"},{"name": f"{city} Beach Resort", "price": 3800, "rating": "4.7", "img": "https://images.unsplash.com/photo-1551882547-b79e2ba5e482?w=400"},{"name": f"{city} City Inn", "price": 2500, "rating": "4.5", "img": "https://images.unsplash.com/photo-1520250497591-112f2f40a3f4?w=400"},{"name": f"{city} Luxury Villa", "price": 6000, "rating": "4.9", "img": "https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?w=400"},]
    transport=[{"type":"taxi", "name": f"{city} City Taxi", "price": 12, "unit": "/km", "img": "https://images.unsplash.com/photo-1449965408869-eaa3f722e40d?w=400"},{"type":"bus", "name": f"{city} Volvo Bus", "price": 500, "unit": "Ticket", "img": "https://images.unsplash.com/photo-1544620347-c4fd4a3d5957?w=400"},{"type":"train", "name": f"{city} Express", "price": 800, "unit": "Ticket", "img": "https://images.unsplash.com/photo-1474487548417-4a6c2f1c1d45?w=400"},{"type":"flight", "name": f"{city} Flight", "price": 3500, "unit": "Ticket", "img": "https://images.unsplash.com/photo-1436491865332-7a61a109cc05?w=400"},]
    food=[{"name": f"{city} Fine Dining", "price": 1200, "rating":"4.8", "img":"https://images.unsplash.com/photo-1414235077428-338989a2e8c0?w=400"},{"name": f"{city} Street Food", "price": 400, "rating":"4.6", "img":"https://images.unsplash.com/photo-1555396273-367ea4eb4db5?w=400"},{"name": f"{city} Cafe", "price": 600, "rating":"4.7", "img":"https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=400"},{"name": f"{city} Lounge", "price": 900, "rating":"4.5", "img":"https://images.unsplash.com/photo-1559339352-11d035aa65de?w=400"},]
    return hotels, transport, food

def get_plan(city, days):
    days=int(days); city_lower=city.lower().strip(); city_title=city.title()
    famous=FAMOUS_PLACES.get(city_lower, [f"{city_title} Palace", f"{city_title} Beach", f"{city_title} Market", f"{city_title} Temple", f"{city_title} Museum", f"{city_title} Famous Street"])
    plan=[]
    for i in range(days):
        place=famous[i % len(famous)]
        if i==0: plan.append(f"Arrival + {place} in {city_title}")
        elif i==days-1: plan.append(f"Morning at {place} + Shopping + Farewell")
        else: plan.append(f"Explore: {place} + Local Food in {city_title}")
    cost=days*4800; hotels,transport,food=get_dynamic_data(city_title)
    commission = int(cost * COMMISSION_RATE / 100)
    vid=VIDEO_MAP.get(city_lower, VIDEO_MAP["default"])
    video=f"https://www.youtube-nocookie.com/embed/{vid}?rel=0"
    ts=int(time.time())
    gallery=[f"https://picsum.photos/seed/{city_lower}1{ts}/400/300", f"https://picsum.photos/seed/{city_lower}2{ts}/400/300", f"https://picsum.photos/seed/{city_lower}3{ts}/400/300", f"https://picsum.photos/seed/{city_lower}4{ts}/400/300"]
    wa=urllib.parse.quote(f"Trip to {city_title} Rs.{cost}")
    return {"city":city_title,"days":days,"plan":plan,"famous":famous,"total_cost":cost,"commission":commission,"emi":cost//days,"wa_text":wa,"hotels":hotels,"transport":transport,"food":food,"video":video,"gallery":gallery}

@app.route('/', methods=['GET','POST'])
def home():
    if 'user' not in session: return render_template_string(AUTH_HTML)
    data=None
    if request.method=='POST' and 'city' in request.form:
        data=get_plan(request.form.get('city'), request.form.get('days','3')); session['last_plan']=data
    user=session.get('user')
    return render_template_string(HOME_HTML, data=session.get('last_plan') if request.method=='GET' else data, user=user, likes_count=likes["count"], bookings_count=len(bookings), wallet_bal=wallets.get(user,0), commission_total=commission_earnings["total"], commission_rate=COMMISSION_RATE)

@app.route('/book')
def book():
    user=session.get('user','Guest')
    price = int(request.args.get('price','0'))
    commission = int(price * COMMISSION_RATE / 100)
    return render_template_string(BOOK_HTML, city=request.args.get('city',''), name=request.args.get('name',''), price=request.args.get('price',''), img=request.args.get('img',''), wallet_bal=wallets.get(user,0), commission=commission, commission_rate=COMMISSION_RATE, upi_id=YOUR_UPI_ID)

@app.route('/pay')
def pay():
    city=request.args.get('city'); name=request.args.get('name'); price=request.args.get('price'); method=request.args.get('method'); phone=request.args.get('phone','9876543210')
    user=session.get('user','Guest')
    price_int=int(price)
    commission = int(price_int * COMMISSION_RATE / 100)
    if method=="Wallet":
        bal=wallets.get(user,0)
        if bal < price_int:
            return f"<h1>Wallet me balance kam hai! Rs.{bal}</h1><a href='/wallet'>Add Money</a>"
        wallets[user]=bal-price_int
    # COMMISSION ADD KARO - YAHI TUMHARA PROFIT HAI
    commission_earnings["total"] += commission
    commission_earnings["history"].append({"id": len(bookings)+1, "name": name, "city": city, "price": price, "commission": commission, "phone": phone, "date": time.strftime("%d-%m-%Y %H:%M")})
    send_real_sms(phone, user, city, price)
    new_booking={"id": len(bookings)+1, "name": name, "city": city, "price": price, "method": method, "phone": phone, "status": "Confirmed", "refund": "0%", "commission": commission}
    bookings.append(new_booking)
    return render_template_string(PAY_HTML, city=city, name=name, price=price, method=method, booking_id=new_booking["id"], phone=phone, wallet_bal=wallets.get(user,0), commission=commission, commission_rate=COMMISSION_RATE, total_earnings=commission_earnings["total"])

@app.route('/wallet')
def wallet_page():
    if 'user' not in session: return redirect('/')
    user=session.get('user')
    return render_template_string(WALLET_HTML, user=user, balance=wallets.get(user,0), commission_total=commission_earnings["total"])

@app.route('/add-money', methods=['POST'])
def add_money():
    user=session.get('user','Guest')
    amt=int(request.form.get('amount',0))
    wallets[user]=wallets.get(user,0)+amt
    return redirect('/wallet')

@app.route('/my-bookings')
def my_bookings():
    if 'user' not in session: return redirect('/')
    user=session.get('user')
    return render_template_string(MY_BOOKINGS_HTML, bookings=bookings, user=user, wallet_bal=wallets.get(user,0), commission_total=commission_earnings["total"])

@app.route('/my-earnings')
def my_earnings():
    if 'user' not in session: return redirect('/')
    return render_template_string(EARNINGS_HTML, total=commission_earnings["total"], history=commission_earnings["history"], count=len(commission_earnings["history"]), commission_rate=COMMISSION_RATE, upi_id=YOUR_UPI_ID)

@app.route('/cancel-booking/<int:bid>', methods=['POST'])
def cancel_booking(bid):
    user=session.get('user','Guest')
    for b in bookings:
        if b['id']==bid and b['status']=='Confirmed':
            b['status']="Cancelled"
            amt=int(int(b['price'])*0.9)
            b['refund']=f"90% Refund Rs.{amt} added to Wallet"
            wallets[user]=wallets.get(user,0)+amt
            # Cancel pe commission wapas minus
            commission_earnings["total"] -= int(b.get('commission',0))
            send_real_sms(b['phone'], user, f"{b['city']} BOOKING CANCELLED. Rs.{amt} refunded", b['price'])
            break
    return redirect('/my-bookings')

@app.route('/thumbs_api')
def thumbs_api(): likes["count"]+=1; return jsonify({"count": likes["count"]})

@app.route('/login', methods=['POST'])
def login():
    u=request.form.get('username'); p=request.form.get('password')
    if u=="admin" and p=="admin123": session['user']=u; return redirect('/')
    if u in registered_users and registered_users[u]==p:
        if u not in wallets: wallets[u]=0
        session['user']=u; return redirect('/')
    return render_template_string(AUTH_HTML)

@app.route('/register', methods=['POST'])
def register(): u=request.form.get('username'); p=request.form.get('password'); registered_users[u]=p; wallets[u]=0; session['user']=u; return redirect('/')
@app.route('/logout')
def logout(): session.clear(); return redirect('/')
@app.route('/admin')
def admin():
    if 'user' not in session: return redirect('/')
    return render_template_string("<h1>Admin - Riya's Earnings</h1><p>Total Commission: Rs.{{total}}</p><p>Wallets: {{wallets}}</p><p>Bookings: {{bookings}}</p><p>Commission History: {{history}}</p><a href='/'>Home</a><br><a href='/my-earnings'>My Earnings Page</a>", total=commission_earnings["total"], wallets=wallets, bookings=bookings, history=commission_earnings["history"])

if __name__=='__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)

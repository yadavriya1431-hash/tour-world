from flask import Flask, request, session, render_template_string, redirect, jsonify
import urllib.parse, random, time

app = Flask(__name__)
app.secret_key = 'tour_world_final_clean'

registered_users = {"riya": "1234"}
likes = {"count": 312}
bookings = []

FAMOUS_PLACES = {
    "mumbai": ["Gateway of India", "Marine Drive", "Juhu Beach", "Siddhivinayak Temple", "Elephanta Caves", "Bandra Sea Link", "Colaba Market", "Haji Ali Dargah"],
    "delhi": ["Red Fort", "India Gate", "Qutub Minar", "Lotus Temple", "Chandni Chowk", "Humayun's Tomb", "Akshardham"],
    "goa": ["Baga Beach", "Fort Aguada", "Dudhsagar Waterfall", "Anjuna Market", "Basilica of Bom Jesus"],
    "thailand": ["Grand Palace Bangkok", "Phi Phi Islands", "Wat Arun Temple", "Patong Beach Phuket", "Chatuchak Market"],
    "bali": ["Ubud Monkey Forest", "Tanah Lot Temple", "Kuta Beach", "Rice Terrace"],
    "singapore": ["Marina Bay Sands", "Gardens by the Bay", "Sentosa Island", "Merlion Park"],
    "dubai": ["Burj Khalifa", "Dubai Mall", "Palm Jumeirah", "Dubai Fountain", "Gold Souk", "Desert Safari"],
    "south korea": ["Gyeongbokgung Palace", "N Seoul Tower", "Bukchon Hanok Village", "Jeju Island", "Myeongdong", "Busan Beach", "DMZ Zone", "Gangnam Street"],
    "korea": ["Gyeongbokgung Palace", "N Seoul Tower", "Bukchon Village", "Myeongdong", "Jeju Island", "Gangnam"],
    "seoul": ["Gyeongbokgung Palace", "N Seoul Tower", "Myeongdong", "Gangnam Street", "Bukchon Village"],
    "paris": ["Eiffel Tower", "Louvre Museum"], "london": ["Big Ben", "London Eye"],
}

VIDEO_MAP = {
    "mumbai": "l5aZJBLAu1E", "delhi": "l5aZJBLAu1E", "goa": "3SsK-cxlj_w",
    "thailand": "3SsK-cxlj_w", "bali": "l5aZJBLAu1E", "dubai": "l5aZJBLAu1E",
    "south korea": "9bZkp7q19f0", "korea": "9bZkp7q19f0", "seoul": "9bZkp7q19f0",
    "default": "l5aZJBLAu1E"
}

# CLEAN AUTH - Admin/User text hata diya
AUTH_HTML = """<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width, initial-scale=1"><title>TOUR WORLD</title><style>*{font-family:sans-serif;box-sizing:border-box}body{margin:0;min-height:100vh;background:#000;display:flex;justify-content:center;align-items:center;padding:20px}.main{width:100%;max-width:1000px;background:#fff;border-radius:30px;overflow:hidden;display:flex}.l{flex:1.2;background:#000;color:white;padding:40px}.l h1{font-size:48px;margin:0;color:#FFD700}.badge{display:inline-block;background:#FFD700;color:#000;padding:6px 12px;border-radius:20px;font-size:11px;font-weight:700;margin:3px}.r{flex:1;padding:35px}input{width:100%;padding:14px;border-radius:12px;border:2px solid #eee;margin:8px 0}.btn{width:100%;padding:14px;border-radius:12px;border:none;font-weight:700;cursor:pointer}.btn-b{background:#000;color:#fff}.btn-y{background:#FFD700;color:#000}@media(max-width:700px){.main{flex-direction:column}}</style></head><body><div class="main"><div class="l"><h1>TOUR<br>WORLD</h1><p>By <b style="color:#FFD700">Riya Yadav</b></p><div style="margin-top:20px"><span class="badge">Hotels</span><span class="badge">Taxi</span><span class="badge">Bus</span><span class="badge">Train</span><span class="badge">Flight</span><span class="badge">Food</span><span class="badge">Admin</span></div></div><div class="r"><h2>Login to TOUR WORLD</h2><form method="POST" action="/login"><input type="text" name="username" placeholder="Username" required><input type="password" name="password" placeholder="Password" required><button class="btn btn-b" type="submit">Login</button></form><div style="text-align:center;margin:15px 0;color:#aaa">— OR —</div><form method="POST" action="/register"><input type="text" name="username" placeholder="New Username" required><input type="password" name="password" placeholder="New Password" required><button class="btn btn-y" type="submit">Create Account</button></form></div></div></body></html>"""

HOME_HTML = """
<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width, initial-scale=1"><title>TOUR WORLD</title><style>*{font-family:sans-serif;box-sizing:border-box}body{margin:0;background:#f5f5f7}.header{background:#000;color:#fff;padding:15px 20px;display:flex;justify-content:space-between;align-items:center;position:sticky;top:0;z-index:99;border-bottom:3px solid #FFD700}.logo{font-weight:800;color:#FFD700;font-size:20px}.strip{display:flex;gap:12px;overflow-x:auto;padding:14px 18px;background:#fff}.strip img{width:250px;height:150px;border-radius:18px;object-fit:cover;flex-shrink:0}.wrap{max-width:1100px;margin:0 auto;padding:10px}.card{background:#fff;border-radius:22px;padding:20px;margin:16px 0;box-shadow:0 8px 25px rgba(0,0,0,0.06)}.inp{padding:13px 16px;border-radius:12px;border:2px solid #eee;margin:5px;outline:none}.btn-p{background:#000;color:#fff;padding:13px 22px;border-radius:12px;border:none;font-weight:700;cursor:pointer}.tool{border:2px solid #eee;background:#fff;padding:10px 14px;border-radius:12px;font-weight:600;cursor:pointer;margin:4px;transition:0.2s}.tool:hover{background:#000;color:#FFD700}.map-box{border-radius:18px;overflow:hidden;border:2px solid #eee}.grid4{display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:10px}.grid2{display:grid;grid-template-columns:1fr 1fr;gap:14px}.h-card{border-radius:16px;overflow:hidden;border:2px solid #eee;background:#fff;text-decoration:none;color:#000;display:block}.h-card img{width:100%;height:110px;object-fit:cover}.h-card div{padding:10px;font-size:13px}.book-btn{background:#000;color:#FFD700;padding:6px 10px;border-radius:20px;font-size:10px;font-weight:700;display:inline-block;margin-top:5px}.search-box{display:flex;gap:8px;margin:10px 0}.search-box input{flex:1;padding:12px;border-radius:10px;border:2px solid #FFD700;outline:none}.search-box button{padding:12px 14px;border-radius:10px;border:none;background:#000;color:#FFD700;font-weight:700;cursor:pointer}.modal{display:none;position:fixed;z-index:1000;left:0;top:0;width:100%;height:100%;background:rgba(0,0,0,0.7);justify-content:center;align-items:center}.modal-content{background:#fff;padding:25px;border-radius:20px;max-width:400px;width:90%;text-align:center;position:relative}.close{position:absolute;right:15px;top:10px;font-size:24px;cursor:pointer}@media(max-width:700px){.grid4{grid-template-columns:1fr 1fr}.grid2{grid-template-columns:1fr}}</style>
<script>
function toggleLang(){let hi=document.getElementById('map-hi');let en=document.getElementById('map-en');let b=document.getElementById('lang-btn');if(hi.style.display=='none'){hi.style.display='block';en.style.display='none';b.innerText='English';}else{hi.style.display='none';en.style.display='block';b.innerText='हिंदी';}}
function searchGalleryChrome(){
  let q=document.getElementById('gallerySearch').value.trim()||'Mumbai';
  window.open(`https://unsplash.com/s/photos/${encodeURIComponent(q)}`,'_blank');
  let imgs=document.querySelectorAll('.gal-img');
  imgs.forEach((img,i)=>{ img.src=`https://picsum.photos/seed/${encodeURIComponent(q)}${i}${Date.now()}/400/300`; });
}
function searchVideoChrome(){
  let q=document.getElementById('videoSearch').value.trim()||'Mumbai';
  window.open(`https://www.youtube.com/results?search_query=${encodeURIComponent(q+' travel vlog 4k')}`,'_blank');
}
function openModal(id){ document.getElementById(id).style.display='flex'; }
function closeModal(id){ document.getElementById(id).style.display='none'; }
function downloadPDF(){ window.print(); }
function likeTrip(){
  fetch('/thumbs_api').then(r=>r.json()).then(data=>{
    document.getElementById('likeBtn').innerText = data.count + ' Likes ❤️';
    document.getElementById('likeBtn').style.background='#FFD700';
    setTimeout(()=>{ document.getElementById('likeBtn').style.background='#fff'; }, 500);
  });
}
</script>
</head><body>
<div class="header"><div class="logo">TOUR WORLD</div><div style="display:flex;gap:8px;align-items:center"><a href="/admin" style="background:#FFD700;color:#000;padding:6px 12px;border-radius:20px;font-size:11px;font-weight:700;text-decoration:none">Admin</a><span style="background:#222;color:#FFD700;padding:6px 12px;border-radius:20px;font-size:11px">Hi {{ user }}</span><button id="lang-btn" onclick="toggleLang()" style="background:#fff;color:#000;border:none;padding:6px 12px;border-radius:20px;font-weight:700;font-size:11px;cursor:pointer">हिंदी</button><a href="/logout" style="color:#999;font-size:11px;text-decoration:none">Logout</a></div></div>
<div class="strip"><img src="https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e"><img src="https://images.unsplash.com/photo-1502602898657-3e91760cbb34"><img src="https://images.unsplash.com/photo-1528164344705-47542687000d"><img src="https://images.unsplash.com/photo-1540959733332-eab4deabeeaf"><img src="https://images.unsplash.com/photo-1492571350019-22de08371fd3"></div>
<div class="wrap"><div class="card" style="border:2px solid #FFD700"><h3 style="margin:0 0 10px 0">Search Any Country / City</h3><form method="POST" action="/"><input class="inp" type="text" name="city" placeholder="Ex: Mumbai, South Korea, Dubai..." required style="width:40%"><input class="inp" type="number" name="days" placeholder="Days" min="1" max="15" required style="width:18%"><button class="btn-p" type="submit">Plan Banao</button></form></div>
{% if data %}<div class="card"><h2 style="margin:0">{{ data.city }} - {{ data.days }} Days</h2><p><b>Rs.{{ data.total_cost }}</b> | EMI Rs.{{ data.emi }}/mo</p>
<div style="background:#fffbe6;border:2px dashed #FFD700;border-radius:16px;padding:14px;margin:15px 0"><h3 style="margin:0 0 10px 0">Famous Places in {{ data.city }}</h3><div style="display:flex;flex-wrap:wrap;gap:8px">{% for place in data.famous %}<span style="background:#000;color:#FFD700;padding:7px 12px;border-radius:20px;font-size:12px;font-weight:600">{{ place }}</span>{% endfor %}</div></div>
<div style="background:#fafafa;border-radius:16px;padding:12px;margin-top:10px">{% for p in data.plan %}<div style="padding:10px;border-bottom:1px solid #eee"><b>Day {{ loop.index }}:</b> {{ p }}</div>{% endfor %}</div>
<h3 style="margin-top:22px">Hotels in {{ data.city }} - Click to Book</h3><div class="grid4">{% for h in data.hotels %}<a href="/book?type=hotel&city={{ data.city }}&name={{ h.name }}&price={{ h.price }}&img={{ h.img }}" class="h-card"><img src="{{ h.img }}"><div><b>{{ h.name }}</b><br>Rs.{{ h.price }}/night {{ h.rating }}<br><span class="book-btn">Book Now</span></div></a>{% endfor %}</div>
<h3 style="margin-top:22px">Taxi | Bus | Train | Flight in {{ data.city }}</h3><div class="grid4">{% for t in data.transport %}<a href="/book?type={{ t.type }}&city={{ data.city }}&name={{ t.name }}&price={{ t.price }}&img={{ t.img }}" class="h-card"><img src="{{ t.img }}"><div><b>{{ t.icon }} {{ t.name }}</b><br>Rs.{{ t.price }} {{ t.unit }}<br><span class="book-btn">Book</span></div></a>{% endfor %}</div>
<h3 style="margin-top:22px">Food in {{ data.city }}</h3><div class="grid4">{% for f in data.food %}<a href="/book?type=food&city={{ data.city }}&name={{ f.name }}&price={{ f.price }}&img={{ f.img }}" class="h-card"><img src="{{ f.img }}"><div><b>{{ f.name }}</b><br>Rs.{{ f.price }} {{ f.rating }}<br><span class="book-btn">Order</span></div></a>{% endfor %}</div>
<h3 style="margin-top:22px">Live Map - {{ data.city }}</h3><div class="map-box" id="map-en"><iframe width="100%" height="340" style="border:0" loading="lazy" src="https://www.google.com/maps?q={{ data.city }}&z=10&output=embed"></iframe></div><div class="map-box" id="map-hi" style="display:none"><iframe width="100%" height="340" style="border:0" loading="lazy" src="https://www.google.com/maps?q={{ data.city }}&hl=hi&z=10&output=embed"></iframe></div>
<div class="grid2" style="margin-top:18px">
<div><h3>Video - {{ data.city }}</h3><div class="search-box"><input id="videoSearch" type="text" placeholder="Ex: Goa beach video..." value="{{ data.city }}"><button onclick="searchVideoChrome()">Search Video</button></div><div class="map-box"><iframe width="100%" height="280" src="{{ data.video }}" frameborder="0" allowfullscreen></iframe></div></div>
<div><h3>Gallery - {{ data.city }}</h3><div class="search-box"><input id="gallerySearch" type="text" placeholder="Ex: gateway photo..." value="{{ data.city }}"><button onclick="searchGalleryChrome()">Search Photo</button></div><div style="display:grid;grid-template-columns:1fr 1fr;gap:10px">{% for img in data.gallery %}<img class="gal-img" src="{{ img }}" style="width:100%;height:135px;border-radius:14px;object-fit:cover;border:2px solid #eee" onerror="this.src='https://images.unsplash.com/photo-1523906834658-6e24ef2386f9?w=400'">{% endfor %}</div></div>
</div>
<h3 style="margin-top:18px">Pro Tools - Click karke use karo</h3>
<div style="display:flex;flex-wrap:wrap;gap:6px">
<button class="tool" onclick="downloadPDF()">PDF</button>
<button class="tool" onclick="openModal('qrModal')">QR</button>
<button class="tool" onclick="openModal('walletModal')">Wallet</button>
<button class="tool" onclick="openModal('emiModal')">EMI</button>
<button class="tool" id="likeBtn" onclick="likeTrip()">{{ likes_count }} Likes</button>
<button class="tool" onclick="openModal('cardModal')">Travel Card</button>
<a href=https://wa.me/?text={{ data.wa_text }} target="_blank" style="text-decoration:none"><button class="tool">WhatsApp</button></a>
</div>
</div>{% endif %}
<div class="card" style="text-align:center;background:#000;color:#fff"><div style="color:#FFD700;font-weight:800">TOUR WORLD</div><div style="font-size:11px;opacity:0.7">By Riya Yadav</div></div></div>
<div id="qrModal" class="modal"><div class="modal-content"><span class="close" onclick="closeModal('qrModal')">&times;</span><h3>Your Trip QR Code</h3>{% if data %}<img src="https://api.qrserver.com/v1/create-qr-code/?size=250x250&data={{ data.wa_text }}" style="border-radius:12px"><p style="font-size:12px">{{ data.city }} - {{ data.days }} Days - Rs.{{ data.total_cost }}</p>{% endif %}</div></div>
<div id="walletModal" class="modal"><div class="modal-content"><span class="close" onclick="closeModal('walletModal')">&times;</span><h3>My Wallet</h3><div style="background:#fffbe6;border:2px dashed #FFD700;border-radius:14px;padding:15px;margin:10px 0"><h2 style="margin:0">Rs. 12,500</h2><p style="margin:5px 0;font-size:12px">Available Balance</p></div><button class="tool" style="background:#000;color:#FFD700" onclick="closeModal('walletModal')">Close</button></div></div>
<div id="emiModal" class="modal"><div class="modal-content"><span class="close" onclick="closeModal('emiModal')">&times;</span><h3>EMI Calculator</h3>{% if data %}<div style="background:#f5f5f7;border-radius:12px;padding:12px;text-align:left;font-size:13px"><p>Total: <b>Rs.{{ data.total_cost }}</b></p><p>3 Months EMI: <b>Rs.{{ (data.total_cost//3) }}</b>/mo</p><p>6 Months EMI: <b>Rs.{{ (data.total_cost//6) }}</b>/mo</p><p>12 Months EMI: <b>Rs.{{ (data.total_cost//12) }}</b>/mo</p></div>{% endif %}<button class="tool" style="background:#000;color:#FFD700;margin-top:10px" onclick="closeModal('emiModal')">Close</button></div></div>
<div id="cardModal" class="modal"><div class="modal-content" style="background:#000;color:#fff"><span class="close" onclick="closeModal('cardModal')" style="color:#FFD700">&times;</span><h3 style="color:#FFD700">TOUR WORLD Travel Card</h3><div style="border:2px solid #FFD700;border-radius:16px;padding:15px;margin:10px 0"><p>Name: {{ user }}</p><p>Card No: TW{{ likes_count }}9852</p><p>Valid: 12/28</p><p style="color:#FFD700">Premium Member</p></div><button class="tool" style="background:#FFD700;color:#000" onclick="closeModal('cardModal')">Close</button></div></div>
</body></html>
"""

ADMIN_HTML = """<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width, initial-scale=1"><title>Admin</title><style>body{font-family:sans-serif;padding:20px;background:#f5f5f7}.card{background:#fff;border-radius:20px;padding:20px;margin:15px 0}</style></head><body><h2>Admin Panel - TOUR WORLD</h2><div class="card"><h3>Users ({{ users|length }})</h3>{% for u,p in users.items() %}<div style="padding:8px;border-bottom:1px solid #eee"><b>{{ u }}</b> - {{ p }}</div>{% endfor %}</div><div class="card"><h3>Bookings: {{ bookings|length }} | Likes: {{ likes }}</h3>{% for b in bookings %}<div style="padding:8px;border-bottom:1px solid #eee">{{ b }}</div>{% endfor %}</div><a href="/" style="background:#000;color:#FFD700;padding:10px 20px;border-radius:20px;text-decoration:none">Home</a></body></html>"""
BOOK_HTML = """<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width, initial-scale=1"><title>Book</title><style>*{font-family:sans-serif;box-sizing:border-box}body{margin:0;background:#f5f5f7;padding:20px}.card{max-width:500px;margin:0 auto;background:#fff;border-radius:24px;overflow:hidden}.card img{width:100%;height:220px;object-fit:cover}.info{padding:22px}.pay-btn{width:100%;padding:16px;border-radius:14px;border:none;font-weight:700;margin:8px 0;display:block;text-align:center;text-decoration:none}.upi{background:#000;color:#FFD700}.card-pay{background:#FFD700;color:#000}.wallet{background:#fff;border:2px solid #000;color:#000}</style></head><body><div class="card"><img src="{{ img }}"><div class="info"><h2 style="margin:0">{{ name }}</h2><p>{{ city }} | Rs.{{ price }}</p><a href="/pay?city={{ city }}&name={{ name }}&price={{ price }}&method=UPI" class="pay-btn upi">UPI Pay</a><a href="/pay?city={{ city }}&name={{ name }}&price={{ price }}&method=Card" class="pay-btn card-pay">Card Pay</a><a href="/pay?city={{ city }}&name={{ name }}&price={{ price }}&method=Wallet" class="pay-btn wallet">Wallet + Net Banking</a><div style="text-align:center;margin-top:15px"><a href="/">Back</a></div></div></div></body></html>"""
PAY_HTML = """<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width, initial-scale=1"><title>Success</title><style>*{font-family:sans-serif}body{margin:0;background:#000;display:flex;justify-content:center;align-items:center;min-height:100vh;padding:20px}.box{background:#fff;border-radius:24px;padding:35px;text-align:center;max-width:400px;width:100%}.tick{width:70px;height:70px;background:#000;color:#FFD700;border-radius:50%;display:flex;justify-content:center;align-items:center;font-size:35px;margin:0 auto 15px auto}</style></head><body><div class="box"><div class="tick">✓</div><h2>Payment Successful!</h2><p>{{ name }}<br>{{ city }}<br><b>Rs.{{ price }}</b> via {{ method }}</p><div style="background:#fffbe6;border:2px dashed #FFD700;border-radius:14px;padding:12px;margin:15px 0">Booking ID: <b>TW{{ booking_id }}</b></div><a href="/" style="background:#000;color:#FFD700;padding:12px 24px;border-radius:20px;text-decoration:none">Back to Home</a></div></body></html>"""

def get_dynamic_data(city):
    hotels = [
        {"name": f"{city} Grand 5 Star", "price": 4500, "rating": "4.8", "img": "https://images.unsplash.com/photo-1566073771259-6a8506099945?w=400"},
        {"name": f"{city} Beach Resort", "price": 3800, "rating": "4.7", "img": "https://images.unsplash.com/photo-1551882547-b79e2ba5e482?w=400"},
        {"name": f"{city} City Inn", "price": 2500, "rating": "4.5", "img": "https://images.unsplash.com/photo-1520250497591-112f2f40a3f4?w=400"},
        {"name": f"{city} Luxury Villa", "price": 6000, "rating": "4.9", "img": "https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?w=400"},
    ]
    transport = [
        {"type":"taxi", "icon":"Taxi", "name": f"{city} City Taxi", "price": 12, "unit": "/km", "img": "https://images.unsplash.com/photo-1449965408869-eaa3f722e40d?w=400"},
        {"type":"bus", "icon":"Bus", "name": f"{city} Volvo Bus", "price": 500, "unit": "Ticket", "img": "https://images.unsplash.com/photo-1544620347-c4fd4a3d5957?w=400"},
        {"type":"train", "icon":"Train", "name": f"{city} Express", "price": 800, "unit": "Ticket", "img": "https://images.unsplash.com/photo-1474487548417-4a6c2f1c1d45?w=400"},
        {"type":"flight", "icon":"Flight", "name": f"{city} Flight", "price": 3500, "unit": "Ticket", "img": "https://images.unsplash.com/photo-1436491865332-7a61a109cc05?w=400"},
    ]
    food = [
        {"name": f"{city} Fine Dining", "price": 1200, "rating":"4.8", "img":"https://images.unsplash.com/photo-1414235077428-338989a2e8c0?w=400"},
        {"name": f"{city} Street Food", "price": 400, "rating":"4.6", "img":"https://images.unsplash.com/photo-1555396273-367ea4eb4db5?w=400"},
        {"name": f"{city} Cafe", "price": 600, "rating":"4.7", "img":"https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=400"},
        {"name": f"{city} Lounge", "price": 900, "rating":"4.5", "img":"https://images.unsplash.com/photo-1559339352-11d035aa65de?w=400"},
    ]
    return hotels, transport, food

def get_plan(city, days):
    days=int(days); city_lower=city.lower().strip(); city_title=city.title()
    famous=FAMOUS_PLACES.get(city_lower, [f"{city_title} Grand Palace", f"{city_title} Main Beach", f"{city_title} Old Market", f"{city_title} Temple", f"{city_title} Museum"])
    plan=[]
    for i in range(days):
        place=famous[i % len(famous)]
        if i==0: plan.append(f"Arrival + Check-in + Visit {place} in {city_title}")
        elif i==days-1: plan.append(f"Morning at {place} + Shopping + Farewell in {city_title}")
        else: plan.append(f"Explore: {place} + Local Food in {city_title}")
    cost=days*4800; hotels,transport,food=get_dynamic_data(city_title)
    vid=VIDEO_MAP.get(city_lower, VIDEO_MAP["default"])
    video=f"https://www.youtube-nocookie.com/embed/{vid}?rel=0"
    ts=int(time.time())
    gallery=[
        f"https://picsum.photos/seed/{city_lower}1{ts}/400/300",
        f"https://picsum.photos/seed/{city_lower}2{ts}/400/300",
        f"https://picsum.photos/seed/{city_lower}3{ts}/400/300",
        f"https://picsum.photos/seed/{city_lower}4{ts}/400/300"
    ]
    wa=urllib.parse.quote(f"Trip to {city_title} Rs.{cost}")
    return {"city":city_title,"days":days,"plan":plan,"famous":famous,"total_cost":cost,"emi":cost//days,"wa_text":wa,"hotels":hotels,"transport":transport,"food":food,"video":video,"gallery":gallery}

@app.route('/', methods=['GET','POST'])
def home():
    if 'user' not in session: return render_template_string(AUTH_HTML)
    data=None
    if request.method=='POST' and 'city' in request.form:
        data=get_plan(request.form.get('city'), request.form.get('days','3')); session['last_plan']=data
    return render_template_string(HOME_HTML, data=session.get('last_plan') if request.method=='GET' else data, user=session.get('user'), likes_count=likes["count"])
@app.route('/admin')
def admin():
    if 'user' not in session: return redirect('/')
    return render_template_string(ADMIN_HTML, users=registered_users, likes=likes["count"], bookings=bookings)
@app.route('/book')
def book(): return render_template_string(BOOK_HTML, city=request.args.get('city',''), name=request.args.get('name',''), price=request.args.get('price',''), img=request.args.get('img',''))
@app.route('/pay')
def pay():
    city=request.args.get('city'); name=request.args.get('name'); price=request.args.get('price'); method=request.args.get('method')
    bookings.append(f"{name} | {city} | Rs.{price} | {method}")
    return render_template_string(PAY_HTML, city=city, name=name, price=price, method=method, booking_id=random.randint(10000,99999))
@app.route('/thumbs_api')
def thumbs_api():
    likes["count"]+=1
    return jsonify({"count": likes["count"]})
@app.route('/login', methods=['POST'])
def login():
    u=request.form.get('username'); p=request.form.get('password')
    if u=="admin" and p=="admin123": session['user']=u; return redirect('/admin')
    if u in registered_users and registered_users[u]==p: session['user']=u; return redirect('/')
    return render_template_string(AUTH_HTML)
@app.route('/register', methods=['POST'])
def register():
    u=request.form.get('username'); p=request.form.get('password'); registered_users[u]=p; session['user']=u; return redirect('/')
@app.route('/logout')
def logout(): session.clear(); return redirect('/')
@app.route('/thumbs')
def thumbs(): likes["count"]+=1; return redirect('/')

if __name__=='__main__': app.run(host='0.0.0.0', port=5000, debug=True)

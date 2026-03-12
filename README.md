# 🏠 Startpage

A personal browser start page featuring a clock, weather widget, quick links, task list, and Google Tasks integration. All settings are stored in the user's browser (localStorage / IndexedDB) — the server holds no personal data, so every visitor gets their own independent configuration.

---

## ✨ Features

- **Clock & Date** — large, clean digital clock with localized date
- **Search Bar** — switch between Google, DuckDuckGo, Brave, Bing and AI engines (ChatGPT, Claude, Gemini); search history and autocomplete
- **Quick Links** — fully customizable; add and remove links from settings
- **Task List** — local tasks + Google Tasks OAuth sync with an instant ↻ refresh button
- **Weather Widget** — powered by [Open-Meteo](https://open-meteo.com) (no API key required); auto-location, city search, °C/°F toggle
- **Background** — 8 gradient presets, remote URL, or upload a file from your computer (stored in IndexedDB)
- **Language** — Turkish / English
- **Per-user settings** — stored entirely in each visitor's browser; multiple users on the same URL never share settings

---

## 📁 Repository Structure

```
startpage/
├── index.html          # The page itself (all HTML/CSS/JS in one file)
├── server.py           # Python 3.13+ compatible static file server
├── Dockerfile          # Docker image definition
├── nginx.conf.sample   # SWAG (nginx) reverse proxy config sample
└── .gitignore
```

---

## 🚀 Installation

### Option 1 — Local (Systemd)

```bash
# Copy files
mkdir -p ~/dev/web
cp index.html server.py ~/dev/web/

# Test
python3 ~/dev/web/server.py
# → http://localhost:8080
```

**Run automatically on boot with systemd:**

```ini
# /etc/systemd/system/startpage.service
[Unit]
Description=Startpage Local Server
After=network.target

[Service]
ExecStart=python3 /home/YOUR_USER/dev/web/server.py
WorkingDirectory=/home/YOUR_USER/dev/web
Restart=always
User=YOUR_USER

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now startpage
```

Set your browser's start page to `http://localhost:8080`.

---

### Option 2 — Docker + SWAG (Recommended)

#### Requirements

- Docker & Docker Compose
- [SWAG](https://docs.linuxserver.io/general/swag) reverse proxy (LinuxServer.io)
- A domain with Cloudflare DNS (or any supported DNS provider)

#### Steps

**a) Copy files to the server:**

```bash
mkdir -p /opt/docker/startpage
cp index.html server.py Dockerfile /opt/docker/startpage/
```

**b) Add the service to your `docker-compose.yml`:**

```yaml
services:
  startpage:
    build: /opt/docker/startpage
    container_name: startpage
    restart: unless-stopped
    networks:
      - your_network   # replace with your actual network name

networks:
  your_network:
    external: true
```

**c) Add the SWAG nginx config:**

Copy `nginx.conf.sample` to SWAG's proxy-confs directory and update the domain:

```bash
cp nginx.conf.sample \
  /opt/docker/appdata/swag/nginx/proxy-confs/start.yourdomain.com.conf
```

Edit the file and make sure `server_name` uses the wildcard format:

```nginx
server_name start.*;
```

> **Why wildcard?** Using `start.*` instead of the full domain means your existing wildcard
> certificate automatically covers this subdomain — no extra certificate needed.

**d) Start the container and reload nginx:**

```bash
docker compose up -d --build startpage
docker exec swag nginx -s reload
```

---

## 🔑 Google Tasks Integration

Google Tasks sync requires an OAuth 2.0 Client ID. It's completely free.

### Google Cloud Console Setup

1. Go to [console.cloud.google.com](https://console.cloud.google.com)
2. Create a new project
3. **APIs & Services → Enable APIs** → enable **Tasks API**
4. **Credentials → Create Credentials → OAuth 2.0 Client ID**
5. Application type: **Web application**
6. Authorized JavaScript origins:
   ```
   https://start.yourdomain.com
   ```
7. Authorized redirect URIs:
   ```
   https://start.yourdomain.com
   ```
8. **OAuth consent screen → Test users** → add your Gmail address

### Connecting on the Page

1. Click ⚙️ in the bottom-right corner → **Tasks** tab
2. Paste your Client ID → **Save**
3. Click **Connect with Google**
4. Select your account and grant permission
5. Tasks are loaded automatically

---

## 🖥️ KDE Plasma Desktop Wallpaper

You can use the page as a live wallpaper on KDE Wayland.

### Required Plugin

[de.unkn0wn.htmlwallpaper](https://store.kde.org/p/1478385) — download from KDE Store or search "HTML Wallpaper" in Plasma Discover.

### Setup

Install the plugin, then replace the `main.qml` file with the customized version below. This version opens external links (search results, quick links) in your default browser while keeping the OAuth flow inside the wallpaper view.

**File path:**
`~/.local/share/plasma/wallpapers/de.unkn0wn.htmlwallpaper/contents/ui/main.qml`

```qml
import QtQuick 2
import QtWebEngine 1.7
import org.kde.plasma.plasmoid

WallpaperItem {
    WebEngineView {
        anchors.fill: parent
        url: wallpaper.configuration.DisplayPage
        zoomFactor: wallpaper.configuration.ZoomFactor
        backgroundColor: "black"

        onCertificateError: function (error) {
            if (wallpaper.configuration.InsecureHTTPS) {
                error.acceptCertificate()
            } else {
                error.rejectCertificate()
            }
        }

        onNavigationRequested: function (request) {
            var targetUrl = request.url.toString()
            var homeUrl = wallpaper.configuration.DisplayPage.toString()
            var homeOrigin = homeUrl.split("/").slice(0, 3).join("/")

            // Keep startpage and Google OAuth inside the wallpaper view
            if (targetUrl.indexOf(homeOrigin) === 0 ||
                targetUrl.indexOf("accounts.google.com") !== -1 ||
                targetUrl.indexOf("google.com/o/oauth2") !== -1) {
                request.action = WebEngineNavigationRequest.AcceptRequest
                return
            }

            // Open everything else in the default browser
            Qt.openUrlExternally(request.url)
            request.action = WebEngineNavigationRequest.IgnoreRequest
        }

        settings.playbackRequiresUserGesture: false
    }
}
```

```bash
plasmashell --replace &
```

Right-click the desktop → **Configure Desktop** → Wallpaper Type: **HTML Wallpaper** → URL: `https://start.yourdomain.com`

---

## ⚙️ Settings Reference

Click ⚙️ in the bottom-right corner to open the settings panel.

| Tab | Contents |
|-----|----------|
| 🎨 Background | Gradient presets, remote URL, file upload |
| 🔍 Search | Default search engine |
| 🔗 Links | Add / remove quick links |
| ✅ Tasks | Google Tasks OAuth Client ID |
| 🌤 Weather | City, auto-location, °C/°F |
| 🌐 Language | Turkish / English |

---

## 🔒 Privacy

- The server **stores no user data whatsoever**
- All settings, tasks, and background images are stored in **the user's own browser**
- Different users visiting the same URL have completely independent configurations
- Google Tasks sync connects directly from the browser to the Google API — no server-side token handling

---

## 🛠️ Technical Stack

| Component | Technology |
|-----------|------------|
| Frontend | Vanilla HTML / CSS / JS (zero dependencies) |
| Server | Python 3.13+ `http.server` |
| Background image | IndexedDB (browser-side, GB-scale storage) |
| Settings | localStorage |
| Weather | [Open-Meteo](https://open-meteo.com) (free, no API key) |
| Geocoding | [Nominatim](https://nominatim.org) (OpenStreetMap) |
| Google Tasks | OAuth 2.0 implicit flow |

---

## 📄 License

MIT
# startpage

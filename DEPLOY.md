# ProjectFlow Pro — PWA Deployment Guide

## Files in this package
```
projectflow-pro/
├── index.html        ← Main app (open this in browser)
├── manifest.json     ← PWA manifest (icons, name, theme)
├── sw.js             ← Service worker (offline + caching)
├── icons/            ← App icons (all sizes)
│   ├── icon-72.png
│   ├── icon-96.png
│   ├── icon-128.png
│   ├── icon-144.png
│   ├── icon-152.png
│   ├── icon-192.png
│   ├── icon-384.png
│   └── icon-512.png
└── DEPLOY.md         ← This file
```

---

## Option A — Deploy to Netlify (Free, 2 minutes)
1. Go to https://netlify.com → "Add new site" → "Deploy manually"
2. Drag the entire `projectflow-pro/` folder into the Netlify drop zone
3. Your app is live at `https://yoursite.netlify.app`
4. On Android: open Chrome → tap menu → "Add to Home screen"
5. On iOS: open Safari → tap Share → "Add to Home Screen"

## Option B — Deploy to GitHub Pages
```bash
git init
git add .
git commit -m "ProjectFlow Pro PWA"
gh repo create projectflow-pro --public --push --source=.
# Enable Pages: Settings → Pages → Branch: main → /root
```

## Option C — Local / LAN (for testing)
```bash
# Python
python3 -m http.server 8080

# Node.js
npx serve . -p 8080

# Then open: http://localhost:8080
```
⚠️ Service workers require HTTPS or localhost. LAN IP won't trigger install prompt.

---

## Installing on Android
1. Open the deployed URL in **Chrome**
2. Wait 3 seconds → tap **"Install"** on the banner
   OR tap Chrome menu (⋮) → "Add to Home screen"
3. Confirm → app icon appears on home screen
4. Launch like a native app — full screen, offline capable

## Installing on iOS (iPhone/iPad)
1. Open in **Safari** (must be Safari for PWA install)
2. Tap the **Share** button (box with arrow)
3. Scroll down → tap **"Add to Home Screen"**
4. Tap "Add" → icon appears on home screen

---

## PWA Features Included
- ✅ Offline support (app shell cached by service worker)
- ✅ Install to home screen (Android + iOS)
- ✅ Full-screen standalone mode (no browser chrome)
- ✅ App icon (all sizes: 72–512px)
- ✅ Splash screen on launch
- ✅ Offline indicator bar
- ✅ Auto-update detection banner
- ✅ URL hash routing (for app shortcuts)
- ✅ Push notification support (ready for backend)
- ✅ Background sync (ready for backend)
- ✅ Safe area insets (notched phone support)

---

## Connecting to CGate Backend
Replace the in-memory `store` in `index.html` with API calls:

```js
// Example: fetch projects from your Node.js/Express API
async function loadProjects() {
  const res = await fetch('https://your-cgate-api.com/api/projects', {
    headers: { Authorization: 'Bearer ' + getToken() }
  });
  store.projects = await res.json();
  renderProjects();
}
```


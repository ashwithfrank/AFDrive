# AFDrive

**Your Personal Cloud. Your Phone. Your Files.**

AFDrive is a lightweight, self-hosted personal cloud storage web app. It's
designed to run on an old Android phone through [Termux](https://termux.dev/),
turning that phone into your own private file server — accessible from your
laptop, tablet, or any other device on the same Wi-Fi network, entirely
without the internet or any third-party cloud service.

- Flask + SQLite backend, vanilla HTML/CSS/JS frontend — no Node.js, no build
  step, no heavy frameworks.
- Files stay on the phone's filesystem. Only account info lives in SQLite.
- Login-protected, with directory-traversal-safe file handling, streamed
  uploads/downloads, and no debug mode in production.
- Mobile-first responsive UI with light/dark mode.

---

## 1. Project structure

```
AFDrive/
├── app.py                 # Flask app: routes, auth, API endpoints
├── config.py               # All configuration, read from environment/.env
├── database.py              # SQLite setup + account verification
├── fs_utils.py              # Safe path handling, listing, search, formatting
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
├── instance/                # Auto-created; holds the generated secret key
├── storage/
│   └── user_files/          # <-- your actual files live here
├── templates/
│   ├── base.html
│   ├── login.html
│   ├── dashboard.html
│   ├── files.html           # file/folder listing, included by dashboard.html
│   └── error.html
└── static/
    ├── css/style.css
    └── js/app.js
```

### A note on the architecture

- **No files are ever stored in SQLite.** The database only holds the
  account (username + password hash). File and folder listings, sizes, and
  modified dates are all read live from the filesystem — this keeps things
  simple and means the app can never show a listing that's out of sync with
  what's actually on disk.
- **All file access goes through `fs_utils.safe_join_storage()`**, which
  resolves every user-supplied path against the storage root and rejects
  anything that would escape it (via `../`, absolute paths, or symlink
  tricks). This is the core security boundary of the whole app.
- The dashboard and the file manager are the same page (`dashboard.html`,
  which includes `files.html` for the listing). Navigating into a folder
  is just a normal link to `/files/<path>` — no client-side routing needed.

---

## 2. Termux setup (Android)

### Step 1 — Install Termux

Install Termux from [F-Droid](https://f-droid.org/packages/com.termux/)
(recommended) or GitHub releases. Avoid the old Play Store build, which is
no longer updated.

### Step 2 — Update packages and install Python

Open Termux and run:

```bash
pkg update
pkg upgrade
pkg install python
```

### Step 3 — Give Termux storage access (optional, only if you want to store
files outside Termux's private folder, e.g. on shared phone storage)

```bash
termux-setup-storage
```

Grant the permission when Android prompts you. This creates a
`~/storage/shared` symlink you can point `AFDRIVE_STORAGE_PATH` at later if
you want your files visible to other Android apps too.

### Step 4 — Get the project onto your phone

Copy the `AFDrive` folder onto your phone (e.g. via `git clone`, a USB
transfer, or Termux's storage access), then:

```bash
cd ~
cd afdrive    # or wherever you placed the AFDrive folder
```

### Step 5 — Install dependencies

```bash
pip install -r requirements.txt
```

### Step 6 — Configure your account

```bash
cp .env.example .env
```

Edit `.env` (e.g. with `nano .env`) and set:

```
AFDRIVE_USERNAME=your_username
AFDRIVE_PASSWORD=your_strong_password
```

This password is only used the **first time** the app starts (when the
database doesn't have an account yet). Pick a real password before that
first run — the default `changeme123` is not safe to leave in place.

### Step 7 — Run the server

```bash
python app.py
```

You should see Flask start up and listen on `0.0.0.0:5000`. Leave this
terminal session running — closing Termux (or letting Android kill it in
the background) stops the server. For longer-running use, consider
Termux's wake lock (`termux-wake-lock`) and/or running inside a Termux
`tmux`/`screen` session so it survives you switching apps.

### Step 8 — Find your phone's local IP address

In Termux:

```bash
ip addr show wlan0 | grep 'inet '
```

Look for something like `inet 192.168.1.42/24` — `192.168.1.42` is your
phone's local IP address.

### Step 9 — Access AFDrive from another device

On any other device connected to the **same Wi-Fi network**, open a
browser and go to:

```
http://PHONE_IP:5000
```

For example: `http://192.168.1.42:5000`

Log in with the username/password you set in `.env`.

### Stopping the server

Back in the Termux session running the app, press `Ctrl + C`.

---

## 3. Running on a desktop/laptop (for development or testing)

The exact same steps work on any machine with Python 3 installed:

```bash
python3 -m venv venv
source venv/bin/activate      # on Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env           # then edit it
python app.py
```

Visit `http://localhost:5000` (or `http://127.0.0.1:5000`).

---

## 4. Configuration reference

All configuration is read from environment variables (or `.env`). See
`.env.example` for the full list with explanations. Key ones:

| Variable | Purpose | Default |
|---|---|---|
| `AFDRIVE_USERNAME` | Initial account username | `admin` |
| `AFDRIVE_PASSWORD` | Initial account password (first run only) | `changeme123` |
| `AFDRIVE_STORAGE_PATH` | Where files are stored on disk | `./storage/user_files` |
| `AFDRIVE_MAX_UPLOAD_SIZE` | Max upload size, in bytes | `2147483648` (2 GB) |
| `AFDRIVE_HOST` | Bind address | `0.0.0.0` |
| `AFDRIVE_PORT` | Bind port | `5000` |
| `AFDRIVE_DEBUG` | Flask debug mode — **keep `false`** | `false` |
| `AFDRIVE_SECRET_KEY` | Session signing key | auto-generated & persisted |
| `AFDRIVE_FORCE_HTTPS` | Mark session cookies secure-only | `false` |
| `AFDRIVE_SESSION_DAYS` | Login session lifetime | `7` |

**Changing your password after first run:** stop the server, delete
`database.db`, set a new `AFDRIVE_PASSWORD` in `.env`, and start the server
again. (A proper in-app "change password" screen is a natural addition —
see Future Features below.)

---

## 5. Security notes

- Passwords are hashed with Werkzeug's `generate_password_hash` — never
  stored in plain text.
- Every filesystem path derived from user input (uploads, downloads,
  renames, folder creation, deletion, previews) is resolved through
  `fs_utils.safe_join_storage()`, which blocks `../` traversal, absolute
  paths, null bytes, and symlink escapes.
- Uploaded files are saved with `0o644` permissions (never executable) and
  are never written into the app's source/template/static directories.
- Filenames are sanitized (via `werkzeug.utils.secure_filename` plus
  AFDrive's own stricter pass) and de-duplicated automatically — an
  upload named `notes.pdf` that already exists becomes `notes (1).pdf`
  rather than silently overwriting the original.
- Downloads are streamed via Flask's `send_file` with conditional/range
  support, so large files are never fully loaded into RAM.
- Flask's debug mode is **off by default** and only turns on if you
  explicitly set `AFDRIVE_DEBUG=true` — don't do that outside local
  development, since it would expose an interactive debugger.
- Basic security headers (`X-Content-Type-Options`, `X-Frame-Options`,
  a restrictive `Content-Security-Policy`, etc.) are set on every response.
- This app is built for **trusted local-network use** (you and people you
  personally let onto your Wi-Fi). It is not hardened for direct exposure
  to the public internet — don't port-forward it without adding a VPN or
  reverse proxy with its own auth/TLS in front.

---

## 6. Feature overview

- **Auth:** login/logout, hashed passwords, protected routes, generic
  "invalid username or password" errors (no user enumeration).
- **Dashboard:** total storage used, files/folders counts, available disk
  space (via `shutil.disk_usage`, standard library only), recent files.
- **File manager:** browse folders, breadcrumbs, create/rename/delete
  files and folders, sort by name/size/date, recursive search.
- **Upload:** multi-file upload with a live progress bar, drag-and-drop
  onto the file list, duplicate-safe naming, traversal-safe filenames.
- **Download:** streamed, correct filename, safe against manipulated URLs.
- **Preview:** images and text files preview inline; PDFs open in an
  embedded viewer; anything else shows "File preview unavailable" with a
  direct download button.
- **UI:** mobile-first responsive layout, light/dark theme (remembered via
  `localStorage`), touch-friendly action menus, toast notifications for
  every action instead of browser `alert()`.

---

## 7. Future features (not implemented in this version)

The codebase is intentionally modular (`fs_utils.py` for filesystem logic,
`database.py` for accounts, `config.py` for settings) so these can be added
later without a rewrite:

- Multiple user accounts
- Shareable file links (public/private, expiring)
- QR code sharing
- Trash / recycle bin instead of hard delete
- File version history
- Per-user storage quotas
- WebDAV / FTP / SFTP support
- Secure remote access via VPN/tunnel
- Automatic phone backup
- Native Flutter/desktop clients
- Optional end-to-end encryption for selected files

---

## 8. Testing checklist

Before relying on a deployment, verify:

- [ ] Login and logout work
- [ ] Unauthenticated users are redirected away from dashboard/API routes
- [ ] Dashboard loads with correct storage/file/folder counts
- [ ] Folder creation, navigation, rename, and delete all work
- [ ] Single and multi-file upload work, with duplicate names handled safely
- [ ] Download produces the correct file and filename
- [ ] Search finds files/folders recursively by name
- [ ] Sorting by name/size/date works in both directions
- [ ] Image, text, and PDF previews work; other types show "unavailable"
- [ ] `../../etc/passwd`-style paths are rejected (try it against `/api/download/..%2f..%2fapp.py`)
- [ ] Mobile and desktop layouts both look right
- [ ] Dark mode toggles and persists across reloads
- [ ] The server starts with `debug=False` and never shows a stack trace
- [ ] Another device on the same Wi-Fi can reach `http://PHONE_IP:5000`

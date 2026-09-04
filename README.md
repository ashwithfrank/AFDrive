# AFDrive

**Your Personal Cloud. Your Phone. Your Files.**

AFDrive is a lightweight, self-hosted personal cloud storage web app. It's designed to run on an old Android phone through **Termux**, turning that phone into your own private file server — accessible from your laptop, tablet, or any other device on the same Wi-Fi network, entirely without the internet or any third-party cloud service.

* Flask + SQLite backend, vanilla HTML/CSS/JS frontend — no Node.js, no build step, no heavy frameworks.
* Files stay on the phone's filesystem. Only account information is stored in SQLite.
* Login-protected, with directory-traversal-safe file handling, streamed uploads/downloads, and no debug mode in production.
* Mobile-first responsive UI with light/dark mode.

---

## 1. Project structure

```text
AFDrive/
├── app.py                 # Flask app: routes, auth, API endpoints
├── config.py              # All configuration, read from environment/.env
├── database.py            # SQLite setup + account verification
├── fs_utils.py            # Safe path handling, listing, search, formatting
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
├── instance/              # Auto-created; holds the generated secret key
├── storage/
│   └── user_files/        # <-- your actual files live here
├── templates/
│   ├── base.html
│   ├── login.html
│   ├── dashboard.html
│   ├── files.html         # File/folder listing, included by dashboard.html
│   └── error.html
└── static/
    ├── css/style.css
    └── js/app.js
```

### A note on the architecture

* No files are ever stored in SQLite. The database only holds the account (username + password hash). File and folder listings, sizes, and modified dates are read live from the filesystem — this keeps things simple and means the app can never show a listing that's out of sync with what's actually on disk.
* All file access goes through `fs_utils.safe_join_storage()`, which resolves every user-supplied path against the storage root and rejects anything that would escape it (via `../`, absolute paths, or symlink tricks). This is the core security boundary of the whole app.
* The dashboard and the file manager are the same page (`dashboard.html`, which includes `files.html` for the listing). Navigating into a folder is just a normal link to `/files/<path>` — no client-side routing needed.

---

## 2. Windows installation

AFDrive can be run on Windows for development, testing, or as a local storage server.

### Step 1 — Install Python

Install **Python 3** and make sure Python is available from the command line.

Check:

```bash
python --version
```

### Step 2 — Get the project

Clone the repository:

```bash
git clone https://github.com/ashwithfrank/AFDrive.git
cd AFDrive
```

Or download the repository as a ZIP and extract it.

### Step 3 — Create a virtual environment

```bash
python -m venv venv
```

Activate it:

```bash
venv\Scripts\activate
```

### Step 4 — Install dependencies

```bash
pip install -r requirements.txt
```

### Step 5 — Configure your account

Copy the example environment file:

```bash
copy .env.example .env
```

Edit `.env` and configure your username and password:

```text
AFDRIVE_USERNAME=your_username
AFDRIVE_PASSWORD=your_strong_password
```

### Step 6 — Run AFDrive

```bash
python app.py
```

Open:

```text
http://localhost:5000
```

or:

```text
http://127.0.0.1:5000
```

---

## 3. macOS installation

AFDrive can be run on macOS using Python 3.

### Step 1 — Install Python

Check whether Python 3 is installed:

```bash
python3 --version
```

### Step 2 — Get the project

```bash
git clone https://github.com/ashwithfrank/AFDrive.git
cd AFDrive
```

### Step 3 — Create a virtual environment

```bash
python3 -m venv venv
```

Activate it:

```bash
source venv/bin/activate
```

### Step 4 — Install dependencies

```bash
pip install -r requirements.txt
```

### Step 5 — Configure your account

```bash
cp .env.example .env
```

Edit `.env` and set:

```text
AFDRIVE_USERNAME=your_username
AFDRIVE_PASSWORD=your_strong_password
```

### Step 6 — Run AFDrive

```bash
python app.py
```

Open:

```text
http://localhost:5000
```

---

## 4. Linux installation

AFDrive can be run on most Linux distributions with Python 3.

### Step 1 — Check Python

```bash
python3 --version
```

### Step 2 — Get the project

```bash
git clone https://github.com/ashwithfrank/AFDrive.git
cd AFDrive
```

### Step 3 — Create a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 4 — Install dependencies

```bash
pip install -r requirements.txt
```

### Step 5 — Configure your account

```bash
cp .env.example .env
```

Edit `.env` and set:

```text
AFDRIVE_USERNAME=your_username
AFDRIVE_PASSWORD=your_strong_password
```

### Step 6 — Run AFDrive

```bash
python app.py
```

Open:

```text
http://localhost:5000
```

---

## 5. Termux setup (Android)

The primary target for AFDrive is an old Android phone running **Termux**.

### Step 1 — Install Termux

Install Termux from **F-Droid** or the official GitHub releases.

Avoid the old Play Store build, which is no longer updated.

### Step 2 — Update packages and install Python

Open Termux and run:

```bash
pkg update
pkg upgrade
pkg install python
```

### Step 3 — Give Termux storage access

This is optional if you want to store files outside Termux's private directory, such as Android shared storage.

```bash
termux-setup-storage
```

Grant the permission when Android prompts you.

This creates:

```text
~/storage/shared
```

which can be used as a storage location through `AFDRIVE_STORAGE_PATH`.

### Step 4 — Get the project onto your phone

Clone the repository:

```bash
pkg install git
git clone https://github.com/ashwithfrank/AFDrive.git
cd AFDrive
```

You can also copy the project to the phone using USB or Android file sharing.

### Step 5 — Install dependencies

```bash
pip install -r requirements.txt
```

### Step 6 — Configure your account

Copy the example configuration:

```bash
cp .env.example .env
```

Edit it:

```bash
nano .env
```

Set:

```text
AFDRIVE_USERNAME=your_username
AFDRIVE_PASSWORD=your_strong_password
```

This password is only used the first time the app starts, when the database doesn't already contain an account.

Pick a real, strong password before the first run.

Do not leave the example password such as `changeme123` in place.

### Step 7 — Run the server

```bash
python app.py
```

AFDrive listens on:

```text
0.0.0.0:5000
```

Leave the Termux session running while the server is in use.

### Step 8 — Find your phone's local IP address

In Termux:

```bash
ip addr show wlan0 | grep 'inet '
```

Look for an address similar to:

```text
inet 192.168.1.42/24
```

In this example:

```text
192.168.1.42
```

is the phone's local IP address.

### Step 9 — Access AFDrive from another device

Connect the other device to the same Wi-Fi network.

Open a browser and visit:

```text
http://PHONE_IP:5000
```

For example:

```text
http://192.168.1.42:5000
```

Log in using the AFDrive username and password configured during setup.

### Stopping the server

Return to the Termux session running AFDrive and press:

```text
Ctrl + C
```

---

## 6. Running AFDrive for longer periods

AFDrive is designed to run on an old Android phone as a local storage server.

For longer-running sessions, Android may suspend or terminate background processes depending on the device and its battery-management settings.

You can use Termux's wake lock:

```bash
termux-wake-lock
```

You can also run AFDrive inside a terminal multiplexer such as `tmux` so that the server session can remain available while you switch between Termux sessions.

The server should still be treated as an application running on Android rather than a guaranteed permanent background service.

Future versions may provide a dedicated Android service/controller to make long-running AFDrive storage nodes easier to manage.

---

## 7. Configuration reference

All configuration is read from environment variables or `.env`.

See `.env.example` for the full list and explanations.

| Variable                  | Purpose                                   | Default                      |
| ------------------------- | ----------------------------------------- | ---------------------------- |
| `AFDRIVE_USERNAME`        | Initial account username                  | `admin`                      |
| `AFDRIVE_PASSWORD`        | Initial account password (first run only) | `changeme123`                |
| `AFDRIVE_STORAGE_PATH`    | Where files are stored on disk            | `./storage/user_files`       |
| `AFDRIVE_MAX_UPLOAD_SIZE` | Maximum upload size in bytes              | `2147483648` (2 GB)          |
| `AFDRIVE_HOST`            | Bind address                              | `0.0.0.0`                    |
| `AFDRIVE_PORT`            | Bind port                                 | `5000`                       |
| `AFDRIVE_DEBUG`           | Flask debug mode — keep `false`           | `false`                      |
| `AFDRIVE_SECRET_KEY`      | Session signing key                       | Auto-generated and persisted |
| `AFDRIVE_FORCE_HTTPS`     | Mark session cookies secure-only          | `false`                      |
| `AFDRIVE_SESSION_DAYS`    | Login session lifetime                    | `7`                          |

### Changing your password

The current version initializes the account from `.env` only when the database does not already contain an account.

To reset the account:

1. Stop the server.
2. Delete `database.db`.
3. Set a new `AFDRIVE_PASSWORD` in `.env`.
4. Start AFDrive again.

A proper in-app password-change screen is planned for a future version.

---

## 8. Security notes

* Passwords are hashed with Werkzeug's `generate_password_hash` and are never stored in plain text.
* Every filesystem path derived from user input (uploads, downloads, renames, folder creation, deletion, previews) is resolved through `fs_utils.safe_join_storage()`.
* Path traversal such as `../`, absolute paths, null bytes, and symlink escapes are blocked.
* Uploaded files are saved with `0o644` permissions and are never written into the app's source, template, or static directories.
* Filenames are sanitized using `werkzeug.utils.secure_filename` together with AFDrive's stricter filename handling.
* Duplicate filenames are handled safely. For example, an upload named `notes.pdf` that already exists becomes `notes (1).pdf` rather than silently overwriting the original.
* Downloads are streamed through Flask with conditional/range support so large files are not fully loaded into RAM.
* Flask debug mode is disabled by default.
* Debug mode should never be enabled when AFDrive is being used as a real storage server.
* Basic security headers such as `X-Content-Type-Options`, `X-Frame-Options`, and a restrictive `Content-Security-Policy` are applied to responses.
* AFDrive is currently designed for trusted local-network use. Do not expose the Flask server directly to the public internet without adding an appropriate security layer.

---

## 9. Feature overview

### Authentication

* Login/logout
* Hashed passwords
* Protected routes
* Generic invalid username/password errors to reduce user enumeration

### Dashboard

* Total storage used
* File count
* Folder count
* Available disk space
* Recent files
* Storage usage information

### File manager

* Browse folders
* Breadcrumb navigation
* Create folders
* Rename files and folders
* Delete files and folders
* Sort by name, size, and date
* Recursive file/folder search

### Upload

* Multiple-file upload
* Live upload progress
* Drag-and-drop support
* Duplicate-safe naming
* Traversal-safe filenames

### Download

* Direct file downloads
* Correct filenames
* Streamed downloads
* Protection against manipulated download paths

### Preview

* Inline image previews
* Text-file previews
* Embedded PDF viewer
* Download option for unsupported file types

### User interface

* Mobile-first responsive design
* Desktop support
* Light/dark theme
* Theme preference remembered using `localStorage`
* Touch-friendly action menus
* Toast notifications

---

## 10. Future features

AFDrive is currently focused on becoming a reliable **offline/local personal cloud**.

Planned improvements include:

### Storage management

* Trash / recycle bin instead of immediate permanent deletion
* File version history
* Storage statistics and detailed usage breakdown
* Per-folder storage information
* Better handling of large storage collections

### Faster and more reliable transfers

* Resumable uploads and downloads
* Pause/resume transfers
* Automatic retry for interrupted transfers
* Transfer queue
* Multiple simultaneous transfers
* Improved transfer performance for large files

### Local network features

* Automatic AFDrive server discovery on the local network
* Device pairing
* QR-based device pairing
* Easier connection without manually entering the server IP address
* Connected-device management
* Server status and connection information

### Backup

* Automatic local backups from connected devices
* Scheduled backups
* Selected-folder backup
* Backup history
* Restore functionality

### Compatibility

* WebDAV support
* Native Android client
* Native desktop client
* Improved integration with Android file management

### Security

* In-app password change
* Two-factor authentication
* More granular device authorization
* Optional encryption for selected files

> Remote internet access is not part of the current development focus. It may be reconsidered as a separate future project once the offline AFDrive architecture is mature.

---

## 11. Testing checklist

Before relying on an AFDrive deployment, verify the following:

* [ ] Login and logout work
* [ ] Unauthenticated users cannot access protected dashboard/API routes
* [ ] Dashboard loads with correct storage, file, and folder counts
* [ ] Folder creation, navigation, rename, and delete work
* [ ] Single and multi-file uploads work
* [ ] Duplicate filenames are handled safely
* [ ] Downloads produce the correct file and filename
* [ ] Search finds files and folders recursively
* [ ] Sorting by name, size, and date works in both directions
* [ ] Image, text, and PDF previews work
* [ ] Unsupported file types show the appropriate unavailable message
* [ ] Path traversal attempts are rejected
* [ ] Mobile layout works correctly
* [ ] Desktop layout works correctly
* [ ] Dark mode toggles and persists after reload
* [ ] Server starts with `debug=False`
* [ ] Server errors do not expose stack traces to users
* [ ] Another device on the same Wi-Fi network can reach AFDrive
* [ ] Large files can be downloaded without excessive memory usage

For example, verify that paths such as:

```text
../../etc/passwd
```

cannot be used to access files outside the AFDrive storage directory.

---

## 12. Contributing

Contributions, suggestions, bug reports, and feature ideas are welcome.

If you find a bug or have an idea for improving AFDrive:

1. Check existing issues.
2. Create a new issue with clear details.
3. Explain how to reproduce the problem when reporting a bug.
4. For feature requests, describe the use case and expected behavior.
5. Keep security-related discussions responsible and avoid publicly posting sensitive information.

For larger changes, open an issue first so the proposed design can be discussed before implementation.

---

## 13. License

See the repository's license file for the terms under which AFDrive can be used, modified, and distributed.

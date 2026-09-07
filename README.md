# Split Expenses 💰

A mobile-friendly **Progressive Web App (PWA)** built with Flask for splitting travel, pilgrimage, and group expenses. It features PIN-protected group access, multi-currency support, smart debt settlement calculations, offline PWA support, and responsive 2-column layout.

---

## 🌟 Key Features

- 🔐 **Isolated Groups & PIN Security**: Group creators set a Group Name and PIN. Friends join using the Group Name + PIN. No full user registration required.
- 💵 **Multi-Currency Support**: Support for 15+ global and regional currencies (INR `₹`, USD `$`, EUR `€`, GBP `£`, AED `د.إ`, THB `฿`, etc.).
- 🧮 **Zero-Drift Settlement Engine**: Smart integer cent split algorithm calculates exact minimum transactions to settle all debts without floating-point rounding drift.
- 📱 **Progressive Web App (PWA)**: Installable on Android, iOS, Windows, and macOS with standalone window support and offline caching via Service Worker.
- 🎨 **Modern Touch-Friendly UI**: Premium mobile-first CSS design with 2-column desktop split view, dark theme, and micro-interactions.

---

## 🚀 Quick Start (Local Development)

### 1. Clone & Install Dependencies

```bash
# Navigate to project directory
cd "Split Expenses"

# Install Python dependencies
pip install -r requirements.txt
```

### 2. Generate PWA Icons (Optional)

```bash
python generate_icons.py
```

### 3. Run the App

```bash
python run.py
```

Open [http://localhost:5000](http://localhost:5000) in your browser.

---

## 🌐 Deploying to PythonAnywhere

### 💡 Frequently Asked Questions

#### 1. Can our application easily deploy to PythonAnywhere?
**Yes, 100%!** The application is built using standard Flask + SQLite + WSGI, which is natively supported out-of-the-box by PythonAnywhere without requiring external database servers or complex containers.

#### 2. How long will the domain host stay active?
- **Free Tier (`yourusername.pythonanywhere.com`)**:
  - Remains active for **3 months (90 days)** per renewal.
  - You can extend it indefinitely for **FREE** by clicking the **"Run until 3 months from now"** button on your PythonAnywhere Web Dashboard tab once every 2–3 months. PythonAnywhere will also send an automated email reminder 7 days before expiry.
- **Paid Tier ($5/month)**: Stays active 24/7 forever without requiring renewal clicks, and allows custom domain names (e.g. `www.splitexpenses.com`).

---

### 📋 Step-by-Step Deployment Instructions

#### Step 1: Create a PythonAnywhere Account
1. Go to [www.pythonanywhere.com](https://www.pythonanywhere.com) and register for a free account.
2. Your default domain will be `https://<your-username>.pythonanywhere.com`.

#### Step 2: Upload Project Files
1. Log in to PythonAnywhere, click **Consoles**, and open a **Bash console**.
2. Clone or upload your code to `/home/<your-username>/split-expenses`:
   ```bash
   git clone <your-repo-url> split-expenses
   # OR upload project ZIP via the Files tab and extract it
   ```

#### Step 3: Set Up Virtual Environment & Dependencies
In the Bash console, run:
```bash
# Create Python 3.10 virtual environment
mkvirtualenv splitexp --python=python3.10

# Change directory and install dependencies
cd ~/split-expenses
pip install -r requirements.txt
```

#### Step 4: Configure the Web App
1. Go to the **Web** tab on PythonAnywhere header menu.
2. Click **"Add a new web app"**.
3. Choose **Manual configuration** (do NOT select Flask template wizard), select **Python 3.10**, and finish.
4. Under the **Code** section:
   - **Source code**: `/home/<your-username>/split-expenses`
   - **Working directory**: `/home/<your-username>/split-expenses`
   - **WSGI configuration file**: Click the file link to edit it, replace its contents with the code below, and click **Save**:

   ```python
   import sys
   import os

   # Replace 'yourusername' with your actual PythonAnywhere username
   path = '/home/yourusername/split-expenses'
   if path not in sys.path:
       sys.path.insert(0, path)

   from app import create_app
   application = create_app('production')
   ```

5. Under the **Virtualenv** section:
   - Enter path: `/home/<your-username>/.virtualenvs/splitexp`

6. Under the **Static files** section, add this entry:
   - **URL**: `/static/`
   - **Directory**: `/home/<your-username>/split-expenses/app/static`

7. Under **Security**:
   - Turn on **Force HTTPS** toggle for SSL security.

#### Step 5: Reload and Test
1. Scroll to the top of the **Web** tab and click **Reload <your-username>.pythonanywhere.com**.
2. Open `https://<your-username>.pythonanywhere.com` in your browser!

---

## 🛠️ Project Structure

```
Split Expenses/
├── app/
│   ├── __init__.py          # Flask Application Factory
│   ├── models.py            # SQLAlchemy Models (Group, Member, Expense)
│   ├── routes.py            # Route Handlers (Create, Join, Session Auth, Settlement)
│   ├── settlement.py        # Zero-drift integer cent debt settlement engine
│   ├── static/              # CSS, JS, PWA icons, manifest, service worker
│   └── templates/           # Jinja2 HTML templates (index, join, join_name, group, settlement)
├── config.py                # App Configuration (Dev & Production)
├── run.py                   # Local development server script
├── wsgi.py                  # PythonAnywhere WSGI entry point
├── generate_icons.py        # Script to generate PNG PWA icons
├── requirements.txt         # Dependency declarations
└── tests/                   # Settlement engine unit tests
```

---

## 🧪 Running Unit Tests

```bash
python -m unittest discover tests
```

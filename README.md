# Split Expenses 💰

A mobile-friendly **Progressive Web App (PWA)** built with Flask for splitting travel, pilgrimage, and group expenses. It features PIN-protected group access, multi-currency support, smart debt settlement calculations, expense editing, offline PWA support, and responsive 2-column layout.

---

## 🌟 Key Features

- 🔐 **Isolated Groups & PIN Security**: Group creators set a Group Name and PIN. Friends join using the Group Name + PIN. No full user registration required.
- 👥 **1-Click Interactive Member Join**: Returning group members can simply click their name chip (`[ 👤 Name ✓ ]`) to join without re-typing their name.
- 🛡️ **Cache Prevention & Session Security**: HTTP `no-store` headers, Service Worker dynamic exemptions, and BFCache auto-revalidation prevent stale browser page snapshots when pressing Back after leaving a group.
- 🎨 **Custom Glassmorphism Confirmation Modals**: Dark-mode modal dialog system replacing plain browser popups (`confirm()`) for Leave Group, Delete Group, and Delete Expense actions.
- 💵 **Multi-Currency Support**: Support for 15+ global and regional currencies (INR `₹`, USD `$`, EUR `€`, GBP `£`, AED `د.إ`, THB `฿`, etc.).
- 🧮 **Zero-Drift Settlement Engine**: Smart integer cent split algorithm calculates exact minimum transactions to settle all debts without floating-point rounding drift.
- ✏️ **Edit & Delete Expenses**: Easily edit wrong entries (amount, description, category, payer, split among) with pre-populated inline edit panels.
- 🧹 **Automated TTL & Manual Group Cleanup**: Built-in 30-day/90-day automatic trip data cleanup script ([cleanup.py](file:///c:/Users/Admin/Documents/POC/Split%20Expenses/cleanup.py)) plus instant 1-click cascade deletion.
- 📱 **Progressive Web App (PWA)**: Installable on Android, iOS, Windows, and macOS with standalone window support and offline caching via Service Worker.
- ✨ **Creator Signature**: Styled application signature in global footer ("Created by Prem").

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

## 🌐 Git Deployment to PythonAnywhere Guide

### 💡 Frequently Asked Questions

#### 1. Can our application easily deploy to PythonAnywhere?
**Yes, 100%!** The application is built using standard Flask + SQLite + WSGI, which is natively supported out-of-the-box by PythonAnywhere without requiring external database servers or complex containers.

#### 2. How long will the domain host stay active?
- **Free Tier (`yourusername.pythonanywhere.com`)**:
  - Remains active for **3 months (90 days)** per renewal.
  - You can extend it indefinitely for **FREE** by clicking the **"Run until 3 months from now"** button on your PythonAnywhere Web Dashboard tab once every 2–3 months. PythonAnywhere will also send an automated email reminder 7 days before expiry.
- **Paid Tier ($5/month)**: Stays active 24/7 forever without requiring renewal clicks, and allows custom domain names (e.g. `www.splitexpenses.com`).

---

### 📋 Step-by-Step Git Deployment Walkthrough

#### Step 1: Push Local Code to Git (GitHub / GitLab / Bitbucket)
If you haven't already pushed your code to Git, run these commands in your local project directory:
```bash
# Initialize git repository
git init

# Add all project files
git add .

# Commit changes
git commit -m "Initial commit of Split Expenses PWA"

# Link to your remote repository (replace with your GitHub repo URL)
git remote add origin https://github.com/your-username/split-expenses.git
git branch -M main
git push -u origin main
```

---

#### Step 2: Register on PythonAnywhere
1. Go to [www.pythonanywhere.com](https://www.pythonanywhere.com) and sign up for a free account.
2. Your live application domain will be `https://<your-username>.pythonanywhere.com`.

---

#### Step 3: Clone Repository on PythonAnywhere
1. Log in to PythonAnywhere, click **Consoles**, and open a **Bash console**.
2. Run `git clone` to pull your repository directly into PythonAnywhere:
   ```bash
   git clone https://github.com/your-username/split-expenses.git ~/split-expenses
   ```

---

#### Step 4: Create Virtual Environment & Install Requirements
In the PythonAnywhere Bash console, run:
```bash
# Create Python 3.10 virtual environment
mkvirtualenv splitexp --python=python3.10

# Navigate to application directory
cd ~/split-expenses

# Install dependencies
pip install -r requirements.txt
```

---

#### Step 5: Configure PythonAnywhere Web App
1. Go to the **Web** tab from the top header menu on PythonAnywhere.
2. Click **"Add a new web app"**.
3. Choose **Manual configuration** (do NOT select Flask template wizard), select **Python 3.10**, and finish.
4. Under the **Code** section:
   - **Source code**: `/home/<your-username>/split-expenses`
   - **Working directory**: `/home/<your-username>/split-expenses`
   - **WSGI configuration file**: Click the file link to edit it, replace its contents with the snippet below, and click **Save**:

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
   - Path: `/home/<your-username>/.virtualenvs/splitexp`

6. Under the **Static files** section, add this mapping:
   - **URL**: `/static/`
   - **Directory**: `/home/<your-username>/split-expenses/app/static`

7. Under **Security**:
   - Turn ON **Force HTTPS** for SSL encryption.

---

#### Step 6: Reload and Test Live App
1. Scroll to the top of the **Web** tab and click **Reload <your-username>.pythonanywhere.com**.
2. Open `https://<your-username>.pythonanywhere.com` in your web browser!

---

#### 🔄 How to Deploy Future Code Updates from Git
Whenever you update code locally and push to GitHub (`git push origin main`), update your live app on PythonAnywhere with two simple steps:

1. Open a **Bash Console** on PythonAnywhere and run:
   ```bash
   cd ~/split-expenses
   git pull origin main
   ```
2. Go to the **Web** tab and click **Reload**!

---

## 🧹 Group & Member Cleanup (Manual & Automatic TTL)

### 1. Manual Cleanup (Instant)
- **Dashboard Button**: On the group header, any group member can click **"🗑️ Delete"**.
- **Cascade Purge**: Confirms with a popup modal and permanently purges the Group, all Members, and all Expenses from SQLite instantly via cascade rules.

---

### 2. Automatic TTL Cleanup (30 Days / 90 Days)
The application includes an automated TTL script ([cleanup.py](file:///c:/Users/Admin/Documents/POC/Split%20Expenses/cleanup.py)) to automatically purge inactive groups after your trip is done.

#### Running Cleanup Manually:
```bash
# Delete groups older than 90 days (default: 3 months)
python cleanup.py

# Delete groups older than 30 days (1 month)
python cleanup.py --days 30
```

#### Scheduling Auto-Cleanup on PythonAnywhere:
1. Go to the **Tasks** tab on PythonAnywhere.
2. Under **Scheduled tasks**, set a daily execution command:
   ```bash
   /home/<your-username>/.virtualenvs/splitexp/bin/python /home/<your-username>/split-expenses/cleanup.py --days 90
   ```
3. Set execution time (e.g., `03:00 UTC`). PythonAnywhere will automatically purge expired trip data every day!

---

## 🛠️ Project Structure

```
Split Expenses/
├── app/
│   ├── __init__.py          # Flask Application Factory
│   ├── models.py            # SQLAlchemy Models (Group, Member, Expense, cleanup_expired_groups)
│   ├── routes.py            # Route Handlers (Create, Join, Edit, Delete, Settlement)
│   ├── settlement.py        # Zero-drift integer cent debt settlement engine
│   ├── static/              # CSS, JS, PWA icons, manifest, service worker
│   └── templates/           # Jinja2 HTML templates (index, join, join_name, group, settlement)
├── config.py                # App Configuration (Dev & Production)
├── run.py                   # Local development server script
├── cleanup.py               # Automated TTL Group & Member Cleanup script
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

# fi_bank
A lightweight scraper that mirrors Finansinspektionen’s (FI) bank registry. It cleans and caches official FI pages, fixes links, and generates a sortable banks.html so you can quickly confirm which Swedish banks are legally distinct—helpful for deposit diversification and risk checks.

# 🇸🇪 Introduction: Why Swedish Banks Matter — and Why This Tool Exists

Sweden has one of the oldest and most stable banking traditions in the world.  
The first Swedish bank, **Stockholms Banco**, was founded in 1656 and introduced Europe’s first banknotes.  
Over the centuries, Sweden developed a banking system built on:

- strong regulation  
- conservative lending culture  
- regional savings banks (sparbanker)  
- cooperative member‑owned banks (medlemsbanker)  
- large commercial banks (bankaktiebolag)  

This mix created a uniquely **diverse and resilient financial ecosystem**.

Yet history shows that no banking system is completely immune to stress. Sweden has experienced:

- the **1870s bank failures**  
- the **1920s credit crisis**  
- the **1990s banking collapse**  
- global shocks such as 2008 and 2023  

Each event reinforced a simple truth:

> **Diversification across distinct legal banking entities is one of the strongest protections for depositors.**

However, modern banking brands can be misleading.  
A single legal bank may operate under:

- multiple regional names  
- merged legacy brands  
- marketing identities  
- subsidiaries without their own license  

This makes it difficult for savers to know whether their money is truly spread across **different banks**, or simply different **logos** of the same institution.

---

## 🎯 Why This Instrument Exists

FI’s Företagsregistret already lists Swedish banks as **legally distinct entities**, each with its own organisationsnummer and FI institutnummer.  
In theory, this means:

> **Each entry in FI’s registry represents a separate, distinct bank.**

This tool does **not** reinterpret FI’s data.  
Instead, it provides a **clear, offline‑friendly, human‑readable way** to *confirm* that distinction and understand it more easily.

It helps answer practical questions such as:

- *Are my deposits spread across different banks or just different brands?*  
- *Which institutions share the same FI institutnummer?*  
- *Which banks belong to which category (BANK, MBANK, SPAR)?*  
- *What authorizations does each bank hold?*  
- *How many truly independent banks exist in each category?*

By scraping FI’s Företagsregistret, cleaning the pages, fixing links, and generating a sortable `banks.html`, this tool becomes a practical instrument for:

- **deposit diversification**  
- **risk management**  
- **due diligence**  
- **financial research**  
- **long‑term archival of FI data**

In short:

> **FI defines the distinct banks — this tool helps you verify and understand that distinction quickly and clearly, so you can make safer, more informed decisions about where to keep your money.**

---

## 🔧 Installation

### 1. Install Python
Download Python from the official website:  
https://www.python.org/downloads/

Make sure to enable **“Add Python to PATH”** during installation (Windows).

### 2. Install required packages
Open a terminal and run:

```bash
pip install requests beautifulsoup4

### 3. Download the scraper
Save the script as:

```
fi_banks.py

### 4. Run the scraper
Generate the interactive HTML index:

```bash
python fi_banks.py --html

Or print results to the console:

```bash
python fi_banks.py

---

## 🧭 How the Scraper Works

┌──────────────────────────────────────────────┐
│ 1. Load FI main list pages (BANK/MBANK/SPAR) │
└───────────────┬──────────────────────────────┘
                │
                ▼
      Extract <table id="institut">
                │
                ▼
┌──────────────────────────────────────────────┐
│ 2. Parse each bank entry                     │
│    - Name                                    │
│    - Organisation number                     │
│    - Category                                │
│    - Link to detail page                     │
└───────────────┬──────────────────────────────┘
                │
                ▼
         Fetch detail page
                │
                ▼
      Extract <div class="page">
                │
                ▼
┌──────────────────────────────────────────────┐
│ 3. Clean & normalize                         │
│    - Remove scripts/styles                   │
│    - Fix broken links                        │
│    - Rewrite breadcrumb → ../banks.html      │
│    - Convert all links → original FI site    │
└───────────────┬──────────────────────────────┘
                │
                ▼
           Save to cache/
                │
                ▼
┌──────────────────────────────────────────────┐
│ 4. Generate banks.html                       │
│    - Link to cached files                    │
│    - Auto-fetch missing cache entries        │
│    - Sortable columns                        │
│    - Color-coded categories                  │
│    - Expandable authorizations               │
└──────────────────────────────────────────────┘

This creates a **local mirror** of FI’s bank registry that is:

- fast  
- searchable  
- offline‑friendly  
- self‑healing  

---

## 🏦 What Is FI Institutnummer?

**FI institutnummer** is a unique regulatory identifier assigned by Finansinspektionen to every supervised financial institution.

### It is:
- a **unique ID** per legal entity  
- used internally by FI for supervision  
- stable over time  

### It is *not*:
- organisationsnummer  
- SWIFT/BIC  
- clearing number  
- bankgiro  

### Why it matters

Two banks with the **same institutnummer** are the **same legal entity**, even if:

- they use different brand names  
- they operate in different regions  
- they market themselves separately  

This is essential for diversification because:

> Deposits in the same legal entity share the same risk, regardless of branding.

---

# 🛡️ Practical Guide: Using This Scraper for Risk Diversification

The scraper helps answer the key question:

## **“Are my deposits spread across truly distinct banks?”**

Here’s how to use the output for diversification.

---

## 1. Identify legally distinct banks

Open `banks.html` and sort by:

- **FI institutnummer**  
- **Organisation number**  
- **Category**  

If two banks share the same institutnummer, they are **not distinct**.

---

## 2. Diversify across categories

Each category has different ownership and risk profiles:

### **Bankaktiebolag (BANK)**
- Standard commercial banks  
- Shareholder-owned  
- Often large and diversified  

### **Medlemsbank (MBANK)**
- Member-owned  
- Cooperative structure  
- Typically conservative and smaller  

### **Sparbank (SPAR)**
- Foundation-owned  
- Local/regional focus  
- Often very stable  

Diversifying across categories reduces correlated risk.

---

## 3. Check authorizations (tillstånd)

Each bank’s detail page lists its regulatory permissions, such as:

- deposit-taking  
- lending  
- investment services  
- payment services  
- cross-border operations  

Banks with **fewer authorizations** often have **simpler, lower-risk business models**.

---

## 4. Avoid “brand traps”

Some well-known brands are not separate banks.  
They may be:

- branches  
- marketing names  
- subsidiaries without their own license

# HyperSenseIQ — AI-Powered Subsurface Intelligence Platform

**See beyond the surface.**

[![Live Platform](https://img.shields.io/badge/Platform-Live-brightgreen)](https://niranjanbilgi.github.io/HyperSenseIQ/)
[![Patent](https://img.shields.io/badge/Patent-Applied%20For-blue)]()
[![Version](https://img.shields.io/badge/Version-2.7-teal)]()

> HyperSenseIQ is a physics-first subsurface intelligence platform for the Indian oil and gas sector. It delivers instant reservoir characterisation, EOR screening, pressure transient analysis, drilling physics, water chemistry and field economics — in a unified browser interface. No installation. No login. No black boxes.

---

## 🚀 Live Platform

**[niranjanbilgi.github.io/HyperSenseIQ](https://niranjanbilgi.github.io/HyperSenseIQ/)**

Four synthetic field datasets pre-loaded:
- **Mumbai High North** — Bassein Limestone, offshore carbonate
- **Cambay Basin — Kalol Ss** — Onshore tight sandstone, Gujarat
- **Ankleshwar — Hazad Ss** — Onshore sandstone, sour service
- **Assam — OIL India** — Tipam Sandstone, Upper Assam Basin

---

## 📊 Modules

| Module | What it delivers | Physics basis |
|--------|-----------------|---------------|
| **Well Intelligence** | Pay zone map, STOIIP, porosity, Sw, permeability | Archie equation, Coates-Timur, density-neutron crossplot |
| **EOR Screening** | 8 methods ranked by P_EOR composite score | 6-domain weighted scoring: Physics, Mechanical, Geological, Chemical, Operational, Techno-Economic |
| **Wettability Diagnostic** | W_mod coefficient, oil-wet vs water-wet | API gravity, connate Sw, irreducible Sw |
| **Thief Zone Diagnostic** | k/φ ratio, TZ_pen applied to injection EOR | Permeability-porosity ratio threshold |
| **Conformance Factor** | CF_mod, water-rock chemistry fitness | Formation water ion profile |
| **Decline Curve** | EUR, remaining reserves, PHF | Arps harmonic b=0.5 |
| **India Fiscal Economics** | NPV, IRR, payback — live Brent crude | GoI royalty, OID cess, GST, ONGC/OIL equity |
| **Spectral Intelligence** | SWIR mineralogy, hydrocarbon signatures | 1730nm oil, 1900nm brine, 2200nm+ clay (patented) |
| **Water Chemistry (Live)** | SSI, WFAR, fluid compatibility, scale inhibitor dose | Stiff-Davis 1952, ion balance |
| **Production Engineering** | Casing, tubing, bean valve, SRP artificial lift | API 5CT, Vogel IPR, Gilbert correlation |
| **Drilling Physics** | PP, FG, ECD, safe mud weight window | Eaton method, Hubbert-Willis |
| **PTA / RTA** | Permeability k, skin S, Horner plot | Craft, Hawkins & Terry; van Everdingen-Hurst |
| **Digital Twin** | SHA-256 provenance, audit trail | Blockchain schema, DGH-compliant |
| **Executive View** | 5-well portfolio summary | Colour-coded health status |
| **Workflow** | 6-step integrated decision chain | PTA → Stimulation → EOR → Chemistry → Completion → Decline |

---

## 🔬 Technical Architecture

```
Input: Wireline LAS file / Well parameters / Pressure CSV
         ↓
Layer 1: Physics Engine (deterministic — fully auditable)
         STOIIP · Arps decline · P_EOR · Horner PTA · Stiff-Davis SSI
         ↓
Layer 2: Modifier Engine
         W_mod × CF_mod × (1 − TZ_pen) → P_EOR_adj
         ↓
Layer 3: India Fiscal Engine
         Live Brent × FX → NPV · IRR · Payback (GoI royalty + OID cess)
         ↓
Layer 4: Spectral AI Engine (patent filed — synthetic demo)
         SWIR transformer → mineralogy → fluid contact
         ↓
Layer 5: Digital Twin
         SHA-256 hash · Provenance chain · DGH-compliant
         ↓
Output: Reservoir characterisation · EOR ranking · Economics · Well diagnostics
```

**Every output is traceable to a named equation and a specific input value. No hidden adjustments. No black boxes.**

---

## 📁 Repository Structure

```
HyperSenseIQ/
├── index.html              # Main platform (14 tabs + Workflow + FAQ)
├── hypersenseiq_story.html # 14-scene animated explainer
├── data/
│   └── brent_live.json     # Live Brent crude (updated hourly by GitHub Action)
├── .github/workflows/
│   └── fetch-brent.yml     # GitHub Action — hourly Brent price update
├── index.py                # PTA/RTA backend (Python/FastAPI)
├── pta_gui.py              # PTA/RTA desktop GUI (PyQt5)
├── requirements.txt        # Python dependencies
└── sample_pressure_test.csv # Sample buildup data (Assam-Well-01)
```

---

## 🧪 Using the PTA/RTA Module

**Browser (no install):**
1. Open the platform → select any well → click **PTA / RTA** tab
2. Synthetic buildup loads automatically from well parameters
3. To use real data: click **Upload CSV** with columns `time_hrs`, `pressure_psi`

**Desktop GUI:**
```bash
pip install -r requirements.txt
python pta_gui.py
```

**Python backend:**
```bash
python index.py
```

---

## 🌊 Live Water Chemistry Calculator

In the **Chemistry** tab, scroll down to the Live Calculator:
- Enter real formation water ions (Ca²⁺, Mg²⁺, HCO₃⁻, Cl⁻, SO₄²⁻, Na⁺, Temperature, pH)
- SSI (Stiff-Davis 1952), TDS, WFAR and scale inhibitor dose compute instantly
- Fluid compatibility matrix updates live
- Click **Reset to dataset defaults** to load formation-specific profiles

---

## 📋 Sample Synthetic Well Parameters

| Well | Formation | k (mD) | Skin | API | EOR Rec |
|------|-----------|--------|------|-----|---------|
| AS-W1 | Tipam Ss, Assam | 180 | +1.2 | 34° | UST |
| AS-W3 | Tipam Ss, Assam | 110 | +3.8 | 32° | Polymer |
| AS-W5 | Tipam Ss, Assam | 68 | −2.8 | 31° | ASP |
| MH-N-01 | Bassein Ls, Mumbai | 420 | +0.8 | 38° | UST |
| CB-04 | Kalol Ss, Cambay | 85 | +4.1 | 29° | Thermal |

---

## 🔒 Data Sovereignty

Data entered in the browser stays in your browser session. Nothing is transmitted to any server. For PSU clients (OIL India, ONGC) requiring on-premise deployment, a local deployment option is available where the platform runs entirely within your network infrastructure.

---

## 📜 Patent

The SWIR hyperspectral spectral intelligence engine is covered by a patent application filed **24 March 2026** (11 claims). Six additional claims drafted. Covers transformer-based mineralogy identification and hydrocarbon contact prediction from core plug images at 900–2500nm.

---

## 📞 Contact

**Niranjan Bilgi** — Inventor & Founder  
+91 9699165381 · niranjanbilgi@yahoo.com  
97/5 Krishna Kunj, Ranade Road, Dadar, Mumbai 400028

*For pilot validation enquiries, platform demonstrations or commercial proposals — response within 24 hours.*

---

*HyperSenseIQ — Built in India. For Indian reservoirs. By an Indian engineer.*

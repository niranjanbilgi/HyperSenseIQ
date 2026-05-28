\# HyperSenseIQ PTA/RTA Platform v2.6



\*\*Pressure Transient Analysis for Oil \& Gas Well Diagnostics\*\*



!\[Status](https://img.shields.io/badge/status-production-brightgreen)

!\[Version](https://img.shields.io/badge/version-2.6-blue)

!\[Python](https://img.shields.io/badge/python-3.8%2B-blue)



\## Overview



HyperSenseIQ is a \*\*production-grade pressure transient analysis (PTA) platform\*\* for well diagnostics in the Indian oil \& gas sector. It automates the complete workflow from pressure test data import to professional analysis reports.



\*\*Developed by:\*\* Niranjan Bilgi, HyperSenseIQ Technologies  

\*\*Patent Status:\*\* Patent Applied For (24 March 2026)  

\*\*GitHub:\*\* https://github.com/niranjanbilgi/HyperSenseIQ



\---



\## Features



\### ✅ Complete Pipeline

\- \*\*Data Import \& Validation\*\* — CSV pressure test files with automatic quality scoring

\- \*\*Horner Plot Analysis\*\* — Permeability (k) and skin factor (s) calculations

\- \*\*Professional Visualization\*\* — Publication-ready Horner plots (300 DPI)

\- \*\*Report Generation\*\* — Text and JSON reports for integration



\### ✅ Production-Ready

\- Command-line interface (CLI) with parameter control

\- Batch processing capability for multiple wells

\- Error handling and data validation

\- 100% data quality scoring system



\### ✅ v2.6 Integration

\- Seamless integration with HyperSenseIQ v2.6\_ProdEng workbook

\- JSON output for programmatic access

\- Standardized well parameter inputs



\---



\## Installation



\### Requirements

\- Python 3.8+

\- numpy >= 2.4.6

\- scipy >= 1.17.1

\- pandas >= 3.0.3

\- matplotlib >= 3.10.9



\### Setup



```bash

\# Clone repository

git clone https://github.com/niranjanbilgi/HyperSenseIQ.git

cd HyperSenseIQ



\# Install dependencies

pip install -r requirements.txt



\# Verify installation

python index.py --help

```



\---



\## Quick Start



\### Basic Usage



```bash

python index.py pressure\_data.csv "Well-Name"

```



\### With Custom Parameters



```bash

python index.py data.csv "Assam-Well-01" --q 150 --h 45 --mu 0.8

```



\### Full Parameter Control



```bash

python index.py pressure\_test.csv "OIL-India-Well" \\

&#x20; --q 150 \\           # Production rate (bbl/d)

&#x20; --B 1.0 \\           # Formation volume factor

&#x20; --mu 0.8 \\          # Viscosity (cp)

&#x20; --h 45 \\            # Pay thickness (ft)

&#x20; --phi 0.22 \\        # Porosity

&#x20; --ct 5e-5 \\         # Total compressibility

&#x20; --rw 0.35           # Wellbore radius (ft)

```



\---



\## Input Format



\### CSV File Structure



Minimum 2 numeric columns (time, pressure):



```csv

time\_hours,pressure\_psi

0.1,1000

0.5,950

1,920

2,850

5,750

10,650

20,550

50,400

100,300

```



\*\*Supported Formats:\*\*

\- Format 1: `time, pressure`

\- Format 2: `time, pressure, temperature`

\- Format 3: `datetime, pressure`



\---



\## Output Files



\### Generated Outputs



1\. \*\*Horner Plot (PNG):\*\* `horner\_plot\_<wellname>\_<timestamp>.png`

&#x20;  - Publication-ready visualization

&#x20;  - 300 DPI resolution

&#x20;  - Professional formatting



2\. \*\*Text Report (TXT):\*\* `PTA\_Report\_<wellname>\_<timestamp>.txt`

&#x20;  - Complete analysis summary

&#x20;  - Data quality assessment

&#x20;  - Well parameters used

&#x20;  - Interpretation guidelines



3\. \*\*JSON Report (JSON):\*\* `PTA\_Report\_<wellname>\_<timestamp>.json`

&#x20;  - Programmatic access

&#x20;  - v2.6\_ProdEng integration ready

&#x20;  - Standardized format



\---



\## Analysis Output Example


# Satellite Constellation Access & Outage Analysis  
**ANSYS STK + Python Automation Project**

## 📌 Overview
This project demonstrates end-to-end **mission design, constellation modeling, and access analysis** using **ANSYS Systems Tool Kit (STK)** automated through **Python**.  
The objective is to evaluate **coverage quality, access gaps, and outage durations** for multiple ground facilities using a LEO satellite constellation inspired by real-world systems.

The project follows an industry-style workflow similar to mission design and operations analysis.

---

## 🛰️ Problem Statement
A low Earth orbit satellite constellation is proposed to provide **near-continuous global coverage**.  
Multiple candidate ground facilities are available, and the task is to:

- Evaluate access between satellites and ground stations
- Identify coverage gaps and outages
- Determine facility viability based on outage limits
- Analyze performance under **degraded constellation conditions**
- Extend the analysis to a **dynamic aircraft mission**

---

## 🧩 Scenario Description
- **Constellation**
  - 4 orbital planes  
  - 8 satellites per plane (32 total)
  - Sun-synchronous style LEO orbits
  - Evenly spaced and staggered true anomalies

- **Ground Segment**
  - 20 candidate ground facilities loaded from an external file
  - Global distribution

- **Sensors**
  - One sensor per satellite
  - Simple conic pattern with wide field of view

- **Time Period**
  - 1 June 2022 – 2 June 2022 (24 hours)

---

## ⚙️ What This Script Does
✔ Automatically launches and controls STK  
✔ Creates a complete satellite constellation programmatically  
✔ Inserts ground facilities from an external file  
✔ Attaches sensors and builds sensor & facility constellations  
✔ Computes access using **Chain objects**  
✔ Extracts access intervals using **STK Data Providers**  
✔ Calculates **maximum outage durations** for each facility  
✔ Applies realistic **azimuth and elevation constraints**  
✔ Simulates a **degraded constellation scenario**  
✔ Integrates and analyzes an **aircraft flight mission**  
✔ Exports all results for reporting and review  

---

## 📊 Analysis Performed
- Continuous vs non-continuous facility access
- Maximum outage duration per facility
- Facility viability based on outage threshold (≤ 5 minutes)
- Facility with the longest communication break
- Aircraft access performance during degraded constellation
- Aircraft position at the start of the longest outage

---

## 📁 Output Files
The script automatically generates:
- `FacXXAccess.txt` – Access intervals per facility  
- `MaxOutageData.txt` – Maximum outage summary  
- `AircraftAccess.txt` – Aircraft access intervals  

These outputs are structured for **post-processing and reporting**.

---

## 🛠️ Tools & Technologies
- **ANSYS STK (Premium / Integration)**
- **Python**
- STK Object Model & Data Providers
- NumPy
- Automated mission scripting

---

## 📈 Key Learnings
- Practical constellation design and trade study workflows  
- Automation of complex STK scenarios using Python  
- Understanding coverage gaps and operational constraints  
- Real-world style mission analysis beyond GUI-based work  
- Integration of space and airborne assets in a single scenario  

---

## 🚀 Why This Project Matters
This is not a toy simulation.  
It reflects **real mission engineering workflows** used in:
- Satellite operations
- Ground network planning
- Coverage and availability studies
- Space system trade analysis

---

## 📌 Author
**Bhuvan Meesala**  
Aerospace Engineering Student  
Mission Design & Space Systems Enthusiast  

---

## 📜 Disclaimer
This project is for **educational and demonstration purposes** only and is based on publicly available concepts and datasets.

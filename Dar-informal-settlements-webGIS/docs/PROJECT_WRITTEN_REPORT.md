# SCHOOL OF EARTH SCIENCES, REAL ESTATE, BUSINESS STUDIES AND INFORMATICS (SERBI)
# DEPARTMENT OF COMPUTER SYSTEMS AND MATHEMATICS (CSM)
# BSc. COMPUTER SYSTEMS AND NETWORKS (BSc. CSN)

**WRITE COURSE CODE:** CSN 2XXX  
**WRITE COURSE NAME:** Project II / Software Engineering Project

**YEAR II 2025/26**

---

**PROJECT TITLE:** UNPLANNED SETTLEMENT MAPPING AND GROWTH TREND VISUALIZATION PLATFORM FOR DAR ES SALAAM, TANZANIA

---

## GROUP (1) MEMBERS

| S/No | STUDENTS’ FULL NAME | REGISTRATION NUMBER |
|------|---------------------|---------------------|
| 1 | SURNAME, First name Middle Name | BSc.CSN/XXXX/20XX |
| 2 | SURNAME, First name Middle Name | BSc.CSN/XXXX/20XX |
| 3 | SURNAME, First name Middle Name | BSc.CSN/XXXX/20XX |
| 4 | SURNAME, First name Middle Name | BSc.CSN/XXXX/20XX |
| 5 | SURNAME, First name Middle Name | BSc.CSN/XXXX/20XX |
| 6 | SURNAME, First name Middle Name | BSc.CSN/XXXX/20XX |

---

## DECLARATION

We, Group 1, hereby declare that this report is our own work and effort. The work in this report was carried out in accordance with the Regulations of the Ardhi University.

We have faithfully acknowledged, given credit to, and referred to the research workers wherever their work has been cited in the text and the body of the dissertation. We further certify that we have not wilfully lifted another’s paragraph, text, data, result e.t.c. reported in the journals, books, magazines, reports, dissertations, thesis e.t.c. or available at web-sites and included them in this project and cited them as our work.

| S/no | Student’s Name | Signature | Date |
|------|----------------|-----------|------|
| 1 | SURNAME, First name Middle Name | ……………………… | …………………. |
| 2 | SURNAME, First name Middle Name | ……………………… | …………………. |
| 3 | SURNAME, First name Middle Name | ……………………… | …………………. |
| 4 | SURNAME, First name Middle Name | ……………………… | …………………. |
| 5 | SURNAME, First name Middle Name | ……………………… | …………………. |
| 6 | SURNAME, First name Middle Name | ……………………… | …………………. |

---

## CERTIFICATION

The undersigned certify that they have read and hereby recommend for acceptance by Ardhi University a project titled: **Unplanned Settlement Mapping and Growth Trend Visualization Platform for Dar es Salaam, Tanzania**, in fulfillment of the requirements for the accomplishment of second year studies at Ardhi University.

………………………………  
**Dr. Godfrey Luwemba**  
(Supervisor)  
Date: ……………….

………………………………  
**Mr. Alexander Moreka**  
(Supervisor)  
Date: ……………….

---

## ACKNOWLEDGEMENT

First and foremost, we give thanks to Almighty God for granting us good health, wisdom, and strength throughout the period of carrying out this project. Without His guidance, the successful completion of this work would not have been possible.

We sincerely express our gratitude to our supervisors, **Dr. Godfrey Luwemba** and **Mr. Alexander Moreka**, for their professional guidance, constructive criticism, and continuous support from the proposal stage to the final implementation of the system. Their advice helped us to remain focused on academic standards and practical relevance.

We also acknowledge **Ardhi University**, particularly the School of Earth Sciences, Real Estate, Business Studies and Informatics (SERBI) and the Department of Computer Systems and Mathematics (CSM), for providing the learning environment and resources that made this project possible. Our appreciation also goes to our fellow ISM2 students and group members for teamwork, idea sharing, and mutual encouragement during system design, coding, testing, and deployment.

Finally, we thank the urban planning and GIS communities in Tanzania, as well as open data providers such as ESA Copernicus, USGS, and Google Earth Engine, whose satellite data and tools supported the spatial analysis component of this study.

---

## LIST OF ABBREVIATIONS AND ACRONYMS

| Abbreviation | Meaning |
|--------------|---------|
| AOI | Area of Interest |
| API | Application Programming Interface |
| ARU | Ardhi University |
| BSI | Bare Soil Index |
| CORS | Cross-Origin Resource Sharing |
| CSV | Comma-Separated Values |
| CSM | Department of Computer Systems and Mathematics |
| GEE | Google Earth Engine |
| ISI | Unplanned Settlement Index |
| JWT | JSON Web Token |
| KPI | Key Performance Indicator |
| NDBI | Normalized Difference Built-up Index |
| NDVI | Normalized Difference Vegetation Index |
| PostGIS | Spatial Extension of PostgreSQL |
| REST | Representational State Transfer |
| SERBI | School of Earth Sciences, Real Estate, Business Studies and Informatics |
| UML | Unified Modeling Language |
| USI | Unplanned Settlement Index |
| WebGIS | Web-based Geographic Information System |

---

## ABSTRACT

Rapid urbanisation in Dar es Salaam has led to the expansion of unplanned settlements that are often under-mapped, poorly documented, and difficult to monitor using conventional field surveys alone. This project developed a Web-based Geographic Information System (WebGIS) titled **Unplanned Settlement Mapping and Growth Trend Visualization Platform** to support spatial analysis, historical change detection, and evidence-based planning for the city covering the period 2005 to 2026.

The study followed a structured software engineering approach beginning with user and system requirements gathering, literature review, system analysis and design, implementation, and testing. Satellite-derived spectral indices including NDBI, NDVI, BSI, and fragmentation were combined into an Unplanned Settlement Index (ISI) to classify settlement areas by probability of unplanned growth. Settlement polygons, yearly metrics, and change-detection results were stored in a PostgreSQL database with PostGIS extension and served through a FastAPI backend.

The frontend was implemented using HTML, CSS, JavaScript, Leaflet, and Chart.js to provide an interactive map with a time slider, probability-based legend, analytics dashboard, downloadable CSV reports, user authentication, and an admin monitoring panel. The system was deployed on Render (backend and database) and Vercel (frontend) to demonstrate a production-ready cloud architecture.

Testing confirmed that core functional requirements such as map visualisation, yearly layer loading, change detection, statistics display, user login, and report download operated as expected. The platform improves accessibility of unplanned settlement data for planners, researchers, students, and policymakers. It is recommended that future work integrate higher-resolution imagery, machine learning classification, and ward-level ground-truthing to strengthen accuracy and policy application.

---

## LIST OF TABLES

**Table 3.1** Methodology Table ……………………………………………………………………… 4  
**Table 5.1** Functional Testing Results …………………………………………………………… 7

---

## LIST OF FIGURES

**Figure 4.1** Three-Tier System Architecture of the Unplanned Settlement WebGIS Platform … 6  
**Figure 4.2** Entity Relationship Diagram of the PostGIS Database …………………………… 6  
**Figure 4.3** Use Case Diagram of the Platform ………………………………………………… 6  
**Figure 5.1** Home Page of the Platform ………………………………………………………… 7  
**Figure 5.2** Interactive Maps Page with Probability Legend and Dashboard ………………… 7  
**Figure 5.3** Statistics Page with Ward and District Analytics ………………………………… 7  
**Figure 5.4** Admin Dashboard for User and Download Monitoring …………………………… 7

---

## TABLE OF CONTENTS

DECLARATION ……………………………………………………………………………………… i  
CERTIFICATION …………………………………………………………………………………… ii  
ACKNOWLEDGEMENT …………………………………………………………………………… iii  
LIST OF ABBREVIATIONS ……………………………………………………………………… iv  
ABSTRACT ………………………………………………………………………………………… v  
LIST OF TABLES ………………………………………………………………………………… viii  
LIST OF FIGURES ………………………………………………………………………………… ix  
CHAPTER ONE: INTRODUCTION ……………………………………………………………… 1  
CHAPTER TWO: LITERATURE REVIEW ……………………………………………………… 2  
CHAPTER THREE: METHODOLOGY …………………………………………………………… 3  
CHAPTER FOUR: SYSTEM ANALYSIS AND DESIGN ………………………………………… 5  
CHAPTER FIVE: IMPLEMENTATION AND TESTING ………………………………………… 7  
CHAPTER SIX: CONCLUSION AND RECOMMENDATION …………………………………… 8  
REFERENCES ……………………………………………………………………………………… 9  
APPENDIX ………………………………………………………………………………………… 10

---

\newpage

# CHAPTER ONE
# INTRODUCTION

## 1.1 General Introduction

Urbanisation is one of the most significant demographic transformations of the twenty-first century, especially in developing countries where cities are growing faster than the capacity of formal planning systems. According to the United Nations Department of Economic and Social Affairs (2018), more than half of the world’s population now lives in urban areas, and this proportion is expected to increase further by 2050. In Sub-Saharan Africa, urban growth has frequently occurred through the expansion of unplanned settlements characterised by inadequate infrastructure, insecure tenure, and limited access to basic services.

Dar es Salaam, the largest city and major economic centre of Tanzania, provides a clear example of this challenge. Kombe and Kreibich (2000) observed that unplanned settlements in Dar es Salaam have developed through complex social, economic, and land governance processes, making them difficult to monitor using traditional paper-based planning methods alone. As the city continues to expand, planners and decision-makers require timely, spatially explicit information on where unplanned settlements are located, how they are changing over time, and which areas show higher probability of future unplanned growth.

Geographic Information Systems (GIS) and remote sensing have become essential tools for studying urban land cover change. Lillesand, Kiefer, and Chipman (2015) explain that satellite imagery allows repeated observation of large areas at relatively low cost compared with exhaustive field mapping. When combined with web technologies, GIS becomes a WebGIS platform that can deliver maps, analytics, and reports to multiple users through standard browsers. This is particularly useful for universities, municipal authorities, NGOs, and researchers who need shared access to spatial evidence.

The present project, developed by ISM2 students at Ardhi University, Makongo, Dar es Salaam, addresses this need by building a cloud-deployed WebGIS platform for **Unplanned Settlement Mapping and Growth Trend Visualization**. The system integrates Google Earth Engine (GEE) processing workflows, a PostGIS spatial database, a FastAPI backend, and a Leaflet-based frontend. It supports analysis years from 2005 to 2026, change detection between years, downloadable CSV reports, user authentication, and administrative monitoring of platform usage. The platform is accessible online and is designed to support evidence-based urban planning, academic research, and public awareness of unplanned settlement dynamics in Dar es Salaam.

## 1.2 Statement of the Problem

Unplanned settlements in Dar es Salaam continue to grow rapidly, yet reliable spatial data on their location, extent, and temporal change remain scattered, outdated, or inaccessible to many stakeholders. Planners, students, and community organisations often lack an integrated digital platform that combines mapping, analytics, and reporting in one system. Existing approaches frequently depend on static maps, manual spreadsheets, or specialised desktop GIS software that requires advanced training.

Although remote sensing and GIS research on unplanned urban growth exists globally and in Tanzania, there remains a gap in student-led, locally contextualised, web-based systems that connect satellite-derived indices, historical settlement layers, district and ward statistics, user accounts, and cloud deployment within a single platform tailored to Dar es Salaam.

Therefore, this project designed and implemented the **Unplanned Settlement Mapping and Growth Trend Visualization Platform** to provide interactive mapping, probability-based settlement classification, growth analytics, and downloadable reports for decision support and academic use.

## 1.3 Objectives

### 1.3.1 General Objective

The general objective of this project is to develop a WebGIS platform that maps, analyses, and visualises unplanned settlements in Dar es Salaam while supporting growth trend monitoring and report generation from 2005 to 2026.

### 1.3.2 Specific Objectives

i. To identify and gather user requirements for the Unplanned Settlement Mapping and Growth Trend Visualization Platform.  
ii. To design the Unplanned Settlement Mapping and Growth Trend Visualization Platform.  
iii. To implement the Unplanned Settlement Mapping and Growth Trend Visualization Platform.  
iv. To test and validate the Unplanned Settlement Mapping and Growth Trend Visualization Platform.

## 1.4 Research Questions

i. What functional and non-functional requirements are needed by users of the Unplanned Settlement Mapping and Growth Trend Visualization Platform?  
ii. What system architecture, database structure, and interface design are suitable for storing and presenting unplanned settlement data in Dar es Salaam?  
iii. How can satellite-derived indices and settlement polygons be implemented in a WebGIS to support yearly visualisation and change detection?  
iv. To what extent does the implemented platform meet its functional requirements during testing and validation?

## 1.5 Significance of the Study

Upon completing this study, the following benefits are expected:

i. Planners and researchers will access interactive maps and statistics on unplanned settlements in Dar es Salaam through a web browser.  
ii. The platform will support evidence-based decision-making by presenting historical growth trends and change detection results.  
iii. Students and academic staff at Ardhi University will have a practical example of integrating remote sensing, databases, APIs, and web development.  
iv. Downloadable CSV reports will improve transparency and sharing of analytical outputs among stakeholders.  
v. The cloud-based design demonstrates a low-cost approach to deploying spatial information systems using modern open-source tools.

## 1.6 Structure of the Report

This report is organised into six chapters. Chapter One introduces the study, problem statement, objectives, research questions, and significance. Chapter Two reviews literature related to unplanned settlements, remote sensing, and WebGIS. Chapter Three explains the methodology used in requirements gathering, design, implementation, and testing. Chapter Four presents system and user requirements together with architectural and database design. Chapter Five describes implementation of each system module and reports testing results. Chapter Six provides conclusions, challenges, limitations, and recommendations for future work. References and appendix materials are presented at the end.

---

# CHAPTER TWO
# LITERATURE REVIEW

## 2.1 Introduction

A literature review is a systematic examination of published research and documented practices related to a study topic. It helps researchers understand what has already been done, identify strengths and weaknesses in existing work, and position a new project within established knowledge. This chapter reviews studies on unplanned settlements, urban remote sensing, GIS-based planning, and WebGIS platforms because these areas form the foundation of the current project.

## 2.2 Related Studies

Kitio and Dubois (2011) examined slum mapping in African cities and showed that spatial data are essential for understanding housing conditions and service deficits in unplanned areas. Their work demonstrated that map-based evidence improves targeting of urban upgrading programmes.

Kombe and Kreibich (2000) studied unplanned urbanisation in Dar es Salaam and highlighted governance, land tenure, and infrastructure challenges. Their findings confirm that local context must guide any digital mapping solution for the city.

Herold, Roberts, and others as summarised by Weng (2012) reviewed remote sensing of urban areas and reported that multispectral indices such as NDVI and built-up indices are widely used to detect urban land cover change over time.

Lillesand, Kiefer, and Chipman (2015) provided foundational principles of remote sensing and image interpretation, explaining how spectral bands from Landsat and Sentinel satellites support land cover classification and change analysis.

Patel et al. (2021) discussed the use of Google Earth Engine for large-scale geospatial processing and noted that cloud platforms reduce the hardware burden on local institutions while enabling repeatable analysis workflows.

Goodchild (2007) introduced the concept of volunteered geographic information and argued that web-based mapping systems have transformed how spatial data are shared between experts and the public.

Plewe (2017) reviewed developments in WebGIS and stated that modern web mapping libraries and REST APIs allow lightweight, interactive spatial applications that can be deployed globally.

UN-Habitat (2020) reported on urban informality and emphasised the need for improved data systems to monitor informal and unplanned urban growth, especially in fast-growing African cities.

Kuffer, Reba, and others in the Global Human Settlement context, as discussed by Florczyk et al. (2019), showed that global settlement layers are useful for broad analysis but may require local calibration for ward-level planning in cities such as Dar es Salaam.

## 2.3 Research Gap

Although the literature provides strong support for mapping unplanned settlements and using remote sensing in urban studies, several gaps remain. Many existing platforms are either global dashboards with limited local detail, desktop GIS projects without web deployment, or research prototypes without user authentication, analytics dashboards, and downloadable reports. Few student-developed systems combine GEE-based index computation, PostGIS storage, FastAPI services, interactive time sliders, change detection, district and ward statistics, and cloud hosting in one integrated platform focused specifically on Dar es Salaam. This project therefore fills the gap by delivering a complete, deployable WebGIS tailored to local unplanned settlement monitoring and visualisation.

---

# CHAPTER THREE
# METHODOLOGY

## 3.1 Introduction

This chapter describes the methods and tools used to carry out the project from requirements gathering to testing and validation. It explains why each method was selected and how it supported achievement of the specific objectives stated in Chapter One.

## 3.2 Selected Methodology

### 3.2.1 General Methodology

The project used the **Agile methodology**. Agile is an iterative software development approach in which work is divided into small cycles called sprints, allowing continuous improvement based on feedback. Agile was chosen because the project involved multiple modules—map interface, API, database, authentication, admin dashboard, and deployment—that needed to be developed, tested, and refined progressively. This approach allowed the group to release working components early and improve them after supervisor review and user observation.

### 3.2.2 Methodology for Gathering User Requirement

User requirements were gathered using **literature review**, **observation**, and **group discussion**. Literature review helped identify standard WebGIS functions and planning data needs. Observation was applied by examining existing mapping websites and university planning workflows to determine what users expect from map tools, legends, downloads, and dashboards. Group discussion allowed the project team and supervisors to agree on priority features such as yearly time slider, change detection, CSV export, login system, and bilingual user guide. These methods were selected because they are practical for an academic project where formal large-scale surveys are limited but expert and peer input is readily available.

### 3.2.3 Methodology for System Design

System design was conducted using **UML-based modelling** and **architectural design documentation**. UML supports clear representation of system actors, use cases, and data relationships. An architectural diagram was prepared to show the interaction between frontend, backend API, and PostGIS database. This approach was chosen because it is standard in software engineering education and helps communicate design decisions to supervisors and developers.

### 3.2.4 Methodology for System Implementation

Implementation was carried out using the following tools and technologies:

- **Python 3.12** and **FastAPI** for the backend REST API because they are modern, fast, and well supported for geospatial services.
- **PostgreSQL 16** with **PostGIS** for spatial data storage and querying.
- **HTML5, CSS3, and JavaScript** for the frontend because they are standard web technologies supported by all browsers.
- **Leaflet** for interactive web mapping and **Chart.js** for analytics charts.
- **Google Earth Engine scripts** for satellite index processing and GeoJSON export.
- **Docker**, **Render**, and **Vercel** for deployment of backend and frontend respectively.

These tools were selected because they are open source or free-tier compatible, well documented, and suitable for geospatial web applications.

### 3.2.5 Methodology for System Testing and Validation

Testing and validation were conducted using **functional testing**, **integration testing**, and **user observation**. Functional testing checked whether each requirement produced the expected output. Integration testing verified communication between frontend, API, and database. User observation was used to assess usability of the map slider, login process, and report download workflow. These methods were appropriate because they directly measure whether the implemented system satisfies the stated requirements.

## 3.3 Methodology Table

**Table 3.1 Methodology Table**

| Specific Objective | Methodology | Tools | Deliverable |
|--------------------|-------------|-------|-------------|
| i. To identify and gather user requirements | Literature review, observation, group discussion | Published articles, existing WebGIS platforms, supervisor feedback | Requirements specification document |
| ii. To design the system | UML modelling, architectural design | Draw.io / UML diagrams, system flow documentation | Architecture diagram, ERD, use case diagram |
| iii. To implement the system | Agile implementation | FastAPI, PostGIS, Leaflet, Chart.js, GEE scripts, Docker | Working WebGIS platform deployed online |
| iv. To test and validate the system | Functional testing, integration testing, user observation | Browser, API docs, health endpoints, test checklist | Test results table and validation report |

---

# CHAPTER FOUR
# SYSTEM ANALYSIS AND DESIGN

## 4.1 Introduction

This chapter presents the analysis and design of the Unplanned Settlement Mapping and Growth Trend Visualization Platform. It explains the system and user requirements that guided development and describes the architecture and database design used to organise spatial and non-spatial data.

## 4.2 Requirement Analysis

Requirement analysis is the process of identifying and documenting what a system must do and the conditions under which it must operate (Sommerville, 2016). In this project, requirements were classified into **system requirements** and **user requirements**. System requirements describe technical resources and environment needed by the platform, while user requirements describe services and quality expectations from the end user’s perspective.

### 4.2.1 System Requirement

System requirements define the hardware, software, and data needed for the platform to function. They ensure that developers configure the environment correctly during implementation and deployment.

#### 4.2.1.1 Data Requirement

The system uses the following data types:

1. **Settlement polygon data** — GeoJSON features representing unplanned settlement boundaries for years 2005, 2010, 2015, 2020, and 2026, stored in PostGIS and served as API GeoJSON layers.  
2. **Spectral index attributes** — NDBI, NDVI, BSI, and fragmentation values attached to each settlement polygon for index computation.  
3. **ISI scores and probability classes** — Derived values used to classify settlements as low, medium, or high probability of unplanned settlement.  
4. **Yearly metrics** — Aggregated statistics such as total area, average ISI, settlement counts, and population proxy per year.  
5. **Change detection records** — Results comparing two years, including new, expanded, contracted, and stable settlements.  
6. **User and activity data** — Accounts, sessions, page visits, and download logs for authentication and admin analytics.  
7. **Area of Interest (AOI)** — Bounding geometry for Dar es Salaam used to frame the map view.

Data were obtained from sample GeoJSON generated for development, GEE export scripts in the repository, and database bootstrap/import scripts.

#### 4.2.1.2 Software Requirement

Software requirements specify the programs and frameworks needed to build and run the system:

1. **PostgreSQL 16 + PostGIS 3.4** — Spatial database for storing settlement geometries and attributes.  
2. **Python 3.12** — Backend programming language.  
3. **FastAPI and Uvicorn** — API framework and server.  
4. **SQLAlchemy and GeoAlchemy2** — Database ORM and spatial support.  
5. **Leaflet 1.9** — Frontend mapping library.  
6. **Chart.js 4.4** — Dashboard and statistics charts.  
7. **Docker** — Containerised deployment on Render.  
8. **Modern web browser** — For accessing the deployed frontend on Vercel.

#### 4.2.1.3 Hardware Requirement

The following hardware was used:

1. **Developer laptops** — Minimum 8 GB RAM and multi-core processor for coding, testing, and running local services.  
2. **Internet connection** — Required for cloud deployment, API access, and satellite data processing through GEE.  
3. **Render cloud server** — Hosts FastAPI backend and PostgreSQL database.  
4. **Vercel hosting environment** — Hosts static frontend assets.  
5. **Standard user devices** — Desktop or mobile devices with a modern browser for end users.

### 4.2.2 User Requirement

User requirements describe what stakeholders expect when using the platform. They are divided into functional and non-functional requirements.

#### 4.2.2.1 Functional Requirement

Functional requirements define specific services the system must provide (Sommerville, 2016). The main functional requirements are:

1. The system shall display an interactive map of unplanned settlements for selected analysis years.  
2. The system shall compute and visualise Unplanned Settlement Index (ISI) probability classes using green, orange, and red colours.  
3. The system shall allow users to compare two years using change detection mode.  
4. The system shall provide dashboards and statistics at city, district, and ward levels.  
5. The system shall allow registered users to download CSV growth and change reports.  
6. The system shall provide login, signup, and admin monitoring of visitors and downloads.

#### 4.2.2.2 Non-functional Requirement

Non-functional requirements define quality attributes of the system:

1. **Usability** — The interface shall be simple enough for students and planners to navigate with minimal training.  
2. **Performance** — The map and charts shall load within acceptable time on standard internet connections.  
3. **Security** — Passwords shall be hashed and authentication tokens used for protected operations.  
4. **Scalability** — Cloud deployment shall allow additional years and settlements to be imported without redesigning the whole system.  
5. **Availability** — The platform shall be accessible online through deployed frontend and backend services.  
6. **Maintainability** — Code shall be modular, with separate frontend, backend, and database layers.

## 4.3 System Design

### 4.3.1 System Architecture

System architecture is the structural organisation of software components and their relationships (Bass, Clements, and Kazman, 2012). The architecture was designed to separate data, business logic, and presentation so that each layer can be maintained independently.

The platform uses a **three-tier architecture**:

```text
┌─────────────────────────────────────────────────────────────┐
│                    PRESENTATION TIER                         │
│  Vercel Frontend: HTML, CSS, JavaScript, Leaflet, Chart.js   │
│  Pages: Home, Maps, Statistics, About, User Guide, Auth, Admin│
└───────────────────────────┬─────────────────────────────────┘
                            │ HTTPS / REST API
┌───────────────────────────▼─────────────────────────────────┐
│                    APPLICATION TIER                          │
│  Render FastAPI Backend: auth, metrics, change detection,    │
│  GeoJSON delivery, CSV export, activity tracking             │
└───────────────────────────┬─────────────────────────────────┘
                            │ SQL / Spatial Queries
┌───────────────────────────▼─────────────────────────────────┐
│                      DATA TIER                               │
│  Render PostgreSQL + PostGIS                                 │
│  Tables: settlements, yearly_metrics, change_detection,      │
│  users, sessions, page_visits, download_logs                 │
└─────────────────────────────────────────────────────────────┘
```

**Figure 4.1 Three-Tier System Architecture of the Unplanned Settlement WebGIS Platform**

Satellite processing occurs in Google Earth Engine, where GeoJSON exports are generated and imported into PostGIS through Python import scripts.

### 4.3.2 Entity Relationship Diagram (If applicable)

An Entity Relationship Diagram (ERD) shows entities, attributes, and relationships in a database (Connolly and Begg, 2015). The ERD was included because the platform depends on a relational spatial database to store settlements, metrics, users, and activity logs.

Main entities and relationships:

```text
users (1) ──────< user_sessions
users (1) ──────< download_logs

settlements ─── contains yearly spatial attributes
yearly_metrics ─ one record per analysis year
change_detection ─ links from_year and to_year settlement changes
page_visits ─── tracks visitor activity
import_log ─── records data import operations
```

**Figure 4.2 Entity Relationship Diagram of the PostGIS Database**

**Use Case Diagram (summary):**

| Actor | Main Use Cases |
|-------|----------------|
| Guest visitor | View home page, browse maps, read user guide |
| Registered user | Login, download CSV reports, view statistics |
| Administrator | Monitor live users, view downloads, manage platform usage |
| System | Import GeoJSON, compute metrics, serve API responses |

**Figure 4.3 Use Case Diagram of the Platform**

---

# CHAPTER FIVE
# IMPLEMENTATION AND TESTING

## 5.1 Introduction

This chapter describes how the Unplanned Settlement Mapping and Growth Trend Visualization Platform was implemented and how it was tested. It explains the main modules developed, their functions, and the results of validation against functional requirements.

## 5.2 Implementation

### 5.2.1 Google Earth Engine Data Processing Module

This module consists of JavaScript scripts stored in the `gee/` folder. Script `01_aoi_definition.js` defines the Dar es Salaam Area of Interest. Other scripts compute spectral indices, derive settlement layers, and export yearly GeoJSON datasets. The outputs are imported into the backend database using Python import scripts. This module provides the spatial evidence base for the platform.

### 5.2.2 Backend API Module

The backend was implemented using FastAPI in `backend/main.py`. It exposes REST endpoints for health checks, settlement layers, yearly metrics, change detection, AOI bounds, location analytics, and CSV export. Supporting services include:

- `isi_model.py` — computes ISI using the formula:  
  `ISI = 0.3(NDBI) + 0.25(1 − NDVI) + 0.2(BSI) + 0.25(Fragmentation)`
- `metrics.py` — computes yearly dashboard indicators.
- `change_detection.py` — identifies new and expanded settlements between years.
- `auth_service.py` and `activity_service.py` — manage users, sessions, visits, and downloads.

The API was deployed on Render using Docker and connects to PostgreSQL/PostGIS.

### 5.2.3 Database Module

PostgreSQL with PostGIS was used to store spatial and tabular data. Tables include `settlements`, `yearly_metrics`, `change_detection`, `users`, `user_sessions`, `page_visits`, and `download_logs`. Bootstrap and import scripts automatically create schema and load GeoJSON on startup when configured.

### 5.2.4 Frontend WebGIS Module

The frontend contains multiple pages:

1. **Home page** — overview, growth charts, and visitor statistics.  
2. **Maps page** — interactive Leaflet map, year slider (2005–2026), probability legend, fullscreen button, green AOI overlay, analytics dashboard, and CSV download.  
3. **Statistics page** — ward table, district growth bars, and downloadable district reports.  
4. **About page** — project description and mission.  
5. **User Guide page** — bilingual instructions in English and Kiswahili.  
6. **Auth page** — login and signup forms.  
7. **Admin page** — live users, visitor counts, and download logs.

The frontend uses probability-based colouring: green for low probability, orange for medium probability, and red for high probability of unplanned settlement. Emergent settlement layers are excluded from display as required by the updated project scope.

### 5.2.5 Authentication and Admin Monitoring Module

Users can create accounts and log in using email and password. JWT-based authentication secures protected endpoints. The admin dashboard shows number of registered users, live sessions, visitor statistics, and a table of users who downloaded reports. This supports accountability and platform monitoring.

### 5.2.6 Deployment Module

The frontend was deployed to Vercel while the backend and database were deployed to Render. Environment variables connect the two services, including `DARINFORMAL_API_URL` on Vercel and `FRONTEND_URL` on Render for CORS configuration. Docker was used to ensure Python 3.12 and GDAL dependencies install correctly on the server.

**Screenshots to insert in final submission:**

- **Figure 5.1** Home Page of the Platform  
- **Figure 5.2** Interactive Maps Page with Probability Legend and Dashboard  
- **Figure 5.3** Statistics Page with Ward and District Analytics  
- **Figure 5.4** Admin Dashboard for User and Download Monitoring

## 5.3 Testing

Testing is the process of executing a system to detect defects and confirm that requirements have been met (Myers, Sandler, and Badgett, 2012). The project applied functional testing, integration testing, and user observation. Functional testing verified each feature independently. Integration testing confirmed that the frontend could retrieve data from the API and that the API could query PostGIS successfully. User observation was used to evaluate map usability, legend clarity, and ease of login.

### 5.3.1 Functional Testing

**Table 5.1 Functional Testing Results**

| S/N | Functional Requirement | Expected Outcome | Test Result |
|-----|------------------------|------------------|-------------|
| 1 | Display interactive map of unplanned settlements | Map loads with settlement polygons for selected year | Pass |
| 2 | Show probability classes on map and legend | Green, orange, and red classes displayed correctly | Pass |
| 3 | Change detection between two years | New and expanded settlements highlighted; summary panel shown | Pass |
| 4 | Display dashboard KPIs and charts | Settlements, area, ISI, growth charts update by year | Pass |
| 5 | User login and signup | Valid credentials allow access; invalid credentials rejected | Pass |
| 6 | Download CSV report | CSV file downloads with yearly growth data | Pass |
| 7 | Admin dashboard monitoring | Visitor counts and download logs visible to admin user | Pass |
| 8 | API health endpoint | `/api/health` returns healthy status and data source information | Pass |

### 5.3.2 Integration Testing

Integration testing confirmed that the Vercel frontend communicates with the Render API, that CORS settings allow authenticated requests, and that GeoJSON features returned by the API render correctly in Leaflet. Database integration was verified through successful import of yearly settlement layers and retrieval of district analytics.

### 5.3.3 User Observation

During observation, users were able to navigate from the home page to the maps page, move the year slider, open popups, switch to fullscreen map view, and download reports after login. Minor usability improvements such as renaming “informal” to “unplanned” and changing risk labels to probability labels were implemented based on feedback.

---

# CHAPTER SIX
# CONCLUSION AND RECOMMENDATION

## 6.1 Introduction

This chapter presents the conclusions drawn from the project, the challenges encountered, limitations of the current system, and recommendations for future development and research.

## 6.2 Conclusion

### 6.2.1 Conclusion on Requirement Gathering

The first specific objective was to identify and gather user requirements for the platform. This was achieved through literature review, observation, and group discussion. The team documented functional needs such as interactive mapping, yearly analysis, report download, and authentication, as well as non-functional needs including usability, security, and online availability.

### 6.2.2 Conclusion on System Design

The second objective was to design the platform. This was achieved by adopting a three-tier architecture and preparing database and use case models. The design supported modular development and cloud deployment, addressing the research gap identified in Chapter Two regarding lack of integrated student-led WebGIS solutions for Dar es Salaam.

### 6.2.3 Conclusion on System Implementation

The third objective was to implement the platform. This was successfully completed using FastAPI, PostGIS, Leaflet, Chart.js, and GEE-based data processing. The final product includes home, maps, statistics, about, user guide, authentication, and admin pages. The maps module visualises unplanned settlement probability and supports change detection and analytics.

### 6.2.4 Conclusion on Testing and Validation

The fourth objective was to test and validate the platform. Functional and integration tests showed that the main requirements were met. The API health endpoint, map visualisation, login system, and CSV downloads operated as expected, confirming that the implemented system is suitable for academic demonstration and planning support.

## 6.3 Challenges and Limitations

One major challenge was configuring cloud deployment on Render, including Python version compatibility, Docker setup, and database connection during cold starts. Another challenge was processing and importing geospatial data with GDAL-dependent libraries, which required careful environment configuration. The project also depends on sample and exported GeoJSON data; therefore, full ground-truthing of every ward boundary and settlement polygon was not completed within the project timeframe. In addition, probability classes are model outputs derived from spectral indices and should be interpreted as decision-support indicators rather than definitive field surveys.

## 6.4 Recommendations

It is recommended that future versions of the platform integrate higher-resolution satellite imagery and machine learning classification to improve settlement detection accuracy. Ward-level field validation should be conducted with local planners and community representatives to strengthen trust in the maps. The system should also be extended to support additional cities and near-real-time monitoring. For sustainability, Ardhi University should continue hosting and maintaining the platform, updating data annually, and training users through workshops and the bilingual user guide.

---

# REFERENCES

Bass, L., Clements, P., & Kazman, R. (2012). *Software architecture in practice* (3rd ed.). Addison-Wesley.

Connolly, T., & Begg, C. (2015). *Database systems: A practical approach to design, implementation, and management* (6th ed.). Pearson.

Florczyk, A. J., Melchiorri, M., Zeidler, J., & Corbane, C. (2019). *GHSL Data Package 2019*. European Commission, Joint Research Centre.

Goodchild, M. F. (2007). Citizens as sensors: The world of volunteered geography. *GeoJournal*, 69(4), 211–221.

Kitio, A., & Dubois, O. (2011). *Slum mapping in African cities: A review*. UN-Habitat / GLTN Discussion Paper.

Kombe, W. J., & Kreibich, V. (2000). Informal settlements in Dar es Salaam: A review of the literature. *Habitat International*, 24(4), 453–465.

Lillesand, T., Kiefer, R. W., & Chipman, J. (2015). *Remote sensing and image interpretation* (7th ed.). Wiley.

Myers, G. J., Sandler, C., & Badgett, T. (2012). *The art of software testing* (3rd ed.). Wiley.

Patel, N., et al. (2021). Google Earth Engine for geospatial analysis: A review. *Remote Sensing Applications: Society and Environment*, 21, 100452.

Plewe, B. (2017). Modern web mapping. In *The International Encyclopedia of Geography* (pp. 1–6). Wiley.

Sommerville, I. (2016). *Software engineering* (10th ed.). Pearson.

UN-Habitat. (2020). *World cities report 2020: The value of sustainable urbanization*. United Nations Human Settlements Programme.

United Nations Department of Economic and Social Affairs. (2018). *World urbanization prospects: The 2018 revision*. United Nations.

Weng, Q. (2012). Remote sensing of impervious surfaces in the urban areas: Requirements, methods, and trends. *Remote Sensing of Environment*, 117, 34–49.

---

# APPENDIX

## Appendix A: Questionnaire for User Requirement Gathering

**Section A: Respondent Information**

1. Name (optional): ___________________________
2. Role: ☐ Student ☐ Planner ☐ Lecturer ☐ Other __________
3. Have you used a WebGIS before? ☐ Yes ☐ No

**Section B: System Requirements**

4. Which features are most important to you?
   - ☐ Interactive map
   - ☐ Year-by-year comparison
   - ☐ Downloadable reports
   - ☐ User login
   - ☐ District and ward statistics

5. What devices do you use to access web maps?
   - ☐ Laptop ☐ Smartphone ☐ Tablet

6. How useful would probability-based colouring be for planning?
   - ☐ Very useful ☐ Useful ☐ Not useful

7. What challenges do you face when accessing unplanned settlement data in Dar es Salaam?

8. What additional features would you recommend for future versions?

---

## Appendix B: Sample API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | System and database health |
| GET | `/api/risk/{year}` | Settlement GeoJSON for year |
| GET | `/api/metrics/trend` | Yearly analytics |
| GET | `/api/metrics/trend/csv` | Growth trend CSV |
| GET | `/api/change/{from}/{to}` | Change detection results |
| GET | `/api/aoi` | Dar es Salaam bounding box |
| POST | `/api/auth/login` | User login |
| POST | `/api/auth/signup` | User registration |

---

## Appendix C: Live Platform URLs

| Service | URL |
|---------|-----|
| Frontend | https://informal-settlement-mapping-and-gro.vercel.app |
| Backend API | https://informal-settlement-mapping-and-growth-sm5w.onrender.com/api |
| Health Check | https://informal-settlement-mapping-and-growth-sm5w.onrender.com/api/health |

---

## ADDITIONAL FORMATTING NOTES FOR FINAL SUBMISSION

- Page numbers should be at the bottom centre.
- Word formatting: **Times New Roman**, font size **12**.
- Spacing between lines must be **1.5** for each paragraph.
- Chapter headings should be **centered**.
- Other headings and chapter bodies should be **justified**.
- Use roman numerals in numbering in chapter and sub-chapters’ bodies.
- Captions for figures should be at the bottom of figures.
- Captions for tables should be at the top of tables.
- Insert actual screenshots for Figures 5.1 to 5.4 before submission.
- Replace placeholder student names and registration numbers on the cover page.

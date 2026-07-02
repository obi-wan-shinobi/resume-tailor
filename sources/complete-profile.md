# Complete detailed profile

## \*\*Role: Software Developer

**Company:** Dalton Maag Ltd. | **Location:** London, UK (Remote) | Dates: Nov 2021 - Feb 2024

**Tech Stack:** TypeScript, Ruby on Rails, PostgreSQL, Python, ElectronJS, VueJS, Django, GitLab CI/CD

### **1. CJK (Chinese-Japanese-Korean) Automation via Genetic Algorithms**

- **The Problem:** CJK scripts contain ~4,000+ ideograms. Designing these across multiple axes (weight, width, slant) is an exponential task (e.g., 3 weights = 12,000 drawings).
- **The Solution:** Built a Python-based **Genetic Algorithm Proof of Concept (POC)**.
  - **Parameterization:** Researched ideogram structures to define parameters like stroke length, radical position, stroke width, and pressure.
  - **Evolutionary Learning:** The system learned these parameters from a "ground truth" set of ~100 designer-drawn glyphs.
  - **Automated Generation:** The GA evolved the remaining thousands of ideograms by optimizing parameters to match the aesthetic DNA of the training set.
- **Outcome:** Projected to reduce production time from **months of manual effort to minutes of automated generation**.

### **2. PriceBot: Financial Health Tracking & Revenue Protection**

- **The Problem:** An automated quoting tool (PriceBot) suffered from silent regressions where updates to underlying data models would over/underprice quotes. This lack of reliability meant managers reverted to manual spreadsheets, and potential revenue losses were in the six figures.
- **The Solution:** \* **Automated Monitoring:** Built a containerized health-tracking service that scraped metrics and compared them against business ground truths.
  - **CI/CD Integration:** Deployed via **GitLab CI/CD** as a scheduled daily job.
  - **Alerting:** Engineered an email and in-app notification system that warned users of pricing regressions in real-time.
- **Outcome:** Productionized the tool, increased organizational trust, and shifted workflow from hours of spreadsheet work to **seconds for automated quote generation**.

### **3. Non-Latin Glyph Complexity & Data Modeling**

- **The Problem:** Pricing font projects requires a "complexity" metric (effort to build). Existing models only covered ~300 simple glyphs. Scripts like Arabic, Greek, and Devanagari were poorly modeled due to ligatures and conjuncts.
- **The Solution:**
  - **Arabic/Cyrillic/Greek:** Refined models by distinguishing between "drawn" components (high complexity) and "accented/composite" components (low complexity).
  - **Devanagari:** Built a structural model from scratch by analyzing the logic of conjuncts and half-forms.
  - **Variable Axis Logic:** Integrated logic to scale complexity based on weight, width, and slant.
- **Outcome:** Expanded accurate pricing coverage from **~300 to ~2,500 glyphs**.

### **4. Graph-Based Project Scheduling Automation**

- **The Problem:** Typeface project planning was manual and non-linear. Designers had to account for dependencies (e.g., Italics cannot start until Regular is approved) and heuristic scaling (e.g., Bold weights take 1.6x the effort of Regular).
- **The Solution:** Modeled the entire development pipeline as a **Dependency Graph** in TypeScript.
  - **Heuristic Mapping:** Encoded effort-scaling variables (1.5x, 1.6x) into graph nodes.
  - **Constraint Resolution:** The algorithm automatically resolved which stages could run in parallel and which were sequential.
- **Outcome:** Reduced project planning time from **hours to minutes**.

### **5. DSedit: Internal Tooling Consolidation**

- **The Problem:** The Unified Font Object (UFO) spec is a complex directory of XML/PLIST files. Changing one font name requires updating `fontinfo.plist`, `groups.plist`, and potentially `.designspace` files. Manual edits were buggy and broke font compilation.
- **The Solution:** Developed **DSedit**, an **ElectronJS + VueJS** app with a **Django** backend.
  - **Abstraction:** The tool acted as a GUI for UFO/Designspace files.
  - **Automated Cascading Updates:** When a user changed an axis value or filename in the UI, the Django backend ensured every relevant XML table was updated correctly to maintain spec compliance.
- **Outcome:** Eliminated manual XML editing and prevented widespread font compilation failures.

---

## **Role: Machine Learning Research Scientist (Consulting)**

**Company:** Relfor Labs Pvt. Ltd. | **Dates:** Sept 2022 – Present

**Tech Stack:** PyTorch, PyTorch Lightning, NVIDIA DGX A100, Numba, Apache Arrow, Pandas, Python, Linux (NVIDIA DDP)

### **1. Edge-Optimized Model Architecture & Inference**

- **The Problem:** The task was audio transition detection (identifying class changes in real-time). The constraints were extreme: 512ms inference windows on resource-constrained Edge NPUs, requiring a 64-second historical context to make accurate predictions. Standard architectures were too compute-heavy for the sliding window requirements.
- **The Solution:** Engineered a **Decomposable CNN Architecture**.
  - **Hierarchical Weight Decomposition:** Built the model such that weights were structured into discrete blocks (512ms, 1s, 2s, 4s... up to 64s).
  - **Embedding Caching Strategy:** During inference, the system caches the embeddings of the previous 63.5 seconds. When the new 512ms segment arrives, the NPU only computes the features for that new segment and retrieves the rest from the cache, significantly reducing compute overhead.
  - **Training Methodology:** Forward and backpropagation were performed on the full 64s Mel-spectrogram data points, but the architecture was strictly enforced to remain decomposable for edge deployment.
- **Outcome:** Enabled real-time, low-latency execution on edge hardware that otherwise could not support 64s window processing.

### **2. Distributed Training Infrastructure**

- **The Problem:** High-resolution Mel-spectrogram time-series data is computationally expensive. Iteration cycles were too slow on standard hardware.
- **The Solution:** Developed a distributed training environment using **PyTorch Lightning** and **Distributed Data Parallel (DDP)** on an **NVIDIA DGX A100** cluster (8 GPUs, 256 cores, 1TB RAM).
- **Outcome:** Accelerated experimentation and model iteration cycles by **~50%**.

### **3. Terabyte-Scale Data Engineering (ETL)**

- **The Problem:** Preprocessing 13TB of raw audio data in UTF-8 format was a massive bottleneck. Traditional Python/Pandas operations were too slow and storage-inefficient.
- **The Solution:**
  - **Computation:** Leveraged **Numba JIT compilation** to optimize Python functions, achieving C/C++ execution speeds for data transformations.
  - **Storage & Memory:** Migrated data from UTF-8 to **Apache Arrow** binary format.
  - **Byte Addressability:** Implemented a byte-addressable storage model for raw data, allowing the system to retrieve any specific data slice without loading the entire file into memory.
- **Outcome:** Achieved an **8x speedup** in processing and a **30% reduction** in storage footprint.

---

## **Role: Machine Learning Engineer**

**Company:** Relfor Labs Pvt. Ltd. | **Dates:** Aug 2021 – Nov 2021

**Tech Stack:** PyTorch, CNN, Mel-spectrograms, InceptionNet (Base)

### **1. Audio Classification & Architecture Innovation**

- **The Problem:** Initial experimentation relied on generic architectures like InceptionNet, which were designed for 2D images and did not natively capture the nuances of 1D/2D audio Mel-spectrogram time-series.
- **The Solution:** Steered the research away from "off-the-shelf" models toward custom CNN architectures designed specifically for the spectral features of audio signals.
- **Outcome:** Achieved a baseline of **~98.6% accuracy** and **~0.98 F1-score** for audio signal classification.

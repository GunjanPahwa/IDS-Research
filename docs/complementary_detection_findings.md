# Complementary Anomaly Detection & Model Benchmark Report

**Project:** NIDS Research — Two-Stage & Unified Classification across 6 Datasets  
**Dataset Analyzed:** UNSW-NB15 Native (82,332 Test Samples, 60 Features)  
**Date:** September 15, 2026  

---

## Executive Summary

While supervised gradient boosting (XGBoost) achieves superior overall F1-score (`0.9219`) and ROC-AUC (`0.9852`), empirical evaluation of an unsupervised bottleneck Autoencoder (`0.8036` F1) reveals a key research finding: **unsupervised anomaly detection provides complementary coverage on attack categories where supervised models struggle.**

Specifically, the Autoencoder detected **572 attack flows (1.26% of all test attacks) that XGBoost missed entirely**, with **87.6% of those unique detections (501 flows) concentrated in the *Fuzzers* attack category** — XGBoost's weakest detection class. Conversely, the Autoencoder suffers severe blind spots on stealthy/probing attacks (*Reconnaissance* and *Shellcode*).

Additionally, evaluation of **TabNet** (attentive tabular deep learning) demonstrated state-of-the-art precision (`0.9269`) and accuracy (`0.9234`), reducing false positives on normal traffic by **~40%** compared to XGBoost, albeit at a ~270× higher CPU training time cost.

---

## 1. Per-Attack Category Recall Breakdown (UNSW-NB15 Native)

Cross-referencing predictions against ground-truth attack sub-types (`UNSW_NB15_testing-set.csv`):

| Attack Category | Test Count ($N$) | XGBoost Recall | Autoencoder Recall | Recall Delta | Caught by **AE Only** | Caught by **XGB Only** | Caught by **Both** | Missed by **Both** |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Analysis** | 677 | 96.60% | **97.93%** | **+1.33%** | **17** | 8 | 646 | 6 |
| **Backdoor** | 583 | **99.66%** | 94.17% | -5.49% | 0 | 32 | 549 | 2 |
| **DoS** | 4,089 | **99.80%** | 93.25% | -6.55% | 7 | 275 | 3,806 | 1 |
| **Exploits** | 11,132 | **99.00%** | 88.44% | -10.56% | 39 | 1,215 | 9,806 | 72 |
| **Fuzzers** | 6,062 | **76.92%** | 49.49% | -27.43% | **501** | 2,164 | 2,499 | 898 |
| **Generic** | 18,871 | **99.98%** | 99.18% | -0.80% | 1 | 152 | 18,716 | 2 |
| **Reconnaissance** | 3,496 | **99.80%** | 30.52% | -69.28% | 3 | 2,425 | 1,064 | 4 |
| **Shellcode** | 378 | **97.88%** | 10.58% | -87.30% | 4 | 334 | 36 | 4 |
| **Worms** | 44 | **100.00%** | 84.09% | -15.91% | 0 | 7 | 37 | 0 |
| *Normal (Benign)* | 37,000 | **84.17%** | 70.69% | -13.48% | - | - | - | - |

---

## 2. Complementary Detection & Venn Breakdown

Out of **45,332 total attack samples** in the UNSW-NB15 Native test set:

```
+-----------------------------------------------------------------------+
| TOTAL TEST ATTACKS: 45,332                                             |
|                                                                       |
|  [ Caught by BOTH XGBoost & Autoencoder ]                             |
|  37,159 flows (81.97%)                                                |
|                                                                       |
|  [ Caught by XGBoost ONLY ]           [ Caught by Autoencoder ONLY ]  |
|  6,612 flows (14.59%)                 572 flows (1.26%)               |
|                                       -> 501 are Fuzzers (87.6%)      |
|                                                                       |
|  [ MISSED BY BOTH - Joint Blind Spot ]                                |
|  989 flows (2.18%) -> 898 are Fuzzers (90.8%)                         |
+-----------------------------------------------------------------------+
```

### Key Technical Insights

1. **Fuzzers Complementary Detection**:
   * *Fuzzers* generate semi-randomized, mutated payloads to break parsers. Because the training set labels only a subset of these mutations, supervised tree splits in XGBoost fail to generalize to novel variations (yielding XGBoost's lowest recall of 76.92%).
   * The Autoencoder, trained strictly on benign baseline traffic, flags these novel mutations via elevated MSE reconstruction loss, catching **501 Fuzzers flows that bypassed XGBoost**.

2. **Reconnaissance & Shellcode Blind Spots**:
   * *Reconnaissance* (port sweeps) and *Shellcode* (compact payload execution) flows utilize standard TCP flags and low byte counts, producing feature distributions that mimic normal traffic.
   * Their median reconstruction errors ($0.0521$ and $0.0439$) are indistinguishable from benign traffic ($0.0508$), causing the Autoencoder to miss 89.4% of Shellcode and 69.5% of Reconnaissance.

---

## 3. Three-Way Model Benchmark (UNSW-NB15 Native)

| Model Architecture | Accuracy | Precision | Recall | F1-Score | ROC-AUC | CPU Train Time | Key Characteristic |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **XGBoost (Baseline)** | 0.9099 | 0.8820 | **0.9656** | 0.9219 | **0.9852** | **1.8s** | Super-fast, high overall recall |
| **TabNet** | **0.9234** | **0.9269** | 0.9347 | **0.9308** | 0.9816 | 492.8s (~8.2m) | Highest accuracy/precision, low FPR |
| **Autoencoder** | 0.7760 | 0.7767 | 0.8323 | 0.8036 | 0.8499 | 44.1s (~0.7m) | Zero-day/Fuzzers anomaly detection |

---

## 4. Architectural Recommendations

1. **XGBoost**: Primary workhorse model for scaling across all 6 datasets and feature spaces (Native, Common-7, Common-5). Exceptional compute-to-performance ratio.
2. **TabNet**: Selective benchmark for high-precision deployment where false alarms must be minimized. Keep as a proof-of-concept / selective deep learning baseline.
3. **Autoencoder**: Do not deploy as a standalone classifier due to stealth-attack blind spots. Retain its reconstruction error output as a **meta-feature in future ensemble models** to boost Fuzzers detection.

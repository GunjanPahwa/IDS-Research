# Label Analysis

This document provides a complete breakdown of labels, sample counts, and percentages for each dataset. This is essential due to the extreme class imbalances typical in IDS datasets.

## KDD99
- **Total Records**: 4,898,431

| Label | Sample Count | Percentage |
| :--- | :---: | :---: |
| smurf | 2,807,886 | 57.3222% |
| neptune | 1,072,017 | 21.8849% |
| normal | 972,781 | 19.8590% |
| satan | 15,892 | 0.3244% |
| ipsweep | 12,481 | 0.2548% |
| portsweep | 10,413 | 0.2126% |
| nmap | 2,316 | 0.0473% |
| back | 2,203 | 0.0450% |
| warezclient | 1,020 | 0.0208% |
| teardrop | 979 | 0.0200% |
| pod | 264 | 0.0054% |
| guess_passwd | 53 | 0.0011% |
| buffer_overflow | 30 | 0.0006% |
| land | 21 | 0.0004% |
| warezmaster | 20 | 0.0004% |
| imap | 12 | 0.0002% |
| rootkit | 10 | 0.0002% |
| loadmodule | 9 | 0.0002% |
| ftp_write | 8 | 0.0002% |
| multihop | 7 | 0.0001% |
| phf | 4 | 0.0001% |
| perl | 3 | 0.0001% |
| spy | 2 | 0.0000% |

## NSL-KDD (KDDTrain+.txt)
- **Total Records**: 125,973

| Label | Sample Count | Percentage |
| :--- | :---: | :---: |
| normal | 67,343 | 53.4583% |
| neptune | 41,214 | 32.7165% |
| satan | 3,633 | 2.8840% |
| ipsweep | 3,599 | 2.8570% |
| portsweep | 2,931 | 2.3267% |
| smurf | 2,646 | 2.1005% |
| nmap | 1,493 | 1.1852% |
| back | 956 | 0.7589% |
| teardrop | 892 | 0.7081% |
| warezclient | 890 | 0.7065% |
| pod | 201 | 0.1596% |
| guess_passwd | 53 | 0.0421% |
| buffer_overflow | 30 | 0.0238% |
| warezmaster | 20 | 0.0159% |
| land | 18 | 0.0143% |
| imap | 11 | 0.0087% |
| rootkit | 10 | 0.0079% |
| loadmodule | 9 | 0.0071% |
| ftp_write | 8 | 0.0064% |
| multihop | 7 | 0.0056% |
| phf | 4 | 0.0032% |
| perl | 3 | 0.0024% |
| spy | 2 | 0.0016% |

## NSL-KDD (KDDTest+.txt)
- **Total Records**: 22,544

| Label | Sample Count | Percentage |
| :--- | :---: | :---: |
| normal | 9,711 | 43.0758% |
| neptune | 4,657 | 20.6574% |
| guess_passwd | 1,231 | 5.4604% |
| mscan | 996 | 4.4180% |
| warezmaster | 944 | 4.1874% |
| apache2 | 737 | 3.2692% |
| satan | 735 | 3.2603% |
| processtable | 685 | 3.0385% |
| smurf | 665 | 2.9498% |
| back | 359 | 1.5924% |
| snmpguess | 331 | 1.4682% |
| saint | 319 | 1.4150% |
| mailbomb | 293 | 1.2997% |
| snmpgetattack | 178 | 0.7896% |
| portsweep | 157 | 0.6964% |
| ipsweep | 141 | 0.6254% |
| httptunnel | 133 | 0.5900% |
| nmap | 73 | 0.3238% |
| pod | 41 | 0.1819% |
| buffer_overflow | 20 | 0.0887% |
| multihop | 18 | 0.0798% |
| named | 17 | 0.0754% |
| ps | 15 | 0.0665% |
| sendmail | 14 | 0.0621% |
| rootkit | 13 | 0.0577% |
| xterm | 13 | 0.0577% |
| teardrop | 12 | 0.0532% |
| xlock | 9 | 0.0399% |
| land | 7 | 0.0311% |
| xsnoop | 4 | 0.0177% |
| ftp_write | 3 | 0.0133% |
| sqlattack | 2 | 0.0089% |
| udpstorm | 2 | 0.0089% |
| perl | 2 | 0.0089% |
| worm | 2 | 0.0089% |
| phf | 2 | 0.0089% |
| loadmodule | 2 | 0.0089% |
| imap | 1 | 0.0044% |

## NSL-KDD (KDDTest-21.txt)
- **Total Records**: 11,850

| Label | Sample Count | Percentage |
| :--- | :---: | :---: |
| normal | 2,152 | 18.1603% |
| neptune | 1,579 | 13.3249% |
| guess_passwd | 1,231 | 10.3882% |
| mscan | 996 | 8.4051% |
| warezmaster | 944 | 7.9662% |
| apache2 | 737 | 6.2194% |
| satan | 727 | 6.1350% |
| processtable | 685 | 5.7806% |
| smurf | 627 | 5.2911% |
| back | 359 | 3.0295% |
| snmpguess | 331 | 2.7932% |
| saint | 309 | 2.6076% |
| mailbomb | 293 | 2.4726% |
| snmpgetattack | 178 | 1.5021% |
| portsweep | 156 | 1.3165% |
| ipsweep | 141 | 1.1899% |
| httptunnel | 133 | 1.1224% |
| nmap | 73 | 0.6160% |
| pod | 41 | 0.3460% |
| buffer_overflow | 20 | 0.1688% |
| multihop | 18 | 0.1519% |
| named | 17 | 0.1435% |
| ps | 15 | 0.1266% |
| sendmail | 14 | 0.1181% |
| rootkit | 13 | 0.1097% |
| xterm | 13 | 0.1097% |
| teardrop | 12 | 0.1013% |
| xlock | 9 | 0.0759% |
| land | 7 | 0.0591% |
| xsnoop | 4 | 0.0338% |
| ftp_write | 3 | 0.0253% |
| loadmodule | 2 | 0.0169% |
| sqlattack | 2 | 0.0169% |
| phf | 2 | 0.0169% |
| perl | 2 | 0.0169% |
| udpstorm | 2 | 0.0169% |
| worm | 2 | 0.0169% |
| imap | 1 | 0.0084% |

## UNSW-NB15 (UNSW_NB15_training-set.csv)
- **Total Records**: 175,341

| Label | Sample Count | Percentage |
| :--- | :---: | :---: |

### Multiclass Labels (`attack_cat`)
| Label | Sample Count | Percentage |
| :--- | :---: | :---: |
| Normal | 56,000 | 31.9378% |
| Generic | 40,000 | 22.8127% |
| Exploits | 33,393 | 19.0446% |
| Fuzzers | 18,184 | 10.3706% |
| DoS | 12,264 | 6.9944% |
| Reconnaissance | 10,491 | 5.9832% |
| Analysis | 2,000 | 1.1406% |
| Backdoor | 1,746 | 0.9958% |
| Shellcode | 1,133 | 0.6462% |
| Worms | 130 | 0.0741% |

### Binary Labels (`label`)
| Label | Sample Count | Percentage |
| :--- | :---: | :---: |
| Attack (1) | 119,341 | 68.0622% |
| Benign (0) | 56,000 | 31.9378% |

## UNSW-NB15 (UNSW_NB15_testing-set.csv)
- **Total Records**: 82,332

| Label | Sample Count | Percentage |
| :--- | :---: | :---: |

### Multiclass Labels (`attack_cat`)
| Label | Sample Count | Percentage |
| :--- | :---: | :---: |
| Normal | 37,000 | 44.9400% |
| Generic | 18,871 | 22.9206% |
| Exploits | 11,132 | 13.5209% |
| Fuzzers | 6,062 | 7.3629% |
| DoS | 4,089 | 4.9665% |
| Reconnaissance | 3,496 | 4.2462% |
| Analysis | 677 | 0.8223% |
| Backdoor | 583 | 0.7081% |
| Shellcode | 378 | 0.4591% |
| Worms | 44 | 0.0534% |

### Binary Labels (`label`)
| Label | Sample Count | Percentage |
| :--- | :---: | :---: |
| Attack (1) | 45,332 | 55.0600% |
| Benign (0) | 37,000 | 44.9400% |

## CIC-IDS2017 (Friday-WorkingHours-Afternoon-DDos.pcap_ISCX.csv)
- **Total Records**: 225,745

| Label | Sample Count | Percentage |
| :--- | :---: | :---: |
| DDoS | 128,027 | 56.7131% |
| BENIGN | 97,718 | 43.2869% |

## CIC-IDS2017 (Friday-WorkingHours-Afternoon-PortScan.pcap_ISCX.csv)
- **Total Records**: 286,467

| Label | Sample Count | Percentage |
| :--- | :---: | :---: |
| PortScan | 158,930 | 55.4793% |
| BENIGN | 127,537 | 44.5207% |

## CIC-IDS2017 (Friday-WorkingHours-Morning.pcap_ISCX.csv)
- **Total Records**: 191,033

| Label | Sample Count | Percentage |
| :--- | :---: | :---: |
| BENIGN | 189,067 | 98.9709% |
| Bot | 1,966 | 1.0291% |

## CIC-IDS2017 (Monday-WorkingHours.pcap_ISCX.csv)
- **Total Records**: 529,918

| Label | Sample Count | Percentage |
| :--- | :---: | :---: |
| BENIGN | 529,918 | 100.0000% |

## CIC-IDS2017 (Thursday-WorkingHours-Afternoon-Infilteration.pcap_ISCX.csv)
- **Total Records**: 288,602

| Label | Sample Count | Percentage |
| :--- | :---: | :---: |
| BENIGN | 288,566 | 99.9875% |
| Infiltration | 36 | 0.0125% |

## CIC-IDS2017 (Thursday-WorkingHours-Morning-WebAttacks.pcap_ISCX.csv)
- **Total Records**: 170,366

| Label | Sample Count | Percentage |
| :--- | :---: | :---: |
| BENIGN | 168,186 | 98.7204% |
| Web Attack � Brute Force | 1,507 | 0.8846% |
| Web Attack � XSS | 652 | 0.3827% |
| Web Attack � Sql Injection | 21 | 0.0123% |

## CIC-IDS2017 (Tuesday-WorkingHours.pcap_ISCX.csv)
- **Total Records**: 445,909

| Label | Sample Count | Percentage |
| :--- | :---: | :---: |
| BENIGN | 432,074 | 96.8973% |
| FTP-Patator | 7,938 | 1.7802% |
| SSH-Patator | 5,897 | 1.3225% |

## CIC-IDS2017 (Wednesday-workingHours.pcap_ISCX.csv)
- **Total Records**: 692,703

| Label | Sample Count | Percentage |
| :--- | :---: | :---: |
| BENIGN | 440,031 | 63.5238% |
| DoS Hulk | 231,073 | 33.3582% |
| DoS GoldenEye | 10,293 | 1.4859% |
| DoS slowloris | 5,796 | 0.8367% |
| DoS Slowhttptest | 5,499 | 0.7938% |
| Heartbleed | 11 | 0.0016% |

## CSE-CIC-IDS2018 (Botnet-Friday-02-03-2018_TrafficForML_CICFlowMeter.parquet)
- **Total Records**: 771,587

| Label | Sample Count | Percentage |
| :--- | :---: | :---: |
| Benign | 627,052 | 81.2678% |
| Bot | 144,535 | 18.7322% |

## CSE-CIC-IDS2018 (Bruteforce-Wednesday-14-02-2018_TrafficForML_CICFlowMeter.parquet)
- **Total Records**: 619,346

| Label | Sample Count | Percentage |
| :--- | :---: | :---: |
| Benign | 525,245 | 84.8064% |
| SSH-Bruteforce | 94,048 | 15.1851% |
| FTP-BruteForce | 53 | 0.0086% |

## CSE-CIC-IDS2018 (DDoS1-Tuesday-20-02-2018_TrafficForML_CICFlowMeter.parquet)
- **Total Records**: 954,846

| Label | Sample Count | Percentage |
| :--- | :---: | :---: |
| DDoS attacks-LOIC-HTTP | 575,364 | 60.2573% |
| Benign | 379,482 | 39.7427% |

## CSE-CIC-IDS2018 (DDoS2-Wednesday-21-02-2018_TrafficForML_CICFlowMeter.parquet)
- **Total Records**: 561,396

| Label | Sample Count | Percentage |
| :--- | :---: | :---: |
| Benign | 360,805 | 64.2693% |
| DDOS attack-HOIC | 198,861 | 35.4226% |
| DDOS attack-LOIC-UDP | 1,730 | 0.3082% |

## CSE-CIC-IDS2018 (DoS1-Thursday-15-02-2018_TrafficForML_CICFlowMeter.parquet)
- **Total Records**: 794,812

| Label | Sample Count | Percentage |
| :--- | :---: | :---: |
| Benign | 743,498 | 93.5439% |
| DoS attacks-GoldenEye | 41,406 | 5.2095% |
| DoS attacks-Slowloris | 9,908 | 1.2466% |

## CSE-CIC-IDS2018 (DoS2-Friday-16-02-2018_TrafficForML_CICFlowMeter.parquet)
- **Total Records**: 591,873

| Label | Sample Count | Percentage |
| :--- | :---: | :---: |
| Benign | 446,619 | 75.4586% |
| DoS attacks-Hulk | 145,199 | 24.5321% |
| DoS attacks-SlowHTTPTest | 55 | 0.0093% |

## CSE-CIC-IDS2018 (Infil1-Wednesday-28-02-2018_TrafficForML_CICFlowMeter.parquet)
- **Total Records**: 456,873

| Label | Sample Count | Percentage |
| :--- | :---: | :---: |
| Benign | 400,424 | 87.6445% |
| Infilteration | 56,449 | 12.3555% |

## CSE-CIC-IDS2018 (Infil2-Thursday-01-03-2018_TrafficForML_CICFlowMeter.parquet)
- **Total Records**: 249,170

| Label | Sample Count | Percentage |
| :--- | :---: | :---: |
| Benign | 187,136 | 75.1037% |
| Infilteration | 62,034 | 24.8963% |

## CSE-CIC-IDS2018 (Web1-Thursday-22-02-2018_TrafficForML_CICFlowMeter.parquet)
- **Total Records**: 830,224

| Label | Sample Count | Percentage |
| :--- | :---: | :---: |
| Benign | 829,883 | 99.9589% |
| Brute Force -Web | 228 | 0.0275% |
| Brute Force -XSS | 79 | 0.0095% |
| SQL Injection | 34 | 0.0041% |

## CSE-CIC-IDS2018 (Web2-Friday-23-02-2018_TrafficForML_CICFlowMeter.parquet)
- **Total Records**: 829,405

| Label | Sample Count | Percentage |
| :--- | :---: | :---: |
| Benign | 828,864 | 99.9348% |
| Brute Force -Web | 340 | 0.0410% |
| Brute Force -XSS | 150 | 0.0181% |
| SQL Injection | 51 | 0.0061% |

## UWF ZeekData
- **Total Records**: 454,846

| Label | Sample Count | Percentage |
| :--- | :---: | :---: |

### Target: `label_binary`
| Label | Sample Count | Percentage |
| :--- | :---: | :---: |
| False | 454,846 | 100.0000% |

### Target: `label_tactic`
| Label | Sample Count | Percentage |
| :--- | :---: | :---: |
| none | 454,846 | 100.0000% |

### Target: `label_technique`
| Label | Sample Count | Percentage |
| :--- | :---: | :---: |
| none | 454,846 | 100.0000% |

### Target: `label_cve`
| Label | Sample Count | Percentage |
| :--- | :---: | :---: |
| none | 454,846 | 100.0000% |


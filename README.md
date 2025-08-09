## Dataset Structure

The dataset is organized into iterations, each containing extracted participant data and a merged ZIP archive of participant files.

```
larfdield_dataset  
└── iteration_1  
│   ├── extracted_files  
│   │   └── [person_hash]  
│   │       ├── metrics.json  
│   │       ├── POLAR_B2E7B722_v1_2023-06-26T10-07-00-664  
│   │       │   ├── ACC.csv  
│   │       │   ├── ECG.csv  
│   │       │   ├── HR.csv  
│   │       │   └── metadata.json  
│   │       ├── POLAR_XXXXXXX_v1_2023-07-01T14-32-00-123  
│   │       │   ├── ACC.csv  
│   │       │   ├── ECG.csv  
│   │       │   ├── HR.csv  
│   │       │   └── metadata.json  
│   │       └── ...  
│   └── zip_participants_merged  
└── iteration_N  
    ├── extracted_files  
    │   └── [person_hash]  
    │       ├── metrics.json  
    │       ├── POLAR_B2E7B722_v1_2023-06-26T10-07-00-664  
    │       │   ├── ACC.csv  
    │       │   ├── ECG.csv  
    │       │   ├── HR.csv  
    │       │   └── metadata.json  
    │       ├── POLAR_YYYYYYY_v1_2023-07-15T09-11-45-987  
    │       │   ├── ACC.csv  
    │       │   ├── ECG.csv  
    │       │   ├── HR.csv  
    │       │   └── metadata.json  
    │       └── ...  
    └── zip_participants_merged

```
   
### `metrics.json` Proposal

Each `metrics.json` file is stored in the root folder of a participant (`[person_hash]`) and contains quality metrics for each recorded `POLAR_...` session.  
Example:

```json
{
    "POLAR_B2E7B722_v1_2023-06-26T10-07-00-664": {
        "ecg_signal_quality": {
            "neurokit": 0.8,
            "biosppy": 0.6
        }
    },
    "POLAR_B2E7B722_v1_2023-06-26T11-27-50-637": {
        "ecg_signal_quality": {
            "neurokit": 0.7,
            "biosppy": 0.5
        }
    }
}
```

`metrics.json` — aggregated quality metrics for all sessions of the participant.


## Dataset Structure

The dataset consists of two main parts: raw, unpacked data (larfield) and the original compressed files (larfield_zipped).

```
data/
├── larfield/
│   ├── iteration_01/
│   │   └── [person_hash]/
│   │       ├── POLAR_B2E7B722_v1_2023-06-26T10-07-00-664/
│   │       │   ├── ACC.csv
│   │       │   ├── ECG.csv
│   │       │   ├── HR.csv
│   │       │   ├── metadata.json
│   │       │   └── metrics.json
│   │       ├── POLAR_XXXXXXX_v1_2023-07-01T14-32-00-123/
│   │       │   ├── ACC.csv
│   │       │   ├── ECG.csv
│   │       │   ├── HR.csv
│   │       │   ├── metadata.json
│   │       │   └── metrics.json
│   │       └── ...
│   ├── iteration_02/
│   │   └── [person_hash]/
│   │       ├── POLAR_B2E7B722_v1_2023-06-26T10-07-00-664/
│   │       │   ├── ACC.csv
│   │       │   ├── ECG.csv
│   │       │   ├── HR.csv
│   │       │   ├── metadata.json
│   │       │   └── metrics.json
│   │       ├── POLAR_YYYYYYY_v1_2023-07-15T09-11-45-987/
│   │       │   ├── ACC.csv
│   │       │   ├── ECG.csv
│   │       │   ├── HR.csv
│   │       │   ├── metadata.json
│   │       │   └── metrics.json
│   │       └── ...
│   └── ...
└── larfield_zipped/
    ├── iteration_01/
    │   └── zip_participants_merged/
    │       └── [person_hash]/
    │           ├── POLAR_B2E7B722_v1_2023-06-26T10-07-00-664.zip
    │           ├── POLAR_XXXXXXX_v1_2023-07-01T14-32-00-123.zip
    │           └── ...
    ├── iteration_02/
    │   └── zip_participants_merged/
    │       └── [person_hash]/
    │           ├── POLAR_B2E7B722_v1_2023-06-26T10-07-00-664.zip
    │           ├── POLAR_YYYYYYY_v1_2023-07-15T09-11-45-987.zip
    │           └── ...
    └── ...
```
   
### `metrics.json` Proposal

Each `metrics.json` file is stored in the root folder of a participant (`[person_hash]`) and contains quality metrics for each recorded `POLAR_...` session.  
Example:

```json
{
  "ecg_signal_quality": {
    "neurokit": 0.8,
    "biosppy": 0.6
  }
}
```

`metrics.json` — aggregated quality metrics for each session.

# How to use:

1. Place the **LarField** dataset in the `data/` folder and name it `larfield_zipped`
2. Unzip the dataset into the `larfield/` folder by running: `python src/dataset_operations/unzip.py`
3. Enter the ./src directory: `cd ./src`
4. Evaluate the ECG signal quality using the following script: `python signal_quality_evaluation.py`
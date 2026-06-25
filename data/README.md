# Data

This project uses drive-end accelerometer data from the
[CWRU Bearing Data Center](https://engineering.case.edu/bearingdatacenter).

**Sampling rate:** 12 kHz  
**Sensor:** Drive-end accelerometer

## Required files

Download the following `.mat` files and place them directly in this `data/`
directory. The files are **not committed** to the repository.

| File | Description | Variable of interest |
|------|-------------|----------------------|
| `Normal_1.mat` | Normal baseline — 1 HP load, ~1772 rpm | `X098_DE_time` |
| `IR007_1.mat` | Inner race fault — 0.007" defect, load 1 | `X108_DE_time` |
| `B007_1.mat` | Ball fault — 0.007" defect, load 1 | `X122_DE_time` |
| `OR007@6_1.mat` | Outer race fault — 0.007" defect, centred at 6 o'clock, load 1 | `X135_DE_time` |

## Where to download

1. Go to <https://engineering.case.edu/bearingdatacenter>
2. Navigate to **Bearing Data** → **12k Drive End Bearing Fault Data**
3. Download the files listed above (they may be served as individual `.mat`
   files or bundled in a zip archive — extract to this folder either way).

## Notes

- All files are MATLAB v5 format and can be loaded with `scipy.io.loadmat`.
- Each `.mat` file may contain multiple variables; only the `DE_time`
  (drive-end) channel listed above is used in this project.
- The normal baseline file is labelled `98.mat` on the CWRU site and contains
  the variable `X098_DE_time`.

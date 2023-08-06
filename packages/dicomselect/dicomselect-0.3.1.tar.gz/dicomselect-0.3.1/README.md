# dicomselect

# Create a new database
```python
from pathlib import Path
from dicomselect.database import Database

db_path = Path('dicomselect_archive.db')
db_path.parent.mkdir(parents=True, exist_ok=True)
db = Database(db_path)
db.create('/path/to/archive', max_workers=4)
```

# Select scans
1. Simple matching of values
```python
from dicomselect.database import Database

mapping = {
    "t2w": {
        "SeriesDescription": [
            "t2_tse_tra_snel_bij bewogen t2 tra",
            "t2_tse_tra",        
            "t2_tse_tra_prostate",
            "t2_tse_tra_snel",
            "t2_tse_tra_Grappa3"
        ]
    },
}

db = Database('/path/to/dicomselect_archive.db').open()
query = db.where("series_description", 'in', mapping["t2w"]["SeriesDescription"])
```

2. Pattern matching and combining queries
```python
from dicomselect.database import Database

mapping = {
    "hbv": {
        "SeriesDescription": [
            "ep2d_diff_tra%CALC_BVAL",
            "diffusie-3Scan-4bval_fsCALC_BVAL"
        ],
        "ImageType": [
            r"DERIVED\PRIMARY\DIFFUSION\CALC_BVALUE\TRACEW\DIS2D\DFC",
            r"DERIVED\PRIMARY\DIFFUSION\CALC_BVALUE\TRACEW\DIS2D",
            r"DERIVED\PRIMARY\DIFFUSION\CALC_BVALUE\TRACEW\ND\DFC",
            r"DERIVED\PRIMARY\DIFFUSION\CALC_BVALUE\TRACEW\NORM\DIS2D",
        ]
    }
}

db = Database('/path/to/dicomselect_archive.db').open()
query1 = db.where("series_description", "LIKE", mapping["hbv"]["SeriesDescription"])
query2 = db.where("image_type", "LIKE", mapping["hbv"]["ImageType"])
query = query1.union(query2)
db.close()
```

# Show info
```python
query.info().filter("series_description").print()
```

# Convert

```python
from dicomselect.database import Database

db = Database('/path/to/dicomselect_archive.db')
plan = db.plan('{patient_id}/{series_description}_{patient_age}', query)
plan.target_dir = '/path/to/target_dir'
plan.extension = '.mha'
plan.print()
plan.execute(max_workers=4)
```

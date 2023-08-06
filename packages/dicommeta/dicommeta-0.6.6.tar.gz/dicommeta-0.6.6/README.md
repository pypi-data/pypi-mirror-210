# DicomMeta

dicommeta is a Python library for efficiently storing large amounts of Dicom Metadata

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install dicommeta.

```bash
pip install dicommeta
```

## Usage

```python
from pprint import pprint

from dicommeta.Utils import Mode
from dicommeta.Struct import Study, Series, Instance

new_dicom_study = Study(
                        StudyInstanceUID='1.3.6.1.4.1.14519.5.2.1.4334.1501.757929841898426427124434115918',
                        SpecificCharacterSet='ISO_IR 100',
                        StudyDate="20190701",
                        StudyTime='023750',
                        AccessionNumber='sdfk324234',
                        ReferringPhysicianName='Dr Strange',
                        PatientName='John Doe',
                        PatientID='A123',
                        StudyUID='study001',
                        PatientBirthDate='20000101',
                        mode=Mode.CT)

new_series01 = Series(seriesUID='series001')
new_series01.add_instance(Instance(SOPinstanceUID='Instance001'))
new_series01.add_instance(Instance(SOPinstanceUID='Instance002'))
new_series01.add_instance(Instance(SOPinstanceUID='Instance002'))
new_dicom_study.add_series(new_series01)
new_series11 = Series(seriesUID='series001')
new_series11.add_instance(Instance(SOPinstanceUID='Instance002'))
new_dicom_study.add_series(new_series11)
new_series11.add_instance(Instance(SOPinstanceUID='Instance003'))
new_dicom_study.add_series(new_series11)

new_series02 = Series(seriesUID='series002')
new_series02.add_instance(Instance(SOPinstanceUID='Instance002'))
new_series02.add_instance(Instance(SOPinstanceUID='Instance003'))
new_dicom_study.add_series(new_series02)

pprint(new_dicom_study.get_dict())
pprint(new_dicom_study.get_series(seriesUID='series002'))

new_study01 = Study(StudyUID='study002', StudyDate=['20200101'])
new_series03 = Series(seriesUID='series003')
new_series03.add_instance(Instance(SOPinstanceUID='Instance01'))
new_study01.add_series(new_series03)

study_list = [new_dicom_study, new_study01]

for study in study_list:
    for instance in study.series_dict:
        pprint(study.get_series(instance))
        print("")

print(new_dicom_study.get_series_ids())

print(new_dicom_study.study_datetime)
print(new_dicom_study.patient_age)

print(new_study01.study_datetime)
print(new_study01.patient_age)


```

## Contributing

Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License

[MIT](https://choosealicense.com/licenses/mit/)
# abuscom-airflow-package



## Getting started

create vurtual environmen
```
python3 -m venv /Users/leonhardholzer/python/3.9

```

use virtual environment

```
source /Users/leonhardholzer/python/3.9/bin/activate
```


install airflow dependencies

```
pip install "apache-airflow[postgres]==2.4.3" --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-2.4.3/constraints-3.9.txt"
```



install module locally

```
pip install .
```

or

```
pip install --upgrade .
```

create distribution
 
```
python setup.py sdist
```

deploy to py test

```
pip install twine 

twine upload --repository-url https://test.pypi.org/legacy/ dist/abuscom-libs-0.1.0.tar.gz       
```

package signieren
```
gpg --detach-sign -a dist/abuscom-libs-0.1.0.tar.gz
```

deploy to py

```
twine upload dist/abuscom-libs-0.1.0.tar.gz dist/abuscom-libs-0.1.0.tar.gz.as
```
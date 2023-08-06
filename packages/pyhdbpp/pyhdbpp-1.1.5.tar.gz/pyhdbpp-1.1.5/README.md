# Python HdbReader

HDB++ is the Tango Control System Archiving Service.
This python3 module provides extraction from multiple hdb++ engines using AbstractReader class API.
For legacy archiving and full hdb++ api (MySQL only) use PyTangoArchiving instead.

www.tango-controls.org
https://gitlab.com/tango-controls/hdbpp

Other related projects providing similar functionality, but not AbstractReader class implementation:

 - https://gitlab.com/tango-controls/hdbpp/pytangoarchiving : provides legacy and HDB++ extraction and configuratio api's (python 2 only)

 - https://github.com/dvjdjvu/hdbpp : python 3 API for extraction/configuration of MySQL/PostgreSQL HDB++ databases, by djvu@inbox.ru


## Install

Just use pip3 :
```
pip3 install pyhdbpp
```

To install run from the project directory :
```
python3 -m pip install .

```

## Configure

There are several methods to instantiate an HDB++ Reader object.

This examples use the TangoBOX virtual image as example :

  https://gitlab.com/tango-controls/tangobox

You can pass the arguments to the reader object :
```
import pyhdbpp
rd = pyhdbpp.reader(
    apiclass = 'pyhdbpp.mariadb.MariaDBReader',
    config = '<user>:<passwd>@<host>:<port>/<db_name>'
    )
```

Or you can pre-configure a default reader using free-properties in the Tango Database :

![pyhdbpp_tangobox_config](doc/pyhdbpp_tangobox_config.png "pyhdbpp config")

In this case, the reader is instantiated just doing:
```
rd = pyhdbpp.get_default_reader()
```

## Extraction

NOTE: Before extracting data from any Tango attribute, it MUST be previously added into HDB++. You may use the hdbconfigurator tool for that purpose :

  https://gitlab.com/tango-controls/hdbpp/hdbpp-configurator 

### Extracting from python

Once the reader object have been created, extract data directly from python :
```
In [1]: import pyhdbpp

In [2]: rd = pyhdbpp.get_default_reader()

In [3]: values = rd.get_attribute_values('sys/tg_test/1/double_scalar','2022-12-24','2023-01-31')

In [4]: len(values)
Out[4]: 1107347

In [5]: values[0]
Out[5]: (1671836401.276, 228.09756225059553, 0, None)
```

### Plotting with taurus

Taurus is an python3 framework for building SCADA user interfaces (Qt) :
  https://taurus-scada.org/

You can plot your data from any python application using taurus (pyqtgraph); it requires configuring your DefaultReader in the Tango Database :
```
$ pip3 install taurus 
$ pip3 install --upgrade taurus-pyqtgraph pyhdbpp
$ taurus trend sys/tg_test/1_double_scalar
```

et voila!
![doc/pyhdbpp_taurus_trend.png](doc/pyhdbpp_taurus_trend.png "doc/pyhdbpp_taurus_trend.png")

# Unit Converter

Unit Converter is a simple python unit converter, that can help you convert various units.

For more information see the documentation [Unit Converter Documentation](https://erimac2.github.io/UnitConverter/).

## Installation

You can install the Real Python Feed Reader from [PyPI](https://pypi.org/project/realpython-reader/):

    python -m pip install realpython-reader

The reader is supported on Python 3.11.0 and above.

## How to use

Unit converter is a Python code package, named `unitconverter.converter`. To use the package, first import it:
    >>> from unitconverter import converter

You can then call various conversion modules:

    >>> converter.convertLength(5, "cm", "m")
    [0.05]
    >>> converter.convertWeight(5, "kg", "g")
    [5000.0]
    >>> converter.convertEnergy(5, "kcal", "J")
    [20920.0]
    >>> converter.convertData(5, "Mb", "mb")
    [40.0]
    >>> converter.convertSpeed(5, "km/h", "m/s")
    [1.38889]
    >>> converter.convertVolume(5, "L", "ml")
    [5000.0]
    >>> converter.convertPressure(5, "psi", "bar")
    [0.344738]
    >>> converter.convertTime(5, "day", "h")
    [120]
    >>> converter.convertTemperature(5, "C", "K")
    [278.15]

You can also import individual modules and use them to convert units:

    >>> from unitconverter.converter import convertLength
    >>> converter.convertLength(5, "cm", "m")
    [0.05]

## License

This package is licensed under the MIT license.

## Release History

**1.0.0**

* Initial release
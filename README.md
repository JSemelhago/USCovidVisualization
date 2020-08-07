# USCovidVisualization

Python scripts that will create a 3D visualization of a choropleth map for Covid-19 cases per capita by county

## Description

### Installation

Use `git clone` to clone this repository in your local directory. 

### Prerequisites

`scripts/USCovidAnalysis.py` requires `Python3` to run. All of the packages it uses can be installed by using `pip3` from the `PyPI` channel. Running this script requires a stable Internet connection in order to generate properly formatted input files as the most recent Covid data is scraped from [USAFacts](https://usafacts.org/visualizations/coronavirus-covid-19-spread-map/).

`scripts/USCovidQGIS.py` can be run using `Python3` but requires the `qgis` package. To get the visual output of the layers produced, the QGIS application should be used. Furthermore, the QGIS application is required to produce the final 3D choropleth map because the `Qgis2threejs` plugin is required.

## Running it

### Steps to Run

1. Run `python3 USCovidAnalysis.py` first to produce the input files
2. Open QGIS and upload `USCovidQGIS.py` to the QGIS Python console and run it
3. Once the layers have been generated, install the `Qgis2threejs` plugin 
4. Upload `USCovidLayers.qgz.qto3settings` and save the 3D choropleth output as a `html` file

### Built With

The following tools were used to build this project:

* [PyCharm](https://www.jetbrains.com/pycharm/) - Python/IPython IDE
* [Python 3.8.5](https://www.python.org/) - Language used
* [QGIS 3.14 ("Pi")](https://qgis.org/en/site/) - Geography processing tool
* [pip3](https://pip.pypa.io/en/stable/) - Package installer


## Output

### HTML

The `html` outputs will not run locally so it is important to run the program again to generate useable `html` files. A choropleth map produced by `plotly` is downloaded as well as the 3D choropleth map by `Qgis2threejs`.

### Screenshots

Because the `html` outputs cannot be run locally, sample screenshots found under `output/screenshots/` were taken for when the program was run on July 17th, 2020.

### `.csv` Files

In order to get Covid per capita, it was necessary to download a population file and format the Covid county data to match the `.geojson` county names. The outputted `.csv` file is used as an input file in the QGIS script.


## Author

**Justin Semelhago** - produced initial release

## License

This project is currently licensed under [Creative Commons Zero v1.0 Universal](https://creativecommons.org/licenses/) license.



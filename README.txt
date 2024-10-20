Pegel Plugin for QGIS


Pegel Plugin is a QGIS plugin designed to visualize Pegel stations across Germany, providing real-time water level measurements and other related data12.

Features

Visualize Pegel Stations: Displays Pegel stations with their current water levels, temperatures, and more2.
Interactive Map: Hover over points to see station details and measurement values.
Graphical Analysis: View 30-day water level trends for selected stations.
User-Friendly Interface: Easy-to-navigate UI with station list, graph display, and control buttons.
Installation
Clone the repository:
git clone https://github.com/yourusername/pegel-plugin.git

Open QGIS and navigate to the Plugin Manager.
Install the plugin from the cloned repository.
Usage
Click the Pegel Plugin icon in QGIS.
Select a station from the list to view its details.
Click the “Graph” button to see the 30-day water level graph3.
Use the “Instructions” button for a detailed guide on using the plugin.
Development
Main Configuration: __init__.py
Modules: Contains layers, styles, and scripts to fetch data from the Pegel API.
Contributing
Feel free to fork the repository and submit pull requests. For major changes, please open an issue first to discuss what you would like to change.

# Modelling-COVID-19-Spread

A Data Analytics project: Geometric modelling of COVID-19 epidemic spread in a supermarket.

Main Code TODOs:
- Create a store graph/network
- Create paths for users (possible paths and chosen paths)
- Create model for virus transmission (distance, R value, etc.)
- Create simulation implementation

## Usage

Install required libraries:

```
python -m pip install networkx pyglet
```

Execute the main script:

```
python ./covid_spread_model/simulation.py
```

## Implementation

The simulation currently supports the construction of a configurable store which takes the form of a NetworkX graph. The simulation can also generate customers that want to visit a random list of sections in the store and determine the optimal path from the store entrance to the store exit that also visits each of those sections.

Simple visualisation has also been implemented which can draw the layout of the store and the path a customer will take.

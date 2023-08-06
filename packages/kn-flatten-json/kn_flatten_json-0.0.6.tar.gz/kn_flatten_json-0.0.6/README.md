
# Project description
Kpt-flatten-json pypi package helps to flatten a dataframe containing complex datatypes like arrays and structures.



## Installation

$ [sudo] pip install kpt_flatten_json

## Function

kpt_flatten_json: Returns a flattened dataframe


## Usage/Examples

```python
from kpt_flatten_json import *

flatdf= kpt_flatten_json(complexdf)
```


## Complex Dataframe


| batters| id| name | ppu | topping| type               |
| :-------- | :------- | :------------------------- |:-------- | :------- | :------------------------- |
| {[{1001, Regular}... | 0001 | Cake|0.55 | [{5001, None}, {5... | donut|

## Flattened Dataframe
| id| name| ppu | type | topping_id | topping_type               | batters_batter_id | batters_batter_type               |
| :-------- | :------- | :------------------------- |:-------- | :------- | :------------------------- |:-------- | :------- |
|0001|Cake|0.55|donut| 5001| None| 1001| Regular|
|0001|Cake|0.55|donut| 5001| None| 1002| Chocolate|
|0001|Cake|0.55|donut| 5001| None| 1003| Blueberry|
|0001|Cake|0.55|donut| 5001| None| 1004| Devil's Food|
|0001|Cake|0.55|donut| 5002| Glazed| 1001| Regular|
|0001|Cake|0.55|donut| 5002| Glazed| 1002| Chocolate|
|0001|Cake|0.55|donut| 5002| Glazed| 1003| Blueberry|
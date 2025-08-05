## How to predict how many people will get on a plane this week

Kalshi has a prediction market on the average number of check-ins at TSA checkpoints in the US each week. This means that if we can forecast the total number of people getting on a plane in a given week, we can determine whether the contracts are priced efficiently or not.

The full article explaining this process is available here: https://medium.com/@colesussmeier/statistical-arbitrage-on-kalshi-2e8ca0470eb5

### Data/ Files

- All data is publicly available (TSA data and Google Trends)

- There are 3 .py files used for scraping/ aggregating data used in the project

- analyze.ipynb: looks at the interaction between covariates and their potential for use in a model

- predict_with_lags.ipynb: Using shifted lagged variables + AutoGluon to build the best weekly model
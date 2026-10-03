# Short-Term Water Level Forecasting for the Danube Using Machine Learning

This thesis focuses on short-term water level forecasting for the Danube River in Korneuburg, Austria. The goal is to compare different forecasting models for the next 24 hours and investigate the effects of upstream stations and weather data on the forecast performance. The forecasted values could be used by FloodAlert to show the future water level trend on its website.

The water level and weather data are preprocessed and combined with engineered features, such as lagged values, water level changes, and rolling statistics. Ridge regression, ARIMA and ARIMAX, tree-based models, and neural networks are trained and compared against a persistence baseline. Feature subsets and hyperparameters are selected based on expanding-window CV, while a chronologically separated test set is used for the final evaluation and final model selection.

Overall, RNN achieves the lowest CV RMSE of 12.02 cm. On the sealed test set, RNN achieves an RMSE of 12.96 cm, while the MLP performs best with an RMSE of 12.11 cm and is therefore selected as the final model. The addition of upstream stations and weather data leads to a decrease in CV RMSE of 23.1% for MLP compared to using only target-station features without weather data. The persistence model performs better than MLP only for the first hour, with MLP performing better for the remaining forecast horizon. However, MLP struggles to predict extreme water levels accurately. At or above the alarm threshold of 545 cm, the RMSE increases to 47.33 cm, with the model systematically underestimating the water level on average.

Finally, a deployment concept describes how the model could be integrated into FloodAlert. The forecasts could provide additional information about future water levels. However, the performance during extreme events is not sufficient to use the forecasts as the sole basis for flood warnings. Furthermore, the results are limited to a single station.

The thesis source code is available in the [cellularegg/uas-master-thesis-code](https://github.com/cellularegg/uas-master-thesis-code) repository.

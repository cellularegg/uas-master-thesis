# Short-Term Water Level Forecasting for the Danube Using Machine Learning

This thesis focuses on short-term water level forecasting for the Danube River in Korneuburg, Austria. The goal is to compare different forecasting models for the next 24 hours and investigate the effects of upstream stations and weather data on the forecast performance. The forecasted values could be used by FloodAlert to show the future water level trend on its website.

The water level and weather data are preprocessed and combined with engineered features, such as lagged values, water level changes, and rolling statistics. Linear models, tree-based models, and neural networks are trained and compared against a persistence baseline. Model selection is based on expanding-window CV, while a chronologically separated test set is only used for the final evaluation.

Overall, XGBoost achieves the lowest CV RMSE of 12.43 cm and is therefore selected as the final model. On the sealed test set, XGBoost achieves an RMSE of 13.90 cm, while the MLP performs better with an RMSE of 12.11 cm. The addition of upstream stations and weather data leads to a decrease in CV RMSE of 25.8% compared to using only target-station features without weather data. The persistence model performs better for the first six hours, with XGBoost performing better for the remaining forecast horizon. However, XGBoost struggles to predict extreme water levels accurately. Above the alarm threshold of 545 cm, the RMSE increases to 71.44 cm, with the model systematically underestimating the water level.

Finally, a deployment concept describes how the model could be integrated into FloodAlert. The forecasts could provide additional information about future water levels. However, the performance during extreme events is not sufficient to use the forecasts as the sole basis for flood warnings. Furthermore, the results are limited to a single station.

The thesis source code is available in the [cellularegg/uas-master-thesis-code](https://github.com/cellularegg/uas-master-thesis-code) repository.

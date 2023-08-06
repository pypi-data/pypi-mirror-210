from ipywidgets import interact, Dropdown
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error, mean_absolute_percentage_error, mean_squared_log_error,make_scorer
from sklearn.metrics import mean_squared_log_error, mean_absolute_percentage_error
from scipy.stats import probplot
import statsmodels.api as sm
import plotly.graph_objects as go
from sklearn.inspection import permutation_importance

def plots_regressao(model,X_test,y_test):
    y_pred=model.predict(X_test)
    def evaluation_metrics():
        
        r2 = r2_score(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        mae = mean_absolute_error(y_test, y_pred)
        mape = mean_absolute_percentage_error(y_test, y_pred) * 100
        rmsle = np.sqrt(mean_squared_log_error(y_test, y_pred))

        metrics = pd.DataFrame({'Metric': ['R2', 'RMSE', 'MAE', 'MAPE', 'RMSLE'],
                                'Value': [r2, rmse, mae, mape, rmsle]})

        fig = go.Figure(data=[go.Table(header=dict(values=['Metric', 'Value']),
                                       cells=dict(values=[metrics['Metric'], metrics['Value']]))])
        fig.show()

    def predicted_vs_real_value_plot():
        fig = px.scatter(x=y_test, y=y_pred, labels={'x': 'Real Value', 'y': 'Predicted Value'}, title='Predicted vs Real Value Plot')
        fig.add_shape(type='line', x0=y_test.min(), x1=y_test.max(), y0=y_test.min(), y1=y_test.max(), yref='y', xref='x', line=dict(color='Black', dash='dash'))
        fig.show()

    def residual_plot():
        residuals = y_test - y_pred
        fig = px.scatter(x=y_pred, y=residuals, labels={'x': 'Predicted Value', 'y': 'Residual'}, title='Residual Plot')
        fig.add_shape(type='line', x0=y_pred.min(), x1=y_pred.max(), y0=0, y1=0, yref='y', xref='x', line=dict(color='Black', dash='dash'))
        fig.show()

    def residual_histogram():
        residuals = y_test - y_pred
        fig = px.histogram(residuals, nbins=20, labels={'value': 'Residual', 'count': 'Frequency'}, title='Residual Histogram')
        fig.show()


    def qq_plot():
        residuals = y_test - y_pred
        qq_data = sm.ProbPlot(residuals)
        theoretical_quantiles, sample_quantiles = qq_data.theoretical_quantiles, qq_data.sample_quantiles

        fig = go.Figure()

        fig.add_trace(go.Scatter(x=theoretical_quantiles, y=sample_quantiles, mode='markers', name='Residuals'))
        min_val = min(np.min(theoretical_quantiles), np.min(sample_quantiles))
        max_val = max(np.max(theoretical_quantiles), np.max(sample_quantiles))
        fig.add_shape(type='line', x0=min_val, x1=max_val, y0=min_val, y1=max_val, yref='y', xref='x', line=dict(color='Red', dash='dash'), name='y=x')

        fig.update_layout(title='Q-Q Plot',
                          xaxis_title='Theoretical Quantiles',
                          yaxis_title='Residuals')
        fig.show()
        
    def variable_vs_prediction_plot():
        X_test_copy = X_test.copy()
        X_test_copy['y_pred'] = y_pred

        num_columns = X_test_copy.select_dtypes(include=np.number).columns
        cat_columns = X_test_copy.select_dtypes(include='object').columns

        for col in num_columns:
            fig = px.scatter(X_test_copy, x=col, y='y_pred', labels={col: col, 'y_pred': 'Predicted Value'}, title=f'{col} vs Predicted Value')
            fig.show()

        for col in cat_columns:
            fig = px.box(X_test_copy, x=col, y='y_pred', labels={col: col, 'y_pred': 'Predicted Value'}, title=f'Median and Spread of Predicted Value by {col}')
            fig.show()
            
    def variable_vs_real_plot():
        X_test_copy = X_test.copy()
        X_test_copy['y_pred'] = y_test

        num_columns = X_test_copy.select_dtypes(include=np.number).columns
        cat_columns = X_test_copy.select_dtypes(include='object').columns

        for col in num_columns:
            fig = px.scatter(X_test_copy, x=col, y='y_pred', labels={col: col, 'y_pred': 'Valor Real'}, title=f'{col} vs Real Value')
            fig.show()

        for col in cat_columns:
            fig = px.box(X_test_copy, x=col, y='y_pred', labels={col: col, 'y_pred': 'Valor Real'}, title=f'Median and Spread of real Value by {col}')
            fig.show()
            
    def permutation_feature_importance():
        scoring_dict = {
            'r2': 'r2',
            'rmse': make_scorer(mean_squared_error, greater_is_better=False, squared=False),
            'mae': 'neg_mean_absolute_error',
            'mape': make_scorer(mean_absolute_percentage_error, greater_is_better=False),
            'rmsle': make_scorer(mean_squared_log_error, greater_is_better=False, squared=False)
        }

        results = {}
        for metric_name, scorer in scoring_dict.items():
            result = permutation_importance(model, X_test, y_test, scoring=scorer, n_repeats=10, random_state=42)
            importance_df = pd.DataFrame({'Feature': X_test.columns,
                                           'Importance': result.importances_mean,
                                           'Importance_std': result.importances_std})
            importance_df.sort_values(by='Importance', ascending=False, inplace=True)
            results[metric_name] = importance_df

        for metric_name, importance_df in results.items():
            fig = px.bar(importance_df, x='Feature', y='Importance', error_y='Importance_std',
                         labels={'Feature': 'Feature', 'Importance': 'Importance'},
                         title=f'Permutation Feature Importance ({metric_name.upper()})')
            fig.show()

    def scatterplot_matrix():
        fig = px.scatter_matrix(pd.DataFrame({'Real Value': y_test, 'Predicted Value': y_pred, 'Residual': y_test - y_pred}))
        fig.update_traces(diagonal_visible=False)
        fig.show()

    def plot_selected(plot_type):
        if plot_type == 'Evaluation Metrics':
            evaluation_metrics()
        elif plot_type == 'Predicted vs Real Value Plot':
            predicted_vs_real_value_plot()
        elif plot_type == 'Residual Plot':
            residual_plot()
        elif plot_type == 'Residual Histogram':
            residual_histogram()
        elif plot_type == 'Q-Q Plot':
            qq_plot()
        elif plot_type == 'Scatterplot Matrix':
            scatterplot_matrix()
        elif plot_type == 'Variable vs Prediction Plot':
            variable_vs_prediction_plot()
        elif plot_type == 'Variable vs Real Plot':
            variable_vs_real_plot()            
        elif plot_type == 'Permutation Feature Importance':
            permutation_feature_importance()
            
    dropdown = Dropdown(options=['Evaluation Metrics', 'Predicted vs Real Value Plot', 'Residual Plot', 'Residual Histogram', 'Q-Q Plot', 'Scatterplot Matrix','Variable vs Prediction Plot','Variable vs Real Plot','Permutation Feature Importance'])
    interact(plot_selected, plot_type=dropdown)
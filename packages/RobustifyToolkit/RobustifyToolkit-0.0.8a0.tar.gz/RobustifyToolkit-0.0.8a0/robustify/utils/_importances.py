import numpy as np
from sklearn.inspection import permutation_importance
from eli5.sklearn import PermutationImportance
from eli5.permutation_importance import get_score_importances
from lime import lime_tabular
import shap

def filter_on_importance_method(model, index, X, y, random_state, scoring, feature_importance_measure, custom_predict):
    switcher = {
        None: lambda: check_for_deafult_properties(model, index, X, y, random_state, scoring),
        'eli5': lambda: calculate_eli5_importances(model, index, X, y, random_state, scoring),
        'lime': lambda: calculate_lime_importances(model, index, X, y, random_state, scoring, custom_predict),
        'shap': lambda: calculate_shap_importances(model, index, X, y, random_state, scoring)
    }
    return switcher.get(feature_importance_measure, lambda: print("Invalid importance measure for {}".format(str(model))))()

def check_for_deafult_properties(model, index, X, y, random_state, scoring):
    if hasattr(model, 'feature_importances_'):
        measured_property = 'feature importance'
        return model.feature_importances_[index], measured_property
    elif hasattr(model, 'coef_'):
        measured_property = 'coefficients'
        if (isinstance(model.coef_[0], (np.ndarray, list))):
            return model.coef_[0][index], measured_property
        else: 
            return model.coef_[index], measured_property  
    else:
        return calculate_permuation_importances(model, index, X, y, random_state, scoring)

def calculate_permuation_importances(model, index, X, y, random_state, scoring):
    try:
        measured_property = 'permutation importance'
        importances = permutation_importance(model, X, y, n_repeats=1, random_state=random_state, n_jobs=-1, scoring=scoring)
        return importances.importances_mean[index], measured_property
    except:
        raise Exception("cound not calculate coefficients or feature importance") 

def calculate_eli5_importances(model, index, X, y, random_state, scoring):
    if not isinstance(scoring, str):
        try:
            measured_property = "eli5_custom_score_function"
            _, score_decreases = get_score_importances(scoring, np.array(X), y, n_iter=1, random_state=random_state)
            feature_importances = np.mean(score_decreases, axis=0)
            return feature_importances[index], measured_property
        except:
            raise Exception("Could not compute eli5 importances") 
    else:
        try: 
            importances = PermutationImportance(model, scoring=scoring, random_state=random_state, n_iter=1, cv="prefit", refit=False).fit(X, y)
            measured_property = "eli5 permutation importance"
            return importances.feature_importances_[index], measured_property
        except:
            raise Exception("Could not compute eli5 importances") 
        
def calculate_lime_importances(model, index, X, y, random_state, scoring, custom_predict):
    try:
        measured_property = "lime explainer"
        explainer = lime_tabular.LimeTabularExplainer(
            training_data=X.to_numpy(),
            feature_names=X.columns.tolist(),
            class_names=['data_type'],
            mode='classification',
            verbose=False)
        values = []
        for i in range(int((X.shape[0]/10))):
            if custom_predict:
                predict_fn_rf = lambda x: custom_predict(model, x).astype(float)
            else:
                predict_fn_rf = lambda x: model.predict_proba(x).astype(float)
            exp = explainer.explain_instance(X.to_numpy()[i], predict_fn_rf, num_features=len(X.columns.tolist()))
            dic = dict(list(exp.as_map().values())[0])
            values.append(dic.get(index))
        average_value = np.mean(values, axis=0)
        return average_value, measured_property
    except:
        raise Exception("Could not compute lime importances") 

def calculate_shap_importances(model, index, X, y, random_state, scoring):
    try:
        measured_property = "shap"
        explainer = shap.Explainer(model)
        shap_values = explainer(X)
        average_values = [sum(sub_list) / len(sub_list) for sub_list in zip(*shap_values.data)]
        return average_values[index], measured_property
    except: 
        raise Exception("Could not compute shap importances")
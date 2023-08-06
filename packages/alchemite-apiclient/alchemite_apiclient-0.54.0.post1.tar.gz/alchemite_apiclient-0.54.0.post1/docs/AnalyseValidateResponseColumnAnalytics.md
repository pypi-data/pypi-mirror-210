# AnalyseValidateResponseColumnAnalytics


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** | The unique name of the column | [optional] 
**num_validation_samples** | **int, none_type** | The number of validation samples for this column in the dataset. | [optional] 
**mcc** | **float, none_type** | The Matthews Correlation Coefficient (MCC) for this categorical column in the dataset.  Null if the column is a descriptor or there is no variation in the column&#39;s values. | [optional] 
**coefficient_of_determination** | **float, none_type** | The coefficient of determination for this column in the dataset.  Null if the column is a descriptor or there is no variation in the column&#39;s values. | [optional] 
**rmse** | **float, none_type** | The root mean squared error for this column in the dataset.  Null if the column is a descriptor or there is no variation in the column&#39;s values. | [optional] 
**uncertainty_divergence** | **float, none_type** | An indication of the extent to which the uncertainty associated with that column deviates from the expected distribution of uncertainties. Values closer to 0 indicate closer match with the expected uncertainty distribution. | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)



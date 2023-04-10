import pandas as pd
import requests

from dagster import MetadataValue, Output, asset


@asset
def user_data():
    """
    
    """
    res = requests.get("https://jsonplaceholder.typicode.com/users").json()
    res = pd.DataFrame(res)

    # recorded metadata can be customized
    return res



# asset dependencies can be inferred from parameter names
@asset
def messages() :
    """ 
    
    """
    res = requests.get("https://jsonplaceholder.typicode.com/posts").json()
    res = pd.DataFrame(res)
    
    return res

@asset
def messages_with_names(user_data, messages):
    """
    
    """
    user_data = user_data.rename({"id":"userId"}, axis='columns')
    res = pd.merge(user_data, messages, on="userId", how="outer", validate="one_to_many")[['username', 'title', 'body']]
    
    res.to_csv('C:\\Users\\YURA\\source\\repos\\pipelines\\messages_with_names.csv', index=False)
    
    metadata = {
        "num_records": len(res),
        "preview": MetadataValue.md(res.to_markdown()),
    }

    return Output(value=res, metadata=metadata)
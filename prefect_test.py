import json
import requests
import pandas as pd
from datetime import datetime
from prefect import task, flow


@task
def extract(url: str) -> dict:
    res = requests.get(url)
    if not res:
        raise Exception('No data fetched!')
    return json.loads(res.content)


@task
def transform(users, messages) -> pd.DataFrame:
    users = pd.DataFrame(users)
    users = users.rename({"id":"userId"}, axis='columns')
    messages = pd.DataFrame(messages)
    res = pd.merge(users, messages, on="userId", how="outer", validate="one_to_many")[['username', 'title', 'body']]
    return res

@task
def load(data: pd.DataFrame, path: str) -> None:
    data.to_csv(path_or_buf=path, index=False)

@flow
def prefect_flow():
    users = extract(url='https://jsonplaceholder.typicode.com/users')
    messages = extract(url='https://jsonplaceholder.typicode.com/posts')
    res = transform(users, messages)
    load(data=res, path=f'C:\\Users\\YURA\\source\\repos\\pipelines\\messages_with_names.csv')


if __name__ == '__main__':
    prefect_flow()
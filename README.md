<h1>CutContour Classifier</h1>
This uses a computer vision model used to classify cut shapes on two classes:

- ```approved```: The cut shape should be produceable
- ```rejected```: The cut shape should not be produceable

This is presented in two flavours:

1. StreamlitApp: Application where you can provide a cimdoc URL from a file and, based on the cutting shape, it provides the cut shape and evaluates ```approved``` or ```rejected```
2. API: API that, provided a .png image of the cut shape, it provides evaluates ```approved``` or ```rejected```


# REST API app

## Start
```cmd
uvicorn ClassifierAPI:app
```

Use ```--reload``` to automatically restart the webservice when the code changes

```cmd
uvicorn ClassifierAPI:app --reload
```

## Swagger

You can access a swagger via ```http://<host>:8000/docs```

## Check file

### Request

`POST /check_file/`

```json
{
  "Url": "<url>",
  "Threshold": 0.5
}
```
```cmd
curl -X 'POST' \
  'http://127.0.0.1:8000/check_file/' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "Url": "<url>",
  "Threshold": 0.5
}'
```

`Url` is an url to download a png file

`Threshold` is a value between 0 and 1 that determines when to consider a file as `approved`

### Response

```json
{
    "Status": "Running",
    "ArtworkURL": "<url>",
    "Threshold": 0.5,
    "ResultName": "c6ef99c7-836c-4235-96e0-b471b922a3e7",
    "ResultURL": "http://127.0.0.1:8000/result/c6ef99c7-836c-4235-96e0-b471b922a3e7"
}
```

## Callback

### Request

`GET /result/{handler_id}`

```cmd
curl -X 'GET' \
  'http://127.0.0.1:8000/result/008bb0de-69f9-43d7-b40a-e72bf18394a1' \
  -H 'accept: application/json'
```

### Response

```json
{
    "Status": "Completed",
    "ArtworkURL": "https://uploads.documents.cimpress.io/v1/uploads/51f7cde0-7f5f-4aac-958f-f5d9dde837f2~100?tenant=prepress-uploads",
    "Threshold": 0.5,
    "ResultName": "c6ef99c7-836c-4235-96e0-b471b922a3e7",
    "ResultURL": "http://127.0.0.1:8000/result/c6ef99c7-836c-4235-96e0-b471b922a3e7",
    "Result": {
        "PredictedValue": 1.5486473614600982e-07,
        "Outcome": "rejected"
    }
}
```




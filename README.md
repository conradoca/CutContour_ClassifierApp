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

`Url` is an url to download a png file

`Threshold` is a value between 0 and 1 that determines when to consider a file as `approved`

### Response

```json
{
  "Status": "Running",
  "ResultName": "008bb0de-69f9-43d7-b40a-e72bf18394a1",
  "ResultURL": "http://127.0.0.1:8000/result/008bb0de-69f9-43d7-b40a-e72bf18394a1"
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
  "Result": {
    "artworkURL": "<url>",
    "threshold": 0.5,
    "predictionValue": 1.5486503457395884e-7,
    "outcome": "rejected"
  }
}
```




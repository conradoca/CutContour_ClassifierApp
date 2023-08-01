<h1 align="center">CutContour Classifier</h1>
This uses a computer vision model used to classify cut shapes on two classes:

- ```approved```: The cut shape should be produceable
- ```rejected```: The cut shape should not be produceable

This is presented in two flavours:

1. StreamlitApp: Application where you can provide a cimdoc URL from a file and, based on the cutting shape, it provides the cut shape and evaluates ```approved``` or ```rejected```
2. API: API that, provided a .png image of the cut shape it provides evaluates ```approved``` or ```rejected```


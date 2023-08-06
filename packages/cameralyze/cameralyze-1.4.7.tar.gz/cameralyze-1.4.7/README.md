# Cameralyze Python Package

```python
import cameralyze
model = cameralyze.Model(api_key="YOUR_API_KEY")
model.set_model(model="4154b8ff-aad5-4ae7-9747-3dcc50ed7ac7")
image = model.read_file(path="")
response = model.predict(image=image)
```

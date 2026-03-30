import sys
import traceback

try:
    from api.myscript import app
    print("Successfully imported app.")
    print("Routes:")
    for route in app.routes:
        print(route.path, route.name)
except Exception as e:
    print("Exception occurred:")
    traceback.print_exc()

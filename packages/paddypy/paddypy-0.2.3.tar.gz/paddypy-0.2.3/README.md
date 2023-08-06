# paddypy

Under construction! Not ready for use yet! Currently experimenting and planning!

Developed by Patrik (c) 2022

## Examples of How To Use (Alpha Version)

 Print and get azure app-configuration keys and flags

```python
from paddypy import access
# does a logging print out of the azure app-configuration keys and flags.
access.listConfig()

key = "username"


# gets the lastest value for a given key
# deactivate_kv_access choose if kv-ref should be accessed (access policies need to be correct)  
value = access.getValue(key=key, deactivate_kv_access=True) 
logging.info("Lastest value: " + value)

# sets a key value
# deactivate_kv_access choose if kv-ref should be accessed (access policies need to be correct)  
value = access.setValue(key=key, value="julia", content_type=None, tags: dict={}, label=None, deactivate_kv_access=False):
logging.info("Lastest value: " + value)
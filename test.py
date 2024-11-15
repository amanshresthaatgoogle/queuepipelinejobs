import json
import base64  # Import base64

data="ewogICAgImRpc3BsYXlfbmFtZSI6ICJteS1maXJzdC1waXBlbGluZSIsICAKICAgICJ0ZW1wbGF0ZV9wYXRoIjogImdzOi8veXZlcnRleGFpcGlwZWxpbmVidWNrZXQvbmFtZV9waXBlbGluZS5qc29uIiwgIAogICAgInBpcGVsaW5lX3Jvb3QiOiAiZ3M6Ly92ZXJ0ZXhhaXBpcGVsaW5lYnVja2V0L3BpcGVsaW5lX3Jvb3QiICAKICB9"

pipeline_request = json.loads(base64.b64decode(data).decode("utf-8"))

encoded = base64.b64decode("help").encode("utf-8")

print(encoded)
import pkg_resources
try:
    version = pkg_resources.require("sequana_depletion")[0].version
except:
    version = ">=0.8.0"


#!/bin/bash
# Fix vendored cmbagent imports to use relative imports

cd /workspaces/Denario

# Fix base_agent imports
find third_party/cmbagent -name "*.py" -exec sed -i 's/from cmbagent\.base_agent import/from ...base_agent import/g' {} \;

# Fix utils imports  
find third_party/cmbagent -name "*.py" -exec sed -i 's/from cmbagent\.utils import/from ...utils import/g' {} \;

# Fix context imports
find third_party/cmbagent -name "*.py" -exec sed -i 's/from cmbagent\.context import/from ...context import/g' {} \;

# Fix cmbagent imports
find third_party/cmbagent -name "*.py" -exec sed -i 's/from cmbagent\.cmbagent import/from ...cmbagent import/g' {} \;

echo "Fixed vendored cmbagent imports"

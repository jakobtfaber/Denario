# MATLAB R2024a Setup Guide for Denario

## Prerequisites

1. **MATLAB R2024a License**: Ensure you have a valid MATLAB R2024a license
2. **MATLAB Installation**: Install MATLAB R2024a on your system
3. **Python Environment**: Use the `cmbagent` conda environment

## Installation Steps

### 1. Install MATLAB R2024a

#### On Linux:
```bash
# Download MATLAB R2024a installer from MathWorks
# Run the installer with appropriate permissions
sudo ./install

# Or install via package manager if available
sudo apt-get install matlab-r2024a  # Ubuntu/Debian
```

#### On macOS:
```bash
# Download MATLAB R2024a from MathWorks
# Mount the DMG and run the installer
# Follow the installation wizard
```

#### On Windows:
```bash
# Download MATLAB R2024a from MathWorks
# Run the installer as administrator
# Follow the installation wizard
```

### 2. Set Environment Variables

Add MATLAB to your PATH and set MATLAB_ROOT:

```bash
# Add to ~/.bashrc or ~/.zshrc
export MATLAB_ROOT="/usr/local/MATLAB/R2024a"  # Adjust path as needed
export PATH="$MATLAB_ROOT/bin:$PATH"

# For conda environment, add to environment activation
conda env config vars set MATLAB_ROOT="/usr/local/MATLAB/R2024a"
```

### 3. Install MATLAB Engine API for Python

```bash
# Activate the conda environment
conda activate cmbagent

# Navigate to MATLAB installation directory
cd $MATLAB_ROOT/extern/engines/python

# Install the MATLAB Engine API
python setup.py install

# Or use pip (if MATLAB is properly installed)
pip install matlabengine
```

### 4. Verify Installation

Run the verification script:

```bash
cd /data/cmbagents
conda activate cmbagent
python Denario/examples/matlab_verification.py
```

## Troubleshooting

### Common Issues

1. **MATLAB not found in PATH**
   - Ensure MATLAB_ROOT is set correctly
   - Add MATLAB bin directory to PATH
   - Restart terminal after setting environment variables

2. **Permission denied errors**
   - Run MATLAB installer with appropriate permissions
   - Check file permissions on MATLAB installation directory

3. **Python Engine API installation fails**
   - Ensure MATLAB is properly installed first
   - Use the setup.py from MATLAB installation directory
   - Check Python version compatibility

4. **MATLAB Engine fails to start**
   - Verify MATLAB license is valid
   - Check MATLAB installation integrity
   - Ensure all required MATLAB toolboxes are installed

### Verification Commands

```bash
# Check MATLAB installation
which matlab
matlab -version

# Check environment variables
echo $MATLAB_ROOT
echo $PATH | grep matlab

# Test Python import
python -c "import matlab.engine; print('MATLAB Engine API available')"

# Test MATLAB Engine start
python -c "import matlab.engine; eng = matlab.engine.start_matlab(); print('MATLAB Engine started successfully')"
```

## Configuration

### MATLAB Provider Configuration

```python
from denario.providers import MATLABProvider

# Basic configuration
matlab_provider = MATLABProvider()

# With custom MATLAB path
matlab_provider = MATLABProvider(matlab_path="/path/to/matlab")

# With license file
matlab_provider = MATLABProvider(license_file="/path/to/license.lic")
```

### Orchestrator Configuration

```python
from denario.providers import PremiumMathematicalOrchestrator

config = {
    'matlab': {
        'enabled': True,
        'path': '/usr/local/MATLAB/R2024a',  # Optional
        'license_file': '/path/to/license.lic'  # Optional
    }
}

orchestrator = PremiumMathematicalOrchestrator(config)
```

## Testing

After installation, run the comprehensive test suite:

```bash
cd /data/cmbagents
conda activate cmbagent
python Denario/examples/matlab_integration_test.py
python Denario/examples/comprehensive_math_test.py
```

## Performance Notes

- **First startup**: MATLAB Engine may take 10-30 seconds to start initially
- **Subsequent calls**: Much faster after initial startup
- **Memory usage**: MATLAB Engine maintains persistent MATLAB session
- **Concurrent access**: Multiple Python processes can share MATLAB Engine

## Support

If you encounter issues:

1. Check MATLAB installation and license
2. Verify environment variables
3. Test MATLAB Engine API installation
4. Review MATLAB logs for errors
5. Contact MathWorks support if needed

# Scripts Directory

This directory contains various utility scripts, tests, and restart scripts for the Denario project.

## Directory Structure

### `/restart/`
Scripts for restarting and running Denario with different configurations:
- `restart_denario_gpt5_reasoning.py` - **MAIN**: Restart with GPT-5 reasoning integration (REBUILT)
- `restart_denario_gemini.py` - Restart using Gemini models
- `restart_denario_advanced.py` - Advanced restart configuration
- `restart_denario_ag2.py` - Restart with AG2 integration
- `run_denario_gemini.py` - Run Denario with Gemini
- `run_restart_skip_paper.sh` - Shell script to run with SKIP_PAPER=1

### `/testing/`
Test scripts for various components:
- `test_gpt5_integration.py` - Test GPT-5 integration functionality
- `test_gpt5_live.py` - Live testing of GPT-5 API
- `test_debug.py` - General debugging tests
- `test_terminal.py` - Terminal functionality tests
- `test_ag2_basic.py` - Basic AG2 testing
- `test_ag2_detection.py` - AG2 detection testing  
- `test_claude_opus.py` - Claude Opus API testing
- `test_gemini_models.py` - Gemini models testing
- `test_gpt5*.py` - Various GPT-5 API tests
- `test_openai_models.py` - OpenAI models testing
- `test_restart_ag2_flow.py` - AG2 restart flow testing

### `/utilities/`
Utility scripts for API and system management:
- `list_anthropic_models.py` - List available Anthropic models (ENHANCED)
- `list_openai_models.py` - List available OpenAI models (ENHANCED)
- `denario_status.py` - Monitor running Denario pipelines (NEW)

### `/temporary/`
Temporary debugging and inspection scripts (safe to delete):
- `tmp_inspect_engineer.py` - Temporary engineer inspection
- `tmp_instantiate_cmbagent.py` - Temporary CMBAgent instantiation test
- `tmp_print_syspath.py` - Temporary sys.path debugging
- `tmp_verify_gpt5_cleanup.py` - Temporary GPT-5 cleanup verification

## Usage

### Running the Main Pipeline
```bash
# From project root (using symlink)
python restart_denario_gpt5_reasoning.py

# Or directly from scripts directory
python scripts/restart/restart_denario_gpt5_reasoning.py

# With paper generation skipped
bash scripts/restart/run_restart_skip_paper.sh
```

## Recent Updates
- **Aug 2025**: Fixed Gemini API integration and GPT-5 reasoning support
- **Aug 2025**: Organized scripts into proper directory structure  
- **Aug 2025**: Added symlink in root for easy access to main script
- **Aug 2025**: Consolidated test_apis directory into scripts structure
- **Aug 2025**: Enhanced API testing utilities with better model detection
- **Aug 2025**: Added denario_status.py for pipeline monitoring
- **Aug 2025**: Rebuilt main restart script with proper error handling

### Testing
```bash
# Test GPT-5 integration
python scripts/testing/test_gpt5_integration.py

# List available models
python scripts/utilities/list_openai_models.py
```

## Notes
- The main production script is `restart_denario_gpt5_reasoning.py`
- Temporary scripts in `/temporary/` are safe to remove after debugging
- All restart scripts should be run from the project root directory

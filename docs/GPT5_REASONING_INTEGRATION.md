# GPT-5 Reasoning Integration for Denario

## Overview

This integration enables GPT-5's advanced reasoning capabilities within Denario's research workflow. It provides a seamless bridge between autogen/cmbagent and OpenAI's new Responses API, allowing GPT-5 to use its reasoning tokens for enhanced scientific analysis.

## Architecture

### Components

1. **`gpt5_responses_adapter.py`** - Core adapter that wraps the Responses API in a chat-completions-like interface
2. **`gpt5_integration.py`** - Monkey-patch layer that intercepts autogen calls and routes GPT-5+reasoning to the Responses API
3. **Restart scripts** - Updated scripts to use GPT-5 reasoning for results generation

### How It Works

1. **Detection**: When an agent config contains `model: "gpt-5*"` AND `reasoning_effort`, the integration activates
2. **Interception**: The monkey patch intercepts `ConversableAgent.generate_oai_reply()` calls
3. **Routing**: GPT-5 calls are routed to `client.responses.create()` instead of `client.chat.completions.create()`
4. **Translation**: Messages are flattened to a prompt, and the response is mapped back to autogen's expected format
5. **Reasoning**: GPT-5 uses reasoning tokens internally, providing higher-quality scientific analysis

## Usage

### Automatic Configuration

The integration automatically detects GPT-5 models and adds reasoning configuration:

```python
# When GPT-5 is detected, these are automatically added:
config = {
    "config_list": [{
        "model": "gpt-5",
        "reasoning_effort": "high",     # Auto-injected
        "verbosity": "medium",          # Auto-injected  
        "max_output_tokens": 4096,      # Auto-injected
        # ... other config
    }]
}
```

### Manual Configuration

You can also explicitly configure reasoning parameters:

```python
from denario.gpt5_integration import install_gpt5_reasoning_support
from denario import Denario

# Activate the integration
install_gpt5_reasoning_support()

# Use string model names - reasoning is auto-configured
denario = Denario(project_dir="project_gemini")
denario.get_results(
    engineer_model="gpt-5",      # Auto-configured with reasoning
    researcher_model="gpt-5",    # Auto-configured with reasoning
    restart_at_step="experiment"
)
```

### Restart with GPT-5 Reasoning

```bash
# Use the dedicated restart script
python restart_denario_gpt5_reasoning.py
```

### Manual Testing

```bash
# Test the integration
python test_gpt5_integration.py

# Test with live API call (requires OPENAI_API_KEY)
python test_gpt5_live.py
```

## Benefits

### Scientific Quality
- **Enhanced reasoning**: GPT-5's reasoning tokens provide deeper analysis of experimental results
- **Better interpretation**: More sophisticated understanding of data patterns and scientific implications
- **Improved conclusions**: Higher-quality synthesis of findings into coherent conclusions

### Technical Advantages
- **Non-invasive**: Minimal changes to existing codebase; works with current autogen/cmbagent workflows
- **Fallback-safe**: If GPT-5 fails, falls back to standard behavior
- **Configurable**: Fine-tune reasoning effort and verbosity per use case

## Configuration Options

### Reasoning Effort
- `"minimal"` - Basic reasoning, fastest
- `"low"` - Light reasoning, good balance
- `"medium"` - Moderate reasoning, recommended default
- `"high"` - Deep reasoning, best quality (slower)

### Verbosity
- `"low"` - Concise output
- `"medium"` - Balanced detail
- `"high"` - Comprehensive explanations

## Integration Points

### Automatic Detection
The integration automatically activates when it detects:
```python
config = {
    "config_list": [{
        "model": "gpt-5",  # or gpt-5-mini, gpt-5-nano
        "reasoning_effort": "medium",  # Any reasoning effort setting
        # ... other config
    }]
}
```

### cmbagent Integration
Works with existing cmbagent logic:
```python
# In cmbagent.py line ~718
if "reasoning_effort" in llm_config['config_list'][0]:
    llm_config.pop('temperature')  # Removed for Responses API
    llm_config.pop('top_p')        # Removed for Responses API
```

## Implementation Notes

### Monkey Patching
- Targets `autogen.ConversableAgent.generate_oai_reply`
- Preserves original method signature and return format
- Thread-safe and isolated per agent instance

### Message Translation
- Converts autogen's message list to single prompt string
- Preserves role information with simple tagging
- Returns content as string (autogen's expected format)

### Error Handling
- Graceful fallback if Responses API fails
- Logging for debugging integration issues
- Preserves autogen's error handling patterns

## Dependencies

- `openai>=1.99.9` (for Responses API support)
- `python-dotenv>=1.0.1` (for environment variable loading)
- Existing Denario dependencies (autogen, cmbagent, etc.)

## Future Enhancements

1. **Tool Integration**: Map function/tool calls to Responses API
2. **Batch Processing**: Support multiple reasoning requests
3. **Caching**: Cache reasoning results for identical inputs
4. **Metrics**: Expose reasoning token usage statistics
5. **Configuration**: More granular control over reasoning parameters

## Troubleshooting

### Common Issues

1. **No reasoning observed**: Check that `reasoning_effort` is in config
2. **API errors**: Verify `OPENAI_API_KEY` and model access
3. **Empty responses**: Check message format and content length
4. **Integration not working**: Verify `install_gpt5_reasoning_support()` returns `True`

### Debug Mode

Enable detailed logging:
```python
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('denario.gpt5_integration')
logger.setLevel(logging.DEBUG)
```

## Conclusion

This integration provides a production-ready way to leverage GPT-5's reasoning capabilities in Denario's scientific research workflows. It maintains compatibility with existing code while enabling significantly enhanced analysis quality through advanced reasoning.

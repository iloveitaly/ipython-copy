from IPython.core.magic import register_line_magic
import base64
import sys

@register_line_magic
def copy(line):
    """IPython magic to copy a variable or string to clipboard."""
    # Try to evaluate 'line' as a variable in the user's namespace
    try:
        content = str(get_ipython().ev(line))
    except:
        content = line # If not a variable, just use the raw text
        
    b64 = base64.b64encode(content.encode()).decode()
    sys.stdout.write(f"\x1b]52;c;{b64}\x07")
    sys.stdout.flush()

# Now you can use:
# %copy my_variable
# %copy "Some direct text"
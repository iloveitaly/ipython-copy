from unittest.mock import patch
import pytest
from argparse import ArgumentTypeError

from IPython.testing.globalipapp import get_ipython
from ipython_copy.ipython_clipboard import IPythonClipboard, valid_identifier, valid_line_num

@pytest.fixture(scope="session")
def ip():
    return get_ipython()

def test_valid_identifier():
    assert valid_identifier("my_var") == "my_var"
    with pytest.raises(ArgumentTypeError):
        valid_identifier("123var")
    with pytest.raises(ArgumentTypeError):
        valid_identifier("def") # keyword

def test_valid_line_num():
    assert valid_line_num("_") == "_"
    assert valid_line_num("7") == "7"
    assert valid_line_num("_i5") == "_i5"
    with pytest.raises(ArgumentTypeError):
        valid_line_num("_invalid")
    with pytest.raises(ArgumentTypeError):
        valid_line_num("not_a_line")

@patch('ipython_copy.ipython_clipboard.pycopy')
def test_clip(mock_pycopy, ip):
    magics = IPythonClipboard(shell=ip)
    ip.user_ns.update({'_': 'last_out', '_7': 'line_7_out', 'my_var': 'var_value'})
    
    # Test cell magic
    magics.clip("first line", "second line")
    mock_pycopy.assert_called_with("first line\nsecond line")
    
    # Test no args (default to _)
    magics.clip("")
    mock_pycopy.assert_called_with("last_out")
    
    # Test line number
    magics.clip("7")
    mock_pycopy.assert_called_with("line_7_out")
    
    # Test known variable
    magics.clip("my_var")
    mock_pycopy.assert_called_with("var_value")
    
    # Test literal text
    magics.clip("hello world")
    mock_pycopy.assert_called_with("hello world")

@patch('ipython_copy.ipython_clipboard.pycopy')
@patch('ipython_copy.ipython_clipboard.pypaste')
def test_pickle(mock_pypaste, mock_pycopy, ip):
    magics = IPythonClipboard(shell=ip)
    ip.user_ns.update({'my_var': [1, 2, 3]})
    
    # Test pickling a variable
    magics.pickle("my_var")
    mock_pycopy.assert_called()
    pickled_data = mock_pycopy.call_args[0][0]
    assert "b'\\x80" in pickled_data or 'b"\\x80' in pickled_data
    
    # Test unpickling into a variable
    mock_pypaste.return_value = pickled_data
    magics.pickle("-o new_var")
    assert ip.user_ns['new_var'] == [1, 2, 3]
    
    # Test unpickling and printing
    with patch('sys.stdout.write') as mock_stdout:
        magics.pickle("")
        mock_stdout.assert_called()

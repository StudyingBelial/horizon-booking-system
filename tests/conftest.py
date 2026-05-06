import pytest

@pytest.hookimpl(trylast=True)
def pytest_configure(config):
    """
    Hooks into the terminal reporter to duplicate all output to test_results.txt.
    """
    # Get the terminal reporter plugin
    tr = config.pluginmanager.get_plugin("terminalreporter")
    if tr:
        # We wrap the terminal writer's write method to also write to our file
        orig_write = tr._tw.write
        
        # Open the file in write mode to refresh it every time
        f = open("test_results.txt", "w", encoding="utf-8")
        
        def new_write(content, **kwargs):
            # Write to the file (strip ANSI colors if necessary, but pytest usually 
            # handles that if not a TTY)
            f.write(content)
            f.flush()
            # Call original write to show on terminal
            orig_write(content, **kwargs)
            
        tr._tw.write = new_write
        # Store file handle in config to close it properly at the end
        config._test_results_file = f

def pytest_unconfigure(config):
    """
    Clean up by closing the file handle.
    """
    if hasattr(config, "_test_results_file"):
        config._test_results_file.close()

"""
gobals_variables.py
===================
Global varaibles:
- verbose
"""
class VARS:
    """
    VARS class
    """
    _verbose = False

    def set_verbose(self, value: bool):
        """
        Set the global verbose value
        """
        VARS._verbose = value

    @property
    def verbose(self):
        """Get verbose"""
        return VARS._verbose

if __name__ == "__main__":
    print(VARS._verbose)

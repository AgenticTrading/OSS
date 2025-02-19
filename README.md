VNPY
  * Setup

    git clone https://github.com/vnpy/vnpy.git
    
    #安裝importlib
    
    python3 -m pip install importlib-metadata
    
    #安裝vnpy_ctp (mac需要source build, 不能從pip)
    
    git clone https://github.com/vnpy/vnpy_ctp
    cd vnpy_ctp
    python3 -m pip install -e .
    
    #安裝vnpy其他packages
    
    python3 -m pip install vnpy_ctastrategy vnpy_ctabacktester vnpy_datamanager vnpy_sqlite
  * Run
    
    python3 examples/veighna_trader/run.py

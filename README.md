# VNPY
  * Setup

    conda create --name vnpy python=3.12

    conda activate vnpy
    
    #安裝importlib
    
    python3 -m pip install importlib-metadata

    python3 -m pip install ta-lib
    
    #安裝vnpy_ctp (mac需要source build, 不能從pip)
    
    git clone https://github.com/vnpy/vnpy_ctp
    
    cd vnpy_ctp
    
    python3 -m pip install -e .
    
    #安裝vnpy其他packages
    
    python3 -m pip install vnpy_ctastrategy vnpy_ctabacktester vnpy_datamanager vnpy_sqlite

    ## 安裝 vnpy in MBP (M4)

    git clone https://github.com/vnpy/vnpy.git
    cd vnpy
    ./install_osx.sh
    
  * Run
    
    python3 examples/veighna_trader/run.py

# Finrobot
  * Modify requirements.txt

    pyautogen==0.5.3
    typing_extensions>=4.9.0


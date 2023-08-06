"""
info:This module the path to external non python files 
autor: Tucudean Adrian-Ionut
date: 22.05.2023
email: Tucudean.Adrian.Ionut@outlook.com
license: MIT
"""
import os
from sparkverse.components.log import logger
VERSION='0.0.6'
logger.info(f"VERSION : \033[92m{VERSION}\033[0m")
CAR    = os.path.join(os.path.dirname(__file__), 'data/player.png')
LEVEL1 = os.path.join(os.path.dirname(__file__), 'data/LineFollower1.png')
LEVEL2 = os.path.join(os.path.dirname(__file__), 'data/LineFollower2.png')
LEVEL3 = os.path.join(os.path.dirname(__file__), 'data/LaneKeeper1.png')
LEVEL4 = os.path.join(os.path.dirname(__file__), 'data/LaneKeeper2.png')
LEVEL5 = os.path.join(os.path.dirname(__file__), 'data/LaneKeeper3.png')
LEVEL6 = os.path.join(os.path.dirname(__file__), 'data/Cropps1.png')
LEVEL7 = os.path.join(os.path.dirname(__file__), 'data/Cropps2.png')
LOGO   = os.path.join(os.path.dirname(__file__), 'data/logo1.png')
if os.path.exists(CAR) and os.path.exists(LEVEL1) and os.path.exists(LOGO):
    logger.info("ASSETS : \033[92mOK\033[0m")
    logger.info("TRACK : \033[92mOK\033[0m")
else:
    logger.error("ASSETS : \033[91mNOT FOUND\033[0m")
SIMULATOR=os.path.join(os.path.dirname(__file__), 'simulator.py')
if os.path.exists(SIMULATOR):
    logger.info("SCRIPTS : \033[92mOK\033[0m")

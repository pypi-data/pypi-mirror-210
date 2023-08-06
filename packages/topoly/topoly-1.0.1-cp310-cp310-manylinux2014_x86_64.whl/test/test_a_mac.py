import matplotlib.pyplot as plt
import pytest  
import logging

log = logging.getLogger() 

def test_single_plot():
    log.info("Testing strange matplotlib problem")
    fig = plt.figure(figsize=(5,5))
    return

if __name__ == '__main__':
    test_single_plot()

### Install
```
git clone 
pip install stimela
stimela build --us-only simms,simulator,wsclean
```

### Run
```
stimela run simkat64.py -g DIRECTION="J2000,0deg,-30deg" -g SKYMODEL=point.txt -g MODE=test -g GJONES=true -g PREFIX=test-run -g SYNTHESIS=1 DTIME=8
```

See the top of the simkat.py file for more info and documentation of the options


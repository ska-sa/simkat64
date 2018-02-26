import stimela
INPUT = "input"                 # Input folder of pipeline. All inputs should be placed here, e.g, sky models

#### 
#The options below can be changed on the command line via the "-g" option.
#Example: stimela run simkat64.py -g PREFIX=blah-blah -g DIRECTION=J2000,0deg,-30deg  
PREFIX = "simkat64-default"     # Prefix for pipeline products
DIRECTION = "J2000,0deg,-30deg" # Pointing/phase center of the simulated observation
GJONES = "yes"                  # Add G-Jones errors to simulation
MAKEMS = "yes"                  # Create/reset MS
SIMSKY = "yes"                  # Simulate sky model into MS
DIRTY_IMAGE = "yes"             # Make dirty image of simulation
MODE = "test"                   # channelization mode. Options are 4k, 32k and test (test is 5 channels of 2MHz)
SYNTHESIS = "0.5"               # Observation time in hours
DTIME = "4"                     # Integration time in seconds
SKYMODEL = "point"              # Sky model name. The sky model file must placed in the input folder. "point" uses a point a 1Jy source at the phase/pointing centre (DIRECTION)
CALFIELD = "yes"

stimela.register_globals()

GJONES = GJONES.lower() in "yebo yes true 1".split()
MAKEMS = MAKEMS.lower() in "yebo yes true 1".split()
SIMSKY = SIMSKY.lower() in "yebo yes true 1".split()
CALFIELD = CALFIELD.lower() in "yebo yes true 1".split()
DIRTY_IMAGE = DIRTY_IMAGE.lower() in "yebo yes true 1".split()
MSDIR = PREFIX + "-msdir"
OUTPUT = PREFIX + "-output"
MS = PREFIX + ".ms"

SYNTHESIS = float(SYNTHESIS)

if SKYMODEL == "point":
    DIRECTION = "J2000,0deg,-30deg"
    SKYMODEL = "point.txt"

SCANS = None

if CALFIELD:
    DIRECTION = [DIRECTION, "J2000,90deg,-45deg"]
    SKYMODEL = [SKYMODEL, "calfield.txt"]
    SCANS = [SYNTHESIS*0.85, SYNTHESIS*0.15]


BW = 856e6 # in Hz
mode = {
    "4k"    : dict(dfreq=BW/4096.0, nchan=4096, im_nchan=16),
    "32k"   : dict(dfreq=BW/32768.0, nchan=32768, im_nchan=16),
    "test"  : dict(dfreq=2e6, nchan=8, im_nchan=4),
}

recipe = stimela.Recipe("Simulate MeerKAT 64 {0:s}".format(PREFIX), ms_dir=MSDIR)

# Make empty MS of simulated observation
if MAKEMS:
    recipe.add("cab/simms", "make_empty_ms", 
        {
            "msname"        : MS,
            "telescope"     : 'meerkat',
            "direction"     : DIRECTION,
            "freq0"         : 856e6 + mode[MODE]["dfreq"]/2, # Centre of first channel
            "dfreq"         : mode[MODE]["dfreq"],
            "nchan"         : mode[MODE]["nchan"],
            "synthesis"     : float(SYNTHESIS),
            "dtime"         : int(DTIME),
            "scan-length"   : SCANS or SYNTHESIS,
        },
        input=INPUT,
        output=OUTPUT,
        label="Make empty MS")

for field,skymodel in enumerate(SKYMODEL):
    if SIMSKY:  
    # Simulate sky into MS
        recipe.add("cab/simulator", "simsky", 
            {
                "msname"    : MS,
                "field-id"  : field,
                "column"    : "DATA",
                "addnoise"  : True,
                "sefd"      : 453,
                "skymodel"  : skymodel,
                "Gjones"    : GJONES,
                "smearing"  : True,
            },
            input=INPUT,
            output=OUTPUT,
            label="Simulate sky into MS")

    if DIRTY_IMAGE:
        # Make dirty image of sky
        recipe.add("cab/wsclean", "make_dirty_image",
            {
                "msname"            : MS,
                "field"             : field,
                "name"              : "{0:s}-FLD_{1:d}".format(PREFIX, field),
                "column"            : "DATA",
                "weight"            : "briggs -1.5",
                "size"              : 10000,
                "trim"              : 8192,
                "scale"             : 1.3,
                "niter"             : 1000000,
                "pol"               : "I",
                "mgain"             : 0.9,
                "auto-mask"         : 20,
                "auto-threshold"    : 0.5,
                "channelsout"       : mode[MODE]["im_nchan"],
                "fit-spectral-pol"  : 4,
                "joinchannels"      : True,
            },
            input=INPUT,
            output=OUTPUT,
            label="Make dirty image")

recipe.run()

import numpy as np
from matplotlib import pyplot

from fcutils import fcio

# The fcio class is used to open the datafile
io = fcio("./th228.fcio")

print("Number of adcs", io.nadcs)
print("Number of samples", io.nsamples)

# Some test parameters
energy_thrs = 0
max_event = 5
status_only = 0
no_status = 0

data = io.traces
rec = 1

while rec:
    rec = io.get_record()
    if rec == 0 or rec == 1 or rec == 2 or rec == 5:
        continue
    if no_status == 0 and rec == 4:
        print(
            "Status:", io.status, io.statustime[0] + io.statustime[1] / 1e6, end=' sec '
        )
        print(io.statustime[2] + io.statustime[3] / 1e6, end=' sec ')
        print(io.cards, end=' cards ')
        print(io.size, end=' ')
        for it in range(0, len(io.environment)):
            if it < 5:
                print(io.environment[it] / 1000, end=' deg ')
            elif it < 11:
                print(io.environment[it] / 1000, end=' V ')
            elif it < 12:
                print(io.environment[it] / 1000, end=' A ')
            elif it < 13:
                print(io.environment[it] / 10, end=' % ')
            elif it < 15:
                print(io.environment[it] / 1000, end=' deg ')
            else:
                print(io.environment[it], end=' ')
        print(
            "err:", io.totalerrors, io.enverrors, io.ctierrors, io.linkerrors, end=' '
        )
        for err in io.othererrors:
            print(err, end=' ')
        print("")

    if status_only:
        continue
    if io.eventnumber > max_event:
        break
    print("  Number of triggered adcs: ", io.numtraces, io.tracelist)
    if io.daqenergy[io.tracelist[0]] < energy_thrs:
        continue

    for adc in io.tracelist:
        print(
            "   FlashCam: ADC: %d Event time: %f bl: %d daq_e: %d"
            % (adc, io.eventtime, io.baseline[adc], io.daqenergy[adc] - 1)
        )
        pyplot.plot(
            np.array(io.traces[adc], dtype=np.int32) - io.baseline[adc],
            label="Trace %d - ch %d" % (io.eventnumber, adc),
        )

    pyplot.xlabel("Time [16 ns]")
    pyplot.ylabel("Baseline subt. amplitude [LSB]")
    pyplot.legend()
    pyplot.show()

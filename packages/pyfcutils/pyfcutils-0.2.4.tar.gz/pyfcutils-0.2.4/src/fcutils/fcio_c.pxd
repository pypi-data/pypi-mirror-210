# distutils: language = c++

cdef extern from "fcio.h":
  FCIOData* FCIOOpen(const char* name, int timeout, int buffer)
  int FCIOClose(FCIOData *x)
  int FCIOGetRecord(FCIOData* x)

  ctypedef struct Data:
    unsigned int reqid
    unsigned int status
    unsigned int eventno
    unsigned int pps
    unsigned int ticks
    unsigned int maxticks
    unsigned int numenv
    unsigned int numctilinks
    unsigned int numlinks
    unsigned int dumm
    unsigned int totalerrors
    unsigned int enverrors
    unsigned int ctierrors
    unsigned int linkerrors
    unsigned int othererrors[5]
    int          environment[16]
    unsigned int ctilinks[4]
    unsigned int linkstates[256]

  ctypedef struct Status:
    int status
    int statustime[10]
    int cards
    int size
    Data data[256]

  ctypedef struct Event:
    int type
    float pulser
    int timeoffset[10]
    int deadregion[10]
    int timestamp[10]
    int num_traces
    unsigned short trace_list[2305]
    unsigned short* trace[2304]
    unsigned short* theader[2304]
    unsigned short traces[2304 * 4002]

  ctypedef struct Calib:
    int status
    int upsample
    int presamples
    float pulseramp
    float threshold
    float pz[2304]
    float bl[2304]
    float pos[2304]
    float max[2304]
    float maxrms[2304]
    float *traces[2304]
    float *ptraces[2304]
    float tracebuf[2304 * 4002]
    float ptracebuf[2304 * 4002]

  ctypedef struct Config:
    int telid
    int adcs
    int triggers
    int eventsamples
    int adcbits
    int sumlength
    int blprecision
    int mastercards
    int triggercards
    int adccards
    int gps

  ctypedef struct FCIOData:
    void *ptmio
    int magic
    Config config
    Calib calib
    Event event
    Status status

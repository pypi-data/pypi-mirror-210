cimport fcio_c
cimport numpy as np

import numpy as np


cdef class fcio:
    """
    Simple cython wrapper to the fcio_c library.
    Provides a view into the traces array of the FCIOData struct, so using e.g. matplotlib is simplified.
    As a simple config readout, one can get the number of adcs channels and number of samples with GetSimpleConfig()
    although both values are also provided with the GetTraces().shape.
    """

    cdef fcio_c.FCIOData* _thisptr

    def __cinit__(self, name):
        """
        Initializer for the c part of the objects, mallocs the FCIOData structure.
        """
        name = name.encode(u"ascii")
        # cdef const char* c_name = name
        self._thisptr = fcio_c.FCIOOpen(name, 0, 0)
        if self._thisptr == NULL:
            raise MemoryError()

    def __init__ (self, name):
        """
        Initializer for the python part of the object, gets called after __cinit__

        Searches for the first config record in the data file and fills the appropriate data members.
        """
        while fcio_c.FCIOGetRecord(self._thisptr) != 1:
            pass

    def __dealloc__(self):
        fcio_c.FCIOClose(self._thisptr)

    cpdef int get_record(self):
        """
        Gets the next event in the data file loaded into the FCIOData struct.
        Use the .traces property to get a memory view wrapped by an np array to the data traces.
        """
        rc = 1
        while rc > 0:
              rc = fcio_c.FCIOGetRecord(self._thisptr)
              return rc
        return 0

    def _constructTraceList(self):
        """
        Returns the list of triggered adcs for the current event
        return np.ndarray(shape=(self.nadcs), dtype=np.int, buffer=tracelist_view)
        """
        cdef unsigned short [:] tracelist_view = self._thisptr.event.trace_list
        return np.ndarray(shape=(self.numtraces), dtype=np.int16, buffer=tracelist_view)

    def _constructTraces(self):
        """
        Returns an numpy array with a view set to the data fields in the traces array of the FCIOData struct.
        """
        cdef unsigned short [:] trace_view = self._thisptr.event.traces
        nptraces = np.ndarray(shape=(self.nadcs,self.nsamples+2), dtype=np.uint16, offset=4, buffer=trace_view)
        shape = (self.nadcs, self.nsamples)
        strides = ( (self.nsamples+2)*nptraces.itemsize, nptraces.itemsize)
        return np.lib.stride_tricks.as_strided(nptraces, shape=shape, strides=strides, writeable=False)

    def _constructTriggerTraces(self):
        """
        Returns an numpy array with a view set to the triggersum fields in the traces array of the FCIOData struct.
        """
        cdef unsigned short [:] triggertrace_view = self._thisptr.event.traces
        nptraces = np.ndarray(shape=(self.ntriggers,self.nsamples+2), dtype=np.uint16, offset=(4 + 2 * (self.nsamples+2) * self.nadcs), buffer=triggertrace_view)
        shape = (self.ntriggers, self.nsamples)
        strides = ( (self.nsamples+2)*nptraces.itemsize, nptraces.itemsize)
        return np.lib.stride_tricks.as_strided(nptraces, shape=shape, strides=strides, writeable=False)

    def _constructTraceHeader(self, offset=0):
        """
        Returns an numpy array with a view into the integrator header field in the traces array of the FCIOData struct.
        """
        cdef unsigned short [:] baseline_view = self._thisptr.event.traces
        nptraces = np.ndarray(shape=(self.nadcs, self.nsamples+2), dtype=np.uint16, offset=offset, buffer=baseline_view)
        shape = (self.nadcs, )
        strides = ( (self.nsamples+2)*nptraces.itemsize, )
        return np.lib.stride_tricks.as_strided(nptraces, shape=shape, strides=strides, writeable=False).astype(np.int16)

    @property
    def nsamples(self):
        return self._thisptr.config.eventsamples

    @property
    def nadcs(self):
        return self._thisptr.config.adcs

    @property
    def telid(self):
        return self._thisptr.config.telid

    @property
    def ntriggers(self):
        return self._thisptr.config.triggers

    @property
    def adcbits(self):
        return self._thisptr.config.adcbits

    @property
    def sumlength(self):
        return self._thisptr.config.sumlength

    @property
    def blprecision(self):
        return self._thisptr.config.blprecision

    @property
    def mastercards(self):
        return self._thisptr.config.mastercards

    @property
    def triggercards(self):
        return self._thisptr.config.triggercards

    @property
    def adccards(self):
        return self._thisptr.config.adccards

    @property
    def gps(self):
        return self._thisptr.config.gps

    @property
    def traces(self):
        return self._constructTraces()

    @property
    def triggertraces(self):
        return self._constructTriggerTraces()

    @property
    def baseline(self):
        return self._constructTraceHeader(offset=0)

    @property
    def daqenergy(self):
        return self._constructTraceHeader(offset=2)

    @property
    def pulser(self):
        return self._thisptr.event.pulser

    @property
    def eventtype(self):
        return self._thisptr.event.type

    @property
    def numtraces(self):
        return self._thisptr.event.num_traces

    @property
    def tracelist(self):
        return self._constructTraceList()

    @property
    def eventtime(self):
        return self._thisptr.event.timeoffset[2] + self._thisptr.event.timestamp[1] + self._thisptr.event.timestamp[2] / (self._thisptr.event.timestamp[3] + 1.0)

    @property
    def runtime(self):
        return self._thisptr.event.timestamp[1] + self._thisptr.event.timestamp[2] / (self._thisptr.event.timestamp[3] + 1.0)

    """
      fcio_event 'timestamp' fields
    """

    @property
    def eventnumber(self):
        return self._thisptr.event.timestamp[0]

    @property
    def timestamp_pps(self):
        return self._thisptr.event.timestamp[1]

    @property
    def timestamp_ticks(self):
        return self._thisptr.event.timestamp[2]

    @property
    def timestamp_maxticks(self):
        return self._thisptr.event.timestamp[3]

    """
      fcio_event 'timeoffset' fields
    """

    @property
    def timeoffset_mu_sec(self):
        return self._thisptr.event.timeoffset[0]

    @property
    def timeoffset_mu_usec(self):
        return self._thisptr.event.timeoffset[1]

    @property
    def timeoffset_master_sec(self):
        return self._thisptr.event.timeoffset[2]

    @property
    def timeoffset_dt_mu_usec(self):
        return self._thisptr.event.timeoffset[3]

    @property
    def timeoffset_abs_mu_usec(self):
        return self._thisptr.event.timeoffset[4]

    @property
    def timeoffset_start_sec(self):
        return self._thisptr.event.timeoffset[5]

    @property
    def timeoffset_start_usec(self):
        return self._thisptr.event.timeoffset[6]

    """
      fcio_event 'deadregion' fields
    """

    @property
    def deadregion_start_pps(self):
        return self._thisptr.event.deadregion[0]

    @property
    def deadregion_start_ticks(self):
        return self._thisptr.event.deadregion[1]

    @property
    def deadregion_stop_pps(self):
        return self._thisptr.event.deadregion[2]

    @property
    def deadregion_stop_ticks(self):
        return self._thisptr.event.deadregion[3]

    @property
    def deadregion_maxticks(self):
        return self._thisptr.event.deadregion[4]

    @property
    def deadtime(self):
        return 1.0*(self._thisptr.event.deadregion[2]-self._thisptr.event.deadregion[0]) + (self._thisptr.event.deadregion[3]-self._thisptr.event.deadregion[1])/(1.0*self._thisptr.event.deadregion[4])

    """
      other fcio_event fields
    """

    """
      fcio_status fields
    """

    @property
    def status(self):
        return self._thisptr.status.status

    @property
    def statustime(self):
        return self._thisptr.status.statustime

    @property
    def cards(self):
        return self._thisptr.status.cards

    @property
    def size(self):
        return self._thisptr.status.size

    @property
    def environment(self):
        return self._thisptr.status.data.environment

    @property
    def totalerrors(self):
        return self._thisptr.status.data.totalerrors

    @property
    def enverrors(self):
        return self._thisptr.status.data.enverrors

    @property
    def ctierrors(self):
        return self._thisptr.status.data.ctierrors

    @property
    def linkerrors(self):
        return self._thisptr.status.data.linkerrors

    @property
    def othererrors(self):
        return self._thisptr.status.data.othererrors

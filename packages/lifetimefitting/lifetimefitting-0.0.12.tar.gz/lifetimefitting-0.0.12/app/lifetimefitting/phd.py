import struct
class Crv:
    def __init__(self, f):
        self.CurveIndex = struct.unpack('i', f.read(4))[0]
        self.TimeOfRecording = struct.unpack('i', f.read(4))[0]
        self.HardwareIdent = f.read(16).decode()
        self.HardwareVersion = f.read(8).decode()
        self.HardwareSerial = struct.unpack('i', f.read(4))[0]
        self.SyncDividerync = struct.unpack('i', f.read(4))[0]
        self.CFDZeroCross0 = struct.unpack('i', f.read(4))[0]
        self.CFDLevel0 = struct.unpack('i', f.read(4))[0]
        self.CFDZeroCross1 = struct.unpack('i', f.read(4))[0]
        self.CFDLevel1 = struct.unpack('i', f.read(4))[0]
        self.Offset = struct.unpack('i', f.read(4))[0]
        self.RoutingChannel = struct.unpack('i', f.read(4))[0]
        self.ExtDevices = struct.unpack('i', f.read(4))[0]
        self.MeasMode = struct.unpack('i', f.read(4))[0]
        self.SubMode = struct.unpack('i', f.read(4))[0]
        self.P1 = struct.unpack('f', f.read(4))[0]
        self.P2 = struct.unpack('f', f.read(4))[0]
        self.P3 = struct.unpack('f', f.read(4))[0]
        self.RangeNo = struct.unpack('i', f.read(4))[0]
        self.Resolution = struct.unpack('f', f.read(4))[0]
        self.Channels = struct.unpack('i', f.read(4))[0]
        self.AcquisitionTime = struct.unpack('i', f.read(4))[0]
        self.StopAfter = struct.unpack('i', f.read(4))[0]
        self.StopReason = struct.unpack('i', f.read(4))[0]
        self.InpRate0 = struct.unpack('i', f.read(4))[0]
        self.InpRate1 = struct.unpack('i', f.read(4))[0]
        self.HistCountRate = struct.unpack('i', f.read(4))[0]
        self.IntegralCount = struct.unpack('d', f.read(8))[0]
        self.Reserved = struct.unpack('i', f.read(4))[0]
        self.DataOffset = struct.unpack('i', f.read(4))[0]
        self.RouterModelCode = struct.unpack('i', f.read(4))[0]
        self.RouterEnabled = struct.unpack('i', f.read(4))[0]
        self.RtCh_InputType = struct.unpack('i', f.read(4))[0]
        self.RtCh_InputLevel = struct.unpack('i', f.read(4))[0]
        self.RtCh_InputEdge = struct.unpack('i', f.read(4))[0]
        self.RtCh_CFDPresent = struct.unpack('i', f.read(4))[0]
        self.RtCh_CFDLevel = struct.unpack('i', f.read(4))[0]
        self.RtCh_CFDZeroCross = struct.unpack('i', f.read(4))[0]

class DisplayCurve:
    def __init__(self, f):
        self.MapTo = struct.unpack('i', f.read(4))[0]
        self.Show = struct.unpack('i', f.read(4))[0]

class Param:
    def __init__(self, f):
        self.Start = struct.unpack('f', f.read(4))[0]
        self.Step = struct.unpack('f', f.read(4))[0]
        self.End = struct.unpack('f', f.read(4))[0]

class RtCh:
    def __init__(self, f):
        self.InputType = struct.unpack('i', f.read(4))[0]
        self.InputLevel = struct.unpack('i', f.read(4))[0]
        self.InputEdge = struct.unpack('i', f.read(4))[0]
        self.CFDPresent = struct.unpack('i', f.read(4))[0]
        self.CFDLevel = struct.unpack('i', f.read(4))[0]
        self.CFDZCross = struct.unpack('i', f.read(4))[0]

class Brd:
    def __init__(self, f):
        self.HardwareIdent = f.read(16).decode()
        self.HardwareVersion = f.read(8).decode()
        self.HardwareSerial = struct.unpack('i', f.read(4))[0]
        self.SyncDivider = struct.unpack('i', f.read(4))[0]
        self.CFDZeroCross0 = struct.unpack('i', f.read(4))[0]
        self.CFDLevel0 = struct.unpack('i', f.read(4))[0]
        self.CFDZeroCross1 = struct.unpack('i', f.read(4))[0]
        self.CFDLevel1 = struct.unpack('i', f.read(4))[0]
        self.Resolution = struct.unpack('f', f.read(4))[0]
        self.RouterModelCode = struct.unpack('i', f.read(4))[0]
        self.RouterEnable = struct.unpack('i', f.read(4))[0]
        self.RtCh_1 = RtCh(f)
        self.RtCh_2 = RtCh(f)
        self.RtCh_3 = RtCh(f)
        self.RtCh_4 = RtCh(f)

class TRF:
    def __init__(self, path):
        if path[-4:] == '.txt':
            self._from_txt(path)
        elif path[-4:] == '.phd':
            self._from_phd(path)
        return
    
    def _x_y(self):
            self.y = self.Counts    
            try:
                self.Resolution = self.Crv.Resolution
            except AttributeError:
                pass
            
            self.Resolution_int = self.Resolution * 1e3
            self.x = [i * self.Resolution for i in range(len(self.Counts))]
    
    def _from_txt(self, path):
        with open(path, 'r') as f:
            lines = f.readlines()
        startLine = 0
        for line in lines:
            if '#PicoHarp 300' in line:
                startLine = 10
                binSize = int(float(lines[8]) * 1e3)

        self.Counts = []
        for line in lines[startLine:]:
            splitline = line.split()
            if len(splitline) == 1:
                try:
                    self.Counts += [int(line)]
                except ValueError:
                    pass
        self.Resolution = binSize * 1e-3
        self.Resolution_int = binSize
        self._x_y()
                 
    def _from_phd(self, path):
        with open(path, 'rb') as f:
            self.ident = f.read(16).decode()
            self.FormatVersion = f.read(6).decode()
            self.CreatorName = f.read(18).decode()
            self.CreatorVersion = f.read(12).decode()
            self.FileTime = f.read(18).decode()
            self.CR_LF = f.read(2).decode()
            self.Comment = f.read(256).decode()
            self.NumberOfCurves = struct.unpack('i', f.read(4))[0]
            self.BitsPerHistogBin = struct.unpack('i', f.read(4))[0]
            self.RoutingChannels = struct.unpack('i', f.read(4))[0]
            self.NumberOfBoards = struct.unpack('i', f.read(4))[0]
            self.ActiveCurve = struct.unpack('i', f.read(4))[0]
            self.MeasurementMode = struct.unpack('i', f.read(4))[0]
            self.SubMode = struct.unpack('i', f.read(4))[0]
            self.RangeNo = struct.unpack('i', f.read(4))[0]
            self.Offset = struct.unpack('i', f.read(4))[0]
            self.AcquisitionTime = struct.unpack('i', f.read(4))[0]
            self.StopAt = struct.unpack('i', f.read(4))[0]
            self.StopOnOvfl = struct.unpack('i', f.read(4))[0]
            self.Restart = struct.unpack('i', f.read(4))[0]
            self.DisplayLinLog = struct.unpack('i', f.read(4))[0]
            self.DisplayTimeAxisFrom = struct.unpack('i', f.read(4))[0]
            self.DisplayTimeAxisTo = struct.unpack('i', f.read(4))[0]
            self.DisplayCountAxisFrom = struct.unpack('i', f.read(4))[0]
            self.DisplayCountAxisTo = struct.unpack('i', f.read(4))[0]


            self.DisplayCurve_1 = DisplayCurve(f)
            self.DisplayCurve_2 = DisplayCurve(f)
            self.DisplayCurve_3 = DisplayCurve(f)
            self.DisplayCurve_4 = DisplayCurve(f)
            self.DisplayCurve_5 = DisplayCurve(f)
            self.DisplayCurve_6 = DisplayCurve(f)
            self.DisplayCurve_7 = DisplayCurve(f)
            self.DisplayCurve_8 = DisplayCurve(f)

            self.Param_1 = Param(f)
            self.Param_2 = Param(f)
            self.Param_3 = Param(f)

            self.RepeatMode = struct.unpack('i', f.read(4))[0]
            self.RepeatsPerCurve = struct.unpack('i', f.read(4))[0]
            self.RepeatTime = struct.unpack('i', f.read(4))[0]
            self.RepeatWaitTime = struct.unpack('i', f.read(4))[0]
            self.ScriptName = f.read(20).decode()
            self.Brd = Brd(f)
            self.Crv = Crv(f)
            self.Counts = []
            for i in range(self.Crv.Channels):
                self.Counts += [struct.unpack('I', f.read(4))[0]]
            self._x_y()

            
            return
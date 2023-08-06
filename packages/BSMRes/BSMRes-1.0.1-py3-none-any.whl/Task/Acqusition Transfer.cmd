@echo off

set /p acqnum=Acquisition Number: 

cd "C:\\Users\standalone\Desktop\Acquisition"

COPY "C:\Users\standalone\Desktop\Acquisition\Acquisition %acqnum%.cdt" "F:\MRes Data\Acquisitions" 
COPY "C:\Users\standalone\Desktop\Acquisition\Acquisition %acqnum%.cdt.ceo" "F:\MRes Data\Acquisitions" 
COPY "C:\Users\standalone\Desktop\Acquisition\Acquisition %acqnum%.cdt.dpo" "F:\MRes Data\Acquisitions" 

cd "F:\MRes Data\Acquisitions"


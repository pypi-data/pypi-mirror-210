import shutil
import os

for i in range(1,50):
    #os.remove(("E:\MRes Data\Participant " + str(i) + "\Calibration Score.csv", "E:\MRes Data\Participant " + str(i) + " Calibration Score.csv")
    #shutil.copyfile("E:\Consent Form.docx", "E:\MRes Data\Participant " + str(i) + "\Participant " + str(i) + " - Consent Form.docx")
    shutil.copyfile("E:\MRes Data\Participant " + str(i) + "\Calibration Score.csv", "E:\MRes Data\Analyses\Participant " + str(i) + " Calibration Score.csv")

print ("Copy Complete")

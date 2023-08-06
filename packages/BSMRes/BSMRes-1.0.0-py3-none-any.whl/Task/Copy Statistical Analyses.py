import shutil
import os

for i in range(1,50):
    #os.remove(("E:\MRes Data\Participant " + str(i) + "\Statistical Analyses.csv", "E:\MRes Data\Participant " + str(i) + " Statistical Analyses.csv")
    #shutil.copyfile("E:\Consent Form.docx", "E:\MRes Data\Participant " + str(i) + "\Participant " + str(i) + " - Consent Form.docx")
    shutil.copyfile("E:\MRes Data\Participant " + str(i) + "\Statistical Analyses.csv", "E:\MRes Data\Analyses\Participant " + str(i) + " Statistical Analyses.csv")

print ("Copy Complete")

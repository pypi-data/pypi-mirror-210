import shutil
import os

for i in range(1,50):
    #os.remove(("E:\MRes Data\Participant " + str(i) + "\Reaction Time.csv", "E:\MRes Data\Participant " + str(i) + " Reaction Time.csv")
    #shutil.copyfile("E:\Consent Form.docx", "E:\MRes Data\Participant " + str(i) + "\Participant " + str(i) + " - Consent Form.docx")
    shutil.copyfile("E:\MRes Data\Participant " + str(i) + "\Reaction Time.csv", "E:\MRes Data\Analyses\Participant " + str(i) + " Reaction Time.csv")
    shutil.copyfile("E:\MRes Data\Participant " + str(i) + "\Reaction Time.csv", "E:\MRes Data\Analyses\Reaction Times\Participant " + str(i) + " Reaction Time.csv")

print ("Copy Complete")

from BodyMap import BodyMap
import matplotlib.pyplot as plt

ax = BodyMap().generate(areas=['head','torso','left hand','right foot'],values=[10,30,22,12],cmap='coolwarm',background='white')
plt.show()

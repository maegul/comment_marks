# > Instructions

# Command Palette > Comment Mark > Comment Marks: Goto Comment

# > Imports

# >> Standard Library
import sys
from dataclasses import dataclass

# >> Third Party
import pandas as pd

# > Classes

class MyClass:
	pass

# >> Dataclasses

@dataclass
class MyData:
	a: int
	b: int

	# >>> Data Methods
	def hypotenuse(self):
		return (self.a**2 + self.b**2)**0.5

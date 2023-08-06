"""
A module programmed by Omer Drkić that adds loads of new features and makes Python easier to use.
"""

import cmath as c
import keyboard as k
import math as m
import os as o
import random as r
import time as t

def ceil(value: float):
  """
  Returns an integer higher than the specified floating point number.
  """
  value = int(value) + 1
  return value

def choose(*values):
  """
  Returns a random item from the specified list.
  """
  return r.choice(values)

def chooseindex(index: int, *values):
  """
  Returns an item from the specified list using a zero-based index.
  """
  return values[index]

def cls():
  """
  Clears the previous console output.
  """
  o.system("cls")

def find(string: str, character: str):
  """
  Returns the number of times a character is repeated in the specified string.
  """
  count = 0
  for i in string:
    if i == character:
      count += 1
    else:
      pass
  return count

def floor(value: float):
  """
  Returns an integer lower than the specified floating point number.
  """
  return int(value)

def key(key: int):
  """
  Pauses the program until the requested key is pressed.
  """
  if key == 0:
    k.wait("escape")
  elif key == 1:
    k.wait("f1")
  elif key == 2:
    k.wait("f2")
  elif key == 3:
    k.wait("f3")
  elif key == 4:
    k.wait("f4")
  elif key == 5:
    k.wait("f5")
  elif key == 6:
    k.wait("f6")
  elif key == 7:
    k.wait("f7")
  elif key == 8:
    k.wait("f8")
  elif key == 9:
    k.wait("f9")
  elif key == 10:
    k.wait("f10")
  elif key == 11:
    k.wait("f11")
  elif key == 12:
    k.wait("f12")
  elif key == 13:
    k.wait("asciitilde")
  elif key == 14:
    k.wait("num 1")
  elif key == 15:
    k.wait("num 2")
  elif key == 16:
    k.wait("num 3")
  elif key == 17:
    k.wait("num 4")
  elif key == 18:
    k.wait("num 5")
  elif key == 19:
    k.wait("num 6")
  elif key == 20:
    k.wait("num 7")
  elif key == 21:
    k.wait("num 8")
  elif key == 22:
    k.wait("num 9")
  elif key == 23:
    k.wait("num 0")
  elif key == 24:
    k.wait("num minus")
  elif key == 25:
    k.wait("equal")
  elif key == 26:
    k.wait("tab")
  elif key == 27:
    k.wait("caps lock")
  elif key == 28:
    k.wait("left shift")
  elif key == 29:
    k.wait("left control")
  elif key == 30:
    k.wait("left win")
  elif key == 31:
    k.wait("left alt")
  elif key == 32:
    k.wait("space")
  elif key == 33:
    k.wait("alt gr")
  elif key == 34:
    k.wait("right win")
  elif key == 35:
    k.wait("menu")
  elif key == 36:
    k.wait("right control")
  elif key == 37:
    k.wait("right shift")
  elif key == 38:
    k.wait("return")
  elif key == 39:
    k.wait("backspace")
  elif key == 40:
    k.wait("q")
  elif key == 41:
    k.wait("w")
  elif key == 42:
    k.wait("e")
  elif key == 43:
    k.wait("r")
  elif key == 44:
    k.wait("t")
  elif key == 45:
    k.wait("y")
  elif key == 46:
    k.wait("u")
  elif key == 47:
    k.wait("i")
  elif key == 48:
    k.wait("o")
  elif key == 49:
    k.wait("p")
  elif key == 50:
    k.wait("a")
  elif key == 51:
    k.wait("s")
  elif key == 52:
    k.wait("d")
  elif key == 53:
    k.wait("f")
  elif key == 54:
    k.wait("g")
  elif key == 55:
    k.wait("h")
  elif key == 56:
    k.wait("j")
  elif key == 57:
    k.wait("k")
  elif key == 58:
    k.wait("l")
  elif key == 59:
    k.wait("z")
  elif key == 60:
    k.wait("x")
  elif key == 61:
    k.wait("c")
  elif key == 62:
    k.wait("v")
  elif key == 63:
    k.wait("b")
  elif key == 64:
    k.wait("n")
  elif key == 65:
    k.wait("m")
  elif key == 66:
    k.wait("bracketleft")
  elif key == 67:
    k.wait("bracketright")
  elif key == 68:
    k.wait("semicolon")
  elif key == 69:
    k.wait("apostrophe")
  elif key == 70:
    k.wait("backslash")
  elif key == 71:
    k.wait("comma")
  elif key == 72:
    k.wait("dot")
  elif key == 73:
    k.wait("slash")
  elif key == 74:
    k.wait("up arrow")
  elif key == 75:
    k.wait("left arrow")
  elif key == 76:
    k.wait("down arrow")
  elif key == 77:
    k.wait("right arrow")
  elif key == 78:
    k.wait("num lock")
  elif key == 79:
    k.wait("num add")
  elif key == 80:
    k.wait("num sub")
  elif key == 81:
    k.wait("num multiply")
  elif key == 82:
    k.wait("num divide")
  elif key == 83:
    k.wait("num enter")
  elif key == 84:
    k.wait("insert")
  elif key == 85:
    k.wait("delete")
  elif key == 86:
    k.wait("home")
  elif key == 87:
    k.wait("end")
  elif key == 88:
    k.wait("page up")
  elif key == 89:
    k.wait("page down")
  elif key == 90:
    k.wait("print screen")
  elif key == 91:
    k.wait("scroll lock")
  elif key == 92:
    k.wait("pause break")

def random(min: float, max: float):
  """
  Returns a random float inside the specified range, including the lowest end but not the highest.
  """
  return r.uniform(min, max)

def replace(string: str, character: str, replace: str):
  """
  Replaces all the instances of a character in the specified string.
  """
  replaced = ""
  for i in string:
    if i == character:
      replaced += replace
    else:
      replaced += i
  return replaced

def round(value: float):
  """
  Rounds the specified float to the closest integer.
  """
  if value * 10 >= (int(value) * 10) + 5:
    return ceil(value)
  else:
    return floor(value)

def roundtodp(value: float, dp: int):
  """
  Rounds the floating point number to the specified number of decimal places.
  """
  return int(value * (10 ** dp)) / 10 ** dp

def tstamp():
  """
  Returns the number of seconds that passed since epoch.
  """
  return int(t.time())

def wait(interval: float):
  """
  Pauses the program for the given number of seconds.
  """
  t.sleep(interval)

def zeropad(value: int, digits: int):
  """
  Pads the specified number out to the given number of digits by adding zeroes to the left, then returns the number as a string.
  """
  value = str(value)
  string = ""
  zeroes = digits - len(value)
  for i in range(zeroes):
    string += "0"
  string += value
  return string

class mathclass:
  pi = 3.1415926535897932384626433832795028841971693993751058209749445923078164062862089986280348253421170679
  """
  Represents the value of Archimedes' Constant (π).
  """

  e = 2.7182818284590452353602874713526624977572470936999595749669676277240766303535475945713821785251664274
  """
  Represents the value of Euler's Number (e).
  """

  def acos(x: float):
    """
    Calculates the arc cosine of X.
    """
    return m.acos(x)

  def acosh(x: float):
    """
    Calculates the inverse hyperbolic cosine of X.
    """
    return m.acosh(x)

  def asin(x: float):
    """
    Calculates the arc sine of X.
    """
    return m.asin(x)

  def asinh(x: float):
    """
    Calculates the inverse hyperbolic sine of X.
    """
    return m.asinh(x)

  def atan(x: float):
    """
    Calculates the arc tangent of X.
    """
    return m.atan(x)

  def atanh(x: float):
    """
    Calculates the inverse hyperbolic tangent of X.
    """
    return m.atanh(x)

  def cbrt(x: float):
    """
    Calculates the cube root of X.
    """
    return m.cbrt(x)

  def clamp(x: float, a: float, b: float):
    """
    Clamps the specified value.
    """
    if x < a:
      return a
    elif x > b:
      return b
    else:
      return x

  def cos(x: float):
    """
    Calculates the cosine of X.
    """
    return m.cos(x)

  def cosh(x: float):
    """
    Calculates the hyperbolic cosine of X.
    """
    return m.cosh(x)

  def cosp(x: float, a: float, b: float):
    """
    Interpolates the cosine of A to B by X.
    """
    return (a + b + (a - b) * m.cos(x * 180)) / 2

  def cubic(x: float, a: float, b: float, c: float, d: float):
    """
    Cubically nterpolates through A, B, C and D by X.
    """
    return math.lerp(math.qarp(a, b, c, x), math.qarp(b, c, d, x), x)

  def distance(x1: float, x2: float, y1: float, y2: float):
    """
    Calculates the distance between two points in a 2D environment.
    """
    return m.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

  def exp(x: float):
    """
    Returns e (Euler's Number) to the power of X.
    """
    return math.e ** x

  def lerp(x: float, a: float, b: float):
    """
    Linearly interpolates A to B by X.
    """
    return a + x * (b - a)

  def ln(x: float):
    """
    Returns the base e logarithm of X.
    """
    return m.log(x, math.e)

  def log(x: float, l: float):
    """
    Returns the specified base logarithm of X.
    """
    return m.log(x, l)

  def log10(x: float):
    """
    Returns the base 10 logarithm of X.
    """
    return m.log10(x)

  def pol(a: int, b: int):
    """
    Converts the specified complex number (A, B) from rectangular coordinates to polar coordinates.
    """
    return c.polar(a, b)

  def qarp(x: float, a: float, b: float, c: float):
    """
    Quadriatically interpolates through A, B and C by X.
    """
    return math.lerp(math.lerp(a, b, x), math.lerp(b, c, x), x)

  def rec(r: float, p: float):
    """
    Converts the specified complex number (R, Φ) from polar coordinates to rectangular coordinates.
    """
    return c.rect(r, p)

  def sign(x):
    """
    Returns 1 for positive values, -1 for negative values or 0 for zero.
    """
    if x > 0:
      return 1
    elif x < 0:
      return - 1
    else:
      return 0

  def sin(x: float):
    """
    Calculates the sine of X.
    """
    return m.sin(x)

  def sinh(x: float):
    """
    Calculates the hyperbolic sine of X.
    """
    return m.sinh(x)

  def sqrt(x: float):
    """
    Calculates the square root of X.
    """
    return m.sqrt(x)

  def tan(x: float):
    """
    Calculates the tangent of X.
    """
    return m.tan(x)

  def tanh(x: float):
    """
    Calculates the hyperbolic tangent of X.
    """
    return m.tanh(x)

  def unlerp(a: float, b: float, y: float):
    """
    Linearly interpolates A to B by Y, e.g. the reverses lerping.
    """
    return (y - a) / (b - a)

class drawclass:
  def line(length: int, formation: int = 0, fixed_width: bool = True):
    """
    Draws a line in the console using full block characters.
    """
    if fixed_width:
      if formation == 0:
        for i in range(length):
          print("██", end = "")
      elif formation == 1:
        indent = 0
        for i in range(length):
          for i in range(indent):
            print("  ", end = "")
          print("██", end = "\n")
          indent += 1
      elif formation == 2:
        for i in range(length):
          print("██", end = "\n")
      elif formation == 3:
        indent = length - 1
        for i in range(length):
          for i in range(indent):
            print("  ", end = "")
          print("██", end = "\n")
          indent -= 1
    else:
      if formation == 0:
        for i in range(length):
          print("█", end = "")
      elif formation == 1:
        indent = 0
        for i in range(length):
          for i in range(indent):
            print(" ", end = "")
          print("█", end = "\n")
          indent += 1
      elif formation == 2:
        for i in range(length):
          print("█", end = "\n")
      elif formation == 3:
        indent = length - 1
        for i in range(length):
          for i in range(indent):
            print(" ", end = "")
          print("█", end = "\n")
          indent -= 1
    print()

  def rect(width: int, height: int, fixed_width: bool = True):
    """
    Draws a rectangle in the console using full block characters.
    """
    if fixed_width:
      for i in range(height):
        for i in range(width):
          print("██", end = "")
        print()
    else:
      for i in range(height):
        for i in range(width):
          print("█", end = "")
        print()
    print()

  def rectb(width: int, height: int, fixed_width: bool = True):
    """
    Draws a rectangle border in the console using full block characters.
    """
    if fixed_width:
      for i in range(width):
        print("██", end = "")
      print()
      for i in range(height):
        print("██", end = "")
        for i in range(2, width):
          print("  ", end = "")
        print("██", end = "")
        print()
      for i in range(width):
        print("██", end = "")
    else:
      for i in range(width):
        print("█", end = "")
      print()
      for i in range(height):
        print("█", end = "")
        for i in range(2, width):
          print(" ", end = "")
        print("█", end = "")
        print()
      for i in range(width):
        print("█", end = "")
    print()

math = mathclass
"""
A sub-class of the miniPy module that extends the math library.
"""

draw = drawclass
"""
A sub-class of the miniPy module that adds in-console drawing functions.
"""
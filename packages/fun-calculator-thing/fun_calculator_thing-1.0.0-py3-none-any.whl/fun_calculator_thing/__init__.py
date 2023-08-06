__version__ = '1.0.0'

class simpleFunctions:
  def add(num1, num2):
    return num1 + num2
  def subtract(num1, num2):
    return num1 - num2
  def multiply(num1, num2):
    return num1 * num2
  def divide(num1, num2):
    return num1 / num2

class fraction:
  def simplify(numerator, denominator):  
    fraction = int(numerator), int(denominator)
  
    GCF = min(abs(numerator), abs(denominator))
  
    while (numerator % GCF) != 0 or (denominator % GCF) != 0:
      GCF -= 1
  
    if round(numerator / GCF) == (numerator / GCF) and round(
        denominator / GCF) == (denominator / GCF):
      denominator /= GCF
      numerator /= GCF
      if numerator % denominator == 0:
        print(int(numerator / denominator))
      else:
        print("{}/{}".format(int(numerator), int(denominator)))

  def add(fraction1, fraction2):
    fraction1 = fraction1.replace("/", " ")
    num1, num2 = fraction1.split()
  
    fraction2 = fraction2.replace("/", " ")
    num3, num4 = fraction2.split()
  
    denominator = int(num2) * int(num4)
    numerator = int(num1) * int(num4) + int(num3) * int(num2)
  
    fraction3 = simple(numerator, denominator)
  
    print(" ")
    print(fraction3)
    
  def subtract(fraction1, fraction2):
    fraction1 = fraction1.replace("/", " ")
    num1, num2 = fraction1.split()
  
    fraction2 = fraction2.replace("/", " ")
    num3, num4 = fraction2.split()
  
    denominator = int(num2) * int(num4)
    numerator = int(num1) * int(num4) - int(num3) * int(num2)
  
    fraction3 = simple(numerator, denominator)
  
    print(" ")
    print(fraction3)

  def multiply(fraction1, fraction2):
    fraction1 = fraction1.replace("/", " ")
    num1, num2 = fraction1.split()
  
    fraction2 = fraction2.replace("/", " ")
    num3, num4 = fraction2.split()
  
    denominator = int(num2) * int(num4)
    numerator = int(num1) * int(num3)
  
    fraction3 = simple(numerator, denominator)
  
    print(" ")
    print(fraction3)

  def divide(fraction1, fraction2):
    fraction1 = fraction1.replace("/", " ")
    num1, num2 = fraction1.split()
  
    fraction2 = fraction2.replace("/", " ")
    num4, num3 = fraction2.split()
  
    denominator = int(num2) * int(num4)
    numerator = int(num1) * int(num3)
  
    fraction3 = simple(numerator, denominator)
  
    print(" ")
    print(fraction3)

  def simple(numerator, denominator):
  
    numerator, denominator = int(numerator), int(denominator)
  
    GCF = min(abs(numerator), abs(denominator))
  
    while (numerator % GCF) != 0 or (denominator % GCF) != 0:
      GCF -= 1
  
    if round(numerator / GCF) == (numerator / GCF) and round(
        denominator / GCF) == (denominator / GCF):
      denominator /= GCF
      numerator /= GCF
      if numerator % denominator == 0:
        return int(numerator / denominator)
      else:
        return ("{}/{}".format(int(numerator), int(denominator)))


## Module Quizz

### Question 1

Complete the function by filling in the missing parts. The color_translator function receives the name of a color, then
prints its hexadecimal value. Currently, it only supports the three additive primary colors (red, green, blue), so it 
returns "unknown" for all other colors.

**Solution**:

```python
def color_translator(color: str):
	if color == "red":
		hex_color = "#ff0000"
	elif color == "green":
		hex_color = "#00ff00"
	elif color == "blue":
		hex_color = "#0000ff"
	else:
		hex_color = "unknown"
	return hex_color

print(color_translator("blue")) # Should be #0000ff
print(color_translator("yellow")) # Should be unknown
print(color_translator("red")) # Should be #ff0000
print(color_translator("black")) # Should be unknown
print(color_translator("green")) # Should be #00ff00
print(color_translator("")) # Should be unknown
```

### Question 4

Students in a class receive their grades as Pass/Fail. Scores of 60 or more (out of 100) mean that the grade is "Pass". 
For lower scores, the grade is "Fail". In addition, scores above 95 (not included) are graded as "Top Score". Fill in 
this function so that it returns the proper grade.

**Solution**:

```python
def exam_grade(score):
	if score > 95:
		grade = "Top Score"
	elif score >= 60:
		grade = "Pass"
	else:
		grade = "Fail"
	return grade

print(exam_grade(65)) # Should be Pass
print(exam_grade(55)) # Should be Fail
print(exam_grade(60)) # Should be Pass
print(exam_grade(95)) # Should be Pass
print(exam_grade(100)) # Should be Top Score
print(exam_grade(0)) # Should be Fail
```

### Question 6

Complete the body of the **_format_name_** function. This function receives the **_first_name_** and **_last_name_**
parameters and then returns a properly formatted string.

Specifically:

If both the **_last_name_** and the **_first_name_** parameters are supplied, the function should return like so:

```python
print(format_name("Ella", "Fitzgerald"))
Name: Fitzgerald, Ella
```

If only **_one_** name parameter is supplied (either the first name or the last name) , the function should return like 
so:

```python
print(format_name("Adele", ""))
Name: Adele
```

or

```python
print(format_name("", "Einstein"))
Name: Einstein
```

Finally, if both names are blank, the function should return the empty string:

```python
print(format_name("", ""))
```

**Solution**:

```python
def format_name(first_name: str, last_name: str) -> str:
	string = ""
	if first_name and last_name:
		string = f"Name: {last_name}, {first_name}" 
	elif first_name or last_name:
		if first_name:
			string = f"Name: {first_name}"
		else:
			string = f"Name: {last_name}"
	return string 

print(format_name("Ernest", "Hemingway"))
# Should return the string "Name: Hemingway, Ernest"

print(format_name("", "Madonna"))
# Should return the string "Name: Madonna"

print(format_name("Voltaire", ""))
# Should return the string "Name: Voltaire"

print(format_name("", ""))
# Should return an empty string
```

### Question 7

The longest_word function is used to compare 3 words. It should return the word with the most number of characters (and 
the first in the list when they have the same length). Fill in the blank to make this happen.

**Solution**:

```python
def greater(str1, str2):
	return len(str1) > len(str2)

def first_greater(str1, str2, str3):
	return greater(str1, str2) and greater(str1, str3)

def same_lengths(str1, str2, str3):
	return len(str1) == len(str2) and len(str1) == len(str3)

def longest_word(word1, word2, word3):
	if first_greater(word1, word2, word3):
		return word1
	elif first_greater(word2, word1, word3):
		return word2
	elif first_greater(word3, word1, word2):
		return word3
	elif same_lengths(word1, word2, word3):
		return word1
	else:
		return word3

print(longest_word("chair", "couch", "table"))
print(longest_word("bed", "bath", "beyond"))
print(longest_word("laptop", "notebook", "desktop"))
```

### Question 10
The fractional_part function divides the numerator by the denominator, and returns just the fractional part (a number
between 0 and 1). Complete the body of the function so that it returns the right number.
Note: Since division by 0 produces an error, if the denominator is 0, the function should return 0 instead of attempting
the division.

```python
def fractional_part(numerator, denominator):
	if denominator == 0:
		return 0
	return (numerator / denominator) - (numerator // denominator)
	# Operate with numerator and denominator to 
# keep just the fractional part of the quotient
	return 0

print(fractional_part(5, 5)) # Should be 0
print(fractional_part(5, 4)) # Should be 0.25
print(fractional_part(5, 3)) # Should be 0.66...
print(fractional_part(5, 2)) # Should be 0.5
print(fractional_part(5, 0)) # Should be 0
print(fractional_part(0, 5)) # Should be 0
```
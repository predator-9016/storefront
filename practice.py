a=10
A=10#refference ids
print(float(a))
print(complex(a))
d=complex(a,21)
f=int(d.real)
print(f)
# we cannot convert directly we can convert seprately by defining the real and imaginary

print(d)
print(type(complex(a)))

print(id(A))
print(id(a))
# Binary to Decimal
binary_str = "1010"
decimal_value = int(binary_str, 2)
print(decimal_value)  # Output: 10

# Octal to Decimal
octal_str = "12"
decimal_value = int(octal_str, 8)
print(decimal_value)  # Output: 10

# Hexadecimal to Decimal
hex_str = "A"
decimal_value = int(hex_str, 16)
print(decimal_value)  # Output: 10


# Convert True to int
bool_value = True
int_value = int(bool_value)
print(int_value)  # Output: 1

# Convert False to int
bool_value = False
int_value = int(bool_value)
print(int_value)  # Output: 0

print(bool(None))#->false
print(bool(''))#->false
print(bool(' '))#->true


bool_list = [True, False, True, False]
int_list = [int(value) for value in bool_list]
print(int_list)


#list
#we can store more than one value, 

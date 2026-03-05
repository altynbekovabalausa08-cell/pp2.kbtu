import re

# 1) 'a' + 0 or more 'b'
def ex1(s):
    return bool(re.fullmatch(r"ab*", s))

# 2) 'a' + 2 to 3 'b'
def ex2(s):
    return bool(re.fullmatch(r"ab{2,3}", s))

# 3) lowercase joined with underscore
def ex3(s):
    return re.findall(r"\b[a-z]+(?:_[a-z]+)+\b", s)

# 4) one uppercase + lowercase letters
def ex4(s):
    return re.findall(r"\b[A-Z][a-z]+\b", s)

# 5) 'a' ... ends with 'b'
def ex5(s):
    return bool(re.fullmatch(r"a.*b", s))

# 6) replace space/comma/dot to colon
def ex6(s):
    return re.sub(r"[ ,\.]+", ":", s)

# 7) snake_case -> camel case
def ex7(s):
    parts = s.strip("_").split("_")
    if not parts or parts == [""]:
        return ""
    return parts[0].lower() + "".join(p[:1].upper() + p[1:].lower() for p in parts[1:] if p)

# 8) split at uppercase letters
def ex8(s):
    return [x for x in re.split(r"(?=[A-Z])", s) if x]

# 9) insert spaces between words starting with capitals
def ex9(s):
    return re.sub(r"(?<!^)(?=[A-Z])", " ", s).strip()

# 10) to snake_case
def ex10(s):
    s = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", s)
    s = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s)
    return s.lower()


if __name__ == "__main__":
    tests = {
        "1": ["a", "ab", "abbb", "ac"],
        "2": ["abb", "abbb", "abbbb", "a"],
        "3": ["abc_def", "a_b_c", "ABC_def", "nope"],
        "4": ["Apple", "Xy", "USA", "aBc"],
        "5": ["ab", "a---b", "ac", "ba"],
        "6": ["hello, world. ok", "a b,c...d"],
        "7": ["snake_case_string", "_hello__world_"],
        "8": ["SplitThisStringABC", "helloWorld"],
        "9": ["InsertSpacesHereNow", "NASAProjectX"],
        "10": ["camelCaseString", "PascalCaseString", "HTTPServerError"],
    }

    print("ex1:", [ex1(x) for x in tests["1"]])
    print("ex2:", [ex2(x) for x in tests["2"]])
    print("ex3:", [ex3(x) for x in tests["3"]])
    print("ex4:", [ex4(x) for x in tests["4"]])
    print("ex5:", [ex5(x) for x in tests["5"]])
    print("ex6:", [ex6(x) for x in tests["6"]])
    print("ex7:", [ex7(x) for x in tests["7"]])
    print("ex8:", [ex8(x) for x in tests["8"]])
    print("ex9:", [ex9(x) for x in tests["9"]])
    print("ex10:", [ex10(x) for x in tests["10"]])
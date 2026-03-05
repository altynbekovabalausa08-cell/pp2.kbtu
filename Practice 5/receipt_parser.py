import re
import json

with open("raw.txt", "r", encoding="utf-8") as f:
    text = f.read()

name_pat = r"(?m)^\d+\.\s*\r?\n(.*)"
price_pat = r"(?m)^Стоимость\s*\r?\n(.*)"
payment_pat = r"(?m)^(.+):\r?\n.*\r?\nИТОГО:"
datetime_pat = r"(?m)^Время:\s*(.*)"

data = {"products": [], "total_price": None, "payment_method": None, "datetime": None}
total_price = 0

for name, price in zip(re.findall(name_pat, text), re.findall(price_pat, text)):
    price = float(price.replace(',', '.').replace(' ', ''))
    data["products"].append({"name": name, "price": price})
    total_price += price

data["total_price"] = total_price
data["payment_method"] = re.search(payment_pat, text).group(1)
data["datetime"] = re.search(datetime_pat, text).group(1)

with open("output.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
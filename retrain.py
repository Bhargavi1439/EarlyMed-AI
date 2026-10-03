from src.train_diabetes import train as train_diabetes
from src.train_heart import train as train_heart
from src.train_kidney import train as train_kidney
from src.train_thyroid import train as train_thyroid

print("Training diabetes...")
train_diabetes()
print("Training heart...")
train_heart()
print("Training kidney...")
train_kidney()
print("Training thyroid...")
train_thyroid()
print("Done!")

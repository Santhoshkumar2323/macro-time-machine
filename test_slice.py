from src.slicer import slice_indicator

result = slice_indicator("fed_funds", window="3Y")
print(result.data.head(10))
print("\nSUMMARY:", result.summary)

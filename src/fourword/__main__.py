from .lib import FourWord

def show(bits: int):
    try:
        fourword = FourWord(bits).text
    except OverflowError as e:
        fourword = f"OverflowError: {e.args[0]}"
    print(f"{bits}: " + fourword)

bits_list = [32,64,128,256,512,768,1024,1280,1536,1792,2048]

print(f"FourWord {bits_list[0]}-{bits_list[-1]}")

for bits in bits_list:
    show(bits)

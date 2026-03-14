import traceback
try:
    import agent
    print('Imported agent')
except Exception:
    traceback.print_exc()
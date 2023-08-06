import examples.iqrfpy_app_helpers as app

rcodes = [-1, 0, 2, 5, 10, 12, 55, 40, 255, 270]
for rcode in rcodes:
    string = app.get_rcode_string(rcode)
    print(string)

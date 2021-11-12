import utmp

with open('/var/run/utmp', 'rb') as fd:
    buf = fd.read()
    for entry in utmp.read(buf):
        print(entry.time, entry.type, entry)

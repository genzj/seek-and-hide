from inotify_simple import INotify, flags


inotify = INotify()
watch_flags = flags.CREATE | flags.DELETE | flags.MODIFY
wd = inotify.add_watch('/var/run/utmp', watch_flags)


# And see the corresponding events:
while True:
    for event in inotify.read():
        print(event)
        for flag in flags.from_mask(event.mask):
            print('    ' + str(flag))

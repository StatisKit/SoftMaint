import platform

SYSTEMS = dict(Linux   = "linux",
               Darwin  = "osx",
               Windows = "win")
SYSTEM = str(platform.system())
if not SYSTEM in SYSTEMS:
    raise ValueError('`' + SYSTEM + '` is not a valid operating system')
else:
    SYSTEM = SYSTEMS[SYSTEM]

if SYSTEM == 'win':
    os.environ["HOME"] = os.environ["USERPROFILE"]
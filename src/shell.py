import os.path
import sys
from Tkinter import Tk

try:
    __file__
except NameError:
    __file__ = sys.argv[0]

import idlelib.configHandler
cfg = {}
for config_type in ['main', 'extensions', 'highlight', 'keys']:
    for path in [
        os.path.dirname(os.path.abspath(__file__)),
        'C:\\Python27\\Lib\\idlelib',
    ]:
        cfg_path = os.path.join(path, 'config-' + config_type + '.def')
        if os.path.exists(cfg_path):
            cfg[config_type] = idlelib.configHandler.IdleConfParser(cfg_path)
idlelib.configHandler.idleConf.defaultCfg = cfg
idlelib.configHandler.idleConf.LoadCfgFiles()

import idlelib
import idlelib.EditorWindow
import idlelib.PyShell
from idlelib.EditorWindow import fixwordbreaks
from idlelib.PyShell import PyShellFileList
idlelib.PyShell.use_subprocess = False


def main():
    base_path = os.path.dirname(os.path.abspath(__file__))
    version_file = os.path.join(base_path, 'VERSION')
    idlelib.PyShell.PyShell.shell_title = "Another Springnote"
    if os.path.exists(version_file):
        idlelib.PyShell.PyShell.shell_title += " (ver. {})".format(
                open(version_file).read().strip())
    root = Tk(className="Idle")
    fixwordbreaks(root)
    root.withdraw()
    flist = PyShellFileList(root)
    idlelib.macosxSupport.setupApp(root, flist)
    flist.open_shell()
    shell = flist.pyshell
    if not shell:
        return
    shell.interp.runcommand("""if 1:
        import sys as _sys
        _sys.argv = %r
        del _sys
        \n""" % (sys.argv,))
    script_path = os.path.normpath(os.path.join(base_path, 'run.py'))
    shell.interp.prepend_syspath(script_path)
    shell.interp.execfile(script_path)
    root.mainloop()
    root.destroy()


if __name__ == '__main__':
    main()
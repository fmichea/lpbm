# stylesheets.py - Stylesheets manager.
# Author: Franck Michea < franck.michea@gmail.com >

import os
import subprocess

import lpbm.constants
import lpbm.tools

def render_with_sass(in_path, out_path):
    try: p = subprocess.Popen(['sass', in_path], stdout=subprocess.PIPE)
    except OSError: return False
    out, err = p.communicate()
    if p.returncode == 0:
        f = open(out_path, 'w')
        f.write(out)
        f.close()
        return True
    return False

class StylesheetsManager(object):
    def __init__(self):
        # Creating directory where stylesheets are output.
        lpbm.tools.mkdir_p(lpbm.constants.ROOT_OUTPUT_STYLESHEETS)

        # Making all stylesheets.
        self.stylesheets = []
        self.stylesheets.extend(self.render_scss())
        self.stylesheets.extend(self.render_pygments_style())

    def render_scss(self):
        res = []
        for root, dirs, files in os.walk(lpbm.constants.ROOT_STYLESHEETS):
            for filename in files:
                if not filename.endswith('.scss'):
                    continue
                in_path = os.path.join(root, filename)
                out_path = os.path.join(lpbm.constants.ROOT_OUTPUT_STYLESHEETS,
                                        filename[:-5] + '.css')
                if render_with_sass(in_path, out_path):
                    res.append(out_path)
        return res

    def render_pygments_style(self):
        # Pygments stylesheet.
        path = os.path.join(lpbm.constants.ROOT_OUTPUT_STYLESHEETS, 'pygments.css')
        subprocess.call('pygmentize -S default -f html > %s' % path, shell=True)
        return [path]

    def copy_verbatim_stylesheets(self):
        res = []
        for root, dirs, files in os.walk(lpbm.constants.ROOT_SRC_STYLESHEETS):
            absroot = root.replace(lpbm.constants.ROOT_SRC_STYLESHEETS, '')[1:]
            for filename in files:
                output =  os.path.join(lpbm.constants.ROOT_OUTPUT_STYLESHEETS,
                                       abspath, filename)
                lpbm.tools.cp(os.path.join(root, filename), output)
                res.append(output)
            for dirname in dirs:
                lpbm.tools.mkdir_p(os.path.join(
                    lpbm.constants.ROOT_OUTPUT_STYLESHEETS,
                    abspath, dirname
                ))
        return res

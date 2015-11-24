"""
A script for automating parts of the astropy (or some affiliated package's)
release process.

Note that this requires GitPython (https://gitpython.readthedocs.org).
"""
from __future__ import print_function, division

import sys

import git


#helper functions
def get_dev_version_info(versionstr):
    from distutils import version

    vers = version.LooseVersion(versionstr)

    devmarker_idx = None
    for i, vi in enumerate(vers.version):
        if not isinstance(vi, int):
            if devmarker_idx is not None:
                raise ValueError('Could not figure out whether version {} is a '
                                 'release or dev version'.format(versionstr))
            devmarker_idx = i

    if devmarker_idx is None:
        return vers.version, None, None
    else:
        if len(vers.version[devmarker_idx:]) == 1:
            postdev = None
        elif len(vers.version[devmarker_idx:]) == 2:
            postdev = vers.version[devmarker_idx+1]
        elif  len(vers.version[devmarker_idx:]) > 2:
            raise ValueError('Too many points after dev markerin version {}'.format(versionstr))

        return vers.version[:devmarker_idx], vers.version[devmarker_idx], postdev


def get_maintainence_branch(versionstr):
    versiontuple, devmarker, postdev = get_dev_version_info(versionstr)
    return 'v' + '.'.join(versiontuple[:2]) + '.x'


def askyn(msg, defaultyes):
    ynstr = ' [Y/n]: ' if defaultyes else ' [y/N]: '
    res = raw_input(msg + ynstr)
    while True:
        if res.strip()=='':
            return defaultyes
        elif res.strip().lower() == 'y':
            return True
        elif res.strip().lower() == 'n':
            return False
        else:
            res = raw_input("I didn't understand that.  Try again?" + ynstr)



def do_release(versionstr, repopath, remotename):
    versiontuple, devmarker, postdev = get_dev_version_info(versionstr)
    branchname = get_maintainence_branch(versionstr)

    repo = git.Repo(repopath)
    repopath = repo.working_tree_dir  # for info below

    for remote in repo.remotes:
        if remote.name == remotename:
            break
    else:
        raise ValueError('Could not find remote {} in repo {}'.format(remotename, repopath))


    for branch in repo.branches:
        if branch.name == branchname:
            break
    else:
        raise ValueError('Could not find branch {} in repo {}'.format(branchname, repopath))


    # now start the process
    if is_astropy_core:
        print('Have you released astropy-helpers yet?  If not, you should do '
              'that first.')

    print("Don't forget to update the contributor list and any relevant changelog statistics...")

    if not askyn("Now we'll check out branch {} and clean the {} repo and  - OK?".format(branchname, repopath)):
        return False

    repo.head = branch
    repo.git.clean('-dfx')
    if repo.is_dirty():
        repo.git.reset('--hard')








if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Run scripts for simplifying/'
                                                 'automating the astropy '
                                                 'release procedure.')

    parser.add_argument('version', help='The version to release')
    parser.add_argument('repo', help='The path to a local copy of the repository', default=None)
    parser.add_argument('remotename', help='The name of the remote to push to', default='origin')

    res = do_release(args.version, args.repo, args.remotename)
    if not res:
        sys.exit(1)

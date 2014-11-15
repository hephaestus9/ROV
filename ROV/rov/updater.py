# -*- coding: utf-8 -*-
"""Radio auto updater."""

# Original code by Mikie (https://github.com/Mikie-Ghost/)
import rov
from rov import RUNDIR, logger, DATA_DIR
import urllib2
import tarfile
import os
import shutil
import platform
import subprocess
import re
from flask import json

# define master repo as user and branch in github repo
user = 'mrkipling'
branch = 'master'


def joinRundir(path):
    """Join rundir with 'path'"""
    return os.path.join(RUNDIR, path)

# file containg currently installed version hash
version_file = os.path.join(DATA_DIR, 'Version.txt')


def writeVersion(hash):
    """Write hash to version file"""
    f = open(version_file, 'w')
    f.write(hash)
    f.close()


def latestCommit():
    """Get SHA hash from latest commit"""
    url = 'https://api.github.com/repos/%s/rov/commits/%s' % (user, branch)
    result = urllib2.urlopen(url).read()
    git = json.JSONDecoder().decode(result)
    return git['sha']


def commitsBehind():
    """Calculate how many commits are missing"""
    url = 'https://api.github.com/repos/%s/rov/compare/%s...%s' % (user, rov.CURRENT_COMMIT, rov.LATEST_COMMIT)
    result = urllib2.urlopen(url).read()
    git = json.JSONDecoder().decode(result)
    return git['total_commits']


def checkGithub():
    """Check github repo for updates"""
    logger.log('UPDATER :: Checking for updates', 'INFO')

    try:
        rov.LATEST_COMMIT = latestCommit()
        if rov.FIRST_RUN:
            rov.CURRENT_COMMIT = rov.LATEST_COMMIT
            writeVersion(rov.CURRENT_COMMIT)
    except:
        logger.log('UPDATER :: Could not get latest commit from github', 'WARNING')

    if rov.CURRENT_COMMIT:

        try:
            rov.COMMITS_BEHIND = commitsBehind()
        except:
            logger.log('UPDATER :: Could not get commits behind from github', 'WARNING')

        if rov.COMMITS_BEHIND >= 1:
            logger.log('UPDATER :: Update available, you are %i commits behind' % rov.COMMITS_BEHIND, 'INFO')
            rov.COMMITS_COMPARE_URL = 'https://github.com/%s/rov/compare/%s...%s' % (user, rov.CURRENT_COMMIT, rov.LATEST_COMMIT)

        elif rov.COMMITS_BEHIND == 0:
            logger.log('UPDATER :: Up to date', 'INFO')

        elif rov.COMMITS_BEHIND == -1:
            logger.log('UPDATER :: Unknown version. Please run the updater', 'INFO')

    else:
        logger.log('UPDATER :: Unknown version. Please run the updater', 'INFO')

    return rov.COMMITS_BEHIND


def RemoveUpdateFiles():
    """Remove the downloaded new version"""
    logger.log('UPDATER :: Removing update files', 'INFO')
    tar_file = joinRundir('rov.tar.gz')
    update_folder = joinRundir('rov-update')

    try:
        if os.path.exists(tar_file):
            logger.log('UPDATER :: Removing %s' % tar_file, 'DEBUG')
            os.remove(tar_file)
    except:
        logger.log('UPDATER :: Could not remove %s' % tar_file, 'WARNING')

    try:
        if os.path.exists(update_folder):
            logger.log('UPDATER :: Removing %s' % update_folder, 'DEBUG')
            shutil.rmtree(update_folder)
    except:
        logger.log('UPDATER :: Could not remove %s' % update_folder, 'WARNING')

    return


def Update():
    """Update rov installation"""
    if rov.USE_GIT:
        update = gitUpdate()
        if update == 'complete':
            return True
        else:
            logger.log('Git update failed, attempting tarball update', 'INFO')

    tar_file = joinRundir('rov.tar.gz')
    update_folder = joinRundir('rov-update')

    # Download repo
    try:
        logger.log('UPDATER :: Downloading update file to %s' % tar_file, 'DEBUG')
        url = urllib2.urlopen('https://github.com/%s/rov/tarball/%s' % (user, branch))
        f = open(tar_file, 'wb')
        f.write(url.read())
        f.close()
    except:
        logger.log('UPDATER :: Failed to download update file', 'WARNING')
        RemoveUpdateFiles()
        return False

    # Write new hash to file
    try:
        logger.log('UPDATER :: Writing new hash to %s' % version_file, 'DEBUG')
        writeVersion(rov.LATEST_COMMIT)
    except:
        logger.log('UPDATER :: Faied to write new hash to version file', 'WARNING')
        RemoveUpdateFiles()
        return False

    # Extract to temp folder
    try:
        logger.log('UPDATER :: Extracting %s' % tar_file, 'DEBUG')
        tar = tarfile.open(tar_file)
        tar.extractall(update_folder)
        tar.close()
    except:
        logger.log('Failed to extract update file', 'WARNING')
        RemoveUpdateFiles()
        return False

    # Overwrite old files with new ones
    root_src_dir = os.path.join(update_folder, '%s-rov-%s' % (user, rov.LATEST_COMMIT[:7]))

    try:
        logger.log('UPDATER :: Overwriting old files', 'DEBUG')
        for src_dir, dirs, files in os.walk(root_src_dir):
            dst_dir = src_dir.replace(root_src_dir, RUNDIR)
            if not os.path.exists(dst_dir):
                os.mkdir(dst_dir)
            for file_ in files:
                src_file = os.path.join(src_dir, file_)
                dst_file = os.path.join(dst_dir, file_)
                if os.path.exists(dst_file):
                    os.remove(dst_file)
                shutil.move(src_file, dst_dir)
    except:
        logger.log('UPDATER :: Failed to overwrite old files', 'WARNING')
        RemoveUpdateFiles()
        return False

    # Clean up
    RemoveUpdateFiles()
    rov.CURRENT_COMMIT = rov.LATEST_COMMIT
    rov.COMMITS_BEHIND = 0

    return True


def runGit(args):
    """Run git command with args as arguments"""
    git_locations = ['git']

    if platform.system().lower() == 'darwin':
        git_locations.append('/usr/local/git/bin/git')

    output = err = None

    for cur_git in git_locations:
        cmd = cur_git + ' ' + args

        try:
            logger.log('UPDATER :: Trying to execute: "' + cmd + '" with shell in ' + RUNDIR, 'DEBUG')
            p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True, cwd=RUNDIR)
            output, err = p.communicate()
            logger.log('UPDATER :: Git output: ' + output, 'DEBUG')
        except OSError:
            logger.log('UPDATER :: Command ' + cmd + ' didn\'t work, couldn\'t find git', 'WARNING')
            continue

        if 'not found' in output or "not recognized as an internal or external command" in output:
            logger.log('UPDATER :: Unable to find git with command ' + cmd, 'WARNING')
            output = None
        elif 'fatal:' in output or err:
            logger.log('UPDATER :: Git returned bad info. Are you sure this is a git installation?', 'WARNING')
            output = None
        elif output:
            break

    return (output, err)


def gitCurrentVersion():
    """Get version hash for local installation"""
    output, err = runGit('rev-parse HEAD')

    if not output:
        logger.log('UPDATER :: Couldn\'t find latest installed version with git', 'WARNING')
        rov.USE_GIT = False
        return None

    current_commit = output.strip()

    if not re.match('^[a-z0-9]+$', current_commit):
        logger.log('UPDATER :: Git output doesn\'t look like a hash, not using it', 'WARNING')
        return None

    writeVersion(current_commit)

    return


def gitUpdate():
    """Update rov using git"""
    output, err = runGit('pull origin %s' % branch)

    if not output:
        logger.log('Couldn\'t download latest version', 'ERROR')
        rov.USE_GIT = False
        return 'failed'

    for line in output.split('\n'):

        if 'Already up-to-date.' in line:
            logger.log('UPDATER :: Already up to date', 'INFO')
            logger.log('UPDATER :: Git output: ' + str(output), 'DEBUG')
            return 'complete'
        elif 'Aborting' in line:
            logger.log('UPDATER :: Unable to update from git: ' + line, 'ERROR')
            logger.log('UPDATER :: Output: ' + str(output), 'DEBUG')
            rov.USE_GIT = False
            return 'failed'

    rov.CURRENT_COMMIT = rov.LATEST_COMMIT
    writeVersion(rov.LATEST_COMMIT)
    rov.COMMITS_BEHIND = 0

    return 'complete'
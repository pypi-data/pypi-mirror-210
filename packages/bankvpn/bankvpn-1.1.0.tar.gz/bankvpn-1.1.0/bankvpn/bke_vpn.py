#!/usr/bin/env python
#
# This script will launch the Cisco AnyConnect Mobility Client from the
# command line, and using credentials stored in the the user's Logon Keychain,
# will initiate a connection to the VPN endpoint.
#
# Requirements:
# - Cisco AnyConnect Mobility Client is assumed to be installed, and in its
# default location.
# - Python 'keyring' package is assumed to be installed.  Please see
# https://pypi.python.org/pypi/keyring for more information.
# - Python 'pexpect' package is assumed to be installed.  Please see
# https://github.com/pexpect/pexpect for more information.
# - You must walk through a manual CLI connection at least once in order to
# know what to populate the below variables with.  You can do that by
# executing `/opt/cisco/secureclient/bin/vpn connect <hostname or ip address>`
# Specifically, take note of the Group Number that you wish this script to
# connect to.  That number will need to be added to the vpngroup variable in
# the next section.
#
#
# v 0.9 2014-02-07 bill@wellingtonnet.net
# v 1.0 2021-01-14 evans.xie@shopee.com
# v 1.1 2023-05-25 jiagui.lin@shopee.com
# base on cisco version : 5.0.00556

import os
import sys
import click
import pexpect
import keyring
import yaml
import re
from .common import get_home_dir, read_file_content, print_error


@click.command()
@click.option('-e', '--env', 'env', default="ShopeeVPN", required=False,
              help='environment to connect, default as ShopeeVPN')
@click.option('-c', '--config', 'config', required=False, help='vpn connection config path')
@click.option('-p', '--pin', 'pin', required=False, help='Duo one time pin')
def main(env, config, pin):
    main1(env, config, pin)


def kill_current_connection():
    try:
        # kill cisco client ui
        os.system('kill -9 `pgrep "Cisco Secure Client"`')
        # try disconnect if in connected state
        os.system('/opt/cisco/secureclient/bin/vpn disconnect')
    except Exception as e:
        print(e)
        pass


def get_connector_config(env, path=None):
    if path is None:
        home = get_home_dir()
        path = '{}/.bke/vpn_config_local.yml'.format(home)
        if not os.path.exists(path):
            raise Exception('vpn connection config path ({}) not exist'.format(path))

    config = read_file_content(path)
    config_yaml = yaml.safe_load(config)
    return config_yaml[env]


def connection(address, vpngroup, username, password_indicator, need_otp, otp=None, flag=None):
    if sys.version_info.major == 2:
        child = pexpect.spawn('/opt/cisco/secureclient/bin/vpn connect ' + address, maxread=5000)
    else:
        child = pexpect.spawn('/opt/cisco/secureclient/bin/vpn connect ' + address, maxread=5000, encoding='utf-8')
    child.logfile = sys.stdout
    if flag == 'sre':
        child.expect('\[y\/n\]:')
        child.sendline("y")
        child.expect('\[y\/n\]:')
        child.sendline("n")
    child.expect('Group: \[.*\]')
    child.sendline(get_group_index(child.before, vpngroup))
    child.expect('Username: \[.*\]')
    child.sendline(username)
    child.expect('Password:')
    child.logfile = None
    password = keyring.get_password(password_indicator, username)
    child.sendline(password)
    if need_otp and otp is not None:
        child.expect('Second Password:')
        child.sendline(otp)
    child.logfile = sys.stdout
    child.expect('  >> state: Connected')


def connection_ph(address, username, password_indicator, need_otp, otp=None, flag=None):
    """
    currently support sg vpn, other idc may use the same connection interaction
    :param flag: remain useless, may use to specific the cisco client of sre team
    :return:
    """
    if sys.version_info.major == 2:
        child = pexpect.spawn('/opt/cisco/secureclient/bin/vpn connect ' + address, maxread=5000)
    else:
        child = pexpect.spawn('/opt/cisco/secureclient/bin/vpn connect ' + address, maxread=5000, encoding='utf-8')
    child.logfile = sys.stdout
    child.expect('\[y\/n\]:')
    child.sendline("y")
    child.expect('Username: \[.*\]')
    child.sendline(username)
    child.expect('Password:')
    child.logfile = None
    password = keyring.get_password(password_indicator, username)
    child.sendline(password)
    if need_otp and otp is not None:
        child.expect('Second Password:')
        child.sendline(otp)
    child.logfile = sys.stdout
    child.expect('\[y\/n\]:')
    child.sendline("y")
    child.expect('  >> state: Connected')

def connection_nogroup(address, vpngroup, username, password_indicator, need_otp, otp=None, flag=None):
    if sys.version_info.major == 2:
        child = pexpect.spawn('/opt/cisco/secureclient/bin/vpn connect ' + address, maxread=5000)
    else:
        child = pexpect.spawn('/opt/cisco/secureclient/bin/vpn connect ' + address, maxread=5000, encoding='utf-8')
    child.logfile = sys.stdout
    if flag == 'sre':
        child.expect('\[y\/n\]:')
        child.sendline("y")
        child.expect('\[y\/n\]:')
        child.sendline("n")
    # child.expect('Group: \[.*\]')
    # child.sendline(get_group_index(child.before, vpngroup))
    child.expect('Username: \[.*\]')
    child.sendline(username)
    child.expect('Password:')
    child.logfile = None
    password = keyring.get_password(password_indicator, username)
    child.sendline(password)
    if need_otp and otp is not None:
        child.expect('Second Password:')
        child.sendline(otp)
    child.logfile = sys.stdout
    child.expect('  >> state: Connected')

def connection_sg(address, vpngroup, username, password_indicator, need_otp, otp=None, flag=None):
    if sys.version_info.major == 2:
        child = pexpect.spawn('/opt/cisco/secureclient/bin/vpn connect ' + address, maxread=5000)
    else:
        child = pexpect.spawn('/opt/cisco/secureclient/bin/vpn connect ' + address, maxread=5000, encoding='utf-8')
    child.logfile = sys.stdout
    if flag == 'sre':
        child.expect('\[y\/n\]:')
        child.sendline("y")
        child.expect('\[y\/n\]:')
        child.sendline("n")
    # child.expect('Group: \[.*\]')
    # child.sendline(get_group_index(child.before, vpngroup))
    child.expect('Username: \[.*\]')
    child.sendline(username)
    child.expect('Password:')
    child.logfile = None
    password = keyring.get_password(password_indicator, username)
    child.sendline(password)
    if need_otp and otp is not None:
        child.expect('Second Password:')
        child.sendline(otp)
    child.logfile = sys.stdout
    child.expect('\[y\/n\]:')
    child.sendline("y")
    child.expect('  >> state: Connected')


def get_group_index(text, group):
    notice = ">> Please enter your username and password."
    choices = text[text.find(notice) + len(notice):len(text)]
    for choice in choices.split('\n'):
        if len(choice.strip()) > 0:
            id_choice = choice.strip().split(')')
            if id_choice[1].strip() == group:
                return id_choice[0]


def launch_ui():
    os.system('open -a "Cisco Secure Client"')


def main1(env=None, config=None, otp=None):
    kill_current_connection()
    try:
        config = get_connector_config(env, config)
        ph_flow = {"ph"}
        nogroup_flow = {"shopee"}
        sg_flow = {"sg"}
        if config.get("area") in ph_flow:
            connection_ph(config['address'], config['username'], config['password-indicator'],
                              config['needOpt'], otp=otp, flag=config.get("flag"))
        elif config.get("area") in sg_flow:
            connection_sg(config['address'], config['vpnGroup'], config['username'],
                          config['password-indicator'], config['needOpt'], otp=otp, flag=config.get("flag"))
        elif config.get("area") in nogroup_flow:
            connection_nogroup(config['address'], config['vpnGroup'], config['username'],
                       config['password-indicator'], config['needOpt'], otp=otp, flag=config.get("flag"))
        else:
            connection(config['address'], config['vpnGroup'], config['username'],
                       config['password-indicator'], config['needOpt'], otp=otp, flag=config.get("flag"))
    except Exception as e:
        print_error("launch AnyConnect error, please check:")
        print_error(">>1.check if missing second password")
        print_error(">>2.check if connection configuration is wrong")
        print(e)
    launch_ui()


if __name__ == '__main__':
    main()

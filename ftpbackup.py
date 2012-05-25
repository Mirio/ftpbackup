#                                    LICENSE BSD 2 CLAUSE                                       #
#                   Copyright 2012 Mirio. All rights reserved.                                  #
#   Redistribution and use in source and binary forms, with or without modification, are        #
#   permitted provided that the following conditions are met:                                   #
#       1. Redistributions of source code must retain the above copyright notice, this list of  #
#      conditions and the following disclaimer.                                                 #
#       2. Redistributions in binary form must reproduce the above copyright notice, this list  #
#      of conditions and the following disclaimer in the documentation and/or other materials   #
#      provided with the distribution.                                                          #
#                                                                                               #
#   THIS SOFTWARE IS PROVIDED BY Mirio ''AS IS'' AND ANY EXPRESS OR IMPLIED                     #
#   WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND    #
#   FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL <COPYRIGHT HOLDER> OR    #
#   CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR         #
#   CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR    #
#   SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON    #
#   ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING          #
#   NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF        #
#   ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.                                                  #
#                                                                                               #
#   The views and conclusions contained in the software and documentation are those of the      #
#   authors and should not be interpreted as representing official policies, either expressed   #
#   or implied, of Mirio                                                                        #


import time, os, sys
import ftplib, argparse,socket

ftp_info = []
print "\nCreated By Mirio"
print "Version: 1.0"
print "\n" * 3
try:
    if len(sys.argv) > 3:
        if ('--host=') in sys.argv[1]:
            if '--user=' in sys.argv[2]:
                if '--pass=' in sys.argv[3]:
                    if '--dir=' in sys.argv[4]:
                        args = sys.argv[1:]
                    else:
                        print "Use --dir for specify dir,"\
                              "for example'--dir=\' for copy all dir" 
                else:
                    print "Use --pass= for specify your ftp password"
            else:
                print "Use --user= for specify your ftp username"
        else:
            print "Use --host= for specify your ftp hostname"
    else:
        print "This program required: --host, --user, --pass, --dir for work."
except IndexError:
    print "Missing Data."
try:
    for opt in args:
        ftp_info.append(opt.split('=')[1])
except NameError:
    sys.exit(1)


try:
    dirs = []
    name_files = []
    path_files = []
    chmod_dirs = []
    chmod_files = []
    local_rootpath = os.getcwd() + '/' + time.strftime('%d_%h_%y-%H_%M')
    ftp = ftplib.FTP(ftp_info[0])
    ftp.login(ftp_info[1],ftp_info[2])
except ftplib.error_perm, resp:
    error(resp)
except socket.error:
    print "Connection Time out or Wrong Host"
    sys.exit(1)

def error(resp):
    if '530' in str(resp):
        print "Incorret Login."
    elif '550' in str(resp):
        print "Directory don't Found!"
    else:
        print resp
        print "Unknow Error."
    sys.exit(1)

def backup_dir():
    datetime = time.strftime('%d_%h_%y-%H_%M')
    if not os.path.exists(datetime):
        os.mkdir(datetime)
        os.chdir(datetime)
    else:
        print "The directory already exists. Wait 1 minute"
        sys.exit(1)

def copy_file(name, id_permission):
    ftp.retrbinary('RETR ' + name, open(name, 'wb').write)
    print "Downloaded: " + path_files[id_permission] + '/' + name
    print "Set Permission: " + chmod_files[id_permission] + '\n' + '-' * 10 + '\n'
    os.chmod(name,int(chmod_files[id_permission], 8))

def copy_folder(path, id_permission):
    os.mkdir(path)
    os.chmod(path,int(chmod_dirs[id_permission], 8))
    print "Created: " + path
    print "Set Permission: " + chmod_dirs[id_permission] + '\n' + '-' * 10 + '\n'

def main():
    backup_dir()
    lista(ftp_info[3])
    recursive()
    os.mkdir(ftp_info[3].lstrip(chr(47)))
    for number_dir in range(len(dirs)):
        copy_folder(dirs[number_dir].lstrip(chr(47)), number_dir)
    for number_files in range(len(name_files)):
        ftp.cwd(path_files[number_files])
        os.chdir(local_rootpath + path_files[number_files])
        copy_file(name_files[number_files], number_files)
    ftp.close()

def lista(percorso):
    ls = []
    ls_filtered = []
    ftp.cwd(percorso)
    ftp.retrlines('MLSD', ls.append)
    for _filter in ls:
        ls_filtered.append(_filter.split('\n'))
    for name in ls_filtered:
        if 'type=cdir' in name[0]:
            pass
        elif 'type=pdir' in name[0]:
            pass
        elif 'type=file' in name[0]:            
            tmp = []
            tmp.append(name[0].split())
            path_files.append(ftp.pwd())
            name_files.append(tmp[0][1])
            tmp_chmod_files = name[0].split(';')
            for x in tmp_chmod_files:
                if 'UNIX.mode=' in x:
                    tmp_split_files = x.split('=')
                    chmod_files.append(tmp_split_files[1])
                else:
                    pass 
        elif 'type=dir' in name[0]:
            tmp = []
            tmp.append(name[0].split())
            dirs.append(ftp.pwd() + '/' + tmp[0][1])
            tmp_chmod_dirs = name[0].split(';')
            for x in tmp_chmod_dirs:
                if 'UNIX.mode=' in x:
                    tmp_split_dirs = x.split('=')
                    chmod_dirs.append(tmp_split_dirs[1])
        else:
            pass

def recursive():
    print "Wait...Searching for the files.."
    for name_dir in dirs:
        lista(name_dir)

try:
    main()
except ftplib.error_perm, resp:
    error(resp)

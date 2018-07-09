#! /usr/bin/env python

#  Copyright (C) 2005 Chengtao Chen
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.


import os,os.path,re,string

def GetSourceList():
	'''return a list contain all *.cpp files in current dir
	'''
	ret = []
	for root, dirs, files in os.walk('./'):
		for f in files:
			if(re.match('^.+\\.[Cc][Pp][Pp]$', f) or re.match('^.+\\.[Cc]$', f)):
				if(os.path.isfile(f)):
					ret.append(f)
	
	for i in range(len(ret)):
		string.strip(ret[i])
	
	return ret

def GetSourceInfo(fileName, info = {}):
	'''retutn a dict contain some info about this file, in format show bellow:
	['ismain']- entry flag, 1 - this file contain a app entry such as main function, 
				0 - this file contian no app entry.
	['arch'] - architecture, 'std' - standard console program, 'wx' - wxWidgets program.
	['lang'] - language, only 'c' and 'cpp' are supported now.
	['depends'] - depends, a list contain all depend file which included by #include "".
	'''
	if(info == {}):
		print '------------------------------------'
		print 'Parsing ',fileName ,'...'
		print '------------------------------------'
		info = {'ismain':0, 'arch':'std', 'lang':'cpp', 'depends':[]}

	if(re.match('^.+\\.[Cc][Pp][Pp]$',fileName)):
		info['lang']='cpp'
	elif (re.match('^.+\\.[Cc]$',fileName)):
		info['lang']='c'

	if(info['depends'].count(fileName) > 0):
		return info

	if(not os.path.isfile(fileName)):
		return info

	info['depends'].append(fileName)

	fd = os.open(fileName, os.O_RDONLY)
	f = os.fdopen(fd)
	lines = f.readlines()

	for l in lines:
		# check if is main()
		if(re.match('^\\s*\\w*\\s+main\\s*\\(.+,.+\\)[^;]*$',l)):
			print 'In file "',fileName,'" contain a main() implement:'
			print '\t', l
			info['ismain'] = 1

		# check if is implement of wxApp
		if(re.match('IMPLEMENT_APP',l)):
			print 'In file "',fileName,'" contain a wxApp  implement:'
			print '\t', l
			info['ismain'] = 1
			info['arch'] = 'wx'

		# check if is wxWidgets
		if( info['arch'] == 'std' ):
			if(re.match('^#\\s*include\\s*[<"]wx[/\\\\].*\\.h[">]\\s*$',l)):
				print 'In file "',fileName,'" include a wxWidgets header: '
				print '\t', l
				info['arch'] = 'wx'
				
		# recursive call GetSourceInfo if include"" a file
		r = re.match('^#\\s*include\\s*"(.*)"\\s*$', l)
		if(r):
			fname = r.expand('\\1')
			info = GetSourceInfo(fname, info)
	
	return info

def GetCompileAddCFlag(arch='std', lang='cpp'):
	cflag = ''
	if(arch=='std'):
		pass
	elif(arch=='wx'):
		if(lang=='cpp'):
			cflag = '`wx-config --cxxflags`'
		elif(lang=='c'):
			print '** ERROR **: Use wxWidgets in .c file. '
	return cflag

def GetLinkAddCFlag(arch='std'):
	cflag = ''
	if(arch=='std'):
		pass
	elif(arch=='wx'):
		cflag = '`wx-config --libs`'
	return cflag

def GenCompileTarget(fileName, config):
	return config['obj_dir'] + '/' + os.path.splitext(fileName)[0] + config['obj_suffix']

def GenCompileCommand(fileName, info, config):
	cmd = ''
	if info['lang'] == 'cpp':
		cmd+= 'gcc'
	else:
		cmd+= 'gcc'
	cmd+= ' ' + fileName
	cmd+= ' -c'
	cmd+= ' -w'
	cmd+= ' ' + config['cflag']
	cmd+= ' ' + GetCompileAddCFlag(info['arch'], info['lang'])
	cmd+= ' -o ' + GenCompileTarget(fileName, config)
	return cmd

def GenLinkTarget(name, config):
	return config['output_dir'] + '/' + name

def GenLinkCommand(group, config):
	cmd = ''
	cmd+= 'gcc'
	cmd+= ' -w'
	for f in group['files']:
		cmd+= ' ' + GenCompileTarget(f, config)
	cmd+= ' ' + config['cflag']
	cmd+= ' ' + GetLinkAddCFlag(group['arch'])
	cmd+= ' -o ' + GenLinkTarget(group['target'], config)
	return cmd


def GenMakeRule(target, depends=[], commands=[], desc=''):
	rule = ''
	deps=''
	for d in depends:
		deps+= ' ' + d
	rule+= target + ' : ' + deps + '\n\t@echo \n' 
	if(desc==''):
		rule+= '\t@echo ">>" ' + target + ' \n'
	else:
		rule+= '\t@echo ' + desc + '\n'
	for cmd in commands:
		rule+= '\t' + cmd + '\n'
	rule+='\n'
	return rule

def GetGroups(src, config):
	groups=[]
	for f, info in src.iteritems():
		if info['ismain'] == 1 :
			groups.append({'target':os.path.splitext(f)[0], 'files':[f], 'arch':'std'})
	for i in range(len(groups)):
		for f1, info in src.iteritems():
			if info['ismain'] == 0 :
				groups[i]['files'].append(f1)
			if info['arch'] !='std' :
				groups[i]['arch'] = info['arch']
	return groups

def GenLinkDepends(files, config):
	targets =[]
	for f in files:
		targets.append(GenCompileTarget(f, config))
	return targets

def CreateDir(path):
	if(not os.path.isdir(path)):
		if os.path.exists(path):
			print "** ERROR **: The path '" + path + "' exists but not a directory, Please delete it and try again."
		else:
			print "Making directory '" + path + "'."
			os.mkdir(path)

def Run():
	src = {}
	sources = GetSourceList()

	for f in sources:
		src[f] = GetSourceInfo(f)

	configs = {}
	configs['debug']   = {'obj_suffix':'.o', 'output_dir':'.','obj_dir':'.d', 'cflag':'-g -D _LDBG'}
	configs['release'] = {'obj_suffix':'.o', 'output_dir':'release', 'obj_dir':'.r', 'cflag':'-O'  }
	configs['profile'] = {'obj_suffix':'.o', 'output_dir':'profile', 'obj_dir':'.p', 'cflag':'-pg' }

	makefile = '# This Makefile was generated by progen\n'
	makefile+= '# source list:\n'
	makefile+= '# \n'
	for f, info in src.iteritems():
		s = ' '
		if info['ismain'] == 1:
			s = '>'
		d = ''
		for f1 in info['depends']:
			d+= '\'' + f1 +'\' '
		makefile+= '#    ' + s + ' \'' + f + '\'\t: ' + d +'\n'
	makefile+= '\n\n'
	
	fd = os.open('Makefile', os.O_CREAT | os.O_WRONLY)
	fo = os.fdopen(fd, 'w')
	fo.truncate(0)

	allTargets=[]
	for c, config in configs.iteritems():
		CreateDir(config['output_dir'])
		CreateDir(config['obj_dir'])
		groups = GetGroups(src, config)
		
		config_deps=[]
		for group in groups:
			config_deps.append(GenLinkTarget(group['target'], config))
		
		config_comment =''
		for f in config_deps:
			config_comment+= f + ' '
		config_comment+=' is ready.'
		
		makefile+= GenMakeRule(c, config_deps, [], config_comment )
            
		for group in groups:
			cmd = GenLinkCommand(group, config)
			makefile+= GenMakeRule(GenLinkTarget(group['target'], config), GenLinkDepends(group['files'], config), [cmd])
			allTargets.append(GenLinkTarget(group['target'], config))
            
		for f, info in src.iteritems():
			cmd  = GenCompileCommand(f, info, config)
			makefile+= GenMakeRule(GenCompileTarget(f, config), info['depends'], [cmd])
			allTargets.append(GenCompileTarget(f, config))
            
	# target ctags
	makefile+= GenMakeRule('ctags', [], ['ctags *.cpp *.c *.h'])
    
	# target clean
	cmd=['rm -f ./tags']
	for f in allTargets:
		cmd.append( 'rm -f ' + f)
	makefile+= GenMakeRule('clean', [], cmd, 'Cleaning ...')
		
	# target progen
	makefile+= GenMakeRule('progen', [], ['progen.py'],'Generating Makefile ...')
	
	fo.write(makefile)
            
Run()


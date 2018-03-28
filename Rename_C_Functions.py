# -*- coding:utf-8 -*-

import os
import os.path
import re
import shutil


def version():
	return 'V2.4'


# 找到指定目录下特点后缀的文件
def find_file_by_types(root, isfullroot, *filetypes):
	tab_of_files = []
	for root, dirs, files in os.walk(root):
		for f in files:
			if os.path.isfile(os.path.join(root, f)) and os.path.splitext(f)[1][1:] in filetypes:  # os.path.join(root,f) 合成一个路径
				if not isfullroot:
					tab_of_files.append(os.path.join(root, f)[len(root) + 1:])
				else:
					tab_of_files.append(os.path.join(root, f))
				# print os.path.join(root,f)
	return tab_of_files


def find_all_c_functions(projectfiles):
	#
	functions = []
	functions_rule = re.compile('^(?!if\b|else\b|while\b|[\s\*])(?:[\w\*~_&]+?\s+){1,6}([\w:\*~_&]+\s*)\([^\);]*\)[^\{;]*?(?:^[^\r\n\{]*;?[\s]+){0,10}\{', re.M)  # 正则表达式设置:

	try:
		for file_path in projectfiles:
			targetfile = open(file_path, 'r')
			data = targetfile.read()
			targetfile.close()

			found_functions = re.findall(functions_rule, data)
			for found_function in found_functions:
				if found_function not in functions:
					functions.append(found_function)
		return [0, functions]
	except IOError, e:
		return [1, e]


def get_data_from_file(root, filename):
	filepath = os.path.join(root, filename)  # 合成全路径
	try:
		c_file = open(filepath, 'r')
		data = c_file.readlines()
		c_file.close()
	except IOError, e:
		return [1, e]
	else:
		newdata = []
		for item in data:
			newdata.append(item.strip())  # 删除行尾换行符
		return [0, newdata]


def get_global(root):
	filename = 'global.ini'
	return get_data_from_file(root, filename)


def get_static_from_ini(root):
	filename = 'static.ini'
	[error_code, data] = get_data_from_file(root, filename)
	newdata = []
	for item in data:
		newdata.append(item.split('\t'))
	return [error_code, newdata]


def get_function_from_ini(root):
	filename = 'function.ini'
	return get_data_from_file(root, filename)


def change_init(root):
	[error_code, global_list] = get_global(root)
	if 1 == error_code:
		return [error_code, global_list]

	[error_code, static_list] = get_static_from_ini(root)
	if 1 == error_code:
		return [error_code, static_list]

	[error_code, function_list] = get_function_from_ini(root)
	if 1 == error_code:
		return [error_code, function_list]

	return [error_code, global_list, static_list, function_list]


def add_null_for_free(root, data):

	free_func_tab = [
		['init_vci_config_lib.c','free(g_p_stVciParamsGroup[i]);','{\n\t\t\t\tfree(g_p_stVciParamsGroup[i]);\n\t\t\t\tg_p_stVciParamsGroup[i]=NULL;\n\t\t\t}'],
		['init_active_ecu_config_lib.c','free(g_p_stGeneralActiveEcuConfigGroup[i])','{\n\t\t\t\tfree(g_p_stGeneralActiveEcuConfigGroup[i]);\n\t\t\t\tg_p_stGeneralActiveEcuConfigGroup[i]=NULL;\n\t\t\t}'],
		['init_protocol_config_lib.c','free(g_p_stISO15765ConfigGroup[i]);','{\n\t\t\t\tfree(g_p_stISO15765ConfigGroup[i]);\n\t\t\t\tg_p_stISO15765ConfigGroup[i]=NULL;\n\t\t\t}'],
		['init_protocol_config_lib.c','free(g_p_stISO14230ConfigGroup[i]);','{\n\t\t\t\tfree(g_p_stISO14230ConfigGroup[i]);\n\t\t\t\tg_p_stISO14230ConfigGroup[i]=NULL;\n\t\t\t}'],
		['init_protocol_config_lib.c','free(g_p_stProtocolEndWith03HConfigGroup[i]);','{\n\t\t\t\tfree(g_p_stProtocolEndWith03HConfigGroup[i]);\n\t\t\t\tg_p_stProtocolEndWith03HConfigGroup[i]=NULL;\n\t\t\t}'],
		['init_protocol_config_lib.c','free(g_p_stVWTP20ConfigGroup[i]);','{\n\t\t\t\tfree(g_p_stVWTP20ConfigGroup[i]);\n\t\t\t\tg_p_stVWTP20ConfigGroup[i]=NULL;\n\t\t\t}'],
		['init_protocol_config_lib.c','free(g_p_stVWTP16ConfigGroup[i]);','{\n\t\t\t\tfree(g_p_stVWTP16ConfigGroup[i]);\n\t\t\t\tg_p_stVWTP16ConfigGroup[i]=NULL;\n\t\t\t}'],
		['init_specific_command_config_lib.c','free(g_stInitXmlGobalVariable.m_p_stCmdList[i].pcCmd);','{\n\t\t\t\tfree(g_stInitXmlGobalVariable.m_p_stCmdList[i].pcCmd);\n\t\t\t\tg_stInitXmlGobalVariable.m_p_stCmdList[i].pcCmd=NULL;\n\t\t\t}'],
		['init_dtc_config_lib.c','free(g_p_stGeneralReadDtcConfigGroup[i]);','{\n\t\t\t\tfree(g_p_stGeneralReadDtcConfigGroup[i]);\n\t\t\t\tg_p_stGeneralReadDtcConfigGroup[i]=NULL;\n\t\t\t}'],
		['init_freeze_config_lib.c','free(g_p_stUDSFreezeDtcConfigGroup[i]);','{\n\t\t\t\tfree(g_p_stUDSFreezeDtcConfigGroup[i]);\n\t\t\t\tg_p_stUDSFreezeDtcConfigGroup[i]=NULL;\n\t\t\t}'],
		['init_freeze_config_lib.c','free(g_p_stUDSFreezeDSConfigGroup[i][j].pcSpecificDIDRule);','{\n\t\t\t\tfree(g_p_stUDSFreezeDSConfigGroup[i][j].pcSpecificDIDRule);\n\t\t\t\tg_p_stUDSFreezeDSConfigGroup[i][j].pcSpecificDIDRule=NULL;\n\t\t\t}'],
		['init_freeze_config_lib.c','free(g_p_stUDSFreezeDSConfigGroup[i]);','{\n\t\t\t\tfree(g_p_stUDSFreezeDSConfigGroup[i]);\n\t\t\t\tg_p_stUDSFreezeDSConfigGroup[i]=NULL;\n\t\t\t}'],
		['init_process_fun_config_lib.c','free(g_p_stProcessFunConfigGroup[i]);','{\n\t\t\t\tfree(g_p_stProcessFunConfigGroup[i]);\n\t\t\t\tg_p_stProcessFunConfigGroup[i]=NULL;\n\t\t\t}'],
		['init_security_access_config_lib.c','free(g_p_stSecurityAccessConfigGroup[i]);','{\n\t\t\t\tfree(g_p_stSecurityAccessConfigGroup[i]);\n\t\t\t\tg_p_stSecurityAccessConfigGroup[i]=NULL;\n\t\t\t}'],
		['init_information_config_lib.c','free(g_p_stInformationGroupConfigGroup[i]->pstDSFormulaConfig[j].pcFormula);','{\n\t\t\t\tfree(g_p_stInformationGroupConfigGroup[i]->pstDSFormulaConfig[j].pcFormula);\n\t\t\t\tg_p_stInformationGroupConfigGroup[i]->pstDSFormulaConfig[j].pcFormula=NULL;\n\t\t\t}'],
		['init_information_config_lib.c','free(g_p_stInformationGroupConfigGroup[i]->pstDSFormulaConfig[j].pStrFormat);','{\n\t\t\t\tfree(g_p_stInformationGroupConfigGroup[i]->pstDSFormulaConfig[j].pStrFormat);\n\t\t\t\tg_p_stInformationGroupConfigGroup[i]->pstDSFormulaConfig[j].pStrFormat=NULL;\n\t\t\t}'],
		['init_information_config_lib.c','free(g_p_stInformationGroupConfigGroup[i]->pstDSFormulaConfig);','\n\t\t\t\tfree(g_p_stInformationGroupConfigGroup[i]->pstDSFormulaConfig);\n\t\t\t\tg_p_stInformationGroupConfigGroup[i]->pstDSFormulaConfig=NULL;\n\t\t\t'],
		['init_information_config_lib.c','free(g_p_stInformationGroupConfigGroup[i]);','\n\t\t\t\tfree(g_p_stInformationGroupConfigGroup[i]);\n\t\t\t\tg_p_stInformationGroupConfigGroup[i]=NULL;\n\t\t\t'],
		['init_freeze_ds_formula_config_lib.c','free(g_p_stFreezeDSFormulaConfig->pstDSFormulaConfig[j].pcFormula);','{\n\t\t\t\tfree(g_p_stFreezeDSFormulaConfig->pstDSFormulaConfig[j].pcFormula);\n\t\t\t\tg_p_stFreezeDSFormulaConfig->pstDSFormulaConfig[j].pcFormula=NULL;\n\t\t\t}'],
		['init_freeze_ds_formula_config_lib.c','free(g_p_stFreezeDSFormulaConfig->pstDSFormulaConfig[j].pStrFormat);','{\n\t\t\t\tfree(g_p_stFreezeDSFormulaConfig->pstDSFormulaConfig[j].pStrFormat);\n\t\t\t\tg_p_stFreezeDSFormulaConfig->pstDSFormulaConfig[j].pStrFormat=NULL;\n\t\t\t}'],
		['init_freeze_ds_formula_config_lib.c','free(g_p_stFreezeDSFormulaConfig->pstDSFormulaConfig);','\n\t\t\t\tfree(g_p_stFreezeDSFormulaConfig->pstDSFormulaConfig);\n\t\t\t\tg_p_stFreezeDSFormulaConfig->pstDSFormulaConfig=NULL;\n\t\t\t'],
		['init_freeze_ds_formula_config_lib.c','free(g_p_stFreezeDSFormulaConfig);','\n\t\t\t\tfree(g_p_stFreezeDSFormulaConfig);\n\t\t\t\tg_p_stFreezeDSFormulaConfig=NULL;\n\t\t\t'],
		['init_idle_link_config_lib.c','free(g_p_stIdleLinkConfigGroup[i]);','{\n\t\t\t\tfree(g_p_stIdleLinkConfigGroup[i]);\n\t\t\t\tg_p_stIdleLinkConfigGroup[i]=NULL;\n\t\t\t}'],
		['ds_lib.c','free(g_stGeneralDSFormulaGroupConfig.pstDSFormulaConfig[j].pcFormula);','{\n\t\t\t\tfree(g_stGeneralDSFormulaGroupConfig.pstDSFormulaConfig[j].pcFormula);\n\t\t\t\tg_stGeneralDSFormulaGroupConfig.pstDSFormulaConfig[j].pcFormula=NULL;\n\t\t\t}'],
		['ds_lib.c','free(g_stGeneralDSFormulaGroupConfig.pstDSFormulaConfig[j].pStrFormat);','{\n\t\t\t\tfree(g_stGeneralDSFormulaGroupConfig.pstDSFormulaConfig[j].pStrFormat);\n\t\t\t\tg_stGeneralDSFormulaGroupConfig.pstDSFormulaConfig[j].pStrFormat=NULL;\n\t\t\t}'],
		['ds_lib.c','free(g_stGeneralDSFormulaGroupConfig.pstDSFormulaConfig);','\n\t\t\t\tfree(g_stGeneralDSFormulaGroupConfig.pstDSFormulaConfig);\n\t\t\t\tg_stGeneralDSFormulaGroupConfig.pstDSFormulaConfig=NULL;\n\t\t\t']
	]

	newdata = data
	for item in free_func_tab:
		if (item[1] in data) and (item[0] in root):
			newdata = item[2]
	return newdata


def remove_the_same_prefix(inlist):
	inlist.sort(key=lambda x: len(x), reverse=False)
	len_of_inlist = len(inlist)
	new_list = inlist[:]
	for i in range(0, len_of_inlist):
		for item in inlist[i:]:
			if (inlist[i] != item) and (0 == item.find(inlist[i])) and (item in new_list):
				new_list.remove(item)
	return new_list


def add_getversion_api(root):
	str_cfiles = ['\\interface\\protocol_interface.c', '\\source\\protocol_interface.c']
	str_hfile = '\\interface\\protocol_interface.h'
	str_c_getversion = '\n//获取库的版本\n\nint get_version()\n{\n\treturn Version;\n}\n'
	str_h_getversion = '\t//获取库的版本\n\tPROTOCOL_API int get_version();\n\n#undef PROTOCOL_API'

	
	for str_cfile in str_cfiles:
		try:
			cfile = open(root + str_cfile, 'r')
			org_data = cfile.read()
			cfile.close()
		except IOError, e:
			if str_cfile==str_cfiles[-1]:
				return [1, 'Can not find protocol_interface.c\n']
			else:
				continue
		else:
			break

	if -1 != org_data.find('#define Version 0000.000.0002'):
		org_data = org_data.replace('#define Version 0000.000.0002', '#define Version 00000000')

	if -1 == org_data.find('int get_version()'):
		org_data = org_data + str_c_getversion

	try:
		cfile = open(root + str_cfile, 'w')
		cfile.write(org_data)
		cfile.close()
	except IOError, e:
		return [1, e]

	try:
		hfile = open(root + str_hfile, 'r')
		org_data = hfile.read()
		hfile.close()
		if -1 == org_data.find('PROTOCOL_API int get_version();'):
			org_data = org_data.replace('#undef PROTOCOL_API', str_h_getversion)
		hfile = open(root + str_hfile, 'w')
		hfile.write(org_data)
		hfile.close()
	except IOError, e:
		return [1, e]
	return [0, 0]


def change_to_ios_staticlib(root, prefix, global_list, static_list, function_list):
	function_list.append('send_cmd')
	function_list.append('receive_cmd')
	function_list.append('time_delay_ms')
	function_list.append('calculate')
	global_list.append('ReturnStatus')

	# print path, prefix, globalData, staticData, functionData
	# return 0

	allnewfiles = find_file_by_types(root, True, 'c', 'h')

	list_allfunctions = find_all_c_functions(allnewfiles)
	function_list = function_list + list_allfunctions[1]
	# 因为在注释中存在04()的结构,导致解析出认为04也是函数(正则表达式的问题)
	if '04' in function_list:
		function_list.remove('04')

	# 删除相同的前缀
	function_list = remove_the_same_prefix(function_list)
	global_list = remove_the_same_prefix(global_list)

	count = 0
	num_of_file = len(allnewfiles)
	for newfile in allnewfiles:
		try:
			c_file = open(newfile, 'r')
			data_org = c_file.readlines()
			c_file.close()
		except IOError, e:
			return [1, e]
		else:
			data_new = ''
			for line in data_org:

				if '#include' in line:
					# 替换反斜杠
					line = line.replace("\\", "/")
				else:
					# 增加程序释放动态分配内存后,指针没有赋值为NULL的情况
					line = add_null_for_free(newfile, line)

					# 处理静态变量
					for item in static_list:
						if (item[1] in line) and (item[0] in newfile):
							line = 'static ' + line

					# 处理全局变量和函数名的时候,会出现重复处理的问题,如g_p_stIdleLinkConfig和g_p_stIdleLinkConfigGroup,会执行两次替换
					for item in function_list:
						if item in line:
							line = line.replace(item, prefix + item)

					# 同一个位置仅替换一次是否可行,这样从长的字符串开始替换,就不会出错了吧?但怎么解决查找多个字符串的问题?
					for item in global_list:
						if item in line:
							line = line.replace(item, prefix+item)

				data_new = data_new + line
				try:
					c_file = open(newfile, 'w')
					c_file.write(data_new)
					c_file.close()
				except IOError, e:
					return [1, e]
		count = count + 1
		print '%03d%%' %(100*count/num_of_file)  # 显示进度
	return [0, 0]


if __name__ == '__main__':

	str_CopyProjectNametxt = 'CopyProjectName.txt'
	str_ProtocolFile = 'PROTOCOL'
	path = os.getcwd()  # 取得当前目录路径
	pathCopyProjectName = os.path.join(path, str_CopyProjectNametxt)  # 合成全路径
	try:
		projectfile = open(pathCopyProjectName, 'r')
		str_projectName = projectfile.readlines()
		projectfile.close()
		str_prefix = str_projectName[0]
	except IOError, e:
		str_prefix = raw_input('input name: ')

	pathPROTOCOL = os.path.join(path, str_ProtocolFile)  # 合成全路径
	if not os.path.isdir(pathPROTOCOL):  # 判断文件夹是否存在
		str_fail = 'Can not find %s\n' % pathPROTOCOL
		result = [1, str_fail]
	else:
		result = change_init(path)
		if 1 == result[0]:
			print result[1]
		else:
			globalData = result[1]
			staticData = result[2]
			functionData = result[3]

			print 'running...'
			pathNewPROTOCOL = os.path.join(path, str_prefix)
			if os.path.isdir(pathNewPROTOCOL):  # 如果存在该目录,则先删除
				shutil.rmtree(pathNewPROTOCOL)
			shutil.copytree(pathPROTOCOL, pathNewPROTOCOL)  # copy一份

			result = add_getversion_api(pathNewPROTOCOL)
			if 1 == result[0]:
				print result[1]
				raw_input('Enterkey to exit')
			else:
				result = change_to_ios_staticlib(pathNewPROTOCOL, str_prefix + '_', globalData, staticData, functionData)
				if 1 == result[0]:
					print result[1]
					raw_input('Enterkey to exit')
				else:
					print 'program finish'

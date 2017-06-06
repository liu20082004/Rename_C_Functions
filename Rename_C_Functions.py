# -*- coding:utf-8 -*-

import os
import os.path
import re
import shutil


# 找到指定目录下特点后缀的文件
def findFileByTypes(path, isfullroot, *filetypes):
	result = []
	for root, dirs, files in os.walk(path):
		for f in files:
			if os.path.isfile(os.path.join(root, f)) and os.path.splitext(f)[1][1:] in filetypes:  # os.path.join(root,f) 合成一个路径
				if False == isfullroot:
					result.append(os.path.join(root, f)[len(path) + 1:])
				else:
					result.append(os.path.join(root, f))
				# print os.path.join(root,f)
	return result

def find_all_C_functions(projectfiles):
	#
	functions = []
	functionsRule = re.compile('^(?!if\b|else\b|while\b|[\s\*])(?:[\w\*~_&]+?\s+){1,6}([\w:\*~_&]+\s*)\([^\);]*\)[^\{;]*?(?:^[^\r\n\{]*;?[\s]+){0,10}\{', re.M)  # 正则表达式设置:

	try:
		for file_path in projectfiles:
			targetfile = open(file_path, 'r')
			data = targetfile.read()
			targetfile.close()

			found_functions = re.findall(functionsRule, data)
			for found_function in found_functions:
				if found_function not in functions:
					functions.append(found_function)
		return [0,functions]
	except IOError, e:
		return [1, e]

def rename_C_Functions(str_C_file):
	try:
		c_file = open(str_C_file, 'r')
		data_org = c_file.readlines()
		c_file.close()
	except IOError, e:
		print e
		return [1, e]

def get_Data_From_File(path, filename):
	filepath = os.path.join(path, filename)  # 合成全路径
	try:
		c_file = open(filepath, 'r')
		data = c_file.readlines()
		c_file.close()
	except IOError, e:
		return [1,e]
	else:
		newdata = []
		for item in data:
			newdata.append(item.strip()) # 删除行尾换行符
		return [0, newdata]

def	 get_Global(path):
	filename = 'global.ini'
	return get_Data_From_File(path, filename)

def get_Static(path):
	filename = 'static.ini'
	[errorCode, data] = get_Data_From_File(path, filename)
	newdata = []
	for item in data:
		newdata.append(item.split('\t'))
	return [errorCode, newdata]

def get_Function(path):
	filename = 'function.ini'
	return get_Data_From_File(path, filename)

def change_init(path):
	[errorCode, globalData] = get_Global(path)
	if 1 == errorCode :
		return [errorCode, globalData]

	[errorCode, staticData] = get_Static(path)
	if 1 == errorCode :
		return [errorCode, staticData]

	[errorCode, functionData] = get_Function(path)
	if 1 == errorCode :
		return [errorCode, functionData]

	return [errorCode, globalData, staticData, functionData]

def add_NULL_For_Free(path,data):

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
		if (item[1] in data) and (item[0] in path):
			newdata = item[2]
	return newdata

def change_to_IOS_StaticLib(path, prefix, globalData, staticData, functionData):
	functionData.append('send_cmd')
	functionData.append('receive_cmd')
	functionData.append('time_delay_ms')
	functionData.append('calculate')
	globalData.append('ReturnStatus')

	#print path, prefix, globalData, staticData, functionData
	#return 0

	allnewfiles = findFileByTypes(path, True, 'c', 'h')

	result = find_all_C_functions(allnewfiles)
	functionData = functionData + result[1]

	# 对全局变量和函数名进行按字符串长度进行排序
	globalData.sort(key=lambda x: len(x), reverse=True)
	functionData.sort(key=lambda x: len(x), reverse=True)

	for newfile in allnewfiles:
		try:
			c_file = open(newfile, 'r')
			data_org = c_file.readlines()
			c_file.close()
		except IOError, e:
			return [1,e]
		else:
			data_new = ''
			for line in data_org:
				# 例外
				if '#include' not in line:

					# 增加程序释放动态分配内存后,指针没有赋值为NULL的情况
					line = add_NULL_For_Free(newfile,line)

					# 处理静态变量
					for item in staticData:
						if (item[1] in line) and (item[0] in newfile):
							line = 'static ' + line

					# 处理全局变量和函数名的时候,会出现重复处理的问题,如g_p_stIdleLinkConfig和g_p_stIdleLinkConfigGroup,会执行两次替换
					for item in functionData:
						if item in line:
							line = line.replace(item, prefix+item)

					for item in globalData:
						if item in line:
							line = line.replace(item, prefix+item)


				data_new = data_new + line
				try:
					c_file = open(newfile, 'w')
					c_file.write(data_new)
					c_file.close()
				except IOError, e:
					return [1, e]
	return [0,0]


if __name__ == '__main__':

	str_ProtocolFile = 'PROTOCOL'
	str_NewProtocolFile = 'NEW_PROTOCOL'
	path = os.getcwd() # 取得当前目录路径
	pathPROTOCOL = os.path.join(path,str_ProtocolFile) # 合成全路径
	if False == os.path.isdir( pathPROTOCOL ) : # 判断文件夹是否存在
		str_fail = 'Can not find %s\n' % pathPROTOCOL
		result = [1, str_fail]
	else :
		result = change_init(path)
		if 1 == result[0]:
			print result[1]
		else:
			globalData = result[1]
			staticData = result[2]
			functionData = result[3]

			pathNewPROTOCOL = os.path.join(path,str_NewProtocolFile)
			if True == os.path.isdir(pathNewPROTOCOL): # 如果存在该目录,则先删除
				shutil.rmtree(pathNewPROTOCOL)
			shutil.copytree(pathPROTOCOL, pathNewPROTOCOL) #copy一份
			result = change_to_IOS_StaticLib(pathNewPROTOCOL, 'a168_', globalData, staticData, functionData)

	#if 0 == result[0]:
	#	for a in result[1]:
	#		print a
	#	raw_input('Program Finish')
	#else:
	#	raw_input(result[1])

import os
import shutil
import zipfile
from rogue_tools import path_tool

def zip(src_path_or_list,out_path,keep_folder=True,compression=None):
	'''
	 "zip", "tar", "gztar", "bztar",
    or "xztar"
	'''
	z = zipfile.ZipFile(out_path,'w',compression=zipfile.ZIP_LZMA)
	__zip(z,src_path_or_list,keep_folder)
	z.close()
def __zip(zip_obj:zipfile.ZipFile,file_or_folder,keep_folder=True,root_folder=''):
	# 如果是列表,遍历之后塞进去
	if type(file_or_folder) == list:
		for path_str in file_or_folder:
			__zip(zip_obj,path_str,keep_folder)
	elif path_tool.is_dir(file_or_folder):
		sub_files = path_tool.get_sub_files(file_or_folder)
		for sub_file in sub_files:
			__zip(zip_obj,sub_file,keep_folder,file_or_folder)
	else:
		if path_tool.is_exists(file_or_folder):
			if keep_folder:
				zip_obj.write(file_or_folder,file_or_folder)
			else:
				zip_obj.write(file_or_folder,os.path.basename(file_or_folder))


def unzip(src_path,out_path):
	'''
	 "zip", "tar", "gztar", "bztar",
    or "xztar"
	'''
	shutil.unpack_archive(src_path,out_path,'zip')

def is_zip_file(src_path):
	return zipfile.is_zipfile(src_path)

	try:
		# 尝试获取zip文件，可以解析就是zip
		zipfile.ZipFile(src_path, 'r')
		return True
	except Exception:
		return False


from PyQt5.QtWidgets import  QFrame
import re

# 导入UI界面
from  Ui_ErrorDecode import Ui_ErrorDecode


# 去除花括号之外的数据
def strip_external_braces (s):
    # 查找"{"的位置
    start_index = s.find("{")
    # 查找"}"的位置
    end_index = s.find("}")
    
    if start_index == -1 :
        start_index = 0
    if end_index == -1:
        end_index = len(s)
    return s[start_index + 1:end_index]
    
def assign_bits_to_variables(decimal_value, var_info):
    """
    将十进制数按位宽分配到各个变量
    
    参数:
    decimal_value: 要分配的十进制数
    var_info: 变量信息列表，格式为[[变量名1, 位宽1], [变量名2, 位宽2], ...]
    
    返回:
    字典，包含变量名和对应的值
    """
    result = {}
    remaining_value = decimal_value
    
    # 从右到左处理每个变量（从最低位开始）
    for var_name, width in var_info:
        # 计算掩码，用于提取指定位数
        mask = (1 << width) - 1
        
        # 提取对应位的值
        value = remaining_value & mask
        
        # 将值存入结果字典
        result[var_name] = value
        
        # 右移剩余位
        remaining_value >>= width
    
    return result

def parse_variable_definitions(data_define):
    # 初始化结果列表
    result = []
    for line in data_define.strip().split('\n'):
        # 跳过空行
        if not line.strip():
            continue
        
        # 移除分号
        line = line.replace(';', '')
    
        # 按冒号分割行，获取变量名和位宽部分
        parts = line.split(':')
        if len(parts) != 2:
            continue
        
        # 获取位宽并转换为整数
        try:
            width = int(parts[1].strip())
        except ValueError:
            continue
            
        # 获取变量名
        # 从变量名部分移除类型信息
        var_parts = parts[0].strip().split()
        var_name = var_parts[-1].strip()
        
        # 添加到结果列表
        result.append([var_name, width])
    return result
    

    
class ErrorDecode(QFrame, Ui_ErrorDecode):
    """ Tab interface """
    def __init__(self, text: str, objectName, parent=None):
        super().__init__(parent=parent)
        self.setupUi(self)
        self.setObjectName(objectName)
        self.number = 0
        self.assigned_values = []
        
        self.lineEdit_input_num.textChanged.connect(self.num_analyze)
        self.textEdit_data_struct.textChanged.connect(self.struct_analyze)

    def struct_analyze(self):
        c_code = self.textEdit_data_struct.toPlainText()
        data_define = strip_external_braces(c_code)
        self.assigned_values = parse_variable_definitions(data_define)
        self.decode()

    def num_analyze(self):
        # 去除前后空格
        num_str = self.lineEdit_input_num.text().strip()
         
        # 检查是否以0x开头或者包含十六进制字符（a-f, A-F）
        hex_chars = set('abcdefABCDEF')
        if any(c in hex_chars for c in num_str) or (num_str.startswith('0x') or num_str.startswith('0X')):
            try:
                # 尝试将其作为十六进制转换
                self.number = int(num_str, 16)
                self.decode()
                return
            except ValueError:
                # 如果转换失败，尝试作为十进制处理
                pass
        
        # 默认为十进制
        try:
            self.number = int(num_str, 10)
            self.decode()
        except ValueError:
            # 如果都失败，返回0
            self.number = 0
        return
    def decode(self):
        if  (self.number == None) or (len(self.assigned_values) == 0):
            return
        result = assign_bits_to_variables(self.number,self.assigned_values)
        print(result)
        out_str = ''
        for res in result:
            print(res)
            print(type(res))
            out_str += res + '  ' + str(result[res])  +'\n'
        self.textBrowser_output.setPlainText(out_str)
            
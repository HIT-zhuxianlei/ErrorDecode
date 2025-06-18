

from PyQt5.QtWidgets import  QFrame
import re
from PyQt5.QtWidgets import  QTableWidget, QTableWidgetItem
from PyQt5.QtGui import QFont

from qfluentwidgets import TableWidget
# 导入UI界面
from  Ui_ErrorDecode import Ui_ErrorDecode
# 搞个循环队列
from collections import deque

# 变量定义存取
from data_define_manager import VariableSaver
class ErrorDecode(QFrame, Ui_ErrorDecode):
    def __init__(self, text: str, objectName, parent=None):
        super().__init__(parent=parent)
        self.setupUi(self)
        self.setObjectName(objectName)
        self.number = 0
        self.assigned_values = []
        self.circular_queue = deque(maxlen=6)        
        self.data_define_name = 'data_define'
        
        # 初始化按钮
        self.lineEdit_input_num.setClearButtonEnabled(True)
        
        # 初始化数字标签
        font = QFont("Arial", 14)
        self.label_num.setFont(font)
        
        # 初始化表格
        self.widget_table.setBorderVisible(True)
        self.widget_table.setBorderRadius(8)
        self.widget_table.setWordWrap(False)
        self.widget_table.setRowCount(6)
        self.widget_table.setColumnCount(4)
        self.widget_table.setColumnWidth(0,240)
        self.widget_table.setItem(0, 0, QTableWidgetItem('变量'))
        self.widget_table.setItem(0, 1, QTableWidgetItem('位宽'))
        self.widget_table.setItem(0, 2, QTableWidgetItem('解析值'))
        
        # 初始化json文件
        self.saver = VariableSaver("data_define.json")
        
        # 初始化列表
        json_data_defines  = self.saver.list_variables()
        if  len(json_data_defines) > 0:
            self.comboBox_data_define.addItems(json_data_defines)
            self.data_define_load()
            
        # 初始化信号与槽
        self.lineEdit_input_num.textChanged.connect(self.num_analyze)
        self.lineEdit_data_define_name.textChanged.connect(self.name_analyze)
        self.textEdit_data_struct.textChanged.connect(self.struct_analyze)
        self.pushButton.clicked.connect(self.data_define_save)
        self.comboBox_data_define.currentTextChanged.connect(self.data_define_load)

    def data_define_load(self):
        self.data_define_name = self.comboBox_data_define.currentText()
        self.assigned_values = self.saver.load_single(self.data_define_name)
        self.log('数据定义已加载')
        self.decode()
    def data_define_save(self):
        if self.assigned_values is not None and len(self.assigned_values) > 0:
            self.log('变量定义名:'+self.data_define_name)
            self.saver.save(self.data_define_name, self.assigned_values)
    def struct_analyze(self):
        c_code = self.textEdit_data_struct.toPlainText()
        input_name = self.lineEdit_data_define_name.text()
        if input_name  == '' :
            analyze_name = self.get_struct_name(c_code)
            self.data_define_name = analyze_name
            self.lineEdit_data_define_name.setText(self.data_define_name)
        else  :
            self.data_define_name = input_name
            
        data_define = self.strip_external_braces(c_code)
        self.assigned_values = self.parse_variable_definitions(data_define)
        self.log('数据类型已更新')
        self.decode()

    def name_analyze(self):
        input_name = self.lineEdit_data_define_name.text()
        if input_name != '' :
            self.data_define_name = input_name
        
    def num_analyze(self):
        # 去除前后空格
        num_str = self.lineEdit_input_num.text().strip()
         
        # 检查是否以0x开头或者包含十六进制字符（a-f, A-F）
        hex_chars = set('abcdefABCDEF')
        if any(c in hex_chars for c in num_str) or (num_str.startswith('0x') or num_str.startswith('0X')):
            try:
                self.log('检测为16进制数据')
                self.number = int(num_str, 16)
                self.decode()
                self.label_num.setText(f"DEC: {self.number} | HEX: 0x{self.number:X}")
                return
            except ValueError:
                pass
        
        # 默认为十进制
        num_chars = set('0123456789')
        if any(c in num_chars for c in num_str):
            try:
                self.log('检测为10进制数据')
                self.number = int(num_str, 10)
                self.decode()
            except ValueError:
                self.number = 0
        else:
            self.log('你好好看看输入的是啥东西!')
            
        self.label_num.setText(f"DEC: {self.number} | HEX: 0x{self.number:X}")
        return
    def decode(self):
        if (self.assigned_values is None):
            return
        result = self.assign_bits_to_variables(self.number,self.assigned_values)
        table_row_cnt = 1
        self.widget_table.setRowCount(len(result)+1)
        
        for res in result:
            self.widget_table.setItem(table_row_cnt, 0, QTableWidgetItem(res))
            self.widget_table.setItem(table_row_cnt, 1, QTableWidgetItem(str(result[res][0])))
            self.widget_table.setItem(table_row_cnt, 2, QTableWidgetItem(str(result[res][1])))
            table_row_cnt = table_row_cnt + 1

        self.log('解析完咯~')
    # 去除花括号之外的数据
    def strip_external_braces (self, s):
        start_index = s.find("{")
        end_index = s.find("}")
        
        if start_index == -1 :
            start_index = 0
        if end_index == -1:
            end_index = len(s)
        return s[start_index + 1:end_index]
        
    def assign_bits_to_variables(self, decimal_value, var_info):
        result = {}
        remaining_value = decimal_value
        # 从右到左处理每个变量（从最低位开始）
        for var_name, width in var_info:
            # 计算掩码, 用于提取指定位数
            mask = (1 << width) - 1
            # 提取对应位的值
            value = remaining_value & mask
            # 将值存入结果字典
            result[var_name] = [width, value]
            # 右移剩余位
            remaining_value >>= width
        return result

    def parse_variable_definitions(self, data_define):
        # 初始化结果列表
        result = []
        for line in data_define.strip().split('\n'):
            # 跳过空行
            if not line.strip():
                continue
            # 删除注释
            line = re.sub(r'//.*', '', line)
            line = re.sub(r'/\*.*?\*/', '', line, flags=re.DOTALL)
            
            # 移除分号
            line = line.replace(';', '')
            # 按冒号分割行, 获取变量名和位宽部分
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
    def get_struct_name(self, input_string):
        """
        提取字符串中在"}"之后的内容，直到遇到非字母数字下划线的字符
        """
        # 找到最后一个"}"的位置
        string = input_string.replace(' ', '').replace('\n', '').replace('\r', '')
        brace_index = string.rfind("}")
        
        if brace_index == -1:
            return ""
        
        # 从"}"后面的位置开始提取
        start_index = brace_index + 1
        
        # 查找第一个非字母数字下划线的字符
        end_index = start_index
        while end_index < len(string) and (string[end_index].isalnum() or string[end_index] == '_'):
            end_index += 1
        
        # 提取符合条件的内容
        return string[start_index:end_index]
    def log(self, message):
        if message == '':
            return
        self.circular_queue.append(message+'\n')
        self.textBrowser_output.setPlainText(''.join(self.circular_queue))
        
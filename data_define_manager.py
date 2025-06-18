# 支持结构体存取
import json
import os
from typing import Dict, List, Any, Union, Optional, TypeVar, Generic

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import  QFrame, QListWidgetItem, QCheckBox
from PyQt5.QtWidgets import  QTableWidget, QTableWidgetItem, QListWidget
from qfluentwidgets import ListWidget, CheckBox

# 导入UI界面
from  Ui_DataDefineManager import Ui_DataDefineManager

# 泛型类型变量, 可用于函数返回值类型检查
T = TypeVar('T')
class VariableSaver(Generic[T]):
    """变量保存工具，支持保存多个二维列表变量到JSON文件"""
    
    def __init__(self, file_path: str = "saved_variables.json"):
        self.file_path = './config/' + file_path
    
    def save(self, name: str, data: List[List[T]]) -> None:
        """保存单个变量到文件
        
        Args:
            name: 变量名称
            data: 变量内容，二维列表
        """
        # 创建保存目录（如果不存在）
        os.makedirs(os.path.dirname(self.file_path) or '.', exist_ok=True)
        
        # 加载已有的数据（如果存在）
        existing_data = self.load()
        
        # 添加或更新当前变量
        existing_data[name] = data
        
        # 写入JSON文件
        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump(existing_data, f, ensure_ascii=False, indent=2)
        
        print(f"成功保存变量 '{name}' 到 {self.file_path}")
    def load(self) -> Dict[str, List[List[T]]]:
        """从文件加载之前保存的所有变量
        
        Returns:
            包含所有保存的变量的字典，键为变量名称，值为对应的二维列表内容
        """
        if not os.path.exists(self.file_path):
            print(f"文件 {self.file_path} 不存在")
            return {}
        
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                loaded_data = json.load(f)
            return loaded_data
        except Exception as e:
            print(f"加载文件时出错: {e}")
            return {}
    
    def load_single(self, variable_name: str) -> Optional[List[List[T]]]:
        all_vars = self.load()
        return all_vars.get(variable_name)
    
    def list_variables(self) -> List[str]:
        """列出文件中保存的所有变量名称
        
        Returns:
            包含所有变量名称的列表
        """
        all_vars = self.load()
        return list(all_vars.keys())
    
    def delete(self, *variable_names: str) -> bool:
        if not variable_names:
            print("未指定要删除的变量名称")
            return False
            
        all_vars = self.load()
        print(f"已加载 {len(all_vars)} 个变量")
        if not all_vars:
            print("文件中没有变量可删除")
            return False
            
        deleted = False
        for name in variable_names:
            if name in all_vars:
                del all_vars[name]
                deleted = True
                print(f"已删除变量: {name}")
            else:
                print(f"变量不存在: {name}")
        
        if deleted:
            # 如果有变量被删除，保存更新后的变量集合
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(all_vars, f, ensure_ascii=False, indent=2)
            print(f"删除操作完成，文件中剩余 {len(all_vars)} 个变量")
            return True
        else:
            print("没有变量被删除")
            return False
    
    def clear(self) -> bool:
        if not os.path.exists(self.file_path):
            print("文件不存在，无需清空")
            return False
            
        try:
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump({}, f, ensure_ascii=False, indent=2)
            print("已清空文件中的所有变量")
            return True
        except Exception as e:
            print(f"清空文件时出错: {e}")
            return False
    
    
class DataDefineManager(QListWidget, Ui_DataDefineManager):
    """数据定义管理器类, 继承自QFrame和Ui_ErrorDecode"""
    def __init__(self, objectName, parent=None):
        super().__init__(parent=parent)
        self.setupUi(self)
        self.setObjectName(objectName)
        
        self.saver = VariableSaver("data_define.json")
        
        self.listWidget_data_define.setUniformItemSizes(True)
        self.listWidget_data_define.setStyleSheet("QListWidget::item { height: 40px; }")
        self.pushButton_delete.clicked.connect(self.data_define_delete)
        
        
        # 获取变量列表并添加带复选框的项
        data_defines = self.saver.list_variables()
        for define_name in data_defines:
            item = QListWidgetItem()
            # item.setText(define_name)
            checkbox = CheckBox(define_name)
            self.listWidget_data_define.addItem(item)
            self.listWidget_data_define.setItemWidget(item, checkbox)

    def  data_define_delete(self):
        for index in range(self.listWidget_data_define.count()):
            item = self.listWidget_data_define.item(index)
            checkbox = self.listWidget_data_define.itemWidget(item)
            if checkbox.isChecked():
                self.saver.delete(checkbox.text())
                self.listWidget_data_define.takeItem(index)  # 移除item
                
                

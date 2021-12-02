import sqlite3
import sys
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QTextEdit

class Coffee(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("main.ui", self)
        self.con = sqlite3.connect("coffee.sqlite")
        self.load_data()

    def load_data(self):
        cur = self.con.cursor()
        title = ['ID', 'Название сорта', 'Степень обжарки', 'молотый/в зернах', 'описание вкуса', 'цена(руб)', 'объем упаковки(гр)']
        self.tableWidget.setColumnCount(len(title))
        self.tableWidget.setHorizontalHeaderLabels(title)
        self.tableWidget.setRowCount(0)
        ssql = "select coffee.id, coffee.name, roastings.name as roasting, coffee.is_ground, coffee.taste_description, coffee.price, coffee.volume from coffee "
        ssql += " inner join roastings on coffee.roasting = roastings.id "
        res = cur.execute(ssql).fetchall()
        self.titles = [description[0] for description in cur.description]
        for i, row in enumerate(res):
            self.tableWidget.setRowCount(
                    self.tableWidget.rowCount() + 1)            
            for j, s in enumerate(row):
                if j == 4:                    
                    text = QTextEdit()
                    text.setText(str(row[j]) if row[j] is not None else '')
                    self.tableWidget.setCellWidget(i, j, text)
                else:
                    cellinfo = QTableWidgetItem(str(row[j]))
                    self.tableWidget.setItem(i, j, cellinfo) 
            self.tableWidget.setRowHeight(i, 90)
        self.tableWidget.resizeColumnsToContents()          
        
        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Coffee()
    ex.show()
    sys.exit(app.exec())
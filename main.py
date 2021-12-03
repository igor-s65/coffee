import sqlite3
import sys
from addEditCoffeeForm import Ui_CoffeeForm
from main_form import Ui_MainWindow
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QTextEdit, QDialog, QMessageBox


class Coffee(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.btn_add.clicked.connect(self.add_coffee)
        self.btn_edit.clicked.connect(self.edit_coffee)
        self.con = sqlite3.connect("data/coffee.sqlite")
        self.newID = 0
        self.isEdit = False
        self.load_data()

    def load_data(self):
        cur = self.con.cursor()
        title = ['ID', 'Название сорта', 'Степень обжарки', 'молотый/в зернах']
        title.extend(['описание вкуса', 'цена(руб)', 'объем упаковки(гр)'])
        self.tableWidget.setColumnCount(len(title))
        self.tableWidget.setHorizontalHeaderLabels(title)
        self.tableWidget.setRowCount(0)
        ssql = "select coffee.id, coffee.name, roastings.name as roasting, coffee.is_ground "
        ssql += ", coffee.taste_description, coffee.price, coffee.volume from coffee"
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

    def add_coffee(self):
        nm = AddEditCoffee(self)
        res = nm.exec()
        if res == QDialog.Accepted:
            rown = self.tableWidget.rowCount()
            self.tableWidget.setRowCount(
                self.tableWidget.rowCount() + 1)
            self.add_line(self.newID, rown)
            self.tableWidget.setRowHeight(rown, 90)

    def add_line(self, id, rown):
        cur = self.con.cursor()
        ssql = "select coffee.id, coffee.name, roastings.name as roasting, coffee.is_ground "
        ssql += ", coffee.taste_description, coffee.price, coffee.volume from coffee"
        ssql += " inner join roastings on coffee.roasting = roastings.id where coffee.id = ?"
        res = cur.execute(ssql, (str(id),)).fetchall()
        row = res[0]
        for j, s in enumerate(row):
            if j == 4:
                text = QTextEdit()
                text.setText(str(row[j]) if row[j] is not None else '')
                self.tableWidget.setCellWidget(rown, j, text)
            else:            
                cellinfo = QTableWidgetItem(str(row[j]))
                self.tableWidget.setItem(rown, j, cellinfo)

    def edit_coffee(self):
        if len(self.tableWidget.selectionModel().selectedRows()) > 1:
            d = QMessageBox.about(self, "Ошибка", "Одновременно редактировать можно только одну строку!")
            return
        if len(self.tableWidget.selectionModel().selectedRows()) == 0:
            d = QMessageBox.about(self, "Ошибка", "Необходимо выделить строку для редактирования!")
            return
        rown = self.tableWidget.selectionModel().selectedRows()[0].row()
        self.newID = self.tableWidget.item(rown, 0).text()
        self.isEdit = True
        nm = AddEditCoffee(self)
        res = nm.exec()
        if res == QDialog.Accepted:
            self.add_line(self.newID, rown)
        self.isEdit = False


class AddEditCoffee(QDialog, Ui_CoffeeForm):

    def __init__(self, parent=None):
        super().__init__()
        self.setupUi(self)
        self.parent = parent
        self.con = sqlite3.connect("data/coffee.sqlite")
        cur = self.con.cursor()
        ssql = "SELECT * FROM roastings order by name"
        self.roastings = cur.execute(ssql).fetchall()
        self.roasting.addItems([line[1] for line in self.roastings])
        self.modified = {}
        if self.parent.isEdit:
            ssql = "select coffee.id, coffee.name, roastings.name as roasting, coffee.is_ground,  "
            ssql += "coffee.taste_description, coffee.price, coffee.volume from coffee"
            ssql += " inner join roastings on coffee.roasting = roastings.id where coffee.id = ?"
            res = cur.execute(ssql, (str(self.parent.newID),)).fetchall()
            self.blend_name.setText(res[0][1])
            self.roasting.setCurrentText(res[0][2])
            self.is_ground.setCurrentText(res[0][3])
            self.taste_description.setText(str(res[0][4]))
            self.price.setValue(float(res[0][5]))
            self.volume.setValue(int(res[0][6]))
            self.modified['blend_name'] = res[0][1]
            self.modified['roasting'] = res[0][2]
            self.modified['is_ground'] = str(res[0][3])
            self.modified['taste_description'] = str(res[0][4])
            self.modified['price'] = str(res[0][5])
            self.modified['volume'] = str(res[0][6])            

    def accept(self):
        if len(self.blend_name.text()) == 0:
            d = QMessageBox.about(self, "Ошибка", "Не заполнено наименование сорта кофе!")
            return
        price, volume = self.price.value(), self.volume.value()
        roasting = -1
        for g in self.roastings:
            if self.roasting.currentText() == g[1]:
                roasting = g[0]
                break
        cur = self.con.cursor()
        if self.parent.isEdit:
            flds = []
            if self.blend_name.text() != self.modified['blend_name']:
                flds.append(f"name = '{self.blend_name.text()}'")
            if self.roasting.currentText() != self.modified['roasting']:
                flds.append(f"roasting = '{roasting}'")
            if self.is_ground.currentText() != self.modified['is_ground']:
                flds.append(f"is_ground = '{self.is_ground.currentText()}'")
            if self.taste_description.toPlainText() != self.modified['taste_description']:
                flds.append(f"taste_description = '{self.taste_description.toPlainText()}'")
            if self.price.text() != self.modified['price']:
                flds.append(f"price = '{self.price.text()}'")
            if self.volume.text() != self.modified['volume']:
                flds.append(f"volume = '{self.volume.text()}'")
            if len(flds) > 0:
                ssql = "update coffee set "
                ssql += ', '.join(flds)
                ssql += " where id = ?"
                cur.execute(ssql, (str(self.parent.newID),))
                self.con.commit()
        else:
            ssql = "insert into coffee ( "
            ssql += ", ".join([f"{x}" for x in self.parent.titles[1:]])
            ssql += ") values ("
            ssql += f"'{self.blend_name.text()}', '{roasting}', '{self.is_ground.currentText()}',"
            ssql += f"'{self.taste_description.toPlainText()}', '{self.price.text()}', '{self.volume.text()}'"
            ssql += ")"
            cur.execute(ssql)
            self.con.commit()
            ssql = "SELECT id FROM coffee WHERE rowid=last_insert_rowid()"
            res = cur.execute(ssql).fetchall()
            self.parent.newID = res[0][0]
        super().accept()
        

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Coffee()
    ex.show()
    sys.exit(app.exec())

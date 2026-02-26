import sqlite3
import tkinter as tk
import pandas as pd
import matplotlib.pyplot as plt
import customtkinter as ctk
import os

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "FinanceData.db")
dataBase = sqlite3.connect(db_path)

window = tk.Tk()
window.geometry("600x300")
window.resizable(False, False)
window.config(bg = "#FFFFFF")
window.title("Simple Personal Finance Tracker")

class FinanceDB:
    def __init__(self):
        self.cursor = dataBase.cursor()

    def Setup(self):
        self.cursor.execute("""
                    
            CREATE TABLE IF NOT EXISTS FinanceData (
                Income INTEGER,
                Groceries INTEGER,
                Rent INTEGER,
                Electricity INTEGER,
                SavePercent INTEGER
            )
                                     
        """)
        
        data = self.fetchData()

        if data["Columns"] == [] and data["Values"] == []:
            self.insertData([0, 0, 0, 0, 0])
        else:
            return

    def insertData(self, data: int):
        self.cursor.execute("""INSERT INTO FinanceData (Income, Groceries, Rent, Electricity, SavePercent) VALUES (?, ?, ?, ?, ?)""", data)

    def fetchData(self):
        self.cursor.row_factory = sqlite3.Row
        
        self.cursor.execute("SELECT * FROM FinanceData")
        row = self.cursor.fetchone()

        if row is None:
            return {"Columns": [], "Values": []}

        columns = row.keys()
        values = [row[col] for col in columns]

        return {"Columns": list(columns), "Values": values}

    def updateData(self, data: int, column: str):
        query = f"UPDATE FinanceData SET {column} = ?"
        self.cursor.execute(query, (data,))
    

class Animations:
    def __init__(self):
        self.swipeFrame = None
    
    def swipeSetup(self, fullscreen: bool):
        if self.swipeFrame is None:
            self.swipeFrame = ctk.CTkFrame(window, width = 600, height = 300 if fullscreen else 200, fg_color = "#FFFFFF")
            self.swipeFrame.place(x = -300, y = 150, anchor = "center")
            self.swipeFrame.lift()

    def swipe(self, fullscreen: bool, x = -300): 
        self.swipeSetup(fullscreen)
        if x < 900: 
            self.swipeFrame.place_configure(x=x) 
            window.after(5, lambda: self.swipe(fullscreen, x+6 if fullscreen else x+10))

class Questionnaire:
    def __init__(self, questions: list):
        self.questions = questions
        self.questionIndex = 0

        self.questionLabel = None
        self.smallLabel = None
        self.entry = None
        self.nextButton = None

    def endQuestionairre(self):
        self.questionLabel.destroy()
        self.smallLabel.destroy()
        self.nextButton.destroy()
        self.entry.destroy()
        
        self.questionIndex = 0
        self.questionLabel = None
        self.smallLabel = None
        self.entry = None
        self.nextButton = None

        dashboard = Dashboard()
        dashboard.Setup()

    def nextClicked(self):
        if self.entry.get() == "":
            self.smallLabel.configure(text = "Please enter a valid input", text_color = "#F16B62")
        else:
            try:
                int(self.entry.get())
                if self.entry.get() == "0":
                    self.smallLabel.configure(text = "Please enter a number greater than zero", text_color = "#F16B62")
                    return
            except:
                self.smallLabel.configure(text = "Please enter numbers only", text_color = "#F16B62")
                return
            
            columnsMap = ["Income", "Groceries", "Rent", "Electricity", "SavePercent"]

            db = FinanceDB()
            db.Setup()
            db.updateData(int(self.entry.get()), columnsMap[self.questionIndex])

            if self.questionIndex + 1 >= len(self.questions):
                anims = Animations()
                anims.swipe(True)
                
                window.after(650, self.endQuestionairre)   
                return
            
            self.nextButton.bind("<Button-1>", self.nextButton.focus_set())

            self.nextButton.configure(command = None)

            anims = Animations()
            anims.swipe(False)
            
            self.questionIndex += 1
            window.after(400, self.Setup)

    def Setup(self):
        window.geometry("600x300")
        if self.questionLabel is None:
            self.questionLabel = ctk.CTkLabel(window, width = 426, height = 52, text_color = "#333333", font = ("Inter", 20), text = self.questions[self.questionIndex])
            self.questionLabel.place(x = 300, y = 98, anchor = "center")
        else:
            self.entry.delete(0, "end")
            self.nextButton.configure(command = self.nextClicked)
            self.smallLabel.configure(text = "(enter your monthly amount)", text_color = "#888888")
            self.questionLabel.configure(text = self.questions[self.questionIndex])

        if self.smallLabel is None:
            self.smallLabel = ctk.CTkLabel(window, width = 426, height = 27, text_color = "#888888", font = ("Inter", 13), text = "(enter your monthly amount)")
            self.smallLabel.place(x = 300, y = 190, anchor = "center")

        if self.entry is None:
            self.entry = ctk.CTkEntry(
                window, 
                width = 426, 
                height = 52, 
                font = ("Inter", 20), 
                placeholder_text = " Enter Amount...", 
                placeholder_text_color = "#757575", 
                text_color = "black", 
                fg_color = "#F9FAFB",
                border_color = "#E0E0E0",
                border_width = 1,
                corner_radius = 7
            )

            self.entry.place(x = 300, y = 150, anchor = "center")
        
        if self.nextButton is None:
            self.nextButton = ctk.CTkButton(window, width = 122, height = 38, text = "Next", text_color= "#FFFFFF", font = ("Inter", 17), corner_radius = 5, fg_color = "#4A90E2", command = self.nextClicked)
            self.nextButton.place(x = 530, y = 275, anchor = "center")

class Dashboard:
    def __init__(self):
        self.mainLabel = None
        self.fig = None
        self.figPlot = None
        self.graph = None
        self.graphCont = None
        self.graphOptionMenu = None
        self.graphOptionMenuCont = None
        self.statsFrame = None
        self.statsDivider = None
        self.statLabel = None
        self.statValLabel = None
        self.retakeQuestionairreButton = None

    def createGraph(self, type: str, posX: int, posY: int, data, dataX: str, dataY: str, labelX: str, labelY: str, ticksX: list, ticksY: list, adjustX: float, adjustY: float):
        self.graphCont = ctk.CTkFrame(window, width = 280, height = 280, fg_color = "#FFFFFF", border_color = "#D9D9D9", border_width = 0.8)
        self.graphCont.place(x = posX, y = posY, anchor = "center")
        
        self.fig = plt.Figure(figsize = (2.6, 2.6), dpi = (100))
       
        self.figPlot = self.fig.add_subplot(1, 1, 1)
        self.figPlot.tick_params(axis = "x", labelsize = 7)
        self.figPlot.tick_params(axis = "y", labelsize = 7) 

        self.graph = FigureCanvasTkAgg(self.fig, self.graphCont)
        self.graph.get_tk_widget().place(x = 140, y = 140, anchor = "center")
        
        data.plot(x = dataX, y = dataY, kind = type, legend = True if type == "line" else False, ax = self.figPlot)

        self.fig.tight_layout()
        self.fig.subplots_adjust(left = adjustX, bottom = adjustY)

        self.figPlot.set_xlabel(labelX, fontsize = 6, fontweight = "medium")
        self.figPlot.set_ylabel(labelY, fontsize = 6, fontweight = "medium")
        
        if type == "bar":
            self.figPlot.set_xticklabels(self.figPlot.get_xticklabels(), rotation = 0, ha = "center")

        if ticksX is not None:
            self.figPlot.set_xticks(ticksX)

        if ticksY is not None:
            self.figPlot.set_yticks(ticksY)

        self.figPlot.grid(True, alpha = 0.25)

    def createPieChart(self, data, values: list, labels: list, posX: int, posY: int):
        self.graphCont = ctk.CTkFrame(window, width = 280, height = 280, fg_color = "#FFFFFF", border_color = "#D9D9D9", border_width = 0.8)
        self.graphCont.place(x = posX, y = posY, anchor = "center")
        
        self.fig = plt.Figure(figsize = (2.7, 2.7), dpi = (100))
       
        self.figPlot = self.fig.add_subplot(1, 1, 1)

        self.graph = FigureCanvasTkAgg(self.fig, self.graphCont)
        self.graph.get_tk_widget().place(x = 140, y = 140, anchor = "center")

        data.plot.pie(labels = labels, y = values, ax = self.figPlot, subplots = True, legend = False, autopct="%1.1f%%", textprops={'fontsize': 6})

        self.fig.tight_layout()

    def selectGraph(self, choice: str):
        db = FinanceDB()
        data = db.fetchData()

        if self.graphCont is not None:
                self.graphCont.destroy()

        if choice == "Expenses Bar Graph":   
            del data["Columns"][0]
            del data["Values"][0]
            del data["Columns"][3]
            del data["Values"][3]

            expensesData = pd.DataFrame(data)

            self.createGraph("bar", 150, 150, expensesData, "Columns", "Values", "Expenses Types", "Amount Spent", None, None, 0.23, 0.14)

        elif choice == "Pie Chart":
            allData = pd.DataFrame(data)

            self.createPieChart(allData, "Values", allData["Columns"], 150, 150)

        elif choice == "Expenses vs Income":
            del data["Columns"][4]
            del data["Values"][4]

            expensesVsIncomeData = pd.DataFrame(data)

            self.createGraph("scatter", 150, 150, expensesVsIncomeData, "Columns", "Values", "", "", None, None, 0.23, 0.14)

    def retakeQuestionairre(self):
        self.mainLabel.destroy()
        self.graphCont.destroy()
        self.graphOptionMenuCont.destroy()
        self.statsFrame.destroy()

        questions = ["What is your income?", "How much do you spend on groceries?", "What is your rent?", "How much do you spend on electricity", "What percent of your income do you save?"]
        questionnaire = Questionnaire(questions)
        questionnaire.Setup()

    def Setup(self):
        if self.mainLabel is None:
            self.mainLabel = ctk.CTkLabel(window, width = 200, height = 100, text = "Choose a graph below", text_color = "#333333", font = ("Inter", 20), anchor = "e")
            self.mainLabel.place(x = 445, y = 30, anchor = "center")

        if self.graphOptionMenuCont is None:
            self.graphOptionMenuCont = ctk.CTkFrame(window, width = 270, height = 40, fg_color = "#F9FAFB", border_width = 1, border_color = "#E0E0E0")
            self.graphOptionMenuCont.place(x = 445, y = 80, anchor = "center")

        if self.graphOptionMenu is None:
            self.graphOptionMenu = ctk.CTkOptionMenu(
                self.graphOptionMenuCont, 
                values = ["Expenses Bar Graph", "Pie Chart", "Expenses vs Income"], 
                width = 266, height = 36, 
                fg_color = "#F9FAFB", 
                text_color = "#757575", 
                button_color = "#F9FAFB", 
                button_hover_color = "#F9FAFB",
                dropdown_fg_color = "#F9FAFB",
                dropdown_text_color = "#656565",
                dropdown_hover_color = "#E6E6E6",
                command = self.selectGraph
            )

            self.graphOptionMenu.place(x = 135, y = 20, anchor = "center")
            self.selectGraph("Expenses Bar Graph")

        if self.statsFrame is None:
            db = FinanceDB()
            data = db.fetchData()

            self.statsFrame = ctk.CTkFrame(window, width = 270, height = 180, fg_color = "#FEFEFE", border_width = 1, border_color = "#E0E0E0")
            self.statsFrame.place(x = 445, y = 200, anchor = "center")

            statLabelPosY = (
                ("Income (Per Month)", 17, str(data["Values"][0])),
                ("Groceries (Per Month)", 43, str(data["Values"][1])),
                ("Rent (Per Month)", 68, str(data["Values"][2])),
                ("Electricity (Per Month)", 93, str(data["Values"][3])),
                ("Save Percentage (Per Month)", 118, str(data["Values"][4]) + "%")
            )

            for labelTxt, posY, valLabelTxt in statLabelPosY:
                self.statLabel = ctk.CTkLabel(self.statsFrame, width = 50, height = 26, text_color = "#656565", font = ("Inter", 12), text = labelTxt, anchor = "w")
                self.statLabel.place(x = 13, y = posY, anchor = "w")

                self.statValLabel = ctk.CTkLabel(self.statsFrame, width = 50, height = 26, text_color = "#333333", font = ("Inter", 12), text = valLabelTxt, anchor = "e")
                self.statValLabel.place(x = 257, y = posY, anchor = "e")

            statsDividerPosY = [30, 55.5, 80.5, 105.5, 131]

            for posY in statsDividerPosY:
                self.statsDivider = ctk.CTkFrame(self.statsFrame, width = 255, height = 2, fg_color = "#E0E0E0")
                self.statsDivider.place(x = 135, y = posY, anchor = "center")
                self.statsDivider.lift()

        if self.retakeQuestionairreButton is None:
            self.retakeQuestionairreButton = ctk.CTkButton(self.statsFrame, width = 260, height = 28, fg_color = "#4A90E2", corner_radius = 3, text = "Retake Questionairre", command = self.retakeQuestionairre)
            self.retakeQuestionairreButton.place(x = 135, y = 161, anchor = "center")

questions = ["What is your income?", "How much do you spend on groceries?", "What is your rent?", "How much do you spend on electricity", "What percent of your income do you save?"]
questionnaire = Questionnaire(questions)
questionnaire.Setup()                                                                                                                                                               

window.bind_all("<Button-1>", lambda event: event.widget.focus_set() if hasattr(event.widget, "focus_set") else None)

window.mainloop()
dataBase.close()
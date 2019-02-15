#!/usr/bin/python3

# Hello World!

import wx, datetime, wx.lib.scrolledpanel, copy, time, os

# Core classes

class Planner(wx.App):

    def __init__(self):
        super(Planner, self).__init__()
        self.plannerFrame = None
        self.currentDate = datetime.date.today()
        self.planCollection = None
        self.selectedPlan = None

        self.testInit()

    def testInit(self):

        self.planCollection = PlanCollection(filePath="./planner1/planner1.plan", inPlannerApp=self)
        #self.planCollection.addPlan(Plan(datetime.date.today(), datetime.time(hour=12), datetime.time(hour=14), "Class", self))
        #self.planCollection.addPlan(Plan(datetime.date(year=2018, month=9, day=13), datetime.time(hour=14), datetime.time(hour=15), "Dinner"))
        #self.planCollection.addPlan(Plan(datetime.date(year=2018, month=9, day=13), datetime.time(hour=17), datetime.time(hour=20), "play Video Games"))

    def initGUI(self):
        self.plannerFrame = PlannerFrame("Planner", (600, 500), self)
        self.plannerFrame.Show()
        self.updatePlanningWindow()
        self.plannerFrame.updateDateText(self.currentDate.strftime("%m/%d/%Y"))

    # updates the planning window and creates all of the respective boxes within the window according to the current date
    def updatePlanningWindow(self):
        self.plannerFrame.planBox.clear()
        planList = self.planCollection.getPlansForDate(self.currentDate)
        for plan in planList:
            self.plannerFrame.planBox.addPlanBoxFromPlan(plan)


    def changeDate(self, inDate):
        if type(inDate) is datetime.date:
            self.currentDate = inDate
            self.plannerFrame.updateDateText(self.currentDate.strftime("%m/%d/%Y"))
        elif type(inDate) is str:
            self.currentDate = datetime.datetime.strptime(inDate, "%m/%d/%Y").date()
            self.plannerFrame.updateDateText(self.currentDate.strftime("%m/%d/%Y"))
        else:
            print "Error: Inputted object is not of correct type"

    def savePlanner(self):
        self.planCollection.savePlan()

    # plan : a string containing the path to the .plan file of the planner
    def changePlanner(self, plan):
        self.unselect()
        self.planCollection.savePlan()
        self.planCollection.loadPlan(plan)
        self.updatePlanningWindow()

    # creates a new planner with the path to the .plan file
    # plan : a string containing the path to the directory of the new planner
    def newPlanner(self, plan):
        # create directory
        os.mkdir(plan)

        # create .plan file
        fileName = plan.rsplit("/", 1)[1] + ".plan"
        plan = plan + "/" + fileName
        file = open(plan, "w")
        file.write(str(0))
        file.close()

        self.changePlanner(plan)

    def addPlan(self, plan):
        self.planCollection.addPlan(plan)
        self.updatePlanningWindow()

    def removePlan(self, plan):
        self.planCollection.removePlan(plan)
        self.updatePlanningWindow()

    def getDate(self):
        return self.currentDate

    def unselect(self):
        if self.selectedPlan is not None:
            self.selectedPlan.panel.SetBackgroundColour(wx.NullColour)
            self.selectedPlan = None

    def selectPlan(self, plan):
        #if type(plan) is not Plan:
        #    raise TypeError("Parameter is not of type Plan")
        #    return
        self.unselect()
        self.selectedPlan = plan

    def getSelectedPlan(self):
        return self.selectedPlan

    def removeSelectedPlan(self):
        if self.selectedPlan is not None:
            self.removePlan(self.selectedPlan)
            self.selectedPlan = None


class Plan:

    def __init__(self):
        self.date = None
        self.startTime = None
        self.endTime = None
        self.descriptionText = None

    def __init__(self, inDate=None, inStartTime=None, inEndTime=None, inText=None, inPlannerApp=None):
        self.plannerApp = inPlannerApp
        self.date = inDate
        self.startTime = inStartTime
        self.endTime = inEndTime
        self.descriptionText = inText
        # the panel which represents the plan within the GUI
        self.panel = None

        # the full path and file name of the file which this plan was loaded from, if it was loaded from a file at all
        self.filePath = None

    def setValues(self, inDate, inStartTime, inEndTime, inText):
        self.date = inDate
        self.startTime = inStartTime
        self.endTime = inEndTime
        self.descriptionText = inText

    def getDate(self):
        return self.date

    def getStartTime(self):
        return self.startTime

    def getEndTime(self):
        return self.endTime

    def select(self, e):
        self.plannerApp.selectPlan(self)
        self.panel.SetBackgroundColour(wx.Colour(166, 255, 166))

    def setPanel(self, inPanel):
        if type(inPanel) is not wx.Panel:
            raise TypeError("Parameter is not of type panel")
        self.panel = inPanel

    def deleteFile(self):
        if self.file is not None:
            os.remove(self.file)

    # file: either a file object or a full path leading to a file which is to be loaded from
    def writeToFile(self, file=None):
        if file is None:
            file = open(self.file, mode='w')
        elif isinstance(file, basestring):
            self.file = file
            file = open(self.file, mode='w')

        file.write(self.date.strftime("%m/%d/%Y") + "\n")
        file.write(self.startTime.strftime("%H:%M") + "\n")
        file.write(self.endTime.strftime("%H:%M") + "\n")
        file.write(self.descriptionText + "\n")
        return

    # file: either a file object or a full path leading to a file which is to be loaded from
    def readFromFile(self, file):
        if isinstance(file, basestring):
            self.file = file
            file = open(self.file)
        str = file.read()
        strArray = str.split("\n")
        self.date = datetime.datetime.strptime(strArray[0], "%m/%d/%Y").date()
        self.startTime = datetime.datetime.strptime(strArray[1], "%H:%M").time()
        self.endTime = datetime.datetime.strptime(strArray[2], "%H:%M").time()
        self.descriptionText = strArray[3]


class PlanCollection:

    def __init__(self, filePath=None, inPlannerApp=None):
        self.plannerApp = inPlannerApp

        self.plansArray = []
        self.filePath = filePath
        self.fileNameIterator = 0

        # file = open("plan.pln")
        # plan = Plan()
        # plan.readFromFile(file)
        # self.plansArray.append(plan)

        if filePath is not None:
            self.loadPlan(filePath)

    def getNextFileName(self):
        folderPath = self.getFolderPath()
        fileStr = os.path.join(folderPath, str(self.fileNameIterator) + ".pln")
        while os.path.isfile(fileStr):
            self.fileNameIterator += 1
            fileStr = os.path.join(folderPath, str(self.fileNameIterator) + ".pln")
        return fileStr

    def getFolderPath(self):
        return self.filePath.rsplit("/", 1)[0] + "/"

    # loads a planner from the plan file provided
    # filePath : the path the the .plan file
    def loadPlan(self, filePath):
        self.filePath = filePath

        # reinitializing the plansArray
        self.plansArray = []

        # loading the fileNameIterator from the .plan file
        plannerFile = open(filePath, mode="r")
        str1 = plannerFile.read()
        self.fileNameIterator = int(str1)

        folderPath = self.getFolderPath()
        fileStrs = os.listdir(folderPath)
        i = 0
        while i < len(fileStrs):
            f = fileStrs[i]
            suffix = f.split(".")[1]
            if suffix != "pln":
                fileStrs.remove(f)
                i -= 1
            i += 1

        for f in fileStrs:
            plan = Plan(inPlannerApp=self.plannerApp)
            plan.readFromFile(os.path.join(self.getFolderPath(), f))
            self.addPlan(plan)


    # saves the plan into the file specified by the filePath
    def savePlan(self, filePath=None):
        if filePath is None:
            filePath = self.filePath
        plannerFile = open(filePath, mode="w")
        plannerFile.write(str(self.fileNameIterator))

    def addPlan(self, planObject):
        if not isinstance(planObject, Plan):
            raise TypeError("Specified parameter is not of type Plan")
        self.plansArray.append(planObject)

    def removePlan(self, planObject):
        if not isinstance(planObject, Plan):
            raise TypeError("Specified parameter is not of type Plan")
        self.plansArray.remove(planObject)
        planObject.deleteFile()

    def getPlansForDate(self, inDate):
        if not isinstance(inDate, datetime.date):
            raise TypeError("Specified parameter is not of type datetime")
        planList = []
        for plan in self.plansArray:
            if plan.getDate() == inDate:
                planList.append(plan)
        return planList


# GUI classes

class PlannerFrame(wx.Frame):

    def __init__(self, title, size, plannerApp):
        super(PlannerFrame, self).__init__(None, title=title, size=size)

        self.plannerApp = plannerApp

        self.menuBar = None
        self.panel = None
        self.dateText = None
        self.leftDateButton = None
        self.middleDateButton = None
        self.rightDateButton = None
        self.planPanel = None

        self.initGUI()

    def initGUI(self):
        # creating the menubar
        self.menuBar = wx.MenuBar()

        menu = wx.Menu()
        self.menuBar.Append(menu, '&File')
        fileItem = menu.Append(wx.ID_ANY, "Save", "Save the current planner")
        self.Bind(wx.EVT_MENU, self.onSave, fileItem)
        fileItem = menu.Append(wx.ID_ANY, "Change planner", "Switch to a different planner")
        self.Bind(wx.EVT_MENU, self.onChangePlanner, fileItem)
        fileItem = menu.Append(wx.ID_ANY, "New planner", "Create a new planner")
        self.Bind(wx.EVT_MENU, self.onNewPlanner, fileItem)
        fileItem = menu.Append(wx.ID_EXIT, "Close", "Exit program")
        self.Bind(wx.EVT_MENU, self.onQuit, fileItem)


        menu = wx.Menu()
        self.menuBar.Append(menu, "&Select")
        selectItem = menu.Append(wx.ID_ANY, "Unselect", "Unselect any currently selected plan")
        self.Bind(wx.EVT_MENU, self.onUnselect, selectItem)

        self.SetMenuBar(self.menuBar)

        # creating the main panel
        self.panel = wx.Panel(self)

        box = wx.BoxSizer(wx.VERTICAL)
        boxBorder = 10

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        self.dateText = wx.StaticText(self.panel, label="08/25/2018", style=wx.ALIGN_CENTER_HORIZONTAL)
        hbox.Add(self.dateText, proportion=1, flag=wx.ALL, border=boxBorder)

        self.leftDateButton = wx.Button(self.panel, label="<")
        self.leftDateButton.Bind(wx.EVT_BUTTON, self.handleDateButtons)
        hbox.Add(self.leftDateButton, proportion=1, flag=wx.LEFT | wx.RIGHT, border=boxBorder)
        self.middleDateButton = wx.Button(self.panel, label="date")
        self.middleDateButton.Bind(wx.EVT_BUTTON, self.handleDateButtons)
        hbox.Add(self.middleDateButton, proportion=2, flag=wx.LEFT | wx.RIGHT, border=boxBorder)
        self.rightDateButton = wx.Button(self.panel, label=">")
        self.rightDateButton.Bind(wx.EVT_BUTTON, self.handleDateButtons)
        hbox.Add(self.rightDateButton, proportion=1, flag=wx.LEFT | wx.RIGHT, border=boxBorder)

        box.Add(hbox, proportion=0, flag=wx.ALL, border=boxBorder)

        hbox1 = wx.BoxSizer(wx.HORIZONTAL)

        self.addPlanButton = wx.Button(self.panel, label="Add Plan")
        self.addPlanButton.Bind(wx.EVT_BUTTON, self.onAddButton)
        hbox1.Add(self.addPlanButton, proportion=1, flag=wx.LEFT | wx.RIGHT, border=boxBorder)
        self.removePlanButton = wx.Button(self.panel, label="Remove Plan")
        self.removePlanButton.Bind(wx.EVT_BUTTON, self.onRemoveButton)
        hbox1.Add(self.removePlanButton, proportion=1, flag=wx.LEFT | wx.RIGHT, border=boxBorder)
        self.editPlanButton = wx.Button(self.panel, label="Edit Plan")
        self.editPlanButton.Bind(wx.EVT_BUTTON, self.onEditButton)
        hbox1.Add(self.editPlanButton, proportion=1, flag=wx.LEFT | wx.RIGHT, border=boxBorder)

        box.Add(hbox1, proportion=0, flag=wx.ALL, border=boxBorder)

        self.planBox = PlannerWindow(self.panel, style=wx.BORDER_SIMPLE, plannerApp=self.plannerApp)
        box.Add(self.planBox, proportion=2, flag=wx.ALL | wx.EXPAND, border=boxBorder)

        self.panel.SetSizer(box)
        box.Layout()

        self.Centre()

        self.SetSize(wx.Size(self.planBox.getVirtualSize().GetWidth(), self.GetSize().GetHeight()))

    def handleDateButtons(self, e):
        date = self.plannerApp.getDate()
        if e.GetId() == self.leftDateButton.GetId():
            date -= datetime.timedelta(days=1)
            self.plannerApp.changeDate(date)
        elif e.GetId() == self.rightDateButton.GetId():
            date += datetime.timedelta(days=1)
            self.plannerApp.changeDate(date)
        elif e.GetId() == self.middleDateButton.GetId():
            dialog = DateDialog(self.plannerApp)
            dialog.ShowModal()
            dialog.Destroy()

        self.plannerApp.updatePlanningWindow()

    def onSave(self, e):
        self.plannerApp.savePlanner()

    def onChangePlanner(self, e):
        fileDialog = wx.FileDialog(self, message="Select planner directory", defaultDir="./",
                                   style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        fileDialog.ShowModal()
        plannerDir = fileDialog.GetPath()
        fileDialog.Destroy()
        if plannerDir != u"":
            self.plannerApp.changePlanner(plannerDir)

    def onNewPlanner(self, e):
        fileDialog = wx.FileDialog(self, message="Select directory and name new planner", defaultDir="./")
        fileDialog.ShowModal()
        plannerDir = fileDialog.GetPath()
        fileDialog.Destroy()
        if plannerDir != u"":
            self.plannerApp.newPlanner(plannerDir)

    def onAddButton(self, e):
        planDialog = PlanDialog(self.plannerApp)
        planDialog.ShowModal()
        planDialog.Destroy()

    def onRemoveButton(self, e):
        self.plannerApp.removeSelectedPlan()

    def onEditButton(self, e):
        if self.plannerApp.getSelectedPlan() is not None:
            dialog = PlanDialog(self.plannerApp, self.plannerApp.getSelectedPlan())
            dialog.ShowModal()
            dialog.Destroy()
            self.plannerApp.updatePlanningWindow()

    def updateDateText(self, inText):
        self.dateText.SetLabelText(inText)

    def onUnselect(self, e):
        self.plannerApp.unselect()

    def onQuit(self, e):
        self.Close()


# A scrollable window which represents each of the user's plans as boxes
class PlannerWindow(wx.ScrolledWindow):

    def __init__(self, parent, id=wx.ID_ANY, virtualSize=wx.Size(750, 1000), style=None, name="", plannerApp=None):
        super(PlannerWindow, self).__init__(parent=parent, id=id, style=style, name=name)

        # a reference to the main Planner object
        self.plannerApp = plannerApp
        # a list containing panels which each represent a specific plan by the user within the window
        self.planBoxList = []
        # the virtual size of the scrollable window of type wx.Size
        self.virtualSize = virtualSize
        self.timesPanel = None
        self.timesSizer = None
        self.planPanel = None
        self.cellSize = None

        self.init()


    def init(self):
        timeGap = 100
        self.cellSize = (self.virtualSize.GetWidth()-timeGap, self.virtualSize.GetHeight()/24)

        self.timesPanel = wx.Panel(self, pos=(0,0), size=(timeGap, self.virtualSize.GetHeight()), style=wx.BORDER_SIMPLE)
        self.timesSizer = wx.GridSizer(rows=24, cols=1, vgap=0, hgap=0)
        self.timesPanel.SetSizer(self.timesSizer)

        self.planPanel = wx.Panel(self, pos=(timeGap, 0), size=(self.virtualSize.GetWidth()-timeGap, self.virtualSize.GetHeight()), style=wx.BORDER_SIMPLE)

        self.SetScrollbars(10, 10, self.virtualSize.GetHeight(), self.virtualSize.GetWidth())
        self.initHourNumbers()

    def initHourNumbers(self):
        self.timesSizer.Add(wx.StaticText(self.timesPanel, label="12 AM"), 0, wx.ALIGN_CENTER)
        i = 1
        while i < 12:
            self.timesSizer.Add(wx.StaticText(self.timesPanel, label=str(i)+" AM"), 0, wx.ALIGN_CENTER)
            i += 1

        self.timesSizer.Add(wx.StaticText(self.timesPanel, label="12 PM"), 0, wx.ALIGN_CENTER)
        i = 1
        while i < 12:
            self.timesSizer.Add(wx.StaticText(self.timesPanel, label=str(i) + " PM"), 0, wx.ALIGN_CENTER)
            i += 1

    def addPlanBoxFromPlan(self, plan):
        if not isinstance(plan, Plan):
            raise TypeError("Specified parameter is not of type Plan")
        startTime = plan.startTime
        endTime = plan.endTime
        text = plan.descriptionText

        floatStart = (float(startTime.hour)+float(startTime.minute)*(1.0/60.0))
        floatEnd = ((float(endTime.hour)+float(endTime.minute)*(1.0/60.0)))
        panelSize = (self.cellSize[0], self.cellSize[1] * ( floatEnd - floatStart))
        panelPos = (0, floatStart*self.cellSize[1])
        panel = wx.Panel(self.planPanel, size=panelSize, pos=panelPos, style=wx.BORDER_SIMPLE)
        plan.setPanel(panel)
        panel.Bind(wx.EVT_LEFT_UP, plan.select)
        text = startTime.strftime("%I:%M%p") + " - " + endTime.strftime("%I:%M%p") + ": " + text
        wx.StaticText(panel, label=text, style=wx.ALIGN_CENTRE).CenterOnParent()

        self.planBoxList.append(panel)

    def removePlanBox(self, id):
        for panel in self.planBoxList:
            if panel.GetId() == id:
                return self.planBoxList.remove(panel)
        return None

    # clears the window of all of the planning boxes inside it and removes them
    def clear(self):
        if len(self.planBoxList) > 0:
            for plan in self.planBoxList:
                plan.Destroy()
        self.planBoxList = []
        self.Fit()

    def getPlanBox(self, id):
        for panel in self.planBoxList:
            if panel.GetId() == id:
                return panel
        return None

    def getVirtualSize(self):
        return self.virtualSize


class PlanDialog(wx.Dialog):

    def __init__(self, inPlannerApp=None, inPlan=None):
        super(PlanDialog, self).__init__(None)

        self.plannerApp = inPlannerApp
        self.initUI()
        self.SetSize(wx.Size(300, 250))
        self.SetTitle("Add Plan")
        self.plan = inPlan
        if self.plan is not None:
            self.loadPlan(inPlan)

    def initUI(self):
        panel = wx.Panel(self)

        sizer = wx.GridSizer(rows=4, cols=2, hgap=10, vgap=10)

        self.startText = wx.StaticText(panel, label="Start Time (TT:TT): ")
        self.startText.CenterOnParent()
        sizer.Add(self.startText, proportion=0, flag=wx.ALIGN_CENTRE)
        self.startBox = wx.TextCtrl(panel)
        sizer.Add(self.startBox, proportion=1, flag=wx.ALIGN_CENTRE)

        self.endText = wx.StaticText(panel, label="End Time (TT:TT): ")
        sizer.Add(self.endText, flag=wx.ALIGN_CENTRE)
        self.endBox = wx.TextCtrl(panel)
        sizer.Add(self.endBox, flag=wx.ALIGN_CENTRE)

        self.descriptionText = wx.StaticText(panel, label="Description: ")
        sizer.Add(self.descriptionText, flag=wx.ALIGN_CENTRE)
        self.descriptionBox = wx.TextCtrl(panel)
        sizer.Add(self.descriptionBox, flag=wx.ALIGN_CENTRE)

        self.okButton = wx.Button(panel, label="accept")
        sizer.Add(self.okButton, flag=wx.ALIGN_CENTRE)
        self.okButton.Bind(wx.EVT_BUTTON, self.onOkay)

        self.cancelButton = wx.Button(panel, label="cancel")
        sizer.Add(self.cancelButton, flag=wx.ALIGN_CENTRE)
        self.cancelButton.Bind(wx.EVT_BUTTON, self.onCancel)

        panel.SetSizer(sizer)

    def loadPlan(self, plan):
        self.startBox.SetValue(plan.startTime.strftime("%I:%M%p"))
        self.endBox.SetValue(plan.endTime.strftime("%I:%M%p"))
        self.descriptionBox.SetValue(plan.descriptionText)

    def onOkay(self, e):
        try:
            startTime = datetime.datetime.fromtimestamp(time.mktime(time.strptime(self.startBox.GetValue(), "%I:%M%p"))).time()
            endTime = datetime.datetime.fromtimestamp(time.mktime(time.strptime(self.endBox.GetValue(), "%I:%M%p"))).time()
        except:
            wx.MessageDialog(None, "Incorrect time format provided. Please type start and end times in correct format", "Error", wx.OK | wx.ICON_ERROR).ShowModal()
            return
        descStr = str(self.descriptionBox.GetValue())

        if self.plan is not None:
            self.plan.setValues(self.plannerApp.getDate(), startTime, endTime, descStr)
            self.plan.writeToFile()
        else:
            self.plan = Plan(self.plannerApp.getDate(), startTime, endTime, descStr, self.plannerApp)
            self.plannerApp.addPlan(self.plan)
            self.plan.writeToFile(self.plannerApp.planCollection.getNextFileName())

        self.plannerApp.unselect()
        self.Close()

    def onCancel(self, e):
        self.Close()


class DateDialog(wx.Dialog):

    def __init__(self, mainApp):
        super(DateDialog, self).__init__(None)

        self.mainApp = mainApp
        self.initUI()
        self.SetSize(wx.Size(300, 200))
        self.SetTitle("Select Date")

    def initUI(self):
        # panel = wx.Panel(self, style=wx.BORDER_SIMPLE)
        # sizer = wx.GridBagSizer()
        #
        # self.dateBox = wx.TextCtrl(parent=panel, id=wx.ID_ANY, value="dd/mm/yyyy")
        # sizer.Add(self.dateBox, pos=(0, 0), span=(1, 2), flag=wx.EXPAND | wx.ALIGN_CENTRE)
        #
        # self.acceptButton = wx.Button(panel, label="accept")
        # self.acceptButton.Bind(wx.EVT_BUTTON, self.onAccept)
        # sizer.Add(self.acceptButton, pos=(1, 0), flag=wx.EXPAND | wx.ALIGN_CENTRE)
        #
        # self.cancelButton = wx.Button(panel, label="cancel")
        # self.cancelButton.Bind(wx.EVT_BUTTON, self.onCancel)
        # sizer.Add(self.cancelButton, pos=(1, 1), flag=wx.EXPAND | wx.ALIGN_CENTRE)
        #
        # panel.SetSizer(sizer)

        panel = wx.Panel(self, style=wx.BORDER_SIMPLE)
        vbox = wx.BoxSizer(wx.VERTICAL)

        self.dateBox = wx.TextCtrl(parent=panel, id=wx.ID_ANY, value="dd/mm/yyyy")
        vbox.Add(self.dateBox, proportion=1, flag=wx.EXPAND | wx.ALIGN_CENTRE)

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        self.acceptButton = wx.Button(panel, label="accept")
        self.acceptButton.Bind(wx.EVT_BUTTON, self.onAccept)
        hbox.Add(self.acceptButton, proportion=1, flag=wx.EXPAND | wx.ALIGN_CENTRE)

        self.cancelButton = wx.Button(panel, label="cancel")
        self.cancelButton.Bind(wx.EVT_BUTTON, self.onCancel)
        hbox.Add(self.cancelButton, proportion=1, flag=wx.EXPAND | wx.ALIGN_CENTRE)
        vbox.Add(hbox, proportion=1, flag=wx.EXPAND | wx.ALIGN_CENTRE)

        panel.SetSizer(vbox)
        panel.Fit()

    def onCancel(self, e):
        self.Close()

    def onAccept(self, e):
        try:
            self.mainApp.changeDate(str(self.dateBox.GetValue()))
        except:
            # open error window
            wx.MessageDialog(None, "Incorrect date format provided. Please input in the following format dd/mm/yyyy",
                             "Error", wx.OK | wx.ICON_ERROR).ShowModal()
            return
        self.Close()


def main():
    app = Planner()
    app.initGUI()
    app.MainLoop()


if __name__ == "__main__":
    main()

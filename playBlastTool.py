import maya.cmds as cmds
from PySide2 import QtGui,QtCore,QtWidgets
from functools import partial
import sys
import os,subprocess


imageSource =  os.path.join(os.environ['USERPROFILE'],"Desktop/playBlastTool/images/")

def genPerspCamList():
    perspCamList = []
    for camName in cmds.listCameras(p=True):
        if camName != 'persp':
            perspCamList.append(camName)
    return perspCamList

class CamBlastTool(QtWidgets.QWidget):
    #---#
    #Attributes
    #---#

    orthographicCamList = cmds.listCameras(o=True)
    perspCamList = genPerspCamList()
    outputDirectory = ""
    blastQuality = 100
    openDirectoryCheck = True
    useResolutionCheck = True
    resolutionDictList = []
    initialCamWidth = cmds.getAttr("defaultResolution.width")
    initialCamHeight = cmds.getAttr("defaultResolution.height")
    resolutionDictList = [ {"camName":"Custom"},
                           {"camName":"HD 1080", "camWidth":1920, "camHeight":1080},
                           {"camName":"HD 720", "camWidth":1280, "camHeight":720},
                           {"camName":"HD 540", "camWidth":960, "camHeight":540},
                           {"camName":"PAL 768", "camWidth":768, "camHeight":576},
                           {"camName":"Targa NTSC", "camWidth":512, "camHeight":482}]
    
    #---#
    #Functions
    #---#
    
    def __init__(self, parent=None):
        super(CamBlastTool,self).__init__(parent=parent)
        self.resize(650,200)
        self.setWindowTitle("Playblast Tool")           
        
        mainLayout = QtWidgets.QVBoxLayout()
        tabsList = QtWidgets.QTabWidget()
        mainLayout.addWidget(tabsList)
        
        tab1 = QtWidgets.QWidget()
        tab1Layout = QtWidgets.QVBoxLayout()
        tab1.setLayout(tab1Layout)
        
        tab2 = QtWidgets.QWidget()
        tab2Layout = QtWidgets.QVBoxLayout()
        tab2.setLayout(tab2Layout)
        
        tabsList.addTab(tab1, "Single")
        tabsList.addTab(tab2, "Multiple")
        
        
        #---#
        #tab1
        #---#
        
        child1Layout = QtWidgets.QVBoxLayout()
        child2Layout = QtWidgets.QGridLayout()
        
        #---#
        #child1Layout
        #---#
        
        self.groupbox1 = QtWidgets.QGroupBox("Camera Controls")
        self.groupbox1Layout = QtWidgets.QGridLayout()
        self.groupbox1.setLayout(self.groupbox1Layout)
        
        self.camBoxLabel = QtWidgets.QLabel("Camera List:")
        
        self.camListBox = QtWidgets.QComboBox()
        self.genCamList()
        currentCamera = self.getCurrentCamera()
        self.camListBox.setCurrentText(currentCamera)
        
        self.groupbox1A = QtWidgets.QGroupBox()
        self.groupbox1ALayout = QtWidgets.QHBoxLayout()
        self.groupbox1A.setLayout(self.groupbox1ALayout)
        
        self.setCamBtn = QtWidgets.QPushButton("Set To Current")
        self.setCamBtn.clicked.connect(partial(self.checkSource,source = "ComboBox"))
        
        self.deleteBtn = QtWidgets.QPushButton("Delete Camera")
        self.deleteBtn.clicked.connect(self.deleteCamera)
        
        self.refreshCamListBtn = QtWidgets.QPushButton("Refresh")
        self.refreshCamListBtn.clicked.connect(self.refreshCamList)
        
        self.createCamLabel = QtWidgets.QLabel("Create Camera:")
        
        self.groupbox1B = QtWidgets.QGroupBox()
        self.groupbox1BLayout = QtWidgets.QHBoxLayout()
        self.groupbox1B.setLayout(self.groupbox1BLayout)
        
        self.createCamLineEdit = QtWidgets.QLineEdit()
        self.createCamLineEdit.setAlignment(QtGui.Qt.AlignCenter)
        self.createCamLineEdit.setPlaceholderText("Case-Sensitive")
        self.createCamLineEdit.textChanged.connect(self.camValidateIcon)
        
        self.camValidateLabel = QtWidgets.QLabel()
        
        self.groupbox1C = QtWidgets.QGroupBox()
        self.groupbox1CLayout = QtWidgets.QHBoxLayout()
        self.groupbox1C.setLayout(self.groupbox1CLayout)
        
        self.createCamBtn = QtWidgets.QPushButton("Create Only")
        self.createCamBtn.clicked.connect(partial(self.createCam,False))
        
        self.createAndSetCamBtn = QtWidgets.QPushButton("Create And Set To Current")
        self.createAndSetCamBtn.clicked.connect(partial(self.createCam,True))
               
        row = 0
        col = 0
        
        self.groupbox1Layout.addWidget(self.camBoxLabel,row,col)
        self.groupbox1Layout.addWidget(self.camListBox,row,col+1)
        self.groupbox1ALayout.addWidget(self.setCamBtn)
        self.groupbox1ALayout.addWidget(self.deleteBtn)
        self.groupbox1Layout.addWidget(self.groupbox1A,row,col+2)
        self.groupbox1Layout.addWidget(self.refreshCamListBtn,row,col+3)
        
        self.groupbox1Layout.addWidget(self.createCamLabel,row+1,col)
        self.groupbox1BLayout.addWidget(self.createCamLineEdit)
        self.groupbox1BLayout.addWidget(self.camValidateLabel)
        self.groupbox1Layout.addWidget(self.groupbox1B,row+1,col+1)
        
        self.groupbox1CLayout.addWidget(self.createCamBtn)
        self.groupbox1CLayout.addWidget(self.createAndSetCamBtn)
        self.groupbox1Layout.addWidget(self.groupbox1C,row+1,col+2)
        
        child1Layout.addWidget(self.groupbox1)
        
        #---#
        #child2Layout
        #---#
        
        self.groupbox2 = QtWidgets.QGroupBox("Playblast Controls")
        self.groupbox2Layout = QtWidgets.QGridLayout()
        self.groupbox2.setLayout(self.groupbox2Layout)
        
        self.setPathLabel = QtWidgets.QLabel("Destination Folder:")
        
        self.groupbox2A = QtWidgets.QGroupBox()
        self.groupbox2ALayout = QtWidgets.QHBoxLayout()
        self.groupbox2A.setLayout(self.groupbox2ALayout)
        
        self.setPathLineEdit = QtWidgets.QLineEdit()
        self.setPathLineEdit.setAlignment(QtGui.Qt.AlignCenter)
                
        self.pathValidateLabel = QtWidgets.QLabel()
        
        workspace = cmds.workspace(q=True, rootDirectory=True)
        defaultPath = os.path.join(workspace,"movies")
        self.setPathLineEdit.setText(defaultPath)
        self.pathValidateIcon(True)
        self.setPathLineEdit.textChanged.connect(self.checkPath)
        
        self.selectPathBtn = QtWidgets.QPushButton("Browse...")
        self.selectPathBtn.clicked.connect(self.selectPath)
        
        self.setFilePrefixLabel = QtWidgets.QLabel("File Prefix:")
        
        self.setFileNameLineEdit = QtWidgets.QLineEdit()
        self.setFileNameLineEdit.setAlignment(QtGui.Qt.AlignCenter)
        self.setFileNameLineEdit.setPlaceholderText("MyPlayblast")
        
        self.minmaxLabel = QtWidgets.QLabel("Animation Start/End:")
        
        self.groupbox2B = QtWidgets.QGroupBox()
        self.groupbox2BLayout = QtWidgets.QHBoxLayout()
        self.groupbox2B.setLayout(self.groupbox2BLayout)
        
        self.minPlaybackSpinBox = QtWidgets.QSpinBox()
        minFrame = self.processMinFrame()
        self.minPlaybackSpinBox.valueChanged.connect(self.setMinFrame)
        
        self.maxPlaybackSpinBox = QtWidgets.QSpinBox()
        maxFrame = self.processMaxFrame()
        self.maxPlaybackSpinBox.valueChanged.connect(self.setMaxFrame)
        
        self.refreshBtn = QtWidgets.QPushButton("Refresh Timeline")
        self.refreshBtn.clicked.connect(self.refreshTimeline)
        
        self.rangeLabel = QtWidgets.QLabel("Playblast Range:")
        self.rangeLineEdit = QtWidgets.QLineEdit()
        self.rangeLineEdit.setAlignment(QtGui.Qt.AlignCenter)
        self.rangeLineEdit.setPlaceholderText("Example: 100-200; 500-550")
        
        self.resolutionLabel = QtWidgets.QLabel("Playblast Resolution:")
        
        self.widthSpinBox = QtWidgets.QSpinBox()
        self.widthSpinBox.setRange(2,4096)
        camWidth = self.initialCamWidth
        self.widthSpinBox.setValue(camWidth)
        
        self.heightSpinBox = QtWidgets.QSpinBox()
        self.heightSpinBox.setRange(2,4096)
        camHeight = self.initialCamHeight
        self.heightSpinBox.setValue(camHeight)
        
        self.widthSpinBox.valueChanged.connect(self.checkCamResolution)
        self.heightSpinBox.valueChanged.connect(self.checkCamResolution)
        
        self.groupbox2C = QtWidgets.QGroupBox()
        self.groupbox2CLayout = QtWidgets.QHBoxLayout()
        self.groupbox2C.setLayout(self.groupbox2CLayout)
        
        self.groupbox2D = QtWidgets.QGroupBox()
        self.groupbox2DLayout = QtWidgets.QHBoxLayout()
        self.groupbox2D.setLayout(self.groupbox2DLayout)
        
        self.resetBtn = QtWidgets.QPushButton("Initial Resolution")
        self.resetBtn.clicked.connect(self.resetToDefaultCamResolution)
        
        self.resolutionOptionBox = QtWidgets.QComboBox()
                                   
        for resolutionDict in self.resolutionDictList:
            self.resolutionOptionBox.addItem(resolutionDict["camName"])
        
        self.resolutionOptionBox.currentTextChanged.connect(self.setPresetResolution)
              
        self.blastBtn = QtWidgets.QPushButton("Playblast!")
        self.blastBtn.clicked.connect(self.processBlast)
        
        self.qualityLabel = QtWidgets.QLabel("Quality:")
        
        self.groupbox2E = QtWidgets.QGroupBox()
        self.groupbox2ELayout = QtWidgets.QHBoxLayout()
        self.groupbox2E.setLayout(self.groupbox2ELayout)
        
        self.blastQualityQuarterRadioBtn = QtWidgets.QRadioButton("Quarter")
        self.blastQualityQuarterRadioBtn.clicked.connect(partial(self.checkQuality,quality="Quarter"))
        
        self.blastQualityThirdRadioBtn = QtWidgets.QRadioButton("Third")
        self.blastQualityThirdRadioBtn.clicked.connect(partial(self.checkQuality,quality="Third"))
        
        self.blastQualityHalfRadioBtn = QtWidgets.QRadioButton("Half")
        self.blastQualityHalfRadioBtn.clicked.connect(partial(self.checkQuality,quality="Half"))
        
        self.blastQualityFullRadioBtn = QtWidgets.QRadioButton("Full")
        self.blastQualityFullRadioBtn.setChecked(True)
        self.blastQualityFullRadioBtn.clicked.connect(partial(self.checkQuality,quality="Full"))
        
        self.groupbox2F = QtWidgets.QGroupBox()
        self.groupbox2FLayout = QtWidgets.QHBoxLayout()
        self.groupbox2F.setLayout(self.groupbox2FLayout)
        
        self.openDirectoryCheckBoxLabel = QtWidgets.QLabel("Open Containing Folder:")
        self.openDirectoryCheckBox = QtWidgets.QCheckBox()
        self.openDirectoryCheckBox.setChecked(False)
        self.openDirectoryCheckBox.stateChanged.connect(self.openDirectory)
        
        
        row = 0
        col = 0
        
        self.groupbox2Layout.addWidget(self.setPathLabel,row,col)
        self.groupbox2Layout.addWidget(self.setPathLineEdit,row,col+1)
        self.groupbox2ALayout.addWidget(self.pathValidateLabel)
        self.groupbox2ALayout.addWidget(self.selectPathBtn)
        self.groupbox2Layout.addWidget(self.groupbox2A,row,col+2)
        
        self.groupbox2Layout.addWidget(self.setFilePrefixLabel,row+1,col)
        self.groupbox2Layout.addWidget(self.setFileNameLineEdit,row+1,col+1)
        
        self.groupbox2Layout.addWidget(self.minmaxLabel,row+2,col)
        self.groupbox2BLayout.addWidget(self.minPlaybackSpinBox)
        self.groupbox2BLayout.addWidget(self.maxPlaybackSpinBox)
        self.groupbox2Layout.addWidget(self.groupbox2B,row+2,col+1)
        self.groupbox2Layout.addWidget(self.refreshBtn,row+2,col+2)
        
        self.groupbox2Layout.addWidget(self.rangeLabel,row+3,col)
        self.groupbox2Layout.addWidget(self.rangeLineEdit,row+3,col+1)
        
        self.groupbox2Layout.addWidget(self.resolutionLabel,row+4,col)
        self.groupbox2CLayout.addWidget(self.widthSpinBox)
        self.groupbox2CLayout.addWidget(self.heightSpinBox)
        self.groupbox2CLayout.addWidget(self.resolutionOptionBox)
        self.groupbox2Layout.addWidget(self.groupbox2C,row+4,col+1)
        self.groupbox2DLayout.addWidget(self.resetBtn)

        self.groupbox2Layout.addWidget(self.groupbox2D,row+4,col+2)
        
        self.groupbox2Layout.addWidget(self.qualityLabel,row+5,col)
        self.groupbox2ELayout.addWidget(self.blastQualityQuarterRadioBtn)
        self.groupbox2ELayout.addWidget(self.blastQualityThirdRadioBtn)
        self.groupbox2ELayout.addWidget(self.blastQualityHalfRadioBtn)
        self.groupbox2ELayout.addWidget(self.blastQualityFullRadioBtn)
        self.groupbox2Layout.addWidget(self.groupbox2E,row+5,col+1)
        
        self.groupbox2FLayout.addWidget(self.openDirectoryCheckBoxLabel)
        self.groupbox2FLayout.addWidget(self.openDirectoryCheckBox)
        self.groupbox2Layout.addWidget(self.groupbox2F,row+5,col+2)
        child2Layout.addWidget(self.groupbox2)
        
        child2Layout.addWidget(self.blastBtn)
        
        tab1Layout.addLayout(child1Layout)
        tab1Layout.addLayout(child2Layout)
        
        #---#
        #tab2
        #---#
        
        #---#
        #chiild3Layout
        #---#
        
        child3Layout = QtWidgets.QVBoxLayout()
        
        self.groupbox3 = QtWidgets.QGroupBox("Batch Playblast")
        self.groupbox3Layout = QtWidgets.QGridLayout()
        self.groupbox3.setLayout(self.groupbox3Layout)
        
        self.sourcePathLabel = QtWidgets.QLabel("File Location:")
        
        self.groupbox3A = QtWidgets.QGroupBox()
        self.groupbox3ALayout = QtWidgets.QHBoxLayout()
        self.groupbox3A.setLayout(self.groupbox3ALayout)
        
        self.sourcePathLineEdit = QtWidgets.QLineEdit()
        self.sourcePathLineEdit.setAlignment(QtGui.Qt.AlignCenter)
                
        self.sourcePathValidateLabel = QtWidgets.QLabel()

        self.sourcePathLineEdit.textChanged.connect(self.checkSourcePath)
        
        self.selectSourcePathBtn = QtWidgets.QPushButton("Browse...")
        self.selectSourcePathBtn.clicked.connect(self.selectSourcePath)
        
        self.batchPlayblastBtn = QtWidgets.QPushButton("Batch Playblast")
        self.batchPlayblastBtn.setEnabled(False)
        self.batchPlayblastBtn.clicked.connect(self.batchPlayblast)
        
        row = 0
        col = 0
        
        self.groupbox3Layout.addWidget(self.sourcePathLabel,row,col)
        self.groupbox3ALayout.addWidget(self.sourcePathLineEdit)
        self.groupbox3ALayout.addWidget(self.sourcePathValidateLabel)
        self.groupbox3Layout.addWidget(self.groupbox3A,row,col+1)
        self.groupbox3Layout.addWidget(self.selectSourcePathBtn,row,col+2)
        self.groupbox3Layout.addWidget(self.batchPlayblastBtn,row,col+3)
        
        child3Layout.addWidget(self.groupbox3)        
        tab2Layout.addLayout(child3Layout)
        

        #---#
        #Outer Layout
        #---#
        
        self.setLayout(mainLayout)
    
    #---#
    #Methods
    #---#      
   
    def genCamList(self):
        self.camListBox.clear()
        for camName in cmds.listCameras():
            self.addCamToCamListBox(camName)
    
    def getCurrentCamera(self):
        panel = cmds.playblast(ae=True)
        modelPanel = panel.split("|")[2]
        currentCamera = cmds.modelPanel(modelPanel,q=True,camera=True)
        return currentCamera
        
    def refreshCamList(self):
        self.genCamList()
        self.createCamLineEdit.clear()
        
    def addCamToCamListBox(self,camName):
        self.camListBox.addItem(camName)
        
    def addCamToPerspCamList(self,camName):
        self.perspCamList.append(camName)
        self.genCamList()
        
    def createCam(self,setCamCheck):
        camName = self.createCamLineEdit.text()
        if not camName:
            QtWidgets.QMessageBox.information(self,"Warning!","Please enter a camera name!")
        else:
            self.perspCamList = genPerspCamList()
            if camName not in self.perspCamList:
                print("Creating camera: {0}".format(camName))
                newCamNode = cmds.camera(name="MyCamera",centerOfInterest=5,focalLength=35,horizontalFilmAperture=1.4,verticalFilmAperture=0.9,
                        overscan=1,filmFit="Fill",nearClipPlane=0.1,farClipPlane=10000,cameraScale=1,orthographic=0)
                newCamName = newCamNode[0]
                newShapeName = newCamNode[1]
                
                if camName != newCamName:
                    if camName[-1] != '1' and newCamName[-1] == '1':
                        shapeName = newShapeName.replace("Shape1","Shape")
                        cmds.rename(newShapeName,shapeName)
                        cmds.rename(newCamName,camName)
                
                self.addCamToPerspCamList(camName)
        
                if setCamCheck == True:
                    self.checkSource("LineEdit")
                                
            else:
                QtWidgets.QMessageBox.information(self,"Warning!","This camera name already exists!")         
                
    def checkSource(self,source):
        if source == "ComboBox":
            camName = self.camListBox.currentText()
            print("Setting {0}".format(camName))
            self.setCam(camName)
        elif source == "LineEdit":
            camName = self.createCamLineEdit.text()
            print("Setting {0}".format(camName))
            self.setCam(camName)
            
    def setCam(self,camName):   
        camShapeName = (cmds.listRelatives(camName))[0]
        if camName not in self.orthographicCamList:
            cmds.lookThru(camShapeName,"perspView")
        else:
            if camName == "top":
                cmds.lookThru(camShapeName,"topView")
            elif camName == "front":
                cmds.lookThru(camShapeName,"frontView")
            elif camName == "side":
                cmds.lookThru(camShapeName,"sideView")

    def camValidateIcon(self):
        camName = self.createCamLineEdit.text()
        if camName not in cmds.listCameras() and camName!= "":
            self.camValidateLabel.setPixmap(QtGui.QPixmap("{0}correct.png".format(imageSource)))
            self.createCamBtn.setEnabled(True)
            self.createAndSetCamBtn.setEnabled(True)
        else:
            self.camValidateLabel.setPixmap(QtGui.QPixmap("{0}wrong.png".format(imageSource)))
            self.createCamBtn.setEnabled(False)
            self.createAndSetCamBtn.setEnabled(False)
    
    def deleteCamera(self):
        camName = self.camListBox.currentText()
        if camName in self.orthographicCamList or camName == 'persp':
            QtWidgets.QMessageBox.information(self,"Warning!","Cannot delete an inbuilt camera!")
        else:
            self.perspCamList = genPerspCamList()
            cmds.select(camName,r=True)
            cmds.delete()
            self.perspCamList.remove(camName)
            self.genCamList()
            
    def checkCamResolution(self):
        camWidth = self.widthSpinBox.value()
        camHeight = self.heightSpinBox.value()
        self.changeCamResolution(camWidth,camHeight)
        
    def changeCamResolution(self,camWidth,camHeight):
        cmds.setAttr("defaultResolution.width",camWidth)
        cmds.setAttr ("defaultResolution.height",camHeight)
        cmds.setAttr("defaultResolution.dar",(camWidth/camHeight))
            
    def setPresetResolution(self):
        camName = self.resolutionOptionBox.currentText()
        print(camName)
        if camName != "Custom":
            for resolutionDict in self.resolutionDictList:
                if camName == resolutionDict["camName"]:
                    camWidth = resolutionDict["camWidth"]
                    camHeight = resolutionDict["camHeight"]
                    self.changeCamResolution(camWidth,camHeight)
                    self.widthSpinBox.setValue(camWidth)
                    self.heightSpinBox.setValue(camHeight)
            
    def resetToDefaultCamResolution(self):
        defaultWidth = self.initialCamWidth
        defaultHeight = self.initialCamHeight
        self.widthSpinBox.setValue(defaultWidth)
        self.heightSpinBox.setValue(defaultHeight)
        self.changeCamResolution(defaultWidth,defaultHeight)
    
    def processMinFrame(self):
        minFrame = cmds.playbackOptions(q=True,ast=True)
        self.minPlaybackSpinBox.setMinimum(minFrame)
        self.minPlaybackSpinBox.setValue(int(minFrame))
        return minFrame
                         
    def setMinFrame(self):
        minFrame = float(self.minPlaybackSpinBox.text())
        cmds.playbackOptions(min=minFrame)
    
    def processMaxFrame(self):
        maxFrame = cmds.playbackOptions(q=True,aet=True)
        self.maxPlaybackSpinBox.setMaximum(maxFrame)
        self.maxPlaybackSpinBox.setValue(int(maxFrame))
        return maxFrame
        
    def setMaxFrame(self):
        maxFrame = float(self.maxPlaybackSpinBox.text())
        cmds.playbackOptions(max=maxFrame)
        
    def refreshTimeline(self):
        self.processMinFrame()
        self.processMaxFrame()
        
    def checkPath(self):
        pathName = self.setPathLineEdit.text()
        if os.path.exists(pathName):
            self.blastBtn.setEnabled(True)
            self.pathValidateIcon(True)
            return True
        else:
            self.blastBtn.setEnabled(False)
            self.pathValidateIcon(False)
            return False
    
    def pathValidateIcon(self,pathCheck):
        if pathCheck == True:
            self.pathValidateLabel.setPixmap(QtGui.QPixmap("{0}correct.png".format(imageSource)))
        else:
            self.pathValidateLabel.setPixmap(QtGui.QPixmap("{0}wrong.png".format(imageSource)))
    
    def selectPath(self):
        dirName = QtWidgets.QFileDialog.getExistingDirectory()
        self.setPathLineEdit.setText(dirName)
       
    def setFileName(self):
        fileName = self.setFileNameLineEdit.text()
        if fileName == "":
            fileName = "MyPlayblast"
        return fileName   
    
    def findRange(self):
        rangeList = []
        entry = self.rangeLineEdit.text()
        
        if entry == "":
            return (rangeList,len(rangeList))
        else:
            if "-" not in entry: #No Range Defined
                cmds.warning("Ranges should be defined by '-'")
            else:
                if ";" not in entry: #Single Range Defined
                    rangeList.append(entry)
                    return (rangeList,len(rangeList))
                else: #Multiple Ranges Defined
                    rangeList = entry.split(";")
                    return (rangeList,len(rangeList))
                    
    def hasDuplicateBlast(self, pathName, fileName):
        files = os.listdir(pathName)
        for f in files:
            if f == fileName:
                return True
        else:
            return False
    
    def overWriteFile(self,fileName):
        overwriteFile = False
        self.generateWarningForDuplicateFile = QtWidgets.QMessageBox.question(self,"Warning!","{0} already exists. Do you want to overwrite?".format(fileName),
                                                  QtWidgets.QMessageBox.Ok|QtWidgets.QMessageBox.Cancel)
        if self.generateWarningForDuplicateFile == QtWidgets.QMessageBox.Ok:
            overwriteFile = True
        return overwriteFile
    
    def processBlast(self):
        rangeList,length = self.findRange()
        if length != 0: #Range Defined
            if length == 1:
                startFrame = (rangeList[0].split("-"))[0]
                endFrame = (rangeList[0].split("-"))[1]
                self.startBlast(startFrame,endFrame)
                                
            if length > 1:
                for i in range(length):
                    startFrame = (rangeList[i].split("-"))[0]
                    endFrame = (rangeList[i].split("-"))[1]
                    self.startBlast(startFrame,endFrame)
                    
        else: #No Range Defined
            startFrame = int(cmds.playbackOptions(q=True,min=True))
            endFrame = int(cmds.playbackOptions(q=True,max=True))
            self.startBlast(startFrame,endFrame)
    
    def startBlast(self,startFrame,endFrame):
        pathName = self.setPathLineEdit.text()
        fileName = "{0}_Range{1}-{2}.mov".format(self.setFileName(),startFrame,endFrame)
        
        checkDuplicateBlast = self.hasDuplicateBlast(pathName,fileName)
        
        if checkDuplicateBlast == False or (checkDuplicateBlast == True and self.overWriteFile(fileName) == True):
            blastQuality = self.blastQuality
            blastWidth = self.widthSpinBox.value()
            blastHeight = self.heightSpinBox.value()

            cmds.playblast(format="qt", 
                           filename=os.path.join(pathName,fileName),
                           forceOverwrite=True,
                           sequenceTime=0,
                           clearCache=1,
                           viewer=0,
                           showOrnaments=1,
                           fp=4,
                           percent=blastQuality,
                           compression="H.264",
                           quality=100,
                           width=blastWidth,
                           height=blastHeight,
                           startTime=startFrame,
                           endTime=endFrame)
            
            if self.openDirectory() == True:
                os.startfile(pathName)
       
    def checkQuality(self,quality):
       if quality == "Quarter":
           self.blastQuality = 25
       elif quality == "Third":
           self.blastQuality = 33
       elif quality == "Half":
           self.blastQuality = 50
       elif quality == "Full":
           self.blastQuality = 100
   
    def openDirectory(self):
        if self.openDirectoryCheckBox.isChecked() == False:
            self.openDirectoryCheck = False
        else:
            self.openDirectoryCheck = True
        return self.openDirectoryCheck
        
    def useResolution(self):
        if self.useResolutionCheckBox.isChecked() == False:
            self.useResolutionCheck = False
        else:
            self.useResolutionCheck = True
        return self.useResolutionCheck
    
    def checkSourcePath(self):
        sourcePathName = self.sourcePathLineEdit.text()
        print (sourcePathName)
        if os.path.exists(sourcePathName):
            self.batchPlayblastBtn.setEnabled(True)
            self.sourcePathValidateIcon(True)
        else:
            self.batchPlayblastBtn.setEnabled(False)
            self.sourcePathValidateIcon(False)
    
    def sourcePathValidateIcon(self,pathCheck):
        if pathCheck == True:
            self.sourcePathValidateLabel.setPixmap(QtGui.QPixmap("{0}correct.png".format(imageSource)))
        else:
            self.sourcePathValidateLabel.setPixmap(QtGui.QPixmap("{0}wrong.png".format(imageSource)))
    
    def selectSourcePath(self):
        dirName = QtWidgets.QFileDialog.getExistingDirectory()
        self.sourcePathLineEdit.setText(dirName)
        
    def batchPlayblast(self):
        dirPath = self.sourcePathLineEdit.text()
        files = []
        for f in os.listdir(dirPath):
            if ".ma" in f:
                files.append(f)
        
        cmds.file(rename="tempFile.ma")
        cmds.file(save=True,type="mayaAscii")
        
        if files != []:
            for f in files:
                cmds.file(f,open=True)
                fileName = f.split(".ma")[0]
                filePath = os.path.join(dirPath,fileName)
                cmds.playblast(format="qt", 
                                   filename=filePath,
                                   forceOverwrite=True,
                                   sequenceTime=0,
                                   clearCache=1,
                                   viewer=0,
                                   showOrnaments=1,
                                   fp=4,
                                   compression="H.264",
                                   quality=100)
                cmds.file(save=True)
        else:
            QtWidgets.QMessageBox.information(self,"Warning!","No Maya files in the directory!")
            

if __name__=="__main__":
    ui = CamBlastTool()
    ui.show()
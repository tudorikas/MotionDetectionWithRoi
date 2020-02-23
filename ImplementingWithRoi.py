import cv2
import numpy as np

class Rois():
    def __init__(self):
        self.listRois=list()


    def choose_ROIs(self,frame):
        self.frame=frame.copy()
        self.save=frame.copy()
        #acum alege tasta
        #d for display ROI
        #r for set ROI
        #s for save
        #c for clear all
        #key=cv2.waitKey(0)

        while True:
            cv2.imshow('image', self.frame)
            cv2.namedWindow('image')
            cv2.setMouseCallback('image', self.extract_coordinates)
            while True:
                key = cv2.waitKey(2)
                if key == ord('s'):
                    print(len(self.listRois))
                    cv2.destroyAllWindows()
                    return True

    def extract_coordinates(self, event, x, y, flags, parameters):
        # Record starting (x,y) coordinates on left mouse button click
        if event == cv2.EVENT_LBUTTONDOWN:
            self.image_coordinates = [(x, y)]
            self.x=x
            self.y=y
            self.extract = True

        # Record ending (x,y) coordintes on left mouse bottom release
        elif event == cv2.EVENT_LBUTTONUP:
            self.image_coordinates.append((x, y))
            self.x2=x
            self.y2=y
            aa=(min(self.x,self.x2),min(self.y,self.y2),max(self.x2,self.x),max(self.y2,self.y))
            self.listRois.append(aa)

            # Draw rectangle around ROI
            cv2.rectangle(self.frame, self.image_coordinates[0], self.image_coordinates[1], (0, 255, 0), 2)
            cv2.imshow('image', self.frame)
            #if len(self.listRois)>1:
            #    self.check_if_overlapping(self.listRois[1][0][0],self.listRois[1][0][1],self.listRois[1][1][0],self.listRois[1][1][1])
            #self.image_coordinates = None
            a=3
        # Clear drawing boxes on right mouse button click
        elif event == cv2.EVENT_RBUTTONDOWN:
            self.listRois=list()
            print("ok")
            self.frame=self.save.copy()
            cv2.imshow('image', self.save)

    def check_if_overlapping(self, x, y, w, h):
        for roi in self.listRois:
            return not (roi[0][0]+roi[1][0] < x or roi[0][0] > x+w or roi[0][1] < y+h or roi[0][1]+roi[1][1] > y)

    def overlap(self,frame1, x, y, w, h):
        for roi in self.listRois:
            #sunt inversate, e x1 si y1 jos stanga
            newx1=x
            newx2=x+w
            newy2=y
            newy1=y+h
            x1=roi[0]
            x2=roi[2]
            y2=roi[1]
            y1=roi[3]
            cv2.rectangle(frame1, (x1, y1), (x2, y2), (0, 255, 0), 2)
            if (x1 < newx2 and x2 > newx1 and
                    y1 > newy2 and y2 < newy1):
                return True
        return False

class staticROI(object):
    def __init__(self):
        self.capture = cv2.VideoCapture('fedex.mp4')

        # Bounding box reference points and boolean if we are extracting coordinates
        self.image_coordinates = []
        self.extract = False
        self.selected_ROI = False

        self.update()


    def update(self):
        while True:
            if self.capture.isOpened():
                # Read frame
                (self.status, self.frame) = self.capture.read()
                cv2.imshow('image', self.frame)
                key = cv2.waitKey(2)

                # Crop image
                if key == ord('c'):
                    self.clone = self.frame.copy()
                    cv2.namedWindow('image')
                    cv2.setMouseCallback('image', self.extract_coordinates)
                    while True:
                        key = cv2.waitKey(2)
                        cv2.imshow('image', self.clone)

                        # Crop and display cropped image
                        if key == ord('c'):
                            self.crop_ROI()
                            self.show_cropped_ROI()

                        # Resume video
                        if key == ord('r'):
                            break
                # Close program with keyboard 'q'
                if key == ord('q'):
                    cv2.destroyAllWindows()
                    exit(1)
            else:
                pass

    def extract_coordinates(self, event, x, y, flags, parameters):
        # Record starting (x,y) coordinates on left mouse button click
        if event == cv2.EVENT_LBUTTONDOWN:
            self.image_coordinates = [(x,y)]
            self.extract = True

        # Record ending (x,y) coordintes on left mouse bottom release
        elif event == cv2.EVENT_LBUTTONUP:
            self.image_coordinates.append((x,y))
            self.extract = False

            self.selected_ROI = True

            # Draw rectangle around ROI
            cv2.rectangle(self.clone, self.image_coordinates[0], self.image_coordinates[1], (0,255,0), 2)

        # Clear drawing boxes on right mouse button click
        elif event == cv2.EVENT_RBUTTONDOWN:
            self.clone = self.frame.copy()
            self.selected_ROI = False

    def crop_ROI(self):
        if self.selected_ROI:
            self.cropped_image = self.frame.copy()

            x1 = self.image_coordinates[0][0]
            y1 = self.image_coordinates[0][1]
            x2 = self.image_coordinates[1][0]
            y2 = self.image_coordinates[1][1]

            self.cropped_image = self.cropped_image[y1:y2, x1:x2]

            print('Cropped image: {} {}'.format(self.image_coordinates[0], self.image_coordinates[1]))
        else:
            print('Select ROI to crop before cropping')




    def show_cropped_ROI(self):
        cv2.imshow('cropped image', self.cropped_image)



cap=cv2.VideoCapture("videos/example_03.mp4")

#frame 1
ret1,frame1=cap.read()

RoisClass=Rois()
RoisClass.choose_ROIs(frame1)


#frame 2
ret2,frame2=cap.read()

while cap.isOpened():
    #find diff between frames
    diff = cv2.absdiff(frame1,frame2)

    gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
    blur=cv2.GaussianBlur(gray,(5,5),0)

    #find threshold
    _,thresh=cv2.threshold(blur,20, 255, cv2.THRESH_BINARY)
    #cv2.imshow("feed3", thresh)
    dilated=cv2.dilate(thresh,None, iterations=3)#3 can be change, more is  better

    #cv2.imshow("feed2", dilated)
    contours,_=cv2.findContours(dilated,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)


    for contour in contours:
        (x,y,w,h)=cv2.boundingRect(contour)

        if cv2.contourArea(contour) < 700:
            continue
        if RoisClass.overlap(frame1,x,y,w,h):
            print("OK")
            cv2.rectangle(frame1,(x,y),(x+w,y+h), (0,255,245), 2)


    #cv2.drawContours(frame1,contours,-1,(0,255,0), 2)



    cv2.imshow("feed", frame1)
    frame1=frame2
    ret,frame2=cap.read()







    if cv2.waitKey(40)==27:
        break

cv2.destroyAllWindows()
cap.release()
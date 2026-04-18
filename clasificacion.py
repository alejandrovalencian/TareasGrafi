import cv2 as cv 

rostro = cv.CascadeClassifier('C:\\Users\\Usuario\\Downloads\\haarcascade_frontalface_alt2.xml')
cap = cv.VideoCapture(0)

while True:
    ret, img = cap.read()
    gris = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    rostros = rostro.detectMultiScale(gris, 1.3, 5)

    for(x,y,w,h) in rostros:

        img = cv.rectangle(img, (x,y), (x+w, y+h), (234, 23,23), 5)

        # OJOS
        img = cv.circle(img, (x + int(w*0.3), y + int(h*0.4)) , 30, (255,255,255), -1 )
        img = cv.circle(img, (x + int(w*0.7), y + int(h*0.4)) , 30, (255,255,255), -1 )
        img = cv.circle(img, (x + int(w*0.3), y + int(h*0.4)) , 10, (0,0,0), -1 )
        img = cv.circle(img, (x + int(w*0.7), y + int(h*0.4)) , 10, (0,0,0), -1 )

        # NARIZ DE PERRO
        cv.ellipse(img,(x+int(w*0.5),y+int(h*0.65)),(int(w*0.15),int(h*0.08)),0,0,360,(40,40,40),-1)

        # LENGUA
        cv.ellipse(img,(x+int(w*0.5),y+int(h*0.9)),(int(w*0.12),int(h*0.2)),0,0,360,(203,192,255),-1)

        # OREJA IZQUIERDA
        cv.ellipse(img,(x+int(w*0.15),y-int(h*0.2)),(int(w*0.15),int(h*0.35)),20,0,360,(60,120,180),-1)

        # OREJA DERECHA
        cv.ellipse(img,(x+int(w*0.85),y-int(h*0.2)),(int(w*0.15),int(h*0.35)),-20,0,360,(60,120,180),-1)

        img2 = img[y:y+h,x:x+w]
        cv.imshow('img2', img2)

    cv.imshow('img', img)

    if cv.waitKey(1)== ord('q'):
        break

cap.release()
cv.destroyAllWindows()
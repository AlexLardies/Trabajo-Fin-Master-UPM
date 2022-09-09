from gpiozero import Button, LED
from time import sleep
from pyrebase import pyrebase
import RPi.GPIO as GPIO

#Asignamos los distintos pines a cada led, botón y motor en la raspberry

pasillo_led=21    #Color Rojo | 2 Leds
pasillo_boton=20

salon_led=6       #Color amarillo
salon_m=9
in5=24
in6=25
salon_boton=17

cocina_led=5      #Color Rojo
cocina_boton=4    

baño_led=26       #Color Rojo y cable blanco
baño_boton=27

hab1_led=13       #Color Azul
hab1_m=8
in1=18
in2=23
hab1_boton=22

hab2_led=19       #Color Verde
hab2_m=11
in3=7
in4=12
hab2_boton=16

#Asignamos los pines para los Leds

led_pasillo = LED(pasillo_led)
led_salon = LED(salon_led)
led_cocina = LED(cocina_led)
led_baño = LED(baño_led)
led_hab1 = LED(hab1_led)
led_hab2 = LED(hab2_led)

#Asignamos los pines a los botones

b_pasillo = Button(pasillo_boton)
b_salon = Button(salon_boton)
b_cocina = Button(cocina_boton)
b_baño = Button(baño_boton)
b_hab1 = Button(hab1_boton)
b_hab2 = Button(hab2_boton)


#Configuracion de los GPIO para que coincidan con los de la raspberry
GPIO.setmode(GPIO.BCM)

#Configuracion de los pines como salida para los motores
GPIO.setup(hab1_m, GPIO.OUT)
GPIO.setup(in1, GPIO.OUT)
GPIO.setup(in2, GPIO.OUT)

GPIO.setup(hab2_m, GPIO.OUT)
GPIO.setup(in3, GPIO.OUT)
GPIO.setup(in4, GPIO.OUT)

GPIO.setup(salon_m, GPIO.OUT)
GPIO.setup(in5, GPIO.OUT)
GPIO.setup(in6, GPIO.OUT)

#Definimos las salidas de PWM
pwm_a=GPIO.PWM(hab1_m,100)
pwm_b=GPIO.PWM(hab2_m,100)
pwm_c=GPIO.PWM(salon_m,100)

pwm_a.start(0)
pwm_b.start(0)
pwm_c.start(0)

#Configuramos Firebase para comunicarse con nuestra Database

serviceAccount={
  "type": "service_account",
  "project_id": "tfm-alfred-fcb26",
  "private_key_id": "**********************************",
  "private_key": "-----BEGIN PRIVATE KEY-----\*************************************\n-----END PRIVATE KEY-----\n",
  "client_email": "firebase-adminsdk-r12ui@tfm-alfred-fcb26.iam.gserviceaccount.com",
  "client_id": "******************************",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-r12ui%40tfm-alfred-fcb26.iam.gserviceaccount.com"
}

firebaseConfig = {
    "apiKey": "****************************",
    "authDomain": "tfm-alfred-fcb26.firebaseapp.com",
    "databaseURL": "https://tfm-alfred-fcb26-default-rtdb.firebaseio.com",
    "projectId": "tfm-alfred-fcb26",
    "storageBucket": "tfm-alfred-fcb26.appspot.com",
    "messagingSenderId": "887503443782",
    "appId": "****************************",
    "measurementId": "G-XJHDXXH7WM",
    "serviceAccount": serviceAccount
}


FB = pyrebase.initialize_app(firebaseConfig)

#Definimos las funciones para controlar los motores y las luces

def Encender(led, hab, db):
    led.on()
    data = {"On" : "true"}
    db.child("Home_Automation").child("luces").child(str(hab)).set(data)

def Apagar(led, hab, db):
    led.off()
    data = {"On" : "false"}
    db.child("Home_Automation").child("luces").child(str(hab)).set(data)

def Subir(P, N, hab, db):
    GPIO.output(P, False)
    GPIO.output(N, True)
    data = {"Up" : "true", "Nivel" : "" , "Down" : "false"}
    db.child("Home_Automation").child("persianas").child(str(hab)).set(data)
    
def Bajar(P, N, hab, db):
    GPIO.output(P, True)
    GPIO.output(N, False)
    data = {"Up" : "false", "Nivel" : "" ,"Down" : "true"}
    db.child("Home_Automation").child("persianas").child(str(hab)).set(data)
    
def Parar(P, N, hab, db):
    GPIO.output(P, False)
    GPIO.output(N, False)
    data = {"Up" : "false", "Nivel" : "" , "Down" : "false"}
    db.child("Home_Automation").child("persianas").child(str(hab)).set(data)
    

try:
    while True:
        
        db=FB.database()
        luces=db.child("Home_Automation").child("luces").get()
        persianas=db.child("Home_Automation").child("persianas").get()
        
        l_habs = {}
        l_valores = {}
        
        #Nos guardamos los valores de cada habitación y su valor en la variable l_habs
        for luces in luces.each():
            l_valores=luces.val()
            l_habs[luces.key()]=l_valores["On"]
        
                    
        p_habs = {}
        p_valores = {} 
            
        #Nos guardamos los valores de  UP, DOWN y Nivel en la varialbe p_habs
        for persianas in persianas.each():
            #print(persianas.key(), persianas.val())
            p_valores=persianas.val()
            p_habs[persianas.key()]=p_valores      
        
        #Control de las luces por maquina de estados
        
        if led_pasillo.value == 1 and l_habs["pasillo"]=="false":
            led_pasillo.off()
        elif led_pasillo.value == 0 and l_habs["pasillo"]=="true":
            led_pasillo.on()
        elif led_pasillo.value == 0 and l_habs["pasillo"]=="false":
            b_pasillo.when_pressed= lambda: Encender(led_pasillo, "pasillo", db)
        elif led_pasillo.value == 1 and l_habs["pasillo"]=="true":
            b_pasillo.when_pressed= lambda: Apagar(led_pasillo, "pasillo", db)
            
        if led_salon.value == 1 and l_habs["salón"]=="false":
            led_salon.off()
        elif led_salon.value == 0 and l_habs["salón"]=="true":
            led_salon.on()
        elif led_salon.value == 0 and l_habs["salón"]=="false":
            b_salon.when_pressed= lambda: Encender(led_salon, "salón", db)
        elif led_salon.value == 1 and l_habs["salón"]=="true":
            b_salon.when_pressed= lambda: Apagar(led_salon, "salón", db)
          
        if p_habs["salón"]["Nivel"] == "":
            if p_habs["salón"]["Up"] == "true":
                Subir(in5, in6, "salón", db)
                pwm_c.ChangeDutyCycle(int(10))
            elif p_habs["salón"]["Down"] == "true":
                Bajar(in5, in6, "salón", db)
                pwm_c.ChangeDutyCycle(int(10))
            elif p_habs["salón"]["Up"] == "false" and p_habs["salón"]["Down"] == "false":
                Parar(in5, in6, "salón", db)
                pwm_c.ChangeDutyCycle(int(10))
        else:
            nivel=float(p_habs["salón"]["Nivel"])
            tiempo=2+(nivel*2/100)
            if p_habs["salón"]["Up"] == "true":
                Subir(in5, in6, "salón", db)
                pwm_c.ChangeDutyCycle(int(10))
                sleep(tiempo)
                Parar(in5, in6, "salón", db)
            elif p_habs["salón"]["Down"] == "true":
                Bajar(in5, in6, "salón", db)
                pwm_c.ChangeDutyCycle(int(10))
                sleep(tiempo)
                Parar(in5, in6, "salón", db)
            
        if led_baño.value == 1 and l_habs["baño"]=="false":
            led_baño.off()
        elif led_baño.value == 0 and l_habs["baño"]=="true":
            led_baño.on()
        elif led_baño.value == 0 and l_habs["baño"]=="false":
            b_baño.when_pressed= lambda: Encender(led_baño, "baño", db)
        elif led_baño.value == 1 and l_habs["baño"]=="true":
            b_baño.when_pressed= lambda: Apagar(led_baño, "baño", db)
            
            
        if led_cocina.value == 1 and l_habs["cocina"]=="false":
            led_cocina.off()
        elif led_cocina.value == 0 and l_habs["cocina"]=="true":
            led_cocina.on()
        elif led_cocina.value == 0 and l_habs["cocina"]=="false":
            b_cocina.when_pressed= lambda: Encender(led_cocina, "cocina", db)
        elif led_cocina.value == 1 and l_habs["cocina"]=="true":
            b_cocina.when_pressed= lambda: Apagar(led_cocina, "cocina", db)
            
        
        if led_hab1.value == 1 and l_habs["habitacion 1"]=="false":
            led_hab1.off()
        elif led_hab1.value == 0 and l_habs["habitacion 1"]=="true":
            led_hab1.on()
        elif led_hab1.value == 0 and l_habs["habitacion 1"]=="false":
            b_hab1.when_pressed= lambda: Encender(led_hab1, "habitacion 1", db)
        elif led_hab1.value == 1 and l_habs["habitacion 1"]=="true":
            b_hab1.when_pressed= lambda: Apagar(led_hab1, "habitacion 1", db)
         
        if p_habs["habitacion 1"]["Nivel"] == "":   
            if p_habs["habitacion 1"]["Up"] == "true" and p_habs["habitacion 1"]["Down"] == "false":
                Subir(in1, in2, "habitacion 1", db)
                pwm_a.ChangeDutyCycle(int(10))
            elif p_habs["habitacion 1"]["Up"] == "false" and p_habs["habitacion 1"]["Down"] == "true":
                Bajar(in1, in2, "habitacion 1", db)
                pwm_a.ChangeDutyCycle(int(10))
            elif p_habs["habitacion 1"]["Up"] == "false" and p_habs["habitacion 1"]["Down"] == "false":
                Parar(in1, in2, "habitacion 1", db)
                pwm_a.ChangeDutyCycle(int(10))
        else:
            nivel=float(p_habs["habitacion 1"]["Nivel"])
            tiempo=2+(nivel*2/100)
            if p_habs["habitacion 1"]["Up"] == "true" and p_habs["habitacion 1"]["Down"] == "false":
                Subir(in1, in2, "habitacion 1", db)
                pwm_a.ChangeDutyCycle(int(10))
                sleep(tiempo)
                Parar(in1, in2, "habitacion 1", db)
            elif p_habs["habitacion 1"]["Up"] == "false" and p_habs["habitacion 1"]["Down"] == "true":
                Bajar(in1, in2, "habitacion 1", db)
                pwm_a.ChangeDutyCycle(int(10))
                sleep(tiempo)
                Parar(in1, in2, "habitacion 1", db)
            
            
        if led_hab2.value == 1 and l_habs["habitacion 2"]=="false":
            led_hab2.off()
        elif led_hab2.value == 0 and l_habs["habitacion 2"]=="true":
            led_hab2.on()
        elif led_hab2.value == 0 and l_habs["habitacion 2"]=="false":
            b_hab2.when_pressed= lambda: Encender(led_hab2, "habitacion 2", db)
        elif led_hab2.value == 1 and l_habs["habitacion 2"]=="true":
            b_hab2.when_pressed= lambda: Apagar(led_hab2, "habitacion 2", db)
            
        if p_habs["habitacion 2"]["Nivel"] == "":   
            if p_habs["habitacion 2"]["Up"] == "true" and p_habs["habitacion 2"]["Down"] == "false":
                Subir(in3, in4, "habitacion 2", db)
                pwm_b.ChangeDutyCycle(int(8))
            elif p_habs["habitacion 2"]["Up"] == "false" and p_habs["habitacion 2"]["Down"] == "true":
                Bajar(in3, in4, "habitacion 2", db)
                pwm_b.ChangeDutyCycle(int(8))
            elif p_habs["habitacion 2"]["Up"] == "false" and p_habs["habitacion 2"]["Down"] == "false":
                Parar(in3, in4, "habitacion 2", db)
                pwm_b.ChangeDutyCycle(int(8))
        else:
            nivel=float(p_habs["habitacion 2"]["Nivel"])
            tiempo=2+(nivel*2/100)
            if p_habs["habitacion 2"]["Up"] == "true" and p_habs["habitacion 2"]["Down"] == "false":
                Subir(in3, in4, "habitacion 2", db)
                pwm_b.ChangeDutyCycle(int(8))
                sleep(tiempo)
                Parar(in3, in4, "habitacion 2", db)
            elif p_habs["habitacion 2"]["Up"] == "false" and p_habs["habitacion 2"]["Down"] == "true":
                Bajar(in3, in4, "habitacion 2", db)
                pwm_b.ChangeDutyCycle(int(8))
                sleep(tiempo)
                Parar(in3, in4, "habitacion 2", db)
                      
            
        sleep(0.2)
        
            
except KeyboardInterrupt:
    print("usuario interrupt")

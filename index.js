'use strict';
 
const functions = require('firebase-functions');
const {WebhookClient} = require('dialogflow-fulfillment');
const {Card, Suggestion} = require('dialogflow-fulfillment');
const admin= require ('firebase-admin');

const firebaseConfig = {
    "apiKey": "********************************",
    "authDomain": "tfm-alfred-fcb26.firebaseapp.com",
    "databaseURL": "https://tfm-alfred-fcb26-default-rtdb.firebaseio.com",
    "projectId": "tfm-alfred-fcb26",
    "storageBucket": "tfm-alfred-fcb26.appspot.com",
    "messagingSenderId": "887503443782",
    "appId": "***********************",
    "measurementId": "G-XJHDXXH7WM"
  };

const serviceAccount={
  "type": "service_account",
  "project_id": "tfm-alfred-fcb26",
  "private_key_id": "58c3bc3497588b0db44b64ce2e420c934ff0e305",
  "private_key": "-----BEGIN PRIVATE KEY-----\*****************/-----END PRIVATE KEY-----\n",
  "client_email": "firebase-adminsdk-r12ui@tfm-alfred-fcb26.iam.gserviceaccount.com",
  "client_id": "117917874725437053562",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-r12ui%40tfm-alfred-fcb26.iam.gserviceaccount.com"
};

admin.initializeApp({
   FIREBASE_CONFIG: firebaseConfig,
   credential:admin.credential.cert(serviceAccount),
   databaseURL:'ws://tfm-alfred-fcb26-default-rtdb.firebaseio.com'
 });


process.env.DEBUG = 'dialogflow:debug'; // enables lib debugging statements
 
exports.dialogflowFirebaseFulfillment = functions.https.onRequest((request, response) => {
  const agent = new WebhookClient({ request, response });

  function delay(time) {
	return new Promise(resolve => setTimeout(resolve, time));
  } 

  function welcome(agent) {
    agent.add(`Welcome to my agent!`);
  }
 
  function fallback(agent) {
    agent.add(`I didn't understand`);
    agent.add(`I'm sorry, can you try again?`);
  }
  
 function On_luces(agent){
   const on_luces=agent.parameters.on_luces;
   const actuadores =agent.parameters.actuadores;
   const zona=agent.parameters.zonas_casa;
   return admin.database().ref('/Home_Automation/'+actuadores+'/'+zona+'/').set({
       On:on_luces
     });

 }
  
 function Off_luces(agent){
   const off_luces=agent.parameters.off_luces;
   const actuadores =agent.parameters.actuadores;
   const zona=agent.parameters.zonas_casa;
   return admin.database().ref('/Home_Automation/'+actuadores+'/'+zona+'/').set({
       On:off_luces
     });

 }

 function On_persianas(agent){
   const on_persianas=agent.parameters.on_persianas;
   const actuadores =agent.parameters.actuadores;
   const zona=agent.parameters.zonas_casa;
   const nivel=agent.parameters.nivel;
   
   if (zona == 'cocina' || zona == 'baño'){
     agent.add('No hay persianas disponibles ni en el baño ni en la cocina');
   } else {
     return admin.database().ref('/Home_Automation/'+actuadores+'/'+zona+'/').set({
       Up:on_persianas,
       Nivel:nivel,
       Down: "false"
       });  
   }
   
   if (nivel == 0) {
	delay(10000);
   } else { delay(100*nivel);
   }
   
   return admin.database().ref('/Home_Automation/'+actuadores+'/'+zona+'/').set({
       Up:"false",
       Nivel:nivel,
       Down: "false"
       });
 }  
  
 function Off_persianas(agent){
   const off_persianas=agent.parameters.off_persianas;
   const actuadores =agent.parameters.actuadores;
   const zona=agent.parameters.zonas_casa;
   const nivel=agent.parameters.nivel;
   
   if (zona == 'cocina' || zona == 'baño'){
     agent.add('No hay persianas disponibles ni en el baño ni en la cocina');
   } else {
     return admin.database().ref('/Home_Automation/'+actuadores+'/'+zona+'/').set({
       Up:"false",
       Nivel:nivel,
       Down: off_persianas
       });
   }
   
     if (nivel == 0) {
      delay(10000);
     } else { 
       delay(100*nivel);
       }
   	  return admin.database().ref('/Home_Automation/'+actuadores+'/'+zona+'/').set({
         Up:"false",
         Nivel:nivel,
         Down: "false"
         });

 }
  
  
  let intentMap = new Map();
  intentMap.set('Default Welcome Intent', welcome);
  intentMap.set('Default Fallback Intent', fallback);
  intentMap.set('On_luces',On_luces);
  intentMap.set('Off_luces',Off_luces);
  intentMap.set('On_persianas',On_persianas);
  intentMap.set('Off_persianas',Off_persianas);
  agent.handleRequest(intentMap);
});


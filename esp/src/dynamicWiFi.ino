

void serverSetup(){
    WiFi.softAP(ssid, pass);                      // setup ssid and pass
    delay(100);                                   // IMPORTANT wait
    WiFi.softAPConfig(local_ip, gateway, subnet); // setup ip, gateway, subnet_mask
    delay(100);                                   // IMPORTANT wait

    // bind handler
    server.on("/", HTTP_GET, handle_OnRootGet);
	server.on("/WiFi", HTTP_GET, handle_OnWiFiGet);
    server.on("/WiFi", HTTP_POST, handle_OnWiFiPost);
	server.on("/Broker", HTTP_GET, handle_OnBrokerGet);
    server.on("/Broker", HTTP_POST, handle_OnBrokerPost);
    server.onNotFound(handle_NotFound);

    server.begin(); // launch Server

    /* Show Infomation */
    Serial.print("SSID: ");
    Serial.println(ssid);
    Serial.print("AP IP address: ");
    Serial.println(local_ip);
    Serial.println("HTTP server started");
}

void clientSetup(){
    File f = SPIFFS.open(settings, "r");
    String ssid = f.readStringUntil('\n');
    String pass = f.readStringUntil('\n');
    f.close();

    ssid.trim();
    pass.trim();

    Serial.println("SSID: " + ssid);
    Serial.println("PASS: " + pass);

    WiFi.begin(ssid.c_str(), pass.c_str());

    while (WiFi.status() != WL_CONNECTED){
        delay(500);
        Serial.print(".");
    }
    Serial.print(" CONNECTED!");
}

void handle_OnRootGet(){
    String html = "<!DOCTYPE html><html><head>";
	html += "<meta name=\"viewport\" content=\"width=device-width,initial-scale=1.0\">";
	html += "<meta charset=\"UTF-8\"><title> ESP32 Setting Page </title></head>";
	html += "<body style=\"max-width: 600px; margin: auto;\">";
	html += "<h1 style=\"text-align: center;\">Select Your Settings</h1>";
	html += "<div style=\"text-align: center;\">";
	html += "<button type=\"button\" onclick=\"location.href='./WiFi'\""; 
	html += "style=\"text-align: center; font-size: 16pt; font-weight: bold; width: 200px; height: 50px;\">";
	html += "WiFi Setting</button></div><br>";
	html += "<div style=\"text-align: center;\">";
	html += "<button type=\"button\" onclick=\"location.href='./Broker'\"";
	html += "style=\"text-align: center; font-size: 16pt; font-weight: bold; width: 200px; height: 50px;\">";
	html += "Broker Setting</button></div></body></html>";
    server.send(200, "text/html", html);
}

void handle_OnWiFiGet(){
    String html = "<!DOCTYPE html><html><head><meta name=\"viewport\" content=\"width=device-width,initial-scale=1.0\"><meta charset=\"UTF-8\"><title> WiFi Setting </title></head>";
    html += "<body style=\"max-width: 600px; margin: auto;\">";
    html += "<h1 style=\"text-align: center;\">ESP32 WiFi Settings</h1>";
    html += "<h3 style=\"text-align: center; color: red; font-weight: bold;\"> Be careful! </br> Only 2.4GHz WiFi can be connected! </h3>";
    html += "<form method='post' style=\"text-align: center;\">";
    html += "<input type='text' name='ssid' placeholder='ssid'></br></br>";
    html += "<input type='text' name='pass' placeholder='pass'></br></br>";
    html += "<input type='submit'><br>";
    html += "</form></body></html>";
    server.send(200, "text/html", html);
}

void handle_OnWiFiPost(){
    String ssid = server.arg("ssid");
    String pass = server.arg("pass");

    Serial.println(ssid);

    File f = SPIFFS.open(settings, "w");
    f.println(ssid);
    f.println(pass);
    f.close();

    String html = "<!DOCTYPE html><html><head><meta name=\"viewport\" content=\"width=device-width,initial-scale=1.0\"><meta charset=\"UTF-8\"><title> WiFi Setting </title></head>";
    html += "<body style=\"max-width: 600px; margin: auto;\">";
    html += "<h1 style=\"text-align: center;\">ESP32 WiFi Settings</h1>";
    html += "<h3 style=\"text-align: center;\"> Complete! </h3>";
    html += ssid + "<br>";
    html += pass + "<br>";
    html += "</body></html>";
    server.send(200, "text/html", html);
}

void handle_OnBrokerGet(){
    String html = "<!DOCTYPE html><html><head><meta name=\"viewport\" content=\"width=device-width,initial-scale=1.0\"><meta charset=\"UTF-8\"><title> Broker Setting </title></head>";
    html += "<body style=\"max-width: 600px; margin: auto;\">";
    html += "<h1 style=\"text-align: center;\">ESP32 Broker Settings</h1>";
    html += "<form method='post' style=\"text-align: center;\">";
    html += "<input type='text' name='host' placeholder='host'></br></br>";
    html += "<input type='text' name='port' placeholder='port'></br></br>";
    html += "<input type='submit'><br>";
    html += "</form></body></html>";
    server.send(200, "text/html", html);
}

void handle_OnBrokerPost(){
    String host = server.arg("host");
    String port = server.arg("port");

    Serial.println(host);

    File f = SPIFFS.open(broker_settings, "w");
    f.println(host);
    f.println(port);
    f.close();

    String html = "<!DOCTYPE html><html><head><meta name=\"viewport\" content=\"width=device-width,initial-scale=1.0\"><meta charset=\"UTF-8\"><title> Broker Setting </title></head>";
    html += "<body style=\"max-width: 600px; margin: auto;\">";
    html += "<h1 style=\"text-align: center;\">ESP32 Broker Settings</h1>";
    html += "<h3 style=\"text-align: center;\"> Complete! </h3>";
    html += host + "<br>";
    html += port + "<br>";
    html += "</body></html>";
    server.send(200, "text/html", html);
}

void handle_NotFound()
{
    server.send(404, "text/plain", "Not found");
}